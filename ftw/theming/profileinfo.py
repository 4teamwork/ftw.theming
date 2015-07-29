from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
import re


class ProfileInfo(object):

    def __init__(self, context):
        self.context = context

    @instance.memoize
    def is_profile_installed(self, profileid):
        profileid = re.sub(r'^profile\-', '', profileid)
        quickinstaller = getToolByName(self.context, 'portal_quickinstaller')
        portal_setup = getToolByName(self.context, 'portal_setup')

        try:
            profileinfo = portal_setup.getProfileInfo(profileid)
        except KeyError:
            return False

        product = profileinfo['product']
        if quickinstaller.isProductInstallable(product) and \
                not quickinstaller.isProductInstalled(product):
            return False

        version = portal_setup.getLastVersionForProfile(profileid)
        return version != 'unknown'
