import warnings


_MESSAGE = ("The package 'five.pt' is deprecated. The functionality was moved"
            " to Zope directly. Use it from "
            " 'Products.PageTemplates.engine'.")

warnings.warn(_MESSAGE, DeprecationWarning)

# BBB
from Products.PageTemplates.engine import Program # noqa
