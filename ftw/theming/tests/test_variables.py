from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.tests import FunctionalTestCase
from ftw.theming.variables import portal_url_variable_resource_factory
from zope.component import getUtility


class TestVariables(FunctionalTestCase):

    def test_portal_url_variable_resource(self):
        registry = getUtility(ISCSSRegistry)
        resources = dict((res.name, res)
                         for res in registry.get_resources(self.portal, self.request))
        self.assertIn('ftw.theming:portal_url', resources.keys())

        resource = resources['ftw.theming:portal_url']
        self.assertEquals('$portal-url: "http://nohost/plone";',
                          resource.get_source(self.portal, self.request).strip())

        self.assertEquals('variables', resource.slot)
