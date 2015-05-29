from ftw.testing import MockTestCase
from ftw.theming.exceptions import CyclicResourceOrder
from ftw.theming.interfaces import ISassRegistry
from ftw.theming.registry import SassRegistry
from ftw.theming.resource import SassResource
from ftw.theming.tests.profileinfo_stub import ProfileInfoStub
from operator import attrgetter
from zope.interface import Interface
from zope.interface.verify import verifyClass


class TestingResource(SassResource):
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


class TestSassRegistry(MockTestCase):

    def test_implements_interface(self):
        verifyClass(ISassRegistry, SassRegistry)

    def test_add_resources(self):
        foo = TestingResource('ftw.theming.tests', 'resources/foo.sass')
        registry = SassRegistry()
        registry.add_resource(foo)
        self.assertEquals([foo], registry.get_resources(object(), object()))

    def test_resources_are_ordered_by_slot_order(self):
        registry = SassRegistry()
        for slotname in ('policy', 'variables', 'addon', 'theme', 'top'):
            registry.add_resource(TestingResource('ftw.theming.tests',
                                                  'resources/foo.sass',
                                                  slot=slotname))

        self.assertEquals(
            ['top', 'variables', 'addon', 'theme', 'policy'],
            slots(registry.get_resources(object(), object())))

    def test_resource_order_is_kept_within_slot(self):
        registry = SassRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.sass'))

        self.assertEquals(
            ['resources/baz.sass', 'resources/foo.sass', 'resources/bar.sass'],
            paths(registry.get_resources(object(), object())))

    def test_only_available_resources_are_returned(self):
        registry = SassRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.sass',
                                              profile='bar:default'))

        self.assertEquals(
            ['resources/foo.sass'],
            paths(registry.get_resources(object(), object(), ProfileInfoStub())))

        self.assertEquals(
            ['resources/foo.sass', 'resources/bar.sass'],
            paths(registry.get_resources(object(), object(),
                                         ProfileInfoStub('bar:default'))))

    def test_include_unavailable_resources(self):
        registry = SassRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.sass',
                                              profile='bar:default'))

        self.assertEquals(
            ['resources/foo.sass'],
            paths(registry.get_resources(object(), object(), ProfileInfoStub())))

        self.assertEquals(
            ['resources/foo.sass', 'resources/bar.sass'],
            paths(registry.get_resources(object(), object(), ProfileInfoStub(),
                                         include_unavailable=True)))

    def test_reordering_resources_within_slot_with_before(self):
        registry = SassRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.sass',
                                              before='resources/bar.sass'))

        self.assertEquals(
            ['resources/foo.sass', 'resources/baz.sass', 'resources/bar.sass'],
            paths(registry.get_resources(object(), object())))

    def test_reordering_resources_within_slot_with_after(self):
        registry = SassRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.sass',
                                              after='resources/bar.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.sass'))

        self.assertEquals(
            ['resources/bar.sass', 'resources/foo.sass', 'resources/baz.sass'],
            paths(registry.get_resources(object(), object())))

    def test_conflicting_order(self):
        registry = SassRegistry()
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/foo.sass',
                                              after='resources/bar.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/bar.sass',
                                              after='resources/foo.sass'))
        registry.add_resource(TestingResource('ftw.theming.tests',
                                              'resources/baz.sass'))

        with self.assertRaises(CyclicResourceOrder) as cm:
            registry.get_resources(object(), object())
        self.assertEquals(
            "Cyclic resource order: [['ftw.theming.tests:resources/bar.sass', "
            "'ftw.theming.tests:resources/foo.sass']]",
            str(cm.exception))
