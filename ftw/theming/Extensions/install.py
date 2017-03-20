from Products.CMFCore.utils import getToolByName


def install(self):
    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-ftw.theming:default')


def uninstall(self):
    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-ftw.theming:uninstall',
        ignore_dependencies=True)
