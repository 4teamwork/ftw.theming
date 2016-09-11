from ftw.theming.interfaces import IResourceDisablerConfig
from ftw.theming.testing import META_ZCML
from unittest2 import TestCase
from zope.component import getUtility


class TestResourceDisablerDirectives(TestCase):
    layer = META_ZCML

    def setUp(self):
        self.layer.load_zcml_string(
            '<configure xmlns="http://namespaces.zope.org/zope"'
            '           package="ftw.theming">'
            '  <utility factory=".resource_disabler.ResourceDisablerConfig" />'
            '</configure>')

    def test_disable_specific_css_resource(self):
        self.assert_enabled_css_resources(
            {'public.css': True, 'editing.css': True},
            'plonetheme.vintage')

        self.load_zcml(
            '<theme:portal_css theme="plonetheme.vintage">'
            '  <theme:disable_resource id="public.css" />'
            '</theme:portal_css>')

        self.assert_enabled_css_resources(
            {'public.css': False, 'editing.css': True},
            'plonetheme.vintage')

    def test_renable_specific_css_resource(self):
        self.load_zcml(
            '<theme:portal_css theme="plonetheme.vintage">'
            '  <theme:disable_resource id="public.css" />'
            '</theme:portal_css>')

        self.assert_enabled_css_resources(
            {'public.css': False, 'editing.css': True},
            'plonetheme.vintage')

        self.load_zcml(
            '<theme:portal_css theme="plonetheme.vintage">'
            '  <theme:enable_resource id="public.css" />'
            '</theme:portal_css>')

        self.assert_enabled_css_resources(
            {'public.css': True, 'editing.css': True},
            'plonetheme.vintage')

    def test_disable_all_plone_resources(self):
        self.load_zcml(
            '<theme:portal_css theme="plonetheme.vintage">'
            '  <theme:disable_plone_css_resources />'
            '</theme:portal_css>')

        self.assert_enabled_css_resources(
            {'base.css': False,
             'reset.css': False,
             '++resource++quickupload_static/uploadify.css': True},
            'plonetheme.vintage')

    def assert_enabled_css_resources(self, expected, theme_name):
        config = getUtility(IResourceDisablerConfig)
        got = {resource_id: config.is_css_resource_enabled(resource_id,
                                                           theme_name)
                for resource_id in expected.keys()}
        self.assertEquals(expected, got)

    def load_zcml(self, *lines):
        self.layer.load_zcml_string('\n'.join((
            '<configure ',
            '    xmlns:theme="http://namespaces.zope.org/ftw.theming"',
            '    i18n_domain="my.package"',
            '    package="ftw.theming.tests"''>',
        ) + lines + (
            '</configure>',
        )))
