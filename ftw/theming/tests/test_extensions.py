from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.tests import FunctionalTestCase
from zope.component import getMultiAdapter


class TestThemingExtensions(FunctionalTestCase):

    def test_function_exists(self):
        self.assert_scss_compilation_result(
            'body{rgb-exists:true;foo-exists:false}',

            'body {'
            ' rgb-exists: function-exists(rgb);'
            ' foo-exists: function-exists(foo);'
            '}')

    def assert_scss_compilation_result(self, expected_css, scss_input, msg=None):
        compiler = getMultiAdapter((self.portal, self.request), ISCSSCompiler)
        got_css = compiler.compile_scss_string(scss_input)
        self.assertEquals(expected_css.strip(), got_css.strip(), msg=msg)
