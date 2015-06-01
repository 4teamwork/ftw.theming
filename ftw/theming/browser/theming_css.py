from ftw.theming.interfaces import ISCSSCompiler
from Products.Five import BrowserView
from zope.component import getMultiAdapter


class ThemingCSSView(BrowserView):

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'text/css; charset=utf-8')
        response.setHeader('X-Theme-Disabled', 'True')
        return self.get_css()

    def get_css(self):
        compiler = getMultiAdapter((self.context, self.request), ISCSSCompiler)
        return compiler.compile()
