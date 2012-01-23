from functools import wraps

from django.http import (HttpResponse, HttpResponseRedirect,
        HttpResponseForbidden)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.cache import patch_vary_headers
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from django.utils.http import urlquote_plus
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.vary import vary_on_headers


class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj

# shortcut for JSON reponses
class JSONResponse(HttpResponse):
    def __init__(self, data={}, callback=None, **kwargs):
        # get rid of mimetype
        kwargs.pop('mimetype', None)
        data = simplejson.dumps(data)
        if callback:
            data = callback + "(" + data + ");" 
        super(JSONResponse, self).__init__(data, mimetype="application/json", **kwargs)


def method_decorator(function_decorator):
    """Converts a function decorator to a method decorator.

    It just makes it ignore first argument.
    """
    def decorator(method):
        @wraps(method)
        def wrapped_method(self, *args, **kwargs):
            def function(*fargs, **fkwargs):
                return method(self, *fargs, **fkwargs)
            return function_decorator(function)(*args, **kwargs)
        return wrapped_method
    return decorator


def require_login(request):
    """Return 403 if request is AJAX. Redirect to login page if not."""
    if request.is_ajax():
        return HttpResponseForbidden('Not logged in')
    else:
        return HttpResponseRedirect('/uzytkownicy/zaloguj')# next?=request.build_full_path())


class AjaxableFormView(object):
    """Subclass this to create an ajaxable view for any form.

    In the subclass, provide at least form_class.

    """
    form_class = None
    # override to customize form look
    template = "ajaxable/form.html"
    submit = _('Send')
    
    title = ''
    success_message = ''
    POST_login = False
    formname = "form"
    form_prefix = None
    full_template = "ajaxable/form_on_page.html"

    @method_decorator(vary_on_headers('X-Requested-With'))
    def __call__(self, request, *args, **kwargs):
        """A view displaying a form, or JSON if request is AJAX."""
        form_args, form_kwargs = self.form_args(request, *args, **kwargs)
        if self.form_prefix:
            form_kwargs['prefix'] = self.form_prefix

        if request.method == "POST":
            # do I need to be logged in?
            if self.POST_login and not request.user.is_authenticated():
                return require_login(request)

            form_kwargs['data'] = request.POST
            form = self.form_class(*form_args, **form_kwargs)
            if form.is_valid():
                add_args = self.success(form, request)
                redirect = request.GET.get('next')
                if not request.is_ajax() and redirect:
                    return HttpResponseRedirect(urlquote_plus(
                            redirect, safe='/?=&'))
                response_data = {'success': True, 
                    'message': self.success_message, 'redirect': redirect}
                if add_args:
                    response_data.update(add_args)
            elif request.is_ajax():
                # Form was sent with errors. Send them back.
                if self.form_prefix:
                    errors = {}
                    for key, value in form.errors.items():
                        errors["%s-%s" % (self.form_prefix, key)] = value
                else:
                    errors = form.errors
                response_data = {'success': False, 'errors': errors}
            if request.is_ajax():
                return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))
        else:
            if (self.POST_login and not request.user.is_authenticated()
                    and not request.is_ajax()):
                return require_login(request)

            form = self.form_class(*form_args, **form_kwargs)
            response_data = None

        template = self.template if request.is_ajax() else self.full_template
        context = {
                self.formname: form, 
                "title": self.title,
                "submit": self.submit,
                "response_data": response_data,
                "ajax_template": self.template,
                "view_args": args,
                "view_kwargs": kwargs,
            }
        context.update(self.extra_context())
        return render_to_response(template, context,
            context_instance=RequestContext(request))

    def form_args(self, request, *args, **kwargs):
        """Override to parse view args and give additional args to the form."""
        return (), {}

    def extra_context(self):
        """Override to pass something to template."""
        return {}

    def success(self, form, request):
        """What to do when the form is valid.
        
        By default, just save the form.

        """
        return form.save(request)