from z3c.pt.expressions import PathTranslator
from z3c.pt.expressions import ExistsTranslator
from z3c.pt.expressions import ZopeExistsTraverser
from z3c.pt.expressions import ProviderTranslator

from Acquisition import aq_base
from OFS.interfaces import ITraversable
from Products.PageTemplates import ZRPythonExpr
from zExceptions import NotFound, Unauthorized

from zope import component
from zope.proxy import removeAllProxies
from zope.traversing.adapters import traversePathElement
from zope.traversing.interfaces import TraversalError
from zope.contentprovider.interfaces import IContentProvider
from zope.contentprovider.interfaces import ContentProviderLookupError


_marker = object()

try:
    import Products.Five.browser.providerexpression
    AQ_WRAP_CP = True
except ImportError:
    AQ_WRAP_CP = False


def render(ob, request):
    """Calls the object, possibly a document template, or just returns
    it if not callable.  (From Products.PageTemplates.Expressions.py)
    """
    # We are only different in the next line. The original function gets a
    # dict-ish namespace passed in, we fake it.
    # ZRPythonExpr.call_with_ns expects to get such a dict
    ns = dict(context=ob, request=request)

    if hasattr(ob, '__render_with_namespace__'):
        ob = ZRPythonExpr.call_with_ns(ob.__render_with_namespace__, ns)
    else:
        # items might be acquisition wrapped
        base = aq_base(ob)
        # item might be proxied (e.g. modules might have a deprecation
        # proxy)
        base = removeAllProxies(base)
        if callable(base):
            try:
                if getattr(base, 'isDocTemp', 0):
                    ob = ZRPythonExpr.call_with_ns(ob, ns, 2)
                else:
                    ob = ob()
            except AttributeError, n:
                if str(n) != '__call__':
                    raise
    return ob


class FiveTraverser(object):
    def __call__(self, base, request, call, *path_items):
        """See ``zope.app.pagetemplate.engine``."""

        length = len(path_items)
        if length:
            i = 0
            while i < length:
                name = path_items[i]
                i += 1
                next = getattr(base, name, _marker)
                if next is not _marker:
                    base = next
                    continue
                else:
                    # special-case dicts for performance reasons
                    if isinstance(base, dict):
                        base = base[name]
                    elif ITraversable.providedBy(base):
                        base = base.restrictedTraverse(name)
                    else:
                        base = traversePathElement(
                            base, name, path_items[i:], request=request)

        if call is False:
            return base
        
        if getattr(base, '__call__', _marker) is not _marker or callable(base):
            # here's where we're different from the standard path
            # traverser
            base = render(base, request)

        return base

class PathTranslator(PathTranslator):
    path_traverse = FiveTraverser()

class FiveExistsTraverser(ZopeExistsTraverser):
    exceptions = AttributeError, LookupError, TypeError, \
                 NotFound, Unauthorized, TraversalError

class ExistsTranslator(ExistsTranslator):
    path_traverse = FiveExistsTraverser()

class FiveContentProviderTraverser(object):
    def __call__(self, context, request, view, name):
        cp = component.queryMultiAdapter(
            (context, request, view), IContentProvider, name=name)

        # provide a useful error message, if the provider was not found.
        if cp is None:
            raise ContentProviderLookupError(name)

        if AQ_WRAP_CP and getattr(cp, '__of__', None) is not None:
            cp = cp.__of__(context)

        cp.update()
        return cp.render()

class FiveProviderTranslator(ProviderTranslator):
    content_provider_traverser = FiveContentProviderTraverser()

path_translator = PathTranslator()
exists_translator = ExistsTranslator()
provider_translator = FiveProviderTranslator()
