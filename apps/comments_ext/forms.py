from django import forms
from django.contrib.comments.forms import CommentForm

from comments_ext.models import CommentWithPrivate


class CommentFormWithPrivate(CommentForm):
    is_private = forms.BooleanField(required=False)

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return CommentWithPrivate

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the title field
        data = super(CommentFormWithPrivate, self).get_comment_create_data()
        data['is_private'] = self.cleaned_data['is_private']
        return data