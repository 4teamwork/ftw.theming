from ftw.theming.interfaces import ISCSSCompiler
from operator import methodcaller
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.memoize import ram
from plone.memoize.interfaces import ICacheChooser
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility


def compute_css_bundle_hash(context):
    """This method creates a hash of the current CSS resource registry.
    We need this in order to detect a bundle recook and flush our caches.
    We do this by using the hash of the currently cooked bundles as part of
    our cache key.
    """
    portal_css = getToolByName(context, 'portal_css')
    theme_resources = dict(reduce(list.__add__,
                                  map(methodcaller('items'),
                                      portal_css.concatenatedResourcesByTheme.values())))
    keys = theme_resources.keys()
    map(keys.extend, theme_resources.values())
    return str(hash(frozenset(keys)))


def get_css_cache_key(func, self):
    if self._debug_mode_enabled():
        raise ram.DontCache

    if self._no_cache_header_present():
        self.invalidate_cache()

    portal = getToolByName(self.context, 'portal_url').getPortalObject()
    navroot = getNavigationRootObject(self.context, portal)
    key = ['/'.join(navroot.getPhysicalPath()),
           compute_css_bundle_hash(self.context)]
    return '.'.join(key)


class ThemingCSSView(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'text/css; charset=utf-8')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)
        return self.get_css()

    @ram.cache(get_css_cache_key)
    def get_css(self):
        compiler = getMultiAdapter((self.context, self.request), ISCSSCompiler)
        return compiler.compile(debug=self._debug_mode_enabled())

    def invalidate_cache(self):
        cache = getUtility(ICacheChooser)('{0}.get_css'.format(__name__))
        cache.ramcache.invalidateAll()

    def _debug_mode_enabled(self):
        cssregistry = getToolByName(self.context, 'portal_css')
        return bool(cssregistry.getDebugMode())

    def _no_cache_header_present(self):
        return self.request.getHeader('Cache-Control') == 'no-cache'
