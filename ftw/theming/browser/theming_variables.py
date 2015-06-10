from ftw.theming.interfaces import ISCSSCompiler
from operator import methodcaller
from Products.Five import BrowserView
from scss.calculator import Calculator
from scss.types import Null
from zope.component import getMultiAdapter
import inspect


def find_object_in_stack(name, klass):
    frame = inspect.currentframe()
    while not isinstance(frame.f_locals.get(name, None), klass):
        frame = frame.f_back
    return frame.f_locals[name]


class ThemingVariablesView(BrowserView):

    def variables(self):
        variables = []
        compiler = getMultiAdapter((self.context, self.request), ISCSSCompiler)

        @compiler.namespace.declare
        def register_theming_variables(vartype, *varnames):
            vartype = vartype.render()
            varnames = map(methodcaller('render'), varnames)
            calculator = find_object_in_stack('self', Calculator)

            for name in varnames:
                name = u'${0}'.format(name)
                value = calculator.namespace.variables.get(name, None)
                value = value and value.render or '???'
                variables.append({'name': name,
                                  'value': value,
                                  'type': vartype})
            return Null()

        compiler.compile()
        return variables
