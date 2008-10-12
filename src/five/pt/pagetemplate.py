import os
import sys

from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_inner
from Globals import package_home

from Products.PageTemplates.Expressions import SecureModuleImporter

from z3c.pt.pagetemplate import PageTemplate, PageTemplateFile


class ViewPageTemplate(property):
    def __init__(self, body, **kwargs):
        self.template = PageTemplate(body, **kwargs)
        property.__init__(self, self.render)


    def render(self, view, default_namespace=None):
        try:
            root = self.getPhysicalRoot()
        except AttributeError:
            try:
                root = view.context.getPhysicalRoot()
            except AttributeError:
                root = None

        context = aq_inner(view.context)

        def template(*args, **kwargs):
            # Next is faster that IUserPreferedLanguages
            language = view.request.get('I18N_LANGUAGE', None)
            namespace = dict(
                view=view,
                context=context,
                request=view.request,
                _context=view.request,
                template=self,
                here=context,
                container=context,
                nothing=None,
                root=root,
                modules=SecureModuleImporter,
                views=ViewMapper(context, view.request),
                target_language=language,
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
