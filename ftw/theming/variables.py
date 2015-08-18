from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.resource import DynamicSCSSResource
from Products.CMFCore.utils import getToolByName
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
