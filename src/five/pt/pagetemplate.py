import os
import sys

from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_get
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.PageTemplates.Expressions import SecureModuleImporter

from z3c.pt import pagetemplate

def get_physical_root(context):
    method = aq_get(context, 'getPhysicalRoot', None)
    if method is not None:
        return method()

class FiveTemplateFile(pagetemplate.PageTemplateFile.template_class):
    utility_builtins = {}

    def prepare_builtins(self, kwargs):
        for key, value in self.utility_builtins.items():
            kwargs.setdefault(key, value)

    def render_macro(self, macro, global_scope=False, parameters=None):
        if parameters is None:
            parameters = {}
        self.prepare_builtins(parameters)
        return super(FiveTemplateFile, self).render_macro(
            macro, global_scope=global_scope, parameters=parameters)

class PageTemplateFile(pagetemplate.PageTemplateFile):
    template_class = FiveTemplateFile
    
    def bind(self, parent, macro=None, global_scope=True):
        context = aq_parent(parent)
        request = aq_get(parent, 'REQUEST')
        root = get_physical_root(context)

        template = self.template

        def render(**kwargs):
            parameters = dict(
                context=context,
                request=request,
                template=parent,
                here=context,
                container=context,
                nothing=None,
                root=root,
                modules=SecureModuleImporter,
                options=kwargs)

            template.prepare_builtins(parameters)
            
            if macro is None:
                return template.render(**parameters)
            else:
                return template.render_macro(
                    macro, global_scope=global_scope, parameters=parameters)
            
        return render

    def __call__(self, parent, **kwargs):
        template = self.bind(parent)
        return template(**kwargs)

class ViewPageTemplate(pagetemplate.ViewPageTemplate):
    def bind(self, view, request=None, macro=None, global_scope=True):
        context = aq_inner(view.context)
        request = view.request
        root = get_physical_root(context)

        def render(**kwargs):
            parameters = dict(
                view=view,
                context=context,
                request=request,
                template=self,
                here=context,
                container=context,
                nothing=None,
                root=root,
                modules=SecureModuleImporter,
                views=ViewMapper(context, request),
                options=kwargs)

            if macro is None:
                return self.template.render(**parameters)
            else:
                return self.template.render_macro(
                    macro, global_scope=global_scope, parameters=parameters)
            
        return render

class ViewPageTemplateFile(ViewPageTemplate, pagetemplate.ViewPageTemplateFile):
    """If ``filename`` is a relative path, the module path of the
    class where the instance is used to get an absolute path."""

    def getId(self):
        return os.path.basename(self.filename)
    
    id = property(getId)
