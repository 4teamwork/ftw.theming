from ftw.theming.compiler import SCSSCompiler
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.tests import FunctionalTestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestCompiler(FunctionalTestCase):

    def test_default_compiler_implements_interface(self):
        verifyClass(ISCSSCompiler, SCSSCompiler)

    def test_compiles_to_css(self):
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        result = compiler.compile()
        self.assertTrue(result, 'Compiled CSS should be empty.')
        self.assertEquals(str, type(result),
                          'Compiled CSS should be an utf-8 bytestring.')
