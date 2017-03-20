from Products.CMFCore.utils import getToolByName


def uninstalled(site):
    config_tool = getToolByName(site, 'portal_controlpanel')
    config_tool.unregisterConfiglet('ThemingResources')
