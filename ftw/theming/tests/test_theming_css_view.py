from ftw.testbrowser import browsing
from ftw.theming.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName
import transaction


class TestThemingCSSView(FunctionalTestCase):

    @browsing
    def test_compiles_anonymously(self, browser):
        browser.open(view='theming.css')
        self.assertEquals('text/css; charset=utf-8',
                          browser.headers['Content-Type'])
        self.assertNotEquals('', browser.contents)

    @browsing
    def test_css_is_registered(self, browser):
        portal_css = getToolByName(self.portal, 'portal_css')
        portal_css.setDebugMode(True)
        transaction.commit()

        browser.open()
        css_urls = [node.attrib.get('href') for node in browser.css('link')]
        self.assertEquals(
            ['http://nohost/plone/portal_css/Sunburst%20Theme/theming.css'],
            filter(lambda url: url.endswith('theming.css'), css_urls))
