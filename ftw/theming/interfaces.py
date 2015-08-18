from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Attribute
from zope.interface import Interface


SLOTS = ('top',
         'variables',
         'mixins',
         'ftw.theming',
         'addon',
         'theme',
         'policy',
         'bottom')


class IThemingLayer(IDefaultPloneLayer):
    """A browser layer provided by the request when the ftw.theming
    Generic Setup profile is installed.
    """


class ISCSSCompiler(Interface):
    """Converts the SCSS to CSS.
    """

    def __init__(context, request):
        """A multi-adapter, adapting a context and a request.
        """

    def compile(debug=False):
        """Compile the scss files looked up from the SCSS registry
        into one CSS file.

        :param debug: Enabling debug mode adds sass debug infos for
          browser plugins.
        :type debug: bool (default: ``False``)
        :returns: The compiled CSS.
        :rtype: utf-8 encoded bytestring
        """


class ISCSSRegistry(Interface):
    """The scss registry holds all registered ISCSSFileResource objects.
    It decides which resources are used for compiling to CSS.
    """

    def add_resource(resource):
        """Add a scss resource to the registry.

        :param resource: A scss resource object.
        :type resource: :py:class:`ftw.theming.interfaces.ISCSSFileResource`
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
        :rtype: list of :py:class:`ftw.theming.interfaces.ISCSSFileResource`
        """

    def get_raw_dynamic_resources(context, request):
        """Returns all dynamic resources without ordering or filtering them.
        This is an efficient lookup for doing such as fast cache calculation.

        :param context: A acquisition wrapped context object.
        :type context: object
        :param request: The request object.
        :param request: object
        :returns: A list of scss resource objects.
        :rtype: list of :py:class:`ftw.theming.interfaces.IDynamicSCSSResource`
        """


class ISCSSResource(Interface):
    """An SCSS resource has a snippet of SCSS code and can tell whether the
    resources should be rendered an a specific context / request / setup.
    """

    name = Attribute('The name of the resource.')
    slot = Attribute('The slot where the resource belongs.'
                     ' This must be one of the list of slots.')
    before = Attribute('Move this resource before the other resource with that'
                       ' name within the same slot.')
    after = Attribute('Move this resource after the other resource with that'
                      ' name within the same slot.')

    def __init__(name, slot='addon', before=None, after=None, source=u''):
        """Initialize an scss resource.

        :param name: The name of the resource.
        :type name: string
        :param slot: The slot where the resource belongs. This must be one of
          the list of slots.
        :type slot: string
        :param before: Move this resource before the other resource with that
          name within the same slot.
        :type before: string (name of other resource)
        :param after: Move this resource after the other resource with that
          name within the same slot.
        :type after: string (name of other resource)
        :param source: The SCSS source.
        :type source: string
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

    def get_source(context, request):
        """Returns the raw SCSS of this resource as string.

        :param context: A acquisition wrapped context object.
        :type context: object
        :param request: The request object.
        :type request: object
        :returns: The raw SCSS
        :rtype: string
        """

    def get_cachekey(context, request):
        """Returns a string which changes when the content source
        changes.

        :param context: A acquisition wrapped context object.
        :type context: object
        :param request: The request object.
        :type request: object
        :returns: cache string
        :rtype: string
        """


class IDynamicSCSSResource(ISCSSResource):
    """A dynamic SCSS resource provides SCSS source which may change.
    In order to have the correct caching, a cachekey is necessary.

    Dynamic resources should either subclass the DynamicSCSSResource class or
    initialize it with at least a name, a source and a cache key.
    """

    def __init__(name, slot='addon', before=None, after=None, source=u''):
        """Initialize an scss resource.

        :param name: The name of the resource.
        :type name: string
        :param slot: The slot where the resource belongs. This must be one of
          the list of slots.
        :type slot: string
        :param before: Move this resource before the other resource with that
          name within the same slot.
        :type before: string (name of other resource)
        :param after: Move this resource after the other resource with that
          name within the same slot.
        :type after: string (name of other resource)
        :param source: The SCSS source.
        :type source: string
        :param cachekey: The cache key which must change when the source changes.
        :type source: string
        """


class ISCSSFileResource(ISCSSResource):
    """A scss resource represents a scss file for registering in the scss registry.
    It holds the relevant information for building the scss pipeline.

    Resources are identified by name. The name of the resource contains the
    package dottedname and the relative path to the file,
    e.g. "my.package.browser/resources/style.scss"
    """

    def __init__(package, relative_path, slot='addon',
                 profile=None, for_=INavigationRoot, layer=Interface,
                 before=None, after=None):
        """Initialize an scss resource.

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


class ISCSSResourceFactory(Interface):
    """An SCSS resource factory creates and returnes an SCSSResource when called.
    """

    def __call__(context, request):
        """Accepts any context and request and returns an SCSSResource object.
        """


class ICSSCaching(Interface):
    """Marker interface for enabling plone.app.caching on the theming resource.
    """
