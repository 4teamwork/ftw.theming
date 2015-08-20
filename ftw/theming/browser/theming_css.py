from ftw.theming.interfaces import ICSSCaching
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
from zope.interface import alsoProvides
import hashlib


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


def is_debug_mode_enabled():
    cssregistry = getToolByName(getSite(), 'portal_css')
    return bool(cssregistry.getDebugMode())


def get_css_cache_key(context, debug_mode_caching=True):
    debug_mode_enabled = is_debug_mode_enabled()
    if not debug_mode_caching and debug_mode_enabled:
        return None

    portal = getToolByName(context, 'portal_url').getPortalObject()
    navroot = getNavigationRootObject(context, portal)
    compiler = getMultiAdapter((context, context.REQUEST), ISCSSCompiler)
    key = [navroot.absolute_url(),
           compute_css_bundle_hash(navroot),
           str(navroot.modified().millis()),
           compiler.get_cachekey(dynamic_resources_only=not debug_mode_enabled)]

    return hashlib.md5('.'.join(key)).hexdigest()


def ramcachekey(func, self):
    cachekey = get_css_cache_key(self.context, debug_mode_caching=False)
    if cachekey is None:
        raise ram.DontCache
    return cachekey


def get_theming_css_url(context):
    """Returns the theming.css URL for a context, relative to
    its navigation root.
    Cachekey params may be added.
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    navroot = getNavigationRootObject(context, portal)
    css_url = '{0}/theming.css'.format(navroot.absolute_url())
    cachekey = get_css_cache_key(context)
    if cachekey:
        css_url += '?cachekey={0}'.format(cachekey)
    return css_url


class ThemingCSSView(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'text/css; charset=utf-8')
        response.setHeader('X-Theme-Disabled', 'True')
        if self.request.get('cachekey'):
            # Do not set cache headers when no cachekey provided.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            # The cache header is only active when plone.app.caching is not
            # configured.
            response.setHeader('Cache-Control', 'private, max-age=31536000')
            alsoProvides(self, ICSSCaching)
        return self.get_css()

    @ram.cache(ramcachekey)
    def get_css(self):
        compiler = getMultiAdapter((self.context, self.request), ISCSSCompiler)
        return compiler.compile(debug=is_debug_mode_enabled())

    def invalidate_cache(self):
        cache = getUtility(ICacheChooser)('{0}.get_css'.format(__name__))
        cache.ramcache.invalidateAll()

    def get_url(self):
        return get_theming_css_url(self.context)


class RedirectToNavrootThemingCSSView(BrowserView):
    """The theming.css should only be shipped on navigation roots,
    but there may be requests (e.g. from tinymce) on other contexts.

    By redirecting to the navigation root we can make sure that the
    client-side caching works efficiently.
    """

    def __call__(self):
        return self.request.response.redirect(self.get_url())

    def get_url(self):
        return get_theming_css_url(self.context)
