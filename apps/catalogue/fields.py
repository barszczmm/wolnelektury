# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.fields.files import FieldFile
from catalogue import app_settings
from catalogue.utils import remove_zip, truncate_html_words
from celery.task import Task, task
from waiter.utils import clear_cache


class EbookFieldFile(FieldFile):
    """Represents contents of an ebook file field."""

    def build(self):
        """Build the ebook immediately."""
        return self.field.builder.build(self)

    def build_delay(self):
        """Builds the ebook in a delayed task."""
        return self.field.builder.delay(self.instance, self.field.attname)


class EbookField(models.FileField):
    """Represents an ebook file field, attachable to a model."""
    attr_class = EbookFieldFile

    def __init__(self, format_name, *args, **kwargs):
        super(EbookField, self).__init__(*args, **kwargs)
        self.format_name = format_name

    @property
    def builder(self):
        """Finds a celery task suitable for the format of the field."""
        return BuildEbook.for_format(self.format_name)

    def contribute_to_class(self, cls, name):
        super(EbookField, self).contribute_to_class(cls, name)

        def has(model_instance):
            return bool(getattr(model_instance, self.attname, None))
        has.__doc__ = None
        has.__name__ = "has_%s" % self.attname
        has.short_description = self.name
        has.boolean = True
        setattr(cls, 'has_%s' % self.attname, has)


class BuildEbook(Task):
    formats = {}

    @classmethod
    def register(cls, format_name):
        """A decorator for registering subclasses for particular formats."""
        def wrapper(builder):
            cls.formats[format_name] = builder
            return builder
        return wrapper

    @classmethod
    def for_format(cls, format_name):
        """Returns a celery task suitable for specified format."""
        return cls.formats.get(format_name, BuildEbookTask)

    @staticmethod
    def transform(wldoc, fieldfile):
        """Transforms an librarian.WLDocument into an librarian.OutputFile.

        By default, it just calls relevant wldoc.as_??? method.

        """
        return getattr(wldoc, "as_%s" % fieldfile.field.format_name)()

    def run(self, obj, field_name):
        """Just run `build` on FieldFile, can't pass it directly to Celery."""
        return self.build(getattr(obj, field_name))

    def build(self, fieldfile):
        book = fieldfile.instance
        out = self.transform(book.wldocument(), fieldfile)
        fieldfile.save(None, File(open(out.get_filename())), save=False)
        if book.pk is not None:
            type(book).objects.filter(pk=book.pk).update(**{
                fieldfile.field.attname: fieldfile
            })
        if fieldfile.field.format_name in app_settings.FORMAT_ZIPS:
            remove_zip(app_settings.FORMAT_ZIPS[fieldfile.field.format_name])
# Don't decorate BuildEbook, because we want to subclass it.
BuildEbookTask = task(BuildEbook, ignore_result=True)


@BuildEbook.register('txt')
@task(ignore_result=True)
class BuildTxt(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_text()


@BuildEbook.register('pdf')
@task(ignore_result=True)
class BuildPdf(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_pdf(morefloats=settings.LIBRARIAN_PDF_MOREFLOATS,
            cover=True)

    def build(self, fieldfile):
        BuildEbook.build(self, fieldfile)
        clear_cache(fieldfile.instance.slug)


@BuildEbook.register('epub')
@task(ignore_result=True)
class BuildEpub(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_epub(cover=True)


@BuildEbook.register('html')
@task(ignore_result=True)
class BuildHtml(BuildEbook):
    def build(self, fieldfile):
        from django.core.files.base import ContentFile
        from fnpdjango.utils.text.slughifi import slughifi
        from sortify import sortify
        from librarian import html
        from catalogue.models import Fragment, Tag

        book = fieldfile.instance

        meta_tags = list(book.tags.filter(
            category__in=('author', 'epoch', 'genre', 'kind')))
        book_tag = book.book_tag()

        html_output = self.transform(
                        book.wldocument(parse_dublincore=False),
                        fieldfile)
        if html_output:
            fieldfile.save(None, ContentFile(html_output.get_string()),
                    save=False)
            type(book).objects.filter(pk=book.pk).update(**{
                fieldfile.field.attname: fieldfile
            })

            # get ancestor l-tags for adding to new fragments
            ancestor_tags = []
            p = book.parent
            while p:
                ancestor_tags.append(p.book_tag())
                p = p.parent

            # Delete old fragments and create them from scratch
            book.fragments.all().delete()
            # Extract fragments
            closed_fragments, open_fragments = html.extract_fragments(fieldfile.path)
            for fragment in closed_fragments.values():
                try:
                    theme_names = [s.strip() for s in fragment.themes.split(',')]
                except AttributeError:
                    continue
                themes = []
                for theme_name in theme_names:
                    if not theme_name:
                        continue
                    tag, created = Tag.objects.get_or_create(
                                        slug=slughifi(theme_name),
                                        category='theme')
                    if created:
                        tag.name = theme_name
                        tag.sort_key = sortify(theme_name.lower())
                        tag.save()
                    themes.append(tag)
                if not themes:
                    continue

                text = fragment.to_string()
                short_text = truncate_html_words(text, 15)
                if text == short_text:
                    short_text = ''
                new_fragment = Fragment.objects.create(anchor=fragment.id, 
                        book=book, text=text, short_text=short_text)

                new_fragment.save()
                new_fragment.tags = set(meta_tags + themes + [book_tag] + ancestor_tags)
            book.html_built.send(sender=book)
            return True
        return False


class OverwritingFieldFile(FieldFile):
    """
        Deletes the old file before saving the new one.
    """

    def save(self, name, content, *args, **kwargs):
        leave = kwargs.pop('leave', None)
        # delete if there's a file already and there's a new one coming
        if not leave and self and (not hasattr(content, 'path') or
                                   content.path != self.path):
            self.delete(save=False)
        return super(OverwritingFieldFile, self).save(
                name, content, *args, **kwargs)


class OverwritingFileField(models.FileField):
    attr_class = OverwritingFieldFile


try:
    # check for south
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([
        (
            [EbookField],
            [],
            {'format_name': ('format_name', {})}
        )
    ], ["^catalogue\.fields\.EbookField"])
    add_introspection_rules([], ["^catalogue\.fields\.OverwritingFileField"])
