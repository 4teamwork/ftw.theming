from ftw.builder import Builder
from ftw.builder import create
from ftw.theming.profileinfo import ProfileInfo
from ftw.theming.tests import FunctionalTestCase
from Products.CMFCore.utils import getToolByName


class TestProfileInfo(FunctionalTestCase):

    def setUp(self):
        super(TestProfileInfo, self).setUp()
        self.package_builder = (Builder('python package')
                                .at_path(self.layer['temp_directory'])
                                .named('the.package')
                                .with_profile(Builder('genericsetup profile')
                                              .with_fs_version('1000')))
        self.portal_setup = getToolByName(self.portal, 'portal_setup')
        self.quickinstaller = getToolByName(self.portal, 'portal_quickinstaller')

    def test_is_profile_installed(self):
        info = ProfileInfo(self.portal)

        with create(self.package_builder).zcml_loaded(self.layer['configurationContext']):
            self.assertFalse(info.is_profile_installed('profile-the.package:default'))
            self.assertFalse(info.is_profile_installed('the.package:default'))

            self.portal_setup.runAllImportStepsFromProfile('profile-the.package:default')
            self.assertTrue(info.is_profile_installed('profile-the.package:default'))
            self.assertTrue(info.is_profile_installed('the.package:default'))

            self.quickinstaller.uninstallProducts(['the.package'])
            self.assertFalse(info.is_profile_installed('profile-the.package:default'))
            self.assertFalse(info.is_profile_installed('the.package:default'))
