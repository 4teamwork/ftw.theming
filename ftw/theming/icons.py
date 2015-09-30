from plone.app.layout.icons import icons
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from zope.component import getUtility
import os.path
import re


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
        normalizer = getUtility(IIDNormalizer)
        image_filename = os.path.basename(self.url)
        image_filename = re.sub(r'\.png$', r'', image_filename)
        mimetype_class = 'icon-mimetype-img-{}'.format(
            normalizer.normalize(image_filename))
        return 'mimetype-icon {}'.format(mimetype_class)
