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
    <tal:block i18n:domain="mydomain" i18n:translate="">
      Inner Slot
    </tal:block>
  </metal:fills>
</metal:use>
""".strip()

simple_i18n = """
<tal:block i18n:domain="mydomain" i18n:translate="">
  Hello, World
</tal:block>
""".strip()

repeat_object = """
<tal:loop repeat="counter python: range(3)" 
          content="python: repeat['counter'].index" />
""".strip()

options_capture_update_base = """
<metal:use use-macro="context/macro_outer/macros/master">
  <metal:fills fill-slot="main_slot">
    <tal:block define="dummy python: capture.update(%s)" />
  </metal:fills>
</metal:use>
""".strip()

def generate_capture_source(names):
    params = ", ".join("%s=%s" % (name, name)
                       for name in names)
    return options_capture_update_base % (params,)

_marker = object()

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
        template = self._makeOne('foo', simple_i18n)
        result = template().strip()
        self.assertEqual(result, u'Hello, World')
        # check that it's editable
        template.pt_editForm()

    def test_macro_with_i18n(self):
        self._makeOne('macro_outer', macro_outer)
        self._makeOne('macro_middle', macro_middle)
        inner = self._makeOne('macro_inner', macro_inner)
        result = inner().strip()
        self.assertEqual(result, u'Inner Slot')

    def test_pt_render_with_macro(self):
        # The pt_render method of ZopePageTemplates allows rendering the
        # template with an expanded (and overriden) set of context
        # variables.
        # It's also used to retrieve the unrendered source for TTW
        # editing purposes.
        # Lets test with some common and some unique variables:
        extra_context = dict(form=object(),
                             context=self.folder,
                             here=object(),)
        capture = dict((name, None) for name in extra_context)
        source = generate_capture_source(capture)
        self._makeOne('macro_outer', macro_outer)
        template = self._makeOne('test_pt_render', source)
        self.assertEqual(template.pt_render(source=True), source)
        extra_context['capture'] = capture
        template.pt_render(extra_context=extra_context)
        del extra_context['capture']
        self.assertEquals(extra_context, capture)

    def test_avoid_recompilation(self):
        template = self._makeOne('foo', simple_i18n)
        macro_outer = self._makeOne('macro_outer', simple_i18n)
        # templates are only compiled after the first call
        self.assertEqual(getattr(template, '_v_template', _marker), _marker)
        template()
        # or the first fetching of macros
        self.assertEqual(getattr(macro_outer, '_v_template', _marker), _marker)
        macro_outer.macros

        template_compiled = template._v_template
        macro_outer_compiled = macro_outer._v_template

        # but they should not be recompiled afterwards
        template()
        macro_outer.macros
        self.assertTrue(template_compiled is template._v_template)
        self.assertTrue(macro_outer_compiled is macro_outer._v_template)

    def test_repeat_object_security(self):
        template = self._makeOne('foo', repeat_object)
        # this should not raise an Unauthorized error
        self.assertEquals(template().strip().split(), u'0 1 2'.split())
