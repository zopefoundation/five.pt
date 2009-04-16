import unittest

from Products.Five import BrowserView
from Testing.ZopeTestCase import ZopeTestCase

from five.pt.pagetemplate import ViewPageTemplateFile

class SimpleView(BrowserView):
    index = ViewPageTemplateFile('simple.pt')

class LocalsView(BrowserView):
    def available(self):
        return 'yes'

    def tagsoup(self):
        return '<foo></bar>'

    index = ViewPageTemplateFile('locals.pt')

class OptionsView(BrowserView):
    index = ViewPageTemplateFile('options.pt')

class TestPageTemplateFile(ZopeTestCase):
    def afterSetUp(self):
        from Products.Five import zcml
        import Products.Five
        import z3c.pt
        zcml.load_config("configure.zcml", Products.Five)
        zcml.load_config("configure.zcml", z3c.pt)

    def test_simple(self):
        view = SimpleView(self.folder, self.folder.REQUEST)
        result = view.index()
        self.failUnless('Hello World' in result)

    def test_locals(self):
        view = LocalsView(self.folder, self.folder.REQUEST)
        result = view.index()
        self.failUnless("view:yes" in result)
        #self.failUnless('Folder at test_folder_1_' in result)
        #self.failUnless('http://nohost' in result)
        self.failUnless('here==context:True' in result)
        self.failUnless('here==container:True' in result)
        self.failUnless("root:(\'\',)" in result)
        self.failUnless("nothing:None" in result)
        self.failUnless("modules:&lt;foo&gt;" in result)

    def test_options(self):
        view = OptionsView(self.folder, self.folder.REQUEST)
        options = dict(
            a=1,
            b=2,
            c='abc',
        )
        result = view.index(**options)
        self.failUnless("a : 1" in result)
        self.failUnless("c : abc" in result)


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
