import os
import sys

from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_get
from Acquisition import aq_inner

from Products.PageTemplates.Expressions import SecureModuleImporter

from z3c.pt import pagetemplate

class ViewPageTemplate(pagetemplate.ViewPageTemplate):
    def bind(self, view, request=None, macro=None, global_scope=True):
        context = aq_inner(view.context)
        request = view.request
        
        # locate physical root
        method = aq_get(context, 'getPhysicalRoot', None)
        if method is not None:
            root = method()
        else:
            root = None

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
