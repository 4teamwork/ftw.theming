from ftw.theming.interfaces import ISCSSResource
from ftw.theming.resource import SCSSResource
from ftw.theming.tests.stubs import CONTEXT
from ftw.theming.tests.stubs import REQUEST
from unittest2 import TestCase
from zope.interface.verify import verifyObject


class TestSCSSResource(TestCase):

    def test_implements_interface(self):
        resource = SCSSResource('foo.scss')
        verifyObject(ISCSSResource, resource)

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

    def test_cachekey_is_compiled_from_source(self):
        resource = SCSSResource('foo.scss', source=u'$foreground = black;')
        self.assertEquals('37a986b6ad84bf77261bf3796a01b458',
                          resource.get_cachekey(None, None))

        resource = SCSSResource('foo.scss', source=u'$foreground = black;')
        self.assertEquals('37a986b6ad84bf77261bf3796a01b458',
                          resource.get_cachekey(None, None))

        resource = SCSSResource('foo.scss', source=u'$foreground = red;')
        self.assertEquals('e7d3c829ae8433699c7c061fd87b5fd6',
                          resource.get_cachekey(None, None))
