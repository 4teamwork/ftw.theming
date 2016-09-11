from ftw.theming.interfaces import IResourceDisablerConfig
from unittest2 import TestCase
from ftw.theming.resource_disabler import ResourceDisablerConfig
from zope.interface.verify import verifyObject


class TestResourceDisablerConfig(TestCase):

    def test_implements_interface(self):
        config = ResourceDisablerConfig()
        verifyObject(IResourceDisablerConfig, config)

    def test_css_resource_enabled_by_default(self):
        config = ResourceDisablerConfig()
        self.assertTrue(config.is_css_resource_enabled('public.css', 'darktheme'))

    def test_disable_css_resource_for_theme(self):
        config = ResourceDisablerConfig()
        config.add_css_resource('public.css', 'darktheme', enabled=False)
        self.assertFalse(config.is_css_resource_enabled('public.css', 'darktheme'))
        self.assertTrue(config.is_css_resource_enabled('public.css', 'lighttheme'))
        config.add_css_resource('public.css', 'darktheme', enabled=True)
        self.assertTrue(config.is_css_resource_enabled('public.css', 'darktheme'))

    def test_disable_plone_resources(self):
        config = ResourceDisablerConfig()
        self.assertTrue(config.is_css_resource_enabled('public.css', 'vintage'))
        self.assertTrue(config.is_css_resource_enabled('my.project.css', 'vintage'))

        config.disable_plone_resources('vintage')
        self.assertFalse(config.is_css_resource_enabled('public.css', 'vintage'))
        self.assertFalse(config.is_css_resource_enabled('authoring.css', 'vintage'))
        self.assertTrue(config.is_css_resource_enabled('my.project.css', 'vintage'))
