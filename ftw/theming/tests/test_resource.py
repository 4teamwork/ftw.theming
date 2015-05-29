from ftw.testing import MockTestCase
from ftw.theming.interfaces import ISCSSResource
from ftw.theming.resource import SCSSResource
from ftw.theming.tests.profileinfo_stub import ProfileInfoStub
from path import Path
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import Interface
from zope.interface.verify import verifyClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestSCSSResource(MockTestCase):

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
        matching_context = self.providing_stub(INavigationRoot)
        not_matching_context = self.providing_stub(Interface)
        request = self.providing_stub(Interface)
        self.replay()

        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss',
                                for_=INavigationRoot, layer=Interface)
        self.assertTrue(resource.available(matching_context, request))
        self.assertFalse(resource.available(not_matching_context, request))

    def test_available__request_must_match_layer_interface(self):
        context = self.providing_stub(Interface)
        matching_request = self.providing_stub(IDefaultBrowserLayer)
        not_matching_request = self.providing_stub(Interface)
        self.replay()

        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss',
                                for_=Interface, layer=IDefaultBrowserLayer)
        self.assertTrue(resource.available(context, matching_request))
        self.assertFalse(resource.available(context, not_matching_request))

    def test_available__profile_must_be_installed_when_defined(self):
        context = self.providing_stub(Interface)
        request = self.providing_stub(Interface)
        self.replay()

        resource = SCSSResource('ftw.theming.tests', 'resources/foo.scss',
                                for_=Interface, layer=Interface,
                                profile='foo.bar:default')

        self.assertTrue(resource.available(context, request,
                                           ProfileInfoStub('foo.bar:default')))
        self.assertFalse(resource.available(context, request, ProfileInfoStub()))
