from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.resource import DynamicSCSSResource
from ftw.theming.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
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

    def test_get_cachekey_returns_a_value(self):
        # The cachekey is based on the modified date of the resource,
        # which changes and therefore we just test that it is positive.
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        self.assertTrue(compiler.get_cachekey())

    def test_get_cachkey_only_with_dynamic_resources(self):
        """In production we only respect cachekeys of dynamic resources in order
        to speed up cachekey calculation and because everything else should be
        static. We also do not want to change cache keys in production too often.

        Therefore the compiler's get_cachekey method has a dynamic_resources_only
        param.
        """
        resource = DynamicSCSSResource('foo', cachekey='foo')
        getUtility(ISCSSRegistry).add_resource(resource)

        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        initial_cachekey = compiler.get_cachekey(dynamic_resources_only=True)
        self.assertEqual(initial_cachekey,
                         compiler.get_cachekey(dynamic_resources_only=True))
        resource.cachekey = 'bar'
        self.assertNotEqual(initial_cachekey,
                            compiler.get_cachekey(dynamic_resources_only=True))
