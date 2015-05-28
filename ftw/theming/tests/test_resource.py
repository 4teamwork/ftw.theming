from ftw.theming.interfaces import ISassResource
from ftw.theming.resource import SassResource
from path import Path
from unittest2 import TestCase
from zope.interface.verify import verifyClass


class TestSassResource(TestCase):

    def test_implements_interface(self):
        verifyClass(ISassResource, SassResource)

    def test_create_resource(self):
        resource = SassResource('ftw.theming.tests', 'resources/foo.sass', 'top')
        self.assertTrue(resource)

    def test_requires_valid_slot(self):
        with self.assertRaises(ValueError):
            SassResource('ftw.theming.tests', 'resource/foo.sass', 'not existing slot')

    def test_package_must_exist(self):
        with self.assertRaises(ImportError):
            SassResource('some.package.that.does.not.exist', 'foo.sass', 'top')

    def test_full_path_is_generated(self):
        resource = SassResource('ftw.theming.tests', 'resources/foo.sass', 'top')
        self.assertEquals(Path(__file__).parent.joinpath('resources/foo.sass'),
                          resource.path)

    def test_file_must_exist(self):
        with self.assertRaises(OSError) as cm:
            SassResource('ftw.theming.tests', 'missing.file.sass', 'top')
        self.assertEquals(
            "[Errno 2] No such file or directory: '{0}/missing.file.sass'".format(
                Path(__file__).parent),
            str(cm.exception))
