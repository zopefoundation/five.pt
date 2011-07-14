from ast import NodeTransformer
from compiler import parse as ast24_parse

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

from RestrictedPython.RestrictionMutator import RestrictionMutator
from RestrictedPython import MutatingWalker

from AccessControl.ZopeGuards import guarded_getattr
from AccessControl.ZopeGuards import guarded_getitem
from AccessControl.ZopeGuards import guarded_apply
from AccessControl.ZopeGuards import guarded_iter
from AccessControl.ZopeGuards import protected_inplacevar

from chameleon.astutil import Symbol
from chameleon.astutil import Static
from chameleon.astutil import NameLookupRewriteVisitor
from chameleon.codegen import template
from chameleon.utils import decode_htmlentities
from sourcecodegen import generate_code

from z3c.pt import expressions

_marker = object()

try:
    import Products.Five.browser.providerexpression
    AQ_WRAP_CP = True
except ImportError:
    AQ_WRAP_CP = False


zope2_exceptions = NameError, \
                   ValueError, \
                   AttributeError, \
                   LookupError, \
                   TypeError, \
                   NotFound, \
                   Unauthorized, \
                   TraversalError


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


class BoboAwareZopeTraverse(object):
    traverse_method = 'restrictedTraverse'

    def __call__(self, base, request, call, *path_items):
        """See ``zope.app.pagetemplate.engine``."""

        length = len(path_items)
        if length:
            i = 0
            method = self.traverse_method
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
                        traverser = getattr(base, method)
                        base = traverser(name)
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


class TrustedBoboAwareZopeTraverse(BoboAwareZopeTraverse):
    traverse_method = 'unrestrictedTraverse'


class PathExpr(expressions.PathExpr):
    exceptions = zope2_exceptions

    traverser = Static(template(
        "cls()", cls=Symbol(BoboAwareZopeTraverse), mode="eval"
        ))


class TrustedPathExpr(PathExpr):
    traverser = Static(template(
        "cls()", cls=Symbol(TrustedBoboAwareZopeTraverse), mode="eval"
        ))


class NocallExpr(expressions.NocallExpr, PathExpr):
    pass


class ExistsExpr(expressions.ExistsExpr):
    exceptions = zope2_exceptions


class ContentProviderTraverser(object):
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


class ProviderExpr(expressions.ProviderExpr):
    traverser = Static(
        template("cls()", cls=Symbol(ContentProviderTraverser), mode="eval")
        )


class RestrictionTransform(NodeTransformer):
    secured = {
        '_getattr_': guarded_getattr,
        '_getitem_': guarded_getitem,
        '_apply_': guarded_apply,
        '_getiter_': guarded_iter,
        '_inplacevar_': protected_inplacevar,
    }

    def visit_Name(self, node):
        value = self.secured.get(node.id)
        if value is not None:
            return Symbol(value)

        return node


class UntrustedPythonExpr(expressions.PythonExpr):
    rm = RestrictionMutator()
    rt = RestrictionTransform()

    def _dynamic_transform(node):
        if node.id == 'repeat':
            node.id = 'wrapped_repeat'

        return node

    nt = NameLookupRewriteVisitor(_dynamic_transform)

    def parse(self, string):
        decoded = decode_htmlentities(string)
        node = ast24_parse(decoded, 'eval').node
        MutatingWalker.walk(node, self.rm)
        string = generate_code(node)
        value = super(UntrustedPythonExpr, self).parse(string)
        self.rt.visit(value)
        self.nt.visit(value)
        return value
