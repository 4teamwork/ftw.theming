from plone.app.layout.navigation.root import getNavigationRootObject
from ftw.theming.browser.theming_css import get_css_cache_key
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class ThemingCSS(ViewletBase):

    template = '<link rel="stylesheet" type="text/css" href="{href}" />'

    def render(self):
        return self.template.format(href=self.css_url())

    def css_url(self):
        navroot_url = self.get_navigation_root().absolute_url()
        css_url = '{0}/theming.css'.format(navroot_url)
        cachekey = get_css_cache_key(self.context)
        if cachekey:
            css_url += '?cachekey={0}'.format(cachekey)
        return css_url

    def get_navigation_root(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return getNavigationRootObject(self.context, portal)
