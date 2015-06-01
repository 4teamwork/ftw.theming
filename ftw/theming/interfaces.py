from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import Interface


SLOTS = ('top',
         'variables',
         'ftw.theming',
         'addon',
         'theme',
         'policy',
         'bottom')


class ISCSSCompiler(Interface):
    """Converts the SCSS to CSS.
    """

    def __init__(context, request):
        """A multi-adapter, adapting a context and a request.
        """

    def compile():
        """Compile the scss files looked up from the SCSS registry
        into one CSS file.

        :returns: The compiled CSS.
        :rtype: utf-8 encoded bytestring
        """


class ISCSSRegistry(Interface):
    """The scss registry holds all registered ISCSSResource objects.
    It decides which resources are used for compiling to CSS.
    """

    def add_resource(resource):
        """Add a scss resource to the registry.

        :param resource: A scss resource object.
        :type resource: :py:class:`ftw.theming.interfaces.ISCSSResource`
        """

    def get_resources(context, request, profileinfo=None,
                      include_unavailable=False):
        """Return the resources for a context and a request.
        The resources are filtered and sorted by slots.

        :param context: A acquisition wrapped context object.
        :type context: object
        :param request: The request object.
        :param request: object
        :param profileinfo: A profileinfo object for checking whether
          the profile is installed.
        :type profile: :py:class:`ftw.theming.profileinfo.ProfileInfo`
        :param include_unavailable: Disable filtering unavailable resources.
        :type include_unavailable: bool (default: False)
        :returns: A list of scss resource objects.
        :rtype: list of :py:class:`ftw.theming.interfaces.ISCSSResource`
        """


class ISCSSResource(Interface):
    """A scss resource represents a scss file for registering in the scss registry.
    It holds the relevant information for building the scss pipeline.

    Resources are identified by name. The name of the resource contains the
    package dottedname and the relative path to the file,
    e.g. "my.package.browser/resources/style.scss"
    """

    def __init__(package, relative_path, slot='addon',
                 profile=None, for_=INavigationRoot, layer=Interface,
                 before=None, after=None):
        """Initialize a scss resource.

        :param package: The name of the python package where the resource is
          registered.
        :type package: string
        :param relative_path: The path to the scss file relative to the
          package directory.
        :type relative_path: string
        :param slot: The slot where the resource belongs. This must be one of
          the list of slots.
        :type slot: string
        :param profile: The name of the Generic Setup profile,
          e.g. "profile-my.package:default".
        :type profile: string
        :param for_: The context interface for which this resource is
          registered. This is usually the Plone site, but may also be
          another navigation root.
        :type for_: :py:class:`zope.interface.Interface`
        :param layer: The request layer interface for which this resource
          is registered.
        :type layer: :py:class:`zope.interface.Interface`
        :param before: Move this resource before the other resource with that
          name within the same slot.
        :type before: string (name of other resource)
        :param after: Move this resource after the other resource with that
          name within the same slot.
        :type after: string (name of other resource)
        """

    def available(context, request, profileinfo=None):
        """Check whether the resource is available for this context.

        Checks applied:

        - ``context`` must provide the ``for_``-interface of the resorce
        - ``request`` must provide the ``layer``-interface of the resorce
        - the profile must be installed.

        :param context: A acquisition wrapped context object.
        :type context: object
        :param request: The request object.
        :type request: object
        :param profileinfo: A profileinfo object for checking whether
          the profile is installed.
        :type profile: :py:class:`ftw.theming.profileinfo.ProfileInfo`
        :returns: ``True`` when the resource is available and should be
          included.
        :rtype: bool
        """

    def get_source():
        """Returns the raw SCSS of this resource as string.

        :returns: The raw SCSS
        :rtype: string
        """
