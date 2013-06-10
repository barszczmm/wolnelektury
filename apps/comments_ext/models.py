# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.models import Comment


class CommentWithPrivate(Comment):
    is_private = models.BooleanField(u'prywatny', default=False,
        help_text=u'zaznacz to pole aby komentarz był widoczny tylko dla zalogowanych użytkowników')

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')