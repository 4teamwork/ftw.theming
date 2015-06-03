from ftw.testbrowser import browsing
from ftw.theming.tests import FunctionalTestCase
from plone.app.testing import SITE_OWNER_NAME


class TestThemingResources(FunctionalTestCase):

    @browsing
    def test_controlpanel_is_available(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='overview-controlpanel')
        browser.find('Theming Resources').click()

        resources = browser.css('table.theming-resources').first.dicts()
        for resource in resources:
            del resource['']
            del resource['#']

        self.assertIn({'For': 'INavigationRoot',
                       'Layer': 'Interface',
                       'Name': 'ftw.theming:resources/scss/reset.scss',
                       'Package': 'ftw.theming',
                       'Profile': 'ftw.theming:default',
                       'Slot': 'ftw.theming'},
                      resources)
