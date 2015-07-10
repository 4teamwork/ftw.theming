from ftw.theming.browser.theming_css import get_theming_css_url
from plone.app.layout.viewlets.common import ViewletBase


class ThemingCSS(ViewletBase):

    template = '<link rel="stylesheet" type="text/css" href="{href}" />'

    def render(self):
        return self.template.format(href=get_theming_css_url(self.context))
