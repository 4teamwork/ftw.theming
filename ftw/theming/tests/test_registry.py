from ftw.testing import MockTestCase
from ftw.theming.exceptions import CyclicResourceOrder
from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.registry import SCSSRegistry
from ftw.theming.resource import SCSSResource
from ftw.theming.tests.profileinfo_stub import ProfileInfoStub
from operator import attrgetter
from zope.interface import Interface
from zope.interface.verify import verifyClass


class TestingResource(SCSSResource):
    """Changes default interfaces ``for_`` and ``layer`` to ``Interface`` so that
    it matches on any objects, which is easier in testing.
    """

    def __init__(self, *args, **kwargs):
        if 'for_' not in kwargs:
            kwargs['for_'] = Interface
        if 'layer' not in kwargs:
            kwargs['layer'] = Interface
        super(TestingResource, self).__init__(*args, **kwargs)


def slots(resources):
    return map(attrgetter('slot'), resources)


def paths(resources):
    return map(attrgetter('relative_path'), resources)


class TestSCSSRegistry(MockTestCase):

    def test_implements_interface(self):
        verifyClass(ISCSSRegistry, SCSSRegistry)

    def test_add_resources(self):
        foo = TestingResource('ftw.theming.tests', 'resources/foo.scss')
        registry = SCSSRegistry()
        registry.add_resource(foo)
        self.assertEquals([foo], registry.get_resources(object(), object()))

    def test_resources_are_ordered_by_slot_order(self):
        registry = SCSSRegistry()
        for slotname in ('policy', 'variables', 'addon', 'theme', 'top'):
            registry.add_resource(TestingResource('ftw.theming.tests',
                                                  'resources/foo.scss',
                                                  slot=slotname))

        self.assertEquals(
            ['top', 'variables', 'addon', 'theme', 'policy'],
            slots(registry.get_resources(object(), object())))

    def test_resource_order_is_kept_within_slot(self):
        registry = SCSSRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.scss'))

        self.assertEquals(
            ['resources/baz.scss', 'resources/foo.scss', 'resources/bar.scss'],
            paths(registry.get_resources(object(), object())))

    def test_only_available_resources_are_returned(self):
        registry = SCSSRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.scss',
                                              profile='bar:default'))

        self.assertEquals(
            ['resources/foo.scss'],
            paths(registry.get_resources(object(), object(), ProfileInfoStub())))

        self.assertEquals(
            ['resources/foo.scss', 'resources/bar.scss'],
            paths(registry.get_resources(object(), object(),
                                         ProfileInfoStub('bar:default'))))

    def test_include_unavailable_resources(self):
        registry = SCSSRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.scss',
                                              profile='bar:default'))

        self.assertEquals(
            ['resources/foo.scss'],
            paths(registry.get_resources(object(), object(), ProfileInfoStub())))

        self.assertEquals(
            ['resources/foo.scss', 'resources/bar.scss'],
            paths(registry.get_resources(object(), object(), ProfileInfoStub(),
                                         include_unavailable=True)))

    def test_reordering_resources_within_slot_with_before(self):
        registry = SCSSRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.scss',
                                              before='resources/bar.scss'))

        self.assertEquals(
            ['resources/foo.scss', 'resources/baz.scss', 'resources/bar.scss'],
            paths(registry.get_resources(object(), object())))

    def test_reordering_resources_within_slot_with_after(self):
        registry = SCSSRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.scss',
                                              after='resources/bar.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.scss'))

        self.assertEquals(
            ['resources/bar.scss', 'resources/foo.scss', 'resources/baz.scss'],
            paths(registry.get_resources(object(), object())))

    def test_conflicting_order(self):
        registry = SCSSRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.scss',
                                              after='resources/bar.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.scss',
                                              after='resources/foo.scss'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.scss'))

        with self.assertRaises(CyclicResourceOrder) as cm:
            registry.get_resources(object(), object())
        self.assertEquals(
            "Cyclic resource order: [['ftw.theming.tests:resources/bar.scss', "
            "'ftw.theming.tests:resources/foo.scss']]",
            str(cm.exception))
