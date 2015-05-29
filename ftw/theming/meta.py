from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.registry import SCSSRegistry
from ftw.theming.resource import SCSSResource
from path import Path
from zope.component import provideUtility
from zope.component import queryUtility
from zope.configuration import fields
from zope.interface import Interface
from zope.schema import TextLine


class IAddSCSSDirective(Interface):

    file = fields.Path(
        title=u'Relative path to the .scss file.',
        required=True)

    slot = TextLine(
        title=u'The name of the slot where the resource should be'
        ' rendered in.',
        required=False)

    profile = TextLine(
        title=u'The name of the profile which needs to be installed'
        u' for this resource to be activated.',
        required=False)

    for_ = fields.GlobalInterface(
        title=u'The interface the context should provide.',
        required=False)

    layer = fields.GlobalInterface(
        title=u'The interface the request should provide.',
        required=False)

    before = TextLine(
        title=u'The name of the resource after which this resource should'
        ' be ordered.',
        description=u'The name consists of "package:relative file path"',
        required=False)

    after = TextLine(
        title=u'The name of the resource after which this resource should'
        ' be ordered.',
        description=u'The name consists of "package:relative file path"',
        required=False)


def add_scss(context, **kwargs):
    """Register an .scss file.
    """

    registry = queryUtility(ISCSSRegistry)
    if registry is None:
        registry = SCSSRegistry()
        provideUtility(registry)

    relpath = Path(kwargs['file']).relpath(
        Path(context.package.__file__).parent)
    resource_args = {
        'package': context.package.__name__,
        'relative_path': relpath}

    for name in ('slot', 'profile', 'for_', 'layer', 'before', 'after'):
        if name in kwargs:
            resource_args[name] = kwargs[name]

    registry.add_resource(SCSSResource(**resource_args))
