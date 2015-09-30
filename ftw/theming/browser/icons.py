from operator import attrgetter
from operator import methodcaller
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import IDynamicViewTypeInformation
from Products.Five import BrowserView
from zope.component import getUtility
import re


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
        normalizer = getUtility(IIDNormalizer)

        def itemize(filename):
            name = normalizer.normalize(re.sub(r'\.png$', r'', filename))
            return {
                'filename': filename,
                'classes': 'mimetype-icon icon-mimetype-img-{}'.format(name),
                'normalized_name': name}

        return map(itemize, icon_paths)
