from ftw.theming.interfaces import ISCSSFileResource
from ftw.theming.interfaces import SLOTS
from ftw.theming.profileinfo import ProfileInfo
from path import Path
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import implements
from zope.interface import Interface


class SCSSFileResource(object):
    """A scss resource represents a scss file for registering in the scss registry.
    It holds the relevant information for building the scss pipeline.
    """
    implements(ISCSSFileResource)

    def __init__(self, package, relative_path, slot='addon',
                 profile=None, for_=INavigationRoot, layer=Interface,
                 before=None, after=None):
        if slot not in SLOTS:
            raise ValueError('Invalid slot "{0}". Valid slots: {1}'.format(
                    slot, SLOTS))

        self.name = self._make_resource_name(package, relative_path)
        self.package = package
        self.relative_path = relative_path
        self.path = self._resolve_path(package, relative_path)
        self.slot = slot
        self.profile = profile
        self.for_ = for_
        self.layer = layer
        self.before = before and self._make_resource_name(package, before)
        self.after = after and self._make_resource_name(package, after)

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

    def get_source(self):
        return self.path.text()

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
