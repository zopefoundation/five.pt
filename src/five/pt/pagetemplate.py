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
    _locals = EContext().locals
    _locals.update(symbol_mapping)    

    # execute code and return evaluation
    exec source in _locals
    return _locals['result']

def evaluate_path(expr):
    return evaluate_expression('path', expr)

def evaluate_exists(expr):
    return evaluate_expression('exists', expr)

class EContext(object):
    """This class emulates the `econtext` variable scope dictionary of
    ZPT; it uses `sys._getframe` to acquire the variable and adds
    required methods."""
    
    _scope = None
    _locals = None

    @property
    def locals(self):
        self.vars; return self._locals
        
    @property
    def vars(self):
        if self._scope is None:
            frame = sys._getframe()
            scope = _marker
            while frame is not None:
                scope = frame.f_locals.get('_scope', _marker)
                if scope is not _marker:
                    self._locals = frame.f_locals
                    break
                frame = frame.f_back
            else:
                raise RuntimeError, "Can't locate variable scope."
            self._scope = scope
        return self._scope
        
    def setLocal(self, name, value):
        self.vars[name] = value

    setGlobal = setLocal
        
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
                path=evaluate_path,
                exists=evaluate_exists,
                root=root,
                user=getSecurityManager().getUser(),
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
