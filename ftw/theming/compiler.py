from ftw.theming.extensions import ThemingExtensions
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.interfaces import ISCSSFileResource
from ftw.theming.interfaces import ISCSSRegistry
from scss.compiler import Compiler
from scss.namespace import Namespace
from scss.source import SourceFile
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
        self.namespace = Namespace()

    def compile(self, debug=False):
        return self._compile(self._get_scss_files(), debug=debug)

    def compile_scss_string(self, source, debug=False):
        source_file = SourceFile.from_string(source)
        return self._compile((source_file,), debug=debug)

    def _get_scss_files(self):
        def make_source_file(resource):
            source = resource.get_source(self.context, self.request)
            if ISCSSFileResource.providedBy(resource):
                path = resource.path
            else:
                path = 'dynamic:{0}'.format(resource.name)
            return SourceFile.from_string(source, path)

        registry = getUtility(ISCSSRegistry)
        resources = registry.get_resources(self.context, self.request)
        return map(make_source_file, resources)

    def _compile(self, files, debug=False):
        compiler = Compiler(
            output_style=debug and 'expanded' or 'compressed',
            generate_source_map=True,
            namespace=self.namespace)
        compiler.extensions.append(ThemingExtensions)
        css = compiler.compile_sources(*files)
        return css.encode('utf-8')
