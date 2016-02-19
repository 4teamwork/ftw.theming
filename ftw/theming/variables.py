from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.resource import DynamicSCSSResource
from plone.namedfile.interfaces import IAvailableSizes
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.interface import provider
import hashlib


@provider(ISCSSResourceFactory)
def portal_url_variable_resource_factory(context, request):
    portal_url = getToolByName(context, 'portal_url')().decode('utf-8')
    cachekey = hashlib.md5(portal_url).hexdigest()
    return DynamicSCSSResource(
        'ftw.theming:portal_url', slot='variables',
        source=u'\n'.join((
               u'$portal-url: "{0}";'.format(portal_url),
               u'@include declare-variables(portal-url);')),
        cachekey=cachekey)


@provider(ISCSSResourceFactory)
def plone_image_sizes(context, request):
    sass_variables_template = (
        '$scale-{name}-width: {width}px;'
        '$scale-{name}-height: {height}px;'
        '@include declare-variables(scale-width-{name}, scale-height-{name});'
        )
    getAvailableSizes = queryUtility(IAvailableSizes)
    sizes = getAvailableSizes()

    def build_sass_map(size):
        width, height = size[1]
        name = size[0]
        return sass_variables_template.format(
            name=name, width=width, height=height)

    cachekey = hashlib.md5(str(sorted(sizes.values()))).hexdigest()
    sizes = map(build_sass_map, sizes.iteritems())

    return DynamicSCSSResource(
        'ftw.theming:image_sizes', slot='variables',
        source=u''.join(sizes),
        cachekey=cachekey)
