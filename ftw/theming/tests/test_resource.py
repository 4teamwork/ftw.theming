from ftw.theming.interfaces import ISCSSResource
from ftw.theming.resource import SCSSResource
from ftw.theming.tests.stubs import CONTEXT
from ftw.theming.tests.stubs import ProfileInfoStub
from ftw.theming.tests.stubs import REQUEST
from ftw.theming.tests.stubs import Stub
from path import Path
from plone.app.layout.navigation.interfaces import INavigationRoot
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestSCSSResource(TestCase):

    def test_implements_interface(self):
        verifyClass(ISCSSResource, SCSSResource)

    def test_create_resource(self):
        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss')
        self.assertTrue(resource)

    def test_requires_valid_slot(self):
        with self.assertRaises(ValueError):
            SCSSResource('ftw.theming.tests', 'resource/foo.scss', 'not existing slot')

    def test_package_must_exist(self):
        with self.assertRaises(ImportError):
            SCSSResource('some.package.that.does.not.exist', 'foo.scss')

    def test_full_path_is_generated(self):
        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss')
        self.assertEquals(Path(__file__).parent.joinpath('resources/foo.scss'),
                          resource.path)

    def test_file_must_exist(self):
        with self.assertRaises(OSError) as cm:
            SCSSResource('ftw.theming.tests', 'missing.file.scss')
        self.assertEquals(
            "[Errno 2] No such file or directory: '{0}/missing.file.scss'".format(
                Path(__file__).parent),
            str(cm.exception))

    def test_available__context_must_match_for_interface(self):
        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss',
                                for_=INavigationRoot)
        self.assertTrue(resource.available(Stub(INavigationRoot), REQUEST))
        self.assertFalse(resource.available(Stub(), REQUEST))

    def test_available__request_must_match_layer_interface(self):
        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss',
                                layer=IDefaultBrowserLayer)
        self.assertTrue(resource.available(CONTEXT, Stub(IDefaultBrowserLayer)))
        self.assertFalse(resource.available(CONTEXT, Stub()))

    def test_available__profile_must_be_installed_when_defined(self):
        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss',
                                profile='foo.bar:default')

        self.assertTrue(resource.available(CONTEXT, REQUEST,
                                           ProfileInfoStub('foo.bar:default')))
        self.assertFalse(resource.available(CONTEXT, REQUEST, ProfileInfoStub()))

    def test_get_source(self):
        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss')
        self.assertMultiLineEqual(
            '\n'.join(('#foo {',
                       '  display: none;',
                       '}')),
            resource.get_source())
        self.assertEquals(unicode, type(resource.get_source()),
                          'Source should be unicode.')
