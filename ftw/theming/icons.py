from Acquisition import aq_base
from ftw.theming import utils
from plone.app.layout.icons import icons
from plone.memoize.instance import memoize


WRAPPER_TEMPLATE = u'<span class="mimetype-icon {cssclass}">{content}</span>'


class CatalogBrainContentIcon(icons.CatalogBrainContentIcon):

    @memoize
    def html_tag(self):
        image_tag = super(CatalogBrainContentIcon, self).html_tag()
        if image_tag is not None:
            return WRAPPER_TEMPLATE.format(
                cssclass=utils.get_mimetype_css_class_from_icon_path(self.url),
                content=image_tag)
        elif getattr(aq_base(self.brain), 'mime_type', False):
            return WRAPPER_TEMPLATE.format(
                cssclass=utils.get_mimetype_css_class_from_mime_type(self.brain.mime_type),
                content='')
        else:
            return None
