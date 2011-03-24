import os

from DateTime import DateTime
from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_get
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import getSecurityManager
from App.config import getConfiguration

from Products.PageTemplates.Expressions import SecureModuleImporter

from chameleon.tales import StringExpr
from chameleon.tales import NotExpr
from chameleon.tales import PythonExpr

from z3c.pt import pagetemplate
from z3c.pt import expressions

from .expressions import PathExpr
from .expressions import ProviderExpr
from .expressions import NocallExpr
from .expressions import ExistsExpr
from .expressions import PythonExpr as SecurePythonExpr


EXTRA_CONTEXT_KEY = '__five_pt_extra_context'


def get_physical_root(context):
    method = aq_get(context, 'getPhysicalRoot', None)
    if method is not None:
        return method()


def same_type(arg1, *args):
    """Compares the class or type of two or more objects. Copied from
    RestrictedPython.
    """
    t = getattr(arg1, '__class__', type(arg1))
    for arg in args:
        if getattr(arg, '__class__', type(arg)) is not t:
            return False
    return True


def test(condition, a, b):
    if condition:
        return a
    return b


class BaseTemplateBase(pagetemplate.BaseTemplate):
    """Base for Zope 2-compatible page template classes."""

    utility_builtins = {}
    encoding = 'utf-8'

    expression_types = {
        'python': SecurePythonExpr,
        'string': StringExpr,
        'not': NotExpr,
        'exists': ExistsExpr,
        'path': PathExpr,
        'provider': ProviderExpr,
        'nocall': NocallExpr,
        }

    # We enable template reload setting in application debug-mode
    if getConfiguration().debug_mode:
        auto_reload = True

    def render_macro(self, macro, parameters=None, **kw):
        context = self._pt_get_context(None, None)

        if parameters is not None:
            context.update(parameters)

        return super(BaseTemplate, self).render_macro(
            macro, parameters=context, **kw)

    def _pt_get_context(self, instance, request, kwargs={}):
        extra_context = kwargs.pop(EXTRA_CONTEXT_KEY, {})
        namespace = dict(self.utility_builtins)

        if instance is not None:
            # instance namespace overrides utility_builtins
            context = aq_parent(instance)
            namespace.update(
                context=context,
                request=request or aq_get(instance, 'REQUEST', None),
                template=self,
                here=context,
                container=context,
                nothing=None,
                same_type=same_type,
                test=test,
                root=get_physical_root(context),
                user=getSecurityManager().getUser(),
                modules=SecureModuleImporter,
                DateTime=DateTime,
                options=kwargs)

        # extra_context (from pt_render()) overrides the default namespace
        namespace.update(extra_context)

        return namespace

class BaseTemplate(BaseTemplateBase):
    """Zope 2-compatible page template class."""

    def __init__(self, body, *args, **kw):
        super(BaseTemplate, self).__init__(body, *args, **kw)
        # keep the body for comparison and caching purposes
        self.body = body

class BaseTemplateFile(BaseTemplateBase, pagetemplate.BaseTemplateFile):
    """Zope 2-compatible page template file class."""


class ViewPageTemplate(pagetemplate.ViewPageTemplate, BaseTemplateBase):

    expression_types = {
        'python': PythonExpr,
        'string': StringExpr,
        'not': NotExpr,
        'exists': ExistsExpr,
        'path': PathExpr,
        'provider': ProviderExpr,
        'nocall': NocallExpr,
        }

    encoding = 'UTF-8'

    def _pt_get_context(self, view, request, kwargs):
        if view is None:
            namespace = {}
        else:
            try:
                request = request or view.request
                context = aq_inner(view.context)
            except AttributeError:
                """This may happen with certain dynamically created
                classes,
                e.g. ``plone.app.form._named.GeneratedClass``.
                """
                view = view.context
                request = view.request
                context = aq_inner(view.context)

            namespace = dict(
                context=context,
                request=request,
                view=view,
                template=self,
                here=context,
                container=context,
                nothing=None,
                root=get_physical_root(context),
                user=getSecurityManager().getUser(),
                modules=SecureModuleImporter,
                views=ViewMapper(context, request),
                options=kwargs)

        return namespace


class ViewPageTemplateFile(ViewPageTemplate,
                           pagetemplate.ViewPageTemplateFile):
    """If ``filename`` is a relative path, the module path of the
    class where the instance is used to get an absolute path."""

    def getId(self):
        return os.path.basename(self.filename)

    id = property(getId)
