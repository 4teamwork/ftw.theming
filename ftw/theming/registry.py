from collections import OrderedDict
from ftw.theming.exceptions import CyclicResourceOrder
from ftw.theming.interfaces import IDynamicSCSSResource
from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.interfaces import SLOTS
from ftw.theming.profileinfo import ProfileInfo
from tarjan import tarjan
from zope.interface import implements


class SCSSRegistry(object):
    implements(ISCSSRegistry)

    def __init__(self):
        self.resources = []

    def add_resource(self, resource):
        self.resources.append(resource)

    def get_resources(self, context, request, profileinfo=None,
                      include_unavailable=False):
        slot_lookup = self._slot_resources_lookup(context, request)
        resources = reduce(list.__add__,
                           map(self.order_resources,
                               map(slot_lookup.get, SLOTS)))

        if not include_unavailable:
            profileinfo = profileinfo or ProfileInfo(context)
            resources = filter(
                lambda res: res.available(context, request, profileinfo),
                resources)
        return resources

    def get_raw_dynamic_resources(self, context, request):
        slot_lookup = self._slot_resources_lookup(context, request)
        resources = reduce(list.__add__, slot_lookup.values())
        return filter(IDynamicSCSSResource.providedBy, resources)

    def order_resources(self, resources):
        if not resources:
            return resources

        graph = OrderedDict((res.name, []) for res in resources)
        for res in resources:
            if res.after and res.after in graph:
                graph[res.name].append(res.after)
            if res.before and res.before in graph:
                graph[res.before].append(res.name)

        groups = tarjan(graph)

        cyclic_order = filter(lambda x: len(x) > 1, groups)
        if cyclic_order:
            raise CyclicResourceOrder(map(sorted, cyclic_order),
                                      resources, graph)

        order = reduce(list.__add__, groups)
        return sorted(resources, key=lambda res: order.index(res.name))

    def _slot_resources_lookup(self, context, request):
        result = dict((slot, []) for slot in SLOTS)
        for resource in self.resources:
            if ISCSSResourceFactory.providedBy(resource):
                resource = resource(context, request)
            if resource is not None:
                result[resource.slot].append(resource)
        return result
