from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testing import freeze
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.tests import FunctionalTestCase
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import adapts
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.lifecycleevent import ObjectModifiedEvent
import re
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
    def test_css_included_in_html(self, browser):
        browser.open()
        self.assert_css_url_present('http://nohost/plone/theming.css')

    @browsing
    def test_css_included_relative_to_navigation_root(self, browser):
        self.grant('Manager')
        folder = create(Builder('folder').titled('Folder'))

        browser.login().open(folder)
        self.assert_css_url_present('http://nohost/plone/theming.css')

        alsoProvides(folder, INavigationRoot)
        transaction.commit()
        browser.reload()
        self.assert_css_url_present('http://nohost/plone/folder/theming.css')

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

    def test_recooking_portal_css_flushes_cache(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Cache does not work...')
        self.portal_css.cookResources()
        self.assertEquals(2, self.view(), 'Recooking portal_css should flush cache.')

    @browsing
    def test_caching_active_when_debugmode_disabled(self, browser):
        self.portal_css.setDebugMode(False)
        browser.open()
        theming_css_url = self.get_css_url('http://nohost/plone/theming.css')
        self.assertIn('?cachekey=', theming_css_url, 'Missing cachekey param.')

        browser.open(theming_css_url)
        self.assertEquals('private, max-age=31536000',
                          browser.headers['Cache-Control'],
                          'Cache headers should be set.')

    @browsing
    def test_caching_inactive_when_debugmode_enabled(self, browser):
        self.portal_css.setDebugMode(True)
        browser.open()
        theming_css_url = self.get_css_url('http://nohost/plone/theming.css')
        self.assertEquals('http://nohost/plone/theming.css', theming_css_url,
                          'Cachekey param should not be set in debug mode.')

        browser.open(theming_css_url)
        self.assertNotIn('Cache-Control', browser.headers,
                         'Cache-Control headers should not be set in debug mode.')

    @browsing
    def test_cachekey_refreshes_when_navroot_changes(self, browser):
        with freeze(datetime(2015, 1, 2, 3, 4)) as clock:
            self.portal_css.setDebugMode(False)
            self.grant('Manager')
            navroot = create(Builder('folder')
                             .titled('Folder')
                             .providing(INavigationRoot))

            browser.open(navroot)
            css_base_url = 'http://nohost/plone/folder/theming.css'
            self.assert_css_url_present(css_base_url)
            theming_css_url = self.get_css_url(css_base_url)

            clock.forward(hours=1)
            navroot.reindexObject()  # updates modified date
            transaction.commit()
            browser.reload()
            self.assertNotEqual(theming_css_url, self.get_css_url(css_base_url),
                                'Cachekey should be refreshed when navroot changes.')

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

    def list_css_urls(self):
        return [node.attrib.get('href') for node in browser.css('link')]

    def get_css_url(self, urlbase):
        xpr = re.compile(r'^{0}($|\?)'.format(re.escape(urlbase)))
        urls = filter(xpr.match, self.list_css_urls())
        try:
            url, = urls
        except ValueError:
            return None
        else:
            return url

    def assert_css_url_present(self, url):
        assert self.get_css_url(url), \
            'No CSS URL "{0}" found in {1}'.format(url, self.list_css_urls())
