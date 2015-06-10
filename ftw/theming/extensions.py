from scss.extension import Extension
from scss.namespace import Namespace
from scss.types import Boolean
import inspect


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
