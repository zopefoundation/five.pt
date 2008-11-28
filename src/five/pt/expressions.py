from z3c.pt.expressions import PathTranslator
from z3c.pt.expressions import ExistsTranslator
from z3c.pt.expressions import ZopeExistsTraverser
from z3c.pt.expressions import ProviderTranslator

from zExceptions import NotFound, Unauthorized

from zope import component
from zope.traversing.adapters import traversePathElement
from zope.traversing.interfaces import TraversalError
from zope.contentprovider.interfaces import IContentProvider
from zope.contentprovider.interfaces import ContentProviderLookupError

from Products.PageTemplates.Expressions import render

_marker = object()

try:
    import Products.Five.browser.providerexpression
    AQ_WRAP_CP = True
except ImportError:
    AQ_WRAP_CP = False
    
class FiveTraverser(object):
    def __call__(self, base, request, call, *path_items):
        """See ``zope.app.pagetemplate.engine``."""

        ob = base
        
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
                    else:
                        base = traversePathElement(
                            base, name, path_items[i:], request=request)

        if call is False:
            return base
        
        if getattr(base, '__call__', _marker) is not _marker or callable(base):
            # here's where we're different from the standard path
            # traverser
            base = render(base, ob)

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
