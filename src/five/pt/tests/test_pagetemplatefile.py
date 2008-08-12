import unittest

from Products.Five import BrowserView
from Testing.ZopeTestCase import ZopeTestCase

from five.pt.pagetemplate import ViewPageTemplateFile


class SimpleView(BrowserView):

    index = ViewPageTemplateFile('simple.pt')


class TestPageTemplateFile(ZopeTestCase):

    def afterSetUp(self):
        from Products.Five import zcml
        import Products.Five
        import z3c.pt
        zcml.load_config("configure.zcml", Products.Five)
        zcml.load_config("configure.zcml", z3c.pt)

    def test_simplefile(self):
        context = self.folder
        request = context.REQUEST

        view = SimpleView(context, request)
        result = view.index()
        self.failUnless('Hello World' in result)


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
