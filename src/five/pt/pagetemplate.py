import os
import sys

from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_get
from Acquisition import aq_inner
from Globals import package_home

from Products.PageTemplates.Expressions import SecureModuleImporter

from z3c.pt.pagetemplate import PageTemplate, PageTemplateFile


class ViewPageTemplate(property):
    def __init__(self, body, **kwargs):
        self.template = PageTemplate(body, **kwargs)
        property.__init__(self, self.render)


    def render(self, view, default_namespace=None):
        context = aq_inner(view.context)
        request = view.request

        # get the root
        root = None
        meth = aq_get(context, 'getPhysicalRoot', None)
        if meth is not None:
            root = meth()

        def template(*args, **kwargs):
            namespace = dict(
                view=view,
                context=context,
                request=request,
                _context=request,
                template=self,
                here=context,
                container=context,
                nothing=None,
                root=root,
                modules=SecureModuleImporter,
                views=ViewMapper(context, request),
                options=kwargs)
            if default_namespace:
                namespace.update(default_namespace)
            return self.template.render(**namespace)

        return template

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)


class ViewPageTemplateFile(ViewPageTemplate):

    def __init__(self, filename, _prefix=None, **kwargs):
        path = self.get_path_from_prefix(_prefix)
        filename = os.path.join(path, filename)
        self.template = PageTemplateFile(filename)
        property.__init__(self, self.render)

    def get_path_from_prefix(self, _prefix):
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = package_home(_prefix)
        return path
