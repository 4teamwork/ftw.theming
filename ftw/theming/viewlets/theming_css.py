from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class ThemingCSS(ViewletBase):

    template = '<link rel="stylesheet" type="text/css" href="{href}" />'

    def render(self):
        return self.template.format(href=self.css_url())

    def css_url(self):
        return '{0}/theming.css'.format(
            self.get_navigation_root().absolute_url())

    def get_navigation_root(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        return getNavigationRootObject(self.context, portal)
