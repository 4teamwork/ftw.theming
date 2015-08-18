from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.testing import THEMING_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import getUtility
import transaction


class FunctionalTestCase(TestCase):
    layer = THEMING_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(ISCSSRegistry)
        self.original_resources = self.registry.resources

    def tearDown(self):
        self.original_resources = self.registry.resources

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, roles)
        transaction.commit()
