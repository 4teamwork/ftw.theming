from ftw.theming.utils import find_object_in_stack
from lxml import etree
from lxml.cssselect import CSSSelector
from path import Path
from scss.calculator import Calculator
from scss.extension import Extension
from scss.namespace import Namespace
from scss.types import Boolean
from scss.types import Url
from zope.dottedname.resolve import resolve
import inspect
import mimetypes


class ThemingExtensions(Extension):
    """Extensions for standard functions provided by ftw.theming.
    """

    name = 'theming'
    namespace = Namespace()


@ThemingExtensions.namespace.declare
def function_exists(name):
    calculator = inspect.currentframe().f_back.f_back.f_locals['self']
    functions = calculator.namespace._functions
    function_names = dict(functions.keys()).keys()
    return Boolean(name.render() in function_names)


@ThemingExtensions.namespace.declare
def embed_resource(relpath, fill_css=None, fill_xpath=None):
    path = find_relative_resource(relpath)
    mimetype, _compression = mimetypes.guess_type(path)
    data = path.bytes()
    data = fill_svg(data, fill_css=fill_css, fill_xpath=fill_xpath)
    return Url(u'data:{0};base64,{1}'.format(
        mimetype.decode('utf-8'),
        data.encode('base64').decode('utf-8')))


def find_relative_resource(relpath):
    calculator = find_object_in_stack('self', Calculator)
    variables = calculator.namespace.variables
    package = variables.get('$current-package').render().strip('"').strip("'")
    module = resolve(package)
    filename = variables.get('$current-relpath').render().strip('"').strip("'")
    directory = Path(module.__file__).parent.joinpath(filename).parent
    path = directory.joinpath(relpath.render().strip('"').strip("'")).abspath()
    if not path.isfile():
        raise ValueError('{0}: File does not exist: {1}'.format(
            filename, path))
    return path


def fill_svg(data, fill_css=None, fill_xpath=None):
    doc = etree.fromstring(data)
    expressions = []

    for xpr, color in fill_xpath or ():
        xpath_xpr = xpr.render().strip('"').strip("'")
        expressions.append((xpath_xpr, color))

    for xpr, color in fill_css or ():
        css_xpr = xpr.render().strip('"').strip("'")
        xpath_xpr = CSSSelector(css_xpr).path
        expressions.append((xpath_xpr, color))

    for xpath_xpr, color in expressions:
        for node in doc.xpath(xpath_xpr):
            node.attrib['fill'] = color.render()

    return etree.tostring(doc)
