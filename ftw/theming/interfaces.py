from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import Interface


SLOTS = ('top',
         'variables',
         'ftw.theming',
         'theme',
         'policy',
         'bottom')


class ISassResource(Interface):
    """A sass resource represents a sass file for registering in the sass registry.
    It holds the relevant information for building the sass pipeline.
    """

    def __init__(package, relative_path, slot,
                 profile=None, for_=INavigationRoot, layer=Interface):
        """Initialize a sass resource.

        :param package: The name of the python package where the resource is
          registered.
        :type package: string
        :param relative_path: The path to the sass file relative to the
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
        :returns: ``True`` when the resource is available and should be included.
        :rtype: bool
        """
