from ftw.theming.interfaces import ISCSSResource
from ftw.theming.resource import SCSSResource
from ftw.theming.tests.stubs import CONTEXT
from ftw.theming.tests.stubs import REQUEST
from unittest2 import TestCase
from zope.interface.verify import verifyClass


class TestSCSSResource(TestCase):

    def test_implements_interface(self):
        verifyClass(ISCSSResource, SCSSResource)

    def test_create_resource(self):
        resource = SCSSResource('foo.scss')
        self.assertTrue(resource)

    def test_requires_valid_slot(self):
        with self.assertRaises(ValueError):
            SCSSResource('foo.scss', slot='not existing slot')

    def test_available__always_returns_True(self):
        resource = SCSSResource('foo.scss')
        self.assertTrue(resource.available(CONTEXT, REQUEST))
        self.assertTrue(resource.available(None, None))

    def test_get_source(self):
        resource = SCSSResource('foo.scss', source=u'$foreground = black;')
        self.assertEquals(u'$foreground = black;',
                          resource.get_source(CONTEXT, REQUEST))
