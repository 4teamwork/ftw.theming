from collections import OrderedDict
from ftw.theming.exceptions import CyclicResourceOrder
from ftw.theming.interfaces import ISassRegistry
from ftw.theming.interfaces import SLOTS
from tarjan import tarjan
from zope.interface import implements


class SassRegistry(object):
    implements(ISassRegistry)

    def __init__(self):
        self.resources = []

    def add_resource(self, resource):
        self.resources.append(resource)

    def get_resources(self, context, request, profileinfo=None,
                      include_unavailable=False):
        resources = reduce(list.__add__,
                           map(self.order_resources,
                               map(self.get_resources_for_slot, SLOTS)))
        if not include_unavailable:
            resources = filter(
                lambda res: res.available(context, request, profileinfo),
                resources)
        return resources

    def get_resources_for_slot(self, slotname):
        return filter(lambda res: res.slot == slotname, self.resources)

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
