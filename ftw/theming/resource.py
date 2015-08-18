from ftw.theming.interfaces import IDynamicSCSSResource
from ftw.theming.interfaces import ISCSSFileResource
from ftw.theming.interfaces import ISCSSResource
from ftw.theming.interfaces import SLOTS
from ftw.theming.profileinfo import ProfileInfo
from path import Path
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import implements
from zope.interface import Interface
import hashlib


class SCSSResource(object):
    """A basic SCSS resource to be extended.
    """
    implements(ISCSSResource)

    def __init__(self, name, slot='addon', before=None, after=None,
                 source=u''):
        if slot not in SLOTS:
            raise ValueError('Invalid slot "{0}". Valid slots: {1}'.format(
                    slot, SLOTS))

        self.name = name
        self.slot = slot
        self.before = before
        self.after = after
        self.source = source

    def available(self, context, request, profileinfo=None):
        return True

    def get_source(self, context, request):
        return self.source

    def get_cachekey(self, context, request):
        raise NotImplementedError(
            'SCSSResource {} has no cachekey'.format(self.name))


class DynamicSCSSResource(SCSSResource):
    """A dynamic SCSS resource provides SCSS source which may change.
    In order to have the correct caching, a cachekey is necessary.

    Dynamic resources should either subclass the DynamicSCSSResource class or
    initialize it with at least a name, a source and a cache key.
    """
    implements(IDynamicSCSSResource)

    def __init__(self, name, slot='addon', before=None, after=None,
                 source=u'', cachekey=None):
        super(DynamicSCSSResource, self).__init__(name=name,
                                                  slot=slot,
                                                  before=before,
                                                  after=after,
                                                  source=source)
        self.cachekey = cachekey

    def get_cachekey(self, context, request):
        if not self.cachekey:
            raise NotImplementedError('No cachekey set.')
        return self.cachekey


class SCSSFileResource(SCSSResource):
    """A scss resource represents a scss file for registering in the scss registry.
    It holds the relevant information for building the scss pipeline.
    """
    implements(ISCSSFileResource)

    def __init__(self, package, relative_path, slot='addon',
                 profile=None, for_=INavigationRoot, layer=Interface,
                 before=None, after=None):
        name = self._make_resource_name(package, relative_path)
        before = before and self._make_resource_name(package, before)
        after = after and self._make_resource_name(package, after)
        super(SCSSFileResource, self).__init__(name, slot=slot,
                                               before=before, after=after)

        self.package = package
        self.relative_path = relative_path
        self.path = self._resolve_path(package, relative_path)
        self.profile = profile
        self.for_ = for_
        self.layer = layer

    def available(self, context, request, profileinfo=None):
        if not self.for_.providedBy(context):
            return False

        if not self.layer.providedBy(request):
            return False

        if self.profile is not None:
            profileinfo = profileinfo or ProfileInfo(context)
            if not profileinfo.is_profile_installed(self.profile):
                return False

        return True

    def get_source(self, context, request):
        return self.path.text('utf-8')

    def get_cachekey(self, context, request):
        return str(self.path.mtime)

    @staticmethod
    def _resolve_path(package, relative_path):
        package_path = Path(__import__(package, fromlist=package).__path__[0])
        absolute_path = package_path.joinpath(relative_path)
        with absolute_path.open():
            pass  # test if file exists
        return absolute_path

    @staticmethod
    def _make_resource_name(package, relative_path):
        if ':' in relative_path:
            return relative_path
        return ':'.join((package, relative_path))
