from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testing import freeze
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.resource import DynamicSCSSResource
from ftw.theming.tests import FunctionalTestCase
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
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

    def test_changing_files_should_update_cache_when_debugmode_active(self):
        self.register_compiler_mock()
        self.assertEquals(1, self.view())
        self.assertEquals(1, self.view(), 'Cache does not work...')
        self.portal_css.setDebugMode(True)
        self.assertEquals(2, self.view(), 'Caching should be disabled in debug mode.')
        self.compiler().imitate_change()
        self.assertEquals(3, self.view(), 'Changing files should change cache')

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

    @browsing
    def test_cachekey_changes_when_dynamic_resource_cachekey_changes(self, browser):
        resource = DynamicSCSSResource('foo', cachekey='foo')
        getUtility(ISCSSRegistry).add_resource(resource)

        self.portal_css.setDebugMode(False)
        browser.open()
        theming_css_url = self.get_css_url('http://nohost/plone/theming.css')
        self.assertIn('?cachekey=', theming_css_url, 'Missing cachekey param.')

        browser.reload()
        self.assertEqual(theming_css_url,
                         self.get_css_url('http://nohost/plone/theming.css'),
                         'URL (cachekey?) did unexpectedly change.')

        resource.cachekey = 'bar'

        browser.reload()
        self.assertNotEqual(theming_css_url,
                            self.get_css_url('http://nohost/plone/theming.css'),
                            'Cachekey should have changed.')

    @browsing
    def test_requests_are_redirected_when_not_no_navroot(self, browser):
        """When configured, TinyMCE makes requests to theming.css relative to
        the current context.
        In order to reuse existing caches, we simply redirect all requests of
        theming.css on non-navroot contexts to their navroot versions, adding
        a cachkey param when necessary.
        """
        self.grant('Manager')
        self.portal_css.setDebugMode(False)
        folder = create(Builder('folder'))
        page = create(Builder('page').within(folder))

        browser.open(page, view='theming.css')
        self.assertRegexpMatches(
            browser.url,
            r'^{}'.format(
                re.escape('http://nohost/plone/theming.css?cachekey=')))

        alsoProvides(folder, INavigationRoot)
        transaction.commit()
        browser.open(page, view='theming.css')
        self.assertRegexpMatches(
            browser.url,
            r'^{}'.format(
                re.escape('http://nohost/plone/folder/theming.css?cachekey=')))

    def test_view_provides_get_url(self):
        """For internal use in templates, the view should provide the theming
        css URL.
        """
        portal_css_url = self.portal.restrictedTraverse('theming.css').get_url()
        self.assertRegexpMatches(
            portal_css_url,
            r'^{}'.format(
                re.escape('http://nohost/plone/theming.css?cachekey=')))

        self.grant('Manager')
        folder = create(Builder('folder'))
        folder_css_url = folder.restrictedTraverse('theming.css').get_url()
        self.assertEquals(portal_css_url, folder_css_url,
                          'The CSS should always be relative to the root.')

    def register_compiler_mock(self):
        sitemanager = self.portal.getSiteManager()
        COMPILER_MOCK_DATA = {'counter': 0,
                              'version': 1}

        @sitemanager.registerAdapter
        class CompilerMock(object):
            implements(ISCSSCompiler)
            adapts(IPloneSiteRoot, Interface)

            def __init__(self, context, request):
                pass

            def compile(self, debug=False):
                COMPILER_MOCK_DATA['counter'] += 1
                return COMPILER_MOCK_DATA['counter']

            def get_cachekey(self, dynamic_resources_only=False):
                return str(COMPILER_MOCK_DATA['version'])

            def imitate_change(self):
                COMPILER_MOCK_DATA['version'] += 1

    def compiler(self):
        return getMultiAdapter((self.portal, self.request), ISCSSCompiler)

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
