"""Monkey-patching page template classes.

Since many templates are instantiated at module-import, we patch using
a duck-typing strategy.

We replace the ``__get__``-method of the ViewPageTemplateFile class
(both the Five variant and the base class). This allows us to return a
Chameleon template instance, transparent to the calling class.
"""

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile as \
     ZopeViewPageTemplateFile

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as \
     FiveViewPageTemplateFile

from five.pt.pagetemplate import ViewPageTemplateFile
from five.pt.pagetemplate import BaseTemplateFile

from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer

try:
    from Products.Five.browser.pagetemplatefile import BoundPageTemplate
except ImportError:
    from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate
    import Acquisition

    class BoundPageTemplate(BoundPageTemplate, Acquisition.Implicit):
        """Implementing Acquisition.interfaces.IAcquirer and
        IAcquisitionWrapper.
        """

        __parent__ = property(lambda self: self.im_self)

        def __call__(self, im_self=None, *args, **kw):
            if self.im_self is None:
                im_self = im_self
            else:
                im_self = aq_base(self.im_self)
                if IAcquirer.providedBy(im_self):
                    im_self = im_self.__of__(im_self.context)
            return self.im_func(im_self, *args, **kw)

    class BaseTemplateFile(BaseTemplateFile, Acquisition.Implicit):
        """Implement Acquisition.interfaces.IAcquirer and
        IAcquisitionWrapper.
        """

_marker = object()

def get_bound_template(self, instance, type):
    if instance is None:
        return self

    template = getattr(self, '_template', _marker)
    if template is _marker:
        self._template = template = ViewPageTemplateFile(self.filename)

    return BoundPageTemplate(template, instance)

def call_template(self, *args, **kw):
    template = getattr(self, '_template', _marker)
    if template is _marker:
        self._template = template = BaseTemplateFile(self.filename)

    if IAcquirer.providedBy(template):
        template = template.__of__(self)

    return template(self, *args, **kw)

def get_macros(self):
    template = getattr(self, '_template', _marker)
    if template is _marker:
        self._template = template = BaseTemplateFile(self.filename)

    return template.__of__(self).macros

FiveViewPageTemplateFile.__get__ = get_bound_template
ZopeViewPageTemplateFile.__get__ = get_bound_template
PageTemplateFile.__call__ = call_template
PageTemplateFile.macros = property(get_macros)

try:
    from five.grok.components import ZopeTwoPageTemplate

    _tpf  = FiveViewPageTemplateFile(__file__)
    class GrokViewAwarePageTemplateFile(ViewPageTemplateFile):
        def pt_getContext(self, *args, **kw):
            global _tpf
            return _tpf.pt_getContext(*args, **kw)
        def pt_render(self, namespace, **kw):
            if "args" in namespace:
                del namespace["args"]
            context=namespace.pop("context")
            request=namespace.pop("request")
            view=namespace["view"]
            return self.__call__(_ob=view, context=context, request=request, **namespace)

    def setFromFilename(self, filename, _prefix=None):
        self._template = GrokViewAwarePageTemplateFile(filename, _prefix)
    ZopeTwoPageTemplate.setFromFilename = setFromFilename
except ImportError:
    pass

