from Testing.ZopeTestCase import ZopeTestCase
from five.pt.pagetemplate import BaseTemplateFile


class TestPageTemplateFile(ZopeTestCase):
    def afterSetUp(self):
        from Products.Five import zcml
        import Products.Five
        import z3c.pt
        import five.pt
        zcml.load_config("configure.zcml", Products.Five)
        zcml.load_config("configure.zcml", five.pt)
        zcml.load_config("configure.zcml", z3c.pt)

    def test_locals_base(self):
        template = BaseTemplateFile('locals_base.pt')
        result = template()
        self.failUnless('here==context:True' in result)
        self.failUnless('container==None:True' in result)
        self.failUnless("nothing:None" in result)

    def test_simple(self):
        template = BaseTemplateFile("simple.pt")
        result = template()
        self.failUnless('Hello world!' in result)

    def test_secure(self):
        soup = '<foo></bar>'
        template = BaseTemplateFile("secure.pt")
        from zExceptions import Unauthorized
        try:
            result = template(soup=soup)
        except Unauthorized:
            pass
        else:
            self.fail("Expected unauthorized.")

        from AccessControl.SecurityInfo import allow_module
        allow_module("cgi")
        result = template(soup=soup)
        self.failUnless('&lt;foo&gt;&lt;/bar&gt;' in result)
