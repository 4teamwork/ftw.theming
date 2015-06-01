from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.interfaces import ISCSSRegistry
from scss import Scss
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface


class SCSSCompiler(object):
    implements(ISCSSCompiler)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def compile(self):
        scss_input = []
        registry = getUtility(ISCSSRegistry)
        for resource in registry.get_resources(self.context, self.request):
            scss_input.append(resource.get_source())
        css = Scss().compile('\n'.join(scss_input))
        return css.encode('utf-8')
