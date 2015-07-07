from collections import OrderedDict
from ftw.theming.interfaces import ISCSSCompiler
from ftw.theming.utils import find_object_in_stack
from operator import methodcaller
from Products.Five import BrowserView
from scss.calculator import Calculator
from scss.types import Null
from zope.component import getMultiAdapter


class ThemingVariablesView(BrowserView):

    def packages(self):
        packages = OrderedDict()
        compiler = getMultiAdapter((self.context, self.request), ISCSSCompiler)

        @compiler.namespace.declare
        def register_theming_variables(*varnames):
            calculator = find_object_in_stack('self', Calculator)
            variables = calculator.namespace.variables
            package = (variables.get('$current-package').render()
                       .strip('"').strip("'"))
            filename = (variables.get('$current-filename').render()
                        .strip('"').strip("'"))
            varnames = map(methodcaller('render'), varnames)

            if package not in packages:
                packages[package] = []

            for name in varnames:
                name = u'${0}'.format(name)
                value = variables.get(name, None)
                vartype = value.__class__.__name__
                value = value and value.render or '???'
                packages[package].append({'filename': filename,
                                           'name': name,
                                           'value': value,
                                           'type': vartype})
            return Null()

        compiler.compile()
        return ({'name': key, 'variables': values}
                for key, values in packages.items())
