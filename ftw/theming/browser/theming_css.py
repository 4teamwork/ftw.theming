from ftw.theming.interfaces import ISCSSCompiler
from operator import methodcaller
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.memoize import ram
from plone.memoize.interfaces import ICacheChooser
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite


def compute_css_bundle_hash(context):
    """This method creates a hash of the current CSS resource registry.
    We need this in order to detect a bundle recook and flush our caches.
    We do this by using the hash of the currently cooked bundles as part of
    our cache key.
    """
    portal_css = getToolByName(context, 'portal_css')
    theme_resources = dict(
        reduce(list.__add__,
               map(methodcaller('items'),
                   portal_css.concatenatedResourcesByTheme.values())))
    keys = theme_resources.keys()
    map(keys.extend, theme_resources.values())
    return str(hash(frozenset(keys)))


def debug_mode_enabled():
    cssregistry = getToolByName(getSite(), 'portal_css')
    return bool(cssregistry.getDebugMode())


def get_css_cache_key(context):
    if debug_mode_enabled():
        return None

    portal = getToolByName(context, 'portal_url').getPortalObject()
    navroot = getNavigationRootObject(context, portal)
    key = [navroot.absolute_url(),
           compute_css_bundle_hash(navroot),
           str(navroot.modified().millis())]
    return '.'.join(key).encode('base64').strip()


def ramcachekey(func, self):
    cachekey = get_css_cache_key(self.context)
    if cachekey is None:
        raise ram.DontCache
    return cachekey


class ThemingCSSView(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'text/css; charset=utf-8')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)
        if self.request.get('cachekey'):
            # Do not set cache headers when no cachekey provided.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            response.setHeader('Cache-Control', 'private, max-age=31536000')
        return self.get_css()

    @ram.cache(ramcachekey)
    def get_css(self):
        compiler = getMultiAdapter((self.context, self.request), ISCSSCompiler)
        return compiler.compile(debug=debug_mode_enabled())

    def invalidate_cache(self):
        cache = getUtility(ICacheChooser)('{0}.get_css'.format(__name__))
        cache.ramcache.invalidateAll()
