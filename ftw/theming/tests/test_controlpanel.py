from ftw.testbrowser import browsing
from ftw.theming.tests import FunctionalTestCase
from plone.app.testing import SITE_OWNER_NAME


class TestControlpanel(FunctionalTestCase):

    @browsing
    def test_controlpanel_is_available(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='overview-controlpanel')
        browser.find('Theming Resources').click()
        self.assertEquals('http://nohost/plone/@@theming-resources',
                          browser.url)

    @browsing
    def test_navigate_from_resources_to_variables(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-resources')
        browser.find('Theming Variables').click()
        self.assertEquals('http://nohost/plone/@@theming-variables',
                          browser.url)

    @browsing
    def test_navigate_from_variables_to_resources(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-variables')
        browser.find('Theming Resources').click()
        self.assertEquals('http://nohost/plone/@@theming-resources',
                          browser.url)

    @browsing
    def test_navigate_from_resources_to_icons(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-resources')
        browser.find('Icons').click()
        self.assertEquals('http://nohost/plone/@@theming-icons',
                          browser.url)

    @browsing
    def test_theming_resources_lists_resources(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-resources')
        resources = browser.css('table.theming-resources').first.dicts()
        for resource in resources:
            del resource['']
            del resource['#']

        self.assertIn(
            {'For': 'INavigationRoot',
             'Layer': 'Interface',
             'Name': 'ftw.theming:resources/scss/default/theming_controlpanel.scss',
             'Package': 'ftw.theming',
             'Profile': 'ftw.theming:default',
             'Slot': 'addon'},
            resources)

    @browsing
    def test_theming_variables_lists_variables(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-variables')
        variables = browser.css('table.theming-variables').first.dicts()

        self.assertIn({'File': 'default_variables.scss',
                       'Name': '$gray-base',
                       'Value': '#403e3d',
                       'Example': ''},
                      variables)

        self.assertIn({'File': 'portal_url',
                       'Name': '$portal-url',
                       'Value': '"http://nohost/plone"',
                       'Example': '"http://nohost/plone"'},
                      variables)

    @browsing
    def test_theming_icons_lists_portal_type_icons(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-icons')
        icons = browser.css('table.theming-portal-type-icons').first.dicts()
        self.assertIn({'Type': 'Folder',
                       'Name': 'folder'}, icons)

    @browsing
    def test_theming_icons_lists_mime_type_icons(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='theming-icons')
        icons = browser.css('table.theming-mime-type-icons').first.dicts()
        self.assertIn({'Name': 'pdf', 'Original': '', 'Icon': ''}, icons)
