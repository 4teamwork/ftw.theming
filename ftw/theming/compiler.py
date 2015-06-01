from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.interfaces import ISCSSRegistry
from scss.compiler import Compiler
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

    def compile(self, debug=False):
        return self._compile(self._get_scss_files(), debug=debug)

    def _get_scss_files(self):
        registry = getUtility(ISCSSRegistry)
        resources = registry.get_resources(self.context, self.request)
        return [res.path for res in resources]

    def _compile(self, files, debug=False):
        compiler = Compiler(
            output_style=debug and 'expanded' or 'compressed',
            generate_source_map=True)
        css = compiler.compile(*files)
        return css.encode('utf-8')
