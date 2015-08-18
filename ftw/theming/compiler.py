from ftw.theming.extensions import ThemingExtensions
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.interfaces import ISCSSFileResource
from ftw.theming.interfaces import ISCSSRegistry
from pathlib import Path
from scss.compiler import Compiler
from scss.namespace import Namespace
from scss.source import SourceFile
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
import hashlib
import os.path


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

    def get_cachekey(self, dynamic_resources_only=False, **kwargs):
        registry = getUtility(ISCSSRegistry)

        if dynamic_resources_only:
            # Usually used in production mode: omit file resources and skip
            # ordering in order to speed up cache generation.
            resources = registry.get_raw_dynamic_resources(self.context, self.request)

        else:
            # Usually used in development mode: include file's modified date
            # in order to be up to date when developing.
            resources = registry.get_resources(self.context, self.request)

        result = hashlib.md5()
        map(result.update, (resource.get_cachekey(self.context, self.request)
                            for resource in resources))
        return result.hexdigest()

    def _get_scss_files(self):
        def make_source_file(resource):
            package = resource.name.split(':')[0]
            relpath = resource.name.split(':')[-1]
            filename = relpath.split('/')[-1]
            source = u'\n'.join((
                    u'$current-package: "{0}";'.format(package),
                    u'$current-relpath: "{0}";'.format(relpath),
                    u'$current-filename: "{0}";'.format(filename),
                    resource.get_source(self.context, self.request)))
            if ISCSSFileResource.providedBy(resource):
                source_file = SourceFile.from_string(
                    source, Path(str(resource.path)))
                source_file.origin = Path(str(resource.path))
                return source_file
            else:
                path = 'dynamic:{0}'.format(resource.name)
                return SourceFile.from_string(source, path)

        registry = getUtility(ISCSSRegistry)
        resources = registry.get_resources(self.context, self.request)
        return map(make_source_file, resources)

    def _compile(self, files, debug=False):
        compiler = Compiler(
            search_path=self._get_search_path_for_files(files),
            output_style=debug and 'expanded' or 'compressed',
            generate_source_map=True,
            namespace=self.namespace)
        compiler.extensions.append(ThemingExtensions())
        css = compiler.compile_sources(*files)
        return css.encode('utf-8')

    def _get_search_path_for_files(self, files):
        directories = []
        for source_file in files:
            if not source_file.path or not source_file.path.startswith('/'):
                continue
            path = os.path.dirname(source_file.path)
            if path not in directories:
                directories.append(path)
        return map(Path, directories)
