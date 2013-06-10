from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.models import Comment


class CommentWithPrivate(Comment):
    is_private = models.BooleanField(_('is private'), default=False)