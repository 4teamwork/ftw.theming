from ftw.theming.exceptions import CyclicResourceOrder
from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.registry import SCSSRegistry
from ftw.theming.resource import DynamicSCSSResource
from ftw.theming.resource import SCSSFileResource
from ftw.theming.resource import SCSSResource
from ftw.theming.tests.stubs import CONTEXT
from ftw.theming.tests.stubs import ProfileInfoStub
from ftw.theming.tests.stubs import REQUEST
from operator import attrgetter
from unittest2 import TestCase
from zope.interface import provider
from zope.interface.verify import verifyObject


def slots(resources):
    return map(attrgetter('slot'), resources)


def paths(resources):
    return map(attrgetter('relative_path'), resources)


class TestSCSSRegistry(TestCase):

    def test_implements_interface(self):
        registry = SCSSRegistry()
        verifyObject(ISCSSRegistry, registry)

    def test_add_resources(self):
        foo = SCSSFileResource('ftw.theming.tests', 'resources/foo.scss')
        registry = SCSSRegistry()
        registry.add_resource(foo)
        self.assertEquals([foo], registry.get_resources(CONTEXT, REQUEST))

    def test_resources_are_ordered_by_slot_order(self):
        registry = SCSSRegistry()
        for slotname in ('policy', 'variables', 'addon', 'theme', 'top'):
            registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                                   'resources/foo.scss',
                                                   slot=slotname))

        self.assertEquals(
            ['top', 'variables', 'addon', 'theme', 'policy'],
            slots(registry.get_resources(CONTEXT, REQUEST)))

    def test_resource_order_is_kept_within_slot(self):
        registry = SCSSRegistry()
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/baz.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/foo.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/bar.scss'))

        self.assertEquals(
            ['resources/baz.scss', 'resources/foo.scss', 'resources/bar.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST)))

    def test_only_available_resources_are_returned(self):
        registry = SCSSRegistry()
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/foo.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/bar.scss',
                                               profile='bar:default'))

        self.assertEquals(
            ['resources/foo.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST, ProfileInfoStub())))

        self.assertEquals(
            ['resources/foo.scss', 'resources/bar.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST,
                                         ProfileInfoStub('bar:default'))))

    def test_include_unavailable_resources(self):
        registry = SCSSRegistry()
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/foo.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/bar.scss',
                                               profile='bar:default'))

        self.assertEquals(
            ['resources/foo.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST, ProfileInfoStub())))

        self.assertEquals(
            ['resources/foo.scss', 'resources/bar.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST, ProfileInfoStub(),
                                         include_unavailable=True)))

    def test_reordering_resources_within_slot_with_before(self):
        registry = SCSSRegistry()
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/foo.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/bar.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/baz.scss',
                                               before='resources/bar.scss'))

        self.assertEquals(
            ['resources/foo.scss', 'resources/baz.scss', 'resources/bar.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST)))

    def test_reordering_resources_within_slot_with_after(self):
        registry = SCSSRegistry()
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/foo.scss',
                                               after='resources/bar.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/bar.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/baz.scss'))

        self.assertEquals(
            ['resources/bar.scss', 'resources/foo.scss', 'resources/baz.scss'],
            paths(registry.get_resources(CONTEXT, REQUEST)))

    def test_conflicting_order(self):
        registry = SCSSRegistry()
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/foo.scss',
                                               after='resources/bar.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/bar.scss',
                                               after='resources/foo.scss'))
        registry.add_resource(SCSSFileResource('ftw.theming.tests',
                                               'resources/baz.scss'))

        with self.assertRaises(CyclicResourceOrder) as cm:
            registry.get_resources(CONTEXT, REQUEST)
        self.assertEquals(
            "Cyclic resource order: [['ftw.theming.tests:resources/bar.scss', "
            "'ftw.theming.tests:resources/foo.scss']]",
            str(cm.exception))

    def test_calls_registered_resource_factories(self):
        foo = SCSSFileResource('ftw.theming.tests', 'resources/foo.scss')
        dynamic = SCSSResource('dynamic-scss', slot='addon',
                               source=u'$foreground = black;')
        bar = SCSSFileResource('ftw.theming.tests', 'resources/baz.scss')

        @provider(ISCSSResourceFactory)
        def dynamic_resource_factory(context, request):
            return dynamic

        registry = SCSSRegistry()
        registry.add_resource(foo)
        registry.add_resource(dynamic_resource_factory)
        registry.add_resource(bar)

        self.assertEquals([foo, dynamic, bar],
                          registry.get_resources(CONTEXT, REQUEST))

    def test_resource_factories_returning_None_are_skipped(self):
        registry = SCSSRegistry()

        @registry.add_resource
        @provider(ISCSSResourceFactory)
        def null_resource_factory(context, request):
            return None

        self.assertEquals([], registry.get_resources(CONTEXT, REQUEST))
        self.assertEquals([], registry.get_resources(CONTEXT, REQUEST,
                                                     include_unavailable=True))

    def test_get_raw_dynamic_resources(self):
        """The get_raw_dynamic_resources method returns all dynamic resources without
        ordering or filtering. This is much more efficient and can be used for fast
        cache calculation.
        """
        foo = SCSSFileResource('ftw.theming.tests', 'resources/foo.scss')
        bar = DynamicSCSSResource('bar')

        registry = SCSSRegistry()
        registry.add_resource(foo)
        registry.add_resource(bar)

        self.assertEquals([bar],
                          registry.get_raw_dynamic_resources(None, None))
