from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.theming.interfaces import IResourceDisablerConfig
from ftw.theming.tests import FunctionalTestCase
from plone.app.testing import applyProfile
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
import transaction


class TestDisableCSSResources(FunctionalTestCase):

    def setUp(self):
        super(TestDisableCSSResources, self).setUp()
        applyProfile(self.portal, 'ftw.theming.tests.vintagetheme:default')
        getToolByName(self.portal, 'portal_css').setDebugMode(True)
        transaction.commit()
        getUtility(IResourceDisablerConfig).reset()

    @browsing
    def test_disable_css_resource(self, browser):
        browser.open()
        self.assertTrue(self.get_css_url('public.css'))
        self.load_zcml(
            '<theme:portal_css theme="ftw.theming.tests.vintagetheme">'
            '  <theme:disable_resource id="public.css" />'
            '</theme:portal_css>')
        browser.reload()
        self.assertFalse(self.get_css_url('public.css'))

    @browsing
    def test_reenable_css_resource(self, browser):
        self.load_zcml(
            '<theme:portal_css theme="ftw.theming.tests.vintagetheme">'
            '  <theme:disable_resource id="public.css" />'
            '</theme:portal_css>')
        browser.open()
        self.assertFalse(self.get_css_url('public.css'))

        self.load_zcml(
            '<theme:portal_css theme="ftw.theming.tests.vintagetheme">'
            '  <theme:enable_resource id="public.css" />'
            '</theme:portal_css>')
        browser.reload()
        self.assertTrue(self.get_css_url('public.css'))

    @browsing
    def test_disable_plone_resources(self, browser):
        browser.open()
        self.assertTrue(self.get_css_url('public.css'))

        self.load_zcml(
            '<theme:portal_css theme="ftw.theming.tests.vintagetheme">'
            '  <theme:disable_plone_css_resources />'
            '</theme:portal_css>')
        browser.reload()
        self.assertFalse(self.get_css_url('public.css'))

    @browsing
    def test_disabling_is_theme_sepcific(self, browser):
        # The theme "ftw.theming.tests.vintagetheme" is active.
        browser.open()
        self.assertTrue(self.get_css_url('public.css'))
        self.assertTrue(self.get_css_url('authoring.css'))

        self.load_zcml(
            '<theme:portal_css theme="ftw.theming.tests.vintagetheme">'
            '  <theme:disable_resource id="public.css" />'
            '</theme:portal_css>'
            '<theme:portal_css theme="plonetheme.fancy">'
            '  <theme:disable_resource id="auuthoring.css" />'
            '</theme:portal_css>')
        browser.reload()
        self.assertFalse(self.get_css_url('public.css'))
        self.assertTrue(self.get_css_url('authoring.css'))

    def load_zcml(self, *lines):
        self.layer['load_zcml_string']('\n'.join((
            '<configure ',
            '    xmlns:theme="http://namespaces.zope.org/ftw.theming"',
            '    i18n_domain="my.package"',
            '    package="ftw.theming.tests"''>',
        ) + lines + (
            '</configure>',
        )))

    def list_css_urls(self):
        return [node.attrib.get('href') for node in browser.css('link')]

    def get_css_url(self, url_end):
        for url in self.list_css_urls():
            if url.endswith(url_end):
                return url

        return None
