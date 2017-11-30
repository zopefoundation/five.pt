import warnings


_MESSAGE = ("The package 'five.pt' is deprecated. The functionality was moved"
            " to Zope directly. Use it from "
            " 'Products.PageTemplates.expressions'.")

warnings.warn(_MESSAGE, DeprecationWarning)

# BBB
from z3c.pt.expressions import ProviderExpr # noqa

from Products.PageTemplates.expression import ( # noqa
    BoboAwareZopeTraverse,
    TrustedBoboAwareZopeTraverse,
    PathExpr,
    TrustedPathExpr,
    NocallExpr,
    ExistsExpr,
    RestrictionTransform,
    UntrustedPythonExpr,
)
