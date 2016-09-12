from ftw.theming.interfaces import IResourceDisablerConfig
from plone.app.theming import utils
from zope.component import getUtility


def CSSRegistryTool_evaluate(self, item, context):
    """Evaluate an object to see if it should be displayed.
    PATCH: let ftw.theming exclude resources.
    """

    if utils.isThemeEnabled(context.REQUEST):
        config = getUtility(IResourceDisablerConfig)
        theme_name = utils.getCurrentTheme()
        resource_id = item.getId()
        if not config.is_css_resource_enabled(resource_id, theme_name):
            return False

    return self._old_evaluate(item, context)
