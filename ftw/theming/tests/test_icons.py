from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.theming.tests import FunctionalTestCase


class TestIconsAreWrapped(FunctionalTestCase):

    @browsing
    def test_navigation(self, browser):
        self.grant('Manager')
        folder = create(Builder('folder').titled(u'The Folder'))
        create(Builder('file').titled(u'The File').with_dummy_content().within(folder))
        create(Builder('navigation portlet'))

        browser.open(folder)
        navigation = browser.css('.portletNavigationTree')
        file_linke_in_navigation = navigation.find('The File')
        self.assertEquals(
            ['mimetype-icon', 'icon-mimetype-img-doc'],
            file_linke_in_navigation.css('span.mimetype-icon').first.classes)

    @browsing
    def test_folder_contents(self, browser):
        self.grant('Manager')
        folder = create(Builder('folder').titled(u'The Folder'))
        create(Builder('file').titled(u'The File').with_dummy_content().within(folder))

        browser.login().open(folder, view='folder_contents')
        rows = browser.css('#listing-table').first.dicts(as_text=False, head_offset=1)
        title_cell = rows[0][u'Title']
        self.assertEquals(u'The File', title_cell.text)
        self.assertEquals(
            ['mimetype-icon', 'icon-mimetype-img-doc'],
            title_cell.css('span.mimetype-icon').first.classes)
