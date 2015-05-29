from ftw.theming.interfaces import ISassRegistry
from ftw.theming.interfaces import SLOTS
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
                           map(self.get_resources_for_slot, SLOTS))
        if not include_unavailable:
            resources = filter(
                lambda res: res.available(context, request, profileinfo),
                resources)
        return resources

    def get_resources_for_slot(self, slotname):
        return filter(lambda res: res.slot == slotname, self.resources)
