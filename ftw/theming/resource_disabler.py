from collections import defaultdict
from ftw.theming.interfaces import IResourceDisablerConfig
from zope.interface import implements


PLONE_RESOURCES = (
    '++resource++plone.app.discussion.stylesheets/discussion.css',
    '++resource++plone.app.jquerytools.dateinput.css',
    '++resource++plone.app.jquerytools.overlays.css',
    '++resource++tinymce.stylesheets/tinymce.css',
    'IEFixes.css',
    'RTL.css',
    'authoring.css',
    'base.css',
    'bbb-kss.css',
    'columns.css',
    'controlpanel.css',
    'deprecated.css',
    'forms.css',
    'invisibles.css',
    'member.css',
    'mobile.css',
    'navtree.css',
    'portlets.css',
    'print.css',
    'public.css',
    'reset.css',

    # ploneCustom.css is empty by default and can be used for TTW customizations,
    # therefore we should not disable it by default.
    # 'ploneCustom.css',
)


class ResourceDisablerConfig(object):
    implements(IResourceDisablerConfig)

    def __init__(self):
        self.reset()

    def add_css_resource(self, resource_id, theme_name, enabled):
        self.resources['portal_css'][theme_name][resource_id] = enabled

    def is_css_resource_enabled(self, resource_id, theme_name):
        return self.resources['portal_css'][theme_name].get(resource_id, True)

    def disable_plone_resources(self, theme_name):
        for resource_id in PLONE_RESOURCES:
            self.add_css_resource(resource_id, theme_name, enabled=False)

    def reset(self):
        self.resources = {'portal_css': defaultdict(dict)}
