from ftw.theming.interfaces import ISCSSFileResource
from ftw.theming.interfaces import ISCSSRegistry
from Products.Five import BrowserView
from zope.component import getUtility


class ThemingResources(BrowserView):

    def resource_items(self):
        for index, resource in enumerate(self.resources(), 1):
            available = resource.available(self.context, self.request)
            cssclasses = 'theming-resource '
            cssclasses += available and 'available' or 'not-available'

            infos = {
                'available': available,
                'cssclasses': cssclasses,
                'index': index,
                'name': resource.name,
                'slot': resource.slot,
                }

            if ISCSSFileResource.providedBy(resource):
                infos.update({
                        'path': resource.path,
                        'package': resource.package,
                        'profile': resource.profile,
                        'for_name': resource.for_.__name__,
                        'for_path': resource.for_.__identifier__,
                        'layer_name': resource.layer.__name__,
                        'layer_path': resource.layer.__identifier__,
                        })

            yield infos

    def resources(self):
        registry = getUtility(ISCSSRegistry)
        return registry.get_resources(self.context, self.request,
                                      include_unavailable=True)
