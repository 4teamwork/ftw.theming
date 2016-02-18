from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.tests import FunctionalTestCase
from zope.component import getUtility


class TestVariables(FunctionalTestCase):

    def test_portal_url_variable_resource(self):
        registry = getUtility(ISCSSRegistry)
        resources = dict((res.name, res)
                         for res in registry.get_resources(self.portal, self.request))
        self.assertIn('ftw.theming:portal_url', resources.keys())

        resource = resources['ftw.theming:portal_url']
        self.assertEquals('$portal-url: "http://nohost/plone";\n'
                          '@include declare-variables(portal-url);',
                          resource.get_source(self.portal, self.request).strip())

        self.assertEquals('variables', resource.slot)

    def test_plone_image_sizes(self):
        registry = getUtility(ISCSSRegistry)
        resources = dict((res.name, res)
                         for res in registry.get_resources(self.portal, self.request))
        self.assertIn('ftw.theming:image_sizes', resources.keys())

        resource = resources['ftw.theming:image_sizes']
        self.assertEquals('variables', resource.slot)

        self.maxDiff = None

        self.assertEqual((
            '$scale-mini-width: 200px;'
            '$scale-mini-height: 200px;'
            '@include declare-variables(scale-width-mini, scale-height-mini);'
            '$scale-thumb-width: 128px;'
            '$scale-thumb-height: 128px;'
            '@include declare-variables(scale-width-thumb, scale-height-thumb);'
            '$scale-large-width: 768px;'
            '$scale-large-height: 768px;'
            '@include declare-variables(scale-width-large, scale-height-large);'
            '$scale-listing-width: 16px;'
            '$scale-listing-height: 16px;'
            '@include declare-variables(scale-width-listing, scale-height-listing);'
            '$scale-tile-width: 64px;'
            '$scale-tile-height: 64px;'
            '@include declare-variables(scale-width-tile, scale-height-tile);'
            '$scale-preview-width: 400px;'
            '$scale-preview-height: 400px;'
            '@include declare-variables(scale-width-preview, scale-height-preview);'
            '$scale-icon-width: 32px;'
            '$scale-icon-height: 32px;'
            '@include declare-variables(scale-width-icon, scale-height-icon);'
            ), resource.get_source(self.portal, self.request).strip())
