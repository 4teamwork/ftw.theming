from ftw.theming import utils
from plone.app.layout.icons import icons
from plone.memoize.instance import memoize


WRAPPER_TEMPLATE = '<span class="{classes}">{content}</span>'


class CatalogBrainContentIcon(icons.CatalogBrainContentIcon):

    @memoize
    def html_tag(self):
        image_tag = super(CatalogBrainContentIcon, self).html_tag()
        if image_tag is None:
            return None
        return WRAPPER_TEMPLATE.format(classes=self.wrapper_classes(),
                                       content=image_tag)

    def wrapper_classes(self):
        return 'mimetype-icon {}'.format(
            utils.get_mimetype_css_class_from_icon_path(self.url)
        )
