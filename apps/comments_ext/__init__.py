from comments_ext.models import CommentWithPrivate
from comments_ext.forms import CommentFormWithPrivate


def get_model():
    return CommentWithPrivate


def get_form():
    return CommentFormWithPrivate