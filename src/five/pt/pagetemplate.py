import os
import sys

from zope import component
from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

from Acquisition import aq_get
from Acquisition import aq_inner
from Acquisition import aq_parent

from AccessControl import getSecurityManager

from Products.PageTemplates.Expressions import SecureModuleImporter

from z3c.pt import pagetemplate

from chameleon.core import types
from chameleon.core import config
from chameleon.core import clauses
from chameleon.core import generation
from chameleon.zpt.interfaces import IExpressionTranslator

from five.pt.expressions import path_translator

_marker = object()
_expr_cache = {}

def get_physical_root(context):
    method = aq_get(context, 'getPhysicalRoot', None)
    if method is not None:
        return method()

def evaluate_expression(pragma, expr):
    key = "%s(%s)" % (pragma, expr)
    cache = getattr(_expr_cache, key, _marker)
    if cache is not _marker:
        symbol_mapping, parts, source = cache
    else:
        translator = component.getUtility(IExpressionTranslator, name=pragma)
        parts = translator.tales(expr)
        stream = generation.CodeIO(symbols=config.SYMBOLS)
        assign = clauses.Assign(parts, 'result')
        assign.begin(stream)
        assign.end(stream)
        source = stream.getvalue()

        symbol_mapping = parts.symbol_mapping.copy()
        if isinstance(parts, types.parts):
            for value in parts:
                symbol_mapping.update(value.symbol_mapping)    

        _expr_cache[key] = symbol_mapping, parts, source

    # acquire template locals and update with symbol mapping
    frame = sys._getframe()
    while frame.f_locals.get('econtext', _marker) is _marker:
        frame = frame.f_back
        if frame is None:
            raise RuntimeError, "Can't locate template frame."

    _locals = frame.f_locals
    _locals.update(symbol_mapping)    

    # execute code and return evaluation
    exec source in _locals
    return _locals['result']

def evaluate_path(expr):
    return evaluate_expression('path', expr)

def evaluate_exists(expr):
    return evaluate_expression('exists', expr)

class BaseTemplateFile(pagetemplate.BaseTemplateFile):
    """Zope 2-compatible page template class."""
    
    utility_builtins = {}

    def render_macro(self, macro, global_scope=False, parameters=None):
        context = self._pt_get_context(None, None)

        if parameters is not None:
            context.update(parameters)
        
        return super(BaseTemplateFile, self).render_macro(
            macro, global_scope=global_scope, parameters=context)

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
                path=evaluate_path,
                exists=evaluate_exists,
                root=get_physical_root(context),
                user=getSecurityManager().getUser(),
                modules=SecureModuleImporter,
                options=kwargs)

        for name, value in self.utility_builtins.items():
            namespace.setdefault(name, value)

        return namespace

class ViewPageTemplate(pagetemplate.ViewPageTemplate):
    def _pt_get_context(self, view, request, kwargs):
        if view is None:
            namespace = {}
        else:
            context = aq_inner(view.context)
            request = request or view.request
            namespace = dict(
                context=context,
                request=request,
                view=view,
                template=self,
                here=context,
                container=context,
                nothing=None,
                path=evaluate_path,
                exists=evaluate_exists,
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
