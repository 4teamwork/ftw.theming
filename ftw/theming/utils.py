from plone.i18n.normalizer import IIDNormalizer
from zope.component import getUtility
import inspect
import os
import re


def find_object_in_stack(name, klass):
    frame = inspect.currentframe()
    while not isinstance(frame.f_locals.get(name, None), klass):
        frame = frame.f_back
    return frame.f_locals[name]


def get_mimetype_css_class_from_icon_path(icon_path):
    normalizer = getUtility(IIDNormalizer)
    image_filename = os.path.basename(icon_path)
    image_filename = re.sub(r'\.png$', r'', image_filename)
    image_filename = re.sub(r'\.gif$', r'', image_filename)
    return 'icon-mimetype-img-{}'.format(
        normalizer.normalize(image_filename, max_length=255)
    )
