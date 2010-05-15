import os

from DateTime import DateTime
from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_get
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl import getSecurityManager
from Products.PageTemplates.Expressions import SecureModuleImporter

from z3c.pt import pagetemplate

def get_physical_root(context):
    method = aq_get(context, 'getPhysicalRoot', None)
    if method is not None:
        return method()

def test(condition, a, b):
    if condition:
        return a
    return b

class BaseTemplate(pagetemplate.BaseTemplate):
    """Zope 2-compatible page template class."""

    utility_builtins = {}
    encoding = 'utf-8'

    def render_macro(self, macro, parameters=None, **kw):
        context = self._pt_get_context(None, None)

        if parameters is not None:
            context.update(parameters)

        return super(BaseTemplate, self).render_macro(
            macro, parameters=context, **kw)

    def _pt_get_context(self, instance, request, kwargs={}):
        if instance is None:
            namespace = {}
        else:
            context = aq_parent(instance)
            namespace = dict(
                context=context,
                request=request or aq_get(instance, 'REQUEST'),
                template=self,
                here=context,
                container=context,
                nothing=None,
                test=test,
                path=pagetemplate.evaluate_path,
                exists=pagetemplate.evaluate_exists,
                root=get_physical_root(context),
                user=getSecurityManager().getUser(),
                modules=SecureModuleImporter,
                DateTime=DateTime,
                options=kwargs)

        for name, value in self.utility_builtins.items():
            namespace.setdefault(name, value)

        return namespace

class BaseTemplateFile(BaseTemplate, pagetemplate.BaseTemplateFile):
    """Zope 2-compatible page template file class."""

class ViewPageTemplate(pagetemplate.ViewPageTemplate):

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
                path=pagetemplate.evaluate_path,
                exists=pagetemplate.evaluate_exists,
                root=get_physical_root(context),
                user=getSecurityManager().getUser(),
                modules=SecureModuleImporter,
                views=ViewMapper(context, request),
                options=kwargs)

        return namespace

class ViewPageTemplateFile(ViewPageTemplate, pagetemplate.ViewPageTemplateFile):
    """If ``filename`` is a relative path, the module path of the
    class where the instance is used to get an absolute path."""

    def getId(self):
        return os.path.basename(self.filename)

    id = property(getId)
