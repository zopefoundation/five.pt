import sys

from zope.interface import classImplements
from zope.configuration.config import ConfigurationMachine
from zope.component import zcml
from zope.viewlet.interfaces import IViewletManager

from Products.Five.viewlet import viewlet
from Products.Five.viewlet import manager

from Products.Five.viewlet import metaconfigure as viewletmeta
from Products.Five.browser import metaconfigure as viewmeta

from five.pt.pagetemplate import ViewPageTemplateFile

def SimpleViewClass(src, offering=None, used_for=None, bases=(), name=u''):
    if offering is None:
        offering = sys._getframe(1).f_globals

    bases += (viewmeta.ViewMixinForTemplates,)

    class_ = type("SimpleViewClass from %s" % src, bases,
                  {'index': ViewPageTemplateFile(src, offering),
                   '__name__': name})

    if used_for is not None:
        class_.__used_for__ = used_for

    return class_

def SimpleViewletClass(src, offering=None, bases=(), attributes=None, name=u''):
    if offering is None:
        offering = sys._getframe(1).f_globals

    # Create the base class hierarchy
    bases += (viewlet.simple, viewlet.ViewletBase)

    attrs = {'index' : ViewPageTemplateFile(src, offering),
             '__name__' : name}
    if attributes:
        attrs.update(attributes)

    # Generate a derived view class.
    class_ = type("SimpleViewletClass from %s" % src, bases, attrs)

    return class_

def ViewletManager2(name, interface, template=None, bases=()):
    attrs = {'__name__' : name}
    if template is not None:
        attrs['template'] = ViewPageTemplateFile(template)

    if manager.ViewletManagerBase not in bases:
        # Make sure that we do not get a default viewlet manager mixin, if the
        # provided base is already a full viewlet manager implementation.
        if not (len(bases) == 1 and
                IViewletManager.implementedBy(bases[0])):
            bases = bases + (manager.ViewletManagerBase,)

    ViewletManager = type(
        '<ViewletManager providing %s>' % interface.getName(), bases, attrs)
    classImplements(ViewletManager, interface)
    return ViewletManager

def page_directive(_context, name, *args, **kwargs):
    class_ = kwargs.get('class_')
    template = kwargs.get('template')

    if template:
        bases = class_ and (class_,) or ()
        kwargs['class_'] = SimpleViewClass(str(template), bases=bases, name=name)
        del kwargs['template']
        
    return viewmeta.page(_context, name, *args, **kwargs)

def viewlet_directive(_context, name, *args, **kwargs):
    class_ = kwargs.get('class_')
    template = kwargs.get('template')

    if template:
        bases = class_ and (class_,) or ()
        kwargs['class_'] = SimpleViewletClass(str(template), bases=bases, name=name)
        del kwargs['template']
        
    return viewletmeta.viewletDirective(_context, name, *args, **kwargs)

def viewlet_manager_directive(_context, name, *args, **kwargs):
    template = kwargs.pop('template', None)
    provides = kwargs.setdefault('provides', IViewletManager)
    class_ = kwargs.get('class_')
    
    if template is None:
        return viewletmeta.viewletManagerDirective(
            _context, name, *args, **kwargs)

    _new = ConfigurationMachine()
    viewletmeta.viewletManagerDirective(_new, name, *args, **kwargs)
    
    for action in _new.actions:
        try:
            discriminator, handler, args = action
            try:
                name = discriminator.__getitem__(0)
            except (AttributeError, IndexError):
                continue

            if name == 'viewletManager':
                assert handler is zcml.handler, \
                       "Unsupported action handler '%s'." % repr(handler)
                new_class = args[1]
                new_class.template = ViewPageTemplateFile(template)
        finally:
            _context.actions.append(action)
            
