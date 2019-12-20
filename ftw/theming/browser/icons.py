from ftw.theming import utils
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
        result = []
        seen_path = set()

        for mimetype in mimetypes_registry.mimetypes():
            if not mimetype.icon_path or not mimetype.mimetypes:
                continue
            if mimetype.icon_path in seen_path:
                continue
            seen_path.add(mimetype.icon_path)

            img_class = utils.get_mimetype_css_class_from_icon_path(mimetype.icon_path)
            mime_type_class = utils.get_mimetype_css_class_from_mime_type(
                mimetype.mimetypes[0])
            result.append({
                'filename': mimetype.icon_path,
                'getIcon_based_classes': 'mimetype-icon {}'.format(img_class),
                'normalized_name': img_class.replace('icon-mimetype-img-', ''),
                'mime_type_based_classes': 'mimetype-icon {}'.format(mime_type_class),
                'normalized_mime_type': mime_type_class.replace('icon-mimetype-mt-', '')})

        return result
