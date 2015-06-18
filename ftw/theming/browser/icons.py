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
