from ftw.testbrowser import browsing
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implements
from zope.interface import Interface
import transaction


class TestThemingCSSView(FunctionalTestCase):

    def setUp(self):
        super(TestThemingCSSView, self).setUp()
        self.view = self.portal.restrictedTraverse('theming.css')
        self.view.invalidate_cache()
        self.portal_css = getToolByName(self.portal, 'portal_css')

    def tearDown(self):
        super(TestThemingCSSView, self).tearDown()
        self.portal_css.setDebugMode(False)

    @browsing
    def test_compiles_anonymously(self, browser):
        browser.open(view='theming.css')
        self.assertEquals('text/css; charset=utf-8',
                          browser.headers['Content-Type'])
        self.assertNotEquals('', browser.contents)

    @browsing
    def test_css_is_registered(self, browser):
        self.portal_css.setDebugMode(True)
        browser.open()
        css_urls = [node.attrib.get('href') for node in browser.css('link')]
        self.assertEquals(
            ['http://nohost/plone/portal_css/Sunburst%20Theme/theming.css'],
            filter(lambda url: url.endswith('theming.css'), css_urls))

    def test_css_is_cached(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Results should be cached but are not.')

    def test_invalidating_cache(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Cache does not work...')
        self.view.invalidate_cache()
        self.assertEquals(2, self.view(), 'invalidate_cache() did not invalidate cache')
        self.assertEquals(2, self.view(), 'Cache does not work...')

    def test_debug_mode_does_not_cache(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Cache does not work...')
        self.portal_css.setDebugMode(True)
        self.assertEquals(2, self.view(), 'Caching should be disabled in debug mode.')
        self.assertEquals(3, self.view(), 'Caching should be disabled in debug mode.')

    def test_no_cache_header_disables_caching(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Cache does not work...')
        self.request.environ['CACHE_CONTROL'] = 'no-cache'
        self.assertEquals(2, self.view(), 'no-cache header does not work')
        self.assertEquals(3, self.view(), 'no-cache header does not work')
        self.request.environ['CACHE_CONTROL'] = 'no-transform'
        self.assertEquals(3, self.view(),
                          'no-cache header should flush the cache for later requests.')
        self.assertEquals(3, self.view(),
                          'no-cache header should flush the cache for later requests.')

    def test_recooking_portal_css_flushes_cache(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Cache does not work...')
        self.portal_css.cookResources()
        self.assertEquals(2, self.view(), 'Recooking portal_css should flush cache.')

    def register_compiler_mock(self):
        sitemanager = self.portal.getSiteManager()
        COMPILER_MOCK_DATA = {'counter': 0}

        @sitemanager.registerAdapter
        class CompilerMock(object):
            implements(ISCSSCompiler)
            adapts(IPloneSiteRoot, Interface)

            def __init__(self, context, request):
                pass

            def compile(self, debug=False):
                COMPILER_MOCK_DATA['counter'] += 1
                return COMPILER_MOCK_DATA['counter']
