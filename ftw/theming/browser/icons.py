from ftw.theming import utils
from operator import attrgetter
from operator import methodcaller
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import IDynamicViewTypeInformation
from Products.Five import BrowserView


class ThemingIcons(BrowserView):

    def get_portal_types(self):
        portal_types = getToolByName(self.context, 'portal_types')
        return map(methodcaller('getId'),
                   filter(IDynamicViewTypeInformation.providedBy,
                          portal_types.objectValues()))

    def get_mime_types(self):
        mimetypes_registry = getToolByName(self.context, 'mimetypes_registry')
        icon_paths = sorted(set(map(attrgetter('icon_path'),
                                    mimetypes_registry.mimetypes())))

        def itemize(filename):
            name = utils.get_mimetype_css_class_from_icon_path(filename)
            return {
                'filename': filename,
                'classes': 'mimetype-icon {}'.format(name),
                'normalized_name': name.replace('icon-mimetype-img-', '')}

        return map(itemize, icon_paths)
