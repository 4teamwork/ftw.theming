from functools import partial
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import re


class Stub(object):

    def __init__(self, *interfaces):
        for iface in interfaces:
            alsoProvides(self, iface)


CONTEXT = Stub(IPloneSiteRoot, INavigationRoot)
REQUEST = Stub(IDefaultBrowserLayer)


class ProfileInfoStub(object):

    def __init__(self, *installed):
        self.installed = map(partial(re.sub, r'^profile\-', ''), installed)

    def is_profile_installed(self, profileid):
        profileid = re.sub(r'^profile\-', '', profileid)
        return profileid in self.installed
