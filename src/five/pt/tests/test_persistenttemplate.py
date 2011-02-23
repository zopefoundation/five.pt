from Testing.ZopeTestCase import ZopeTestCase
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

macro_outer = """
<metal:defm define-macro="master">
    <metal:defs define-slot="main_slot">
      Outer Slot
    </metal:defs>
</metal:defm>
""".strip()

macro_middle = """
<metal:def define-macro="master">
  <metal:use use-macro="here/macro_outer/macros/master">
    <metal:fill fill-slot="main_slot">
      <metal:defs define-slot="main_slot">
        Middle Slot
      </metal:defs>
    </metal:fill>
  </metal:use>
</metal:def>
""".strip()

macro_inner = """
<metal:use use-macro="here/macro_middle/macros/master">
  <metal:fills fill-slot="main_slot">
    Inner Slot
  </metal:fills>
</metal:use>
""".strip()

class TestPersistent(ZopeTestCase):
    def afterSetUp(self):
        from Products.Five import zcml
        import Products.Five
        import z3c.pt
        import five.pt
        zcml.load_config("configure.zcml", Products.Five)
        zcml.load_config("configure.zcml", five.pt)
        zcml.load_config("configure.zcml", z3c.pt)
        self.setRoles(['Manager'])

    def _makeOne(self, template_id, source):
        return manage_addPageTemplate(self.folder, template_id, text=source)

    def test_simple(self):
        template = self._makeOne('foo',
                                 '<tal:block content="string:Hello, World" />')
        result = template()
        self.assertEqual(result, u'Hello, World')
        # check that it's editable
        template.pt_editForm()

    def test_macro(self):
        self._makeOne('macro_outer', macro_outer)
        self._makeOne('macro_middle', macro_middle)
        inner = self._makeOne('macro_inner', macro_inner)
        result = inner().strip()
        self.assertEqual(result, u'Inner Slot')
