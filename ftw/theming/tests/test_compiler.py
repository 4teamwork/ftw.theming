from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.tests import FunctionalTestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyObject


class TestCompiler(FunctionalTestCase):

    def test_default_compiler_implements_interface(self):
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        verifyObject(ISCSSCompiler, compiler)

    def test_compiles_to_css(self):
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        result = compiler.compile()
        self.assertTrue(result, 'Compiled CSS should be empty.')
        self.assertEquals(str, type(result),
                          'Compiled CSS should be an utf-8 bytestring.')

    def test_compiling_with_debug_mode(self):
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        self.assertTrue(compiler.compile(debug=True),
                        'Compiled CSS should be empty.')

    def test_compile_scss_string(self):
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        result = compiler.compile_scss_string('$red: red;'
                                              'body { background-color: $red; }')
        self.assertEquals('body{background-color:red}', result.strip())
