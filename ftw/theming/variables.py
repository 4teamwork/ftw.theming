from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.resource import SCSSResource
from Products.CMFCore.utils import getToolByName
from zope.interface import provider


@provider(ISCSSResourceFactory)
def portal_url_variable_resource_factory(context, request):
    portal_url = getToolByName(context, 'portal_url')().decode('utf-8')
    return SCSSResource(
        'ftw.theming:portal_url', slot='variables',
        source=u'\n'.join((
                u'$portal-url: "{0}";'.format(portal_url),
                u'@include declare-variables(portal-url);')))
