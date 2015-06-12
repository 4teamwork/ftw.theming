from ftw.theming.interfaces import ISCSSRegistry
from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.resource import SCSSResource
from ftw.theming.testing import META_ZCML
from ftw.theming.tests.stubs import CONTEXT
from ftw.theming.tests.stubs import ProfileInfoStub
from ftw.theming.tests.stubs import REQUEST
from operator import attrgetter
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from unittest2 import TestCase
from zope.component import getUtility
from zope.configuration.xmlconfig import ZopeXMLConfigurationError
from zope.interface import Interface
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import ftw.theming.tests


class TestSCSSDirective(TestCase):
    layer = META_ZCML

    def test_register_resource(self):
        self.load_zcml('<theme:scss file="resources/foo.scss" />')
        self.assertDictContainsSubset(
            {'name': 'ftw.theming.tests:resources/foo.scss',
             'package': 'ftw.theming.tests',
             'relative_path': 'resources/foo.scss',
             'slot': 'addon',
             'profile': None,
             'for_': INavigationRoot,
             'layer': Interface,
             'before': None,
             'after': None},
            self.get_resource_vars())

    def test_slot(self):
        self.load_zcml('<theme:scss file="resources/foo.scss" slot="theme" />')
        self.assertDictContainsSubset({'slot': 'theme'},
                                      self.get_resource_vars())

    def test_valid_slot_required(self):
        with self.assertRaises(ZopeXMLConfigurationError) as cm:
            self.load_zcml('<theme:scss file="resources/foo.scss"'
                           ' slot="any" />')
        self.assertEquals('Invalid slot "any". Valid slots:'
                          ' (\'top\', \'variables\', \'mixins\', \'ftw.theming\','
                          ' \'addon\', \'theme\', \'policy\', \'bottom\')',
                          str(cm.exception.evalue))

    def test_profile(self):
        self.load_zcml('<theme:scss file="resources/foo.scss"'
                       ' profile="foo:default" />')
        self.assertDictContainsSubset({'profile': 'foo:default'},
                                      self.get_resource_vars())

    def test_for(self):
        self.load_zcml(
            '<theme:scss file="resources/foo.scss"'
            ' for="Products.CMFPlone.interfaces.siteroot.IPloneSiteRoot" />')
        self.assertDictContainsSubset({'for_': IPloneSiteRoot},
                                      self.get_resource_vars())

    def test_layer(self):
        self.load_zcml(
            '<theme:scss file="resources/foo.scss"'
            ' layer="zope.publisher.interfaces.browser.IDefaultBrowserLayer"'
            ' />')
        self.assertDictContainsSubset({'layer': IDefaultBrowserLayer},
                                      self.get_resource_vars())

    def test_before(self):
        self.load_zcml(
            '<theme:scss file="resources/foo.scss" before="bar:bar.scss" />')
        self.assertDictContainsSubset({'before': 'bar:bar.scss'},
                                      self.get_resource_vars())

    def test_after(self):
        self.load_zcml(
            '<theme:scss file="resources/foo.scss" after="bar:bar.scss" />')
        self.assertDictContainsSubset({'after': 'bar:bar.scss'},
                                      self.get_resource_vars())

    def test_complex_directive(self):
        self.load_zcml(
            '<theme:resources'
            '      slot="theme"'
            '      profile="foo:default"'
            '      for="Products.CMFPlone.interfaces.siteroot.IPloneSiteRoot"'
            '      layer="zope.publisher.interfaces.browser.IDefaultBrowserLayer">'
            '  <theme:scss'
            '        file="resources/foo.scss"'
            '        before="bar:bar.scss"'
            '        after="baz:baz.scss" />'
            '</theme:resources>')

        self.assertDictContainsSubset(
            {'name': 'ftw.theming.tests:resources/foo.scss',
             'package': 'ftw.theming.tests',
             'relative_path': 'resources/foo.scss',
             'slot': 'theme',
             'profile': 'foo:default',
             'for_': IPloneSiteRoot,
             'layer': IDefaultBrowserLayer,
             'before': 'bar:bar.scss',
             'after': 'baz:baz.scss'},
            self.get_resource_vars())

    def test_complex_directive_with_changed_slot(self):
        self.load_zcml(
            '<theme:resources slot="theme">'
            '  <theme:scss'
            '        file="resources/foo.scss"'
            '        slot="variables" />'
            '</theme:resources>')

        self.assertDictContainsSubset(
            {'name': 'ftw.theming.tests:resources/foo.scss',
             'package': 'ftw.theming.tests',
             'relative_path': 'resources/foo.scss',
             'slot': 'variables',
             'profile': None,
             'for_': INavigationRoot,
             'layer': Interface,
             'before': None,
             'after': None},
            self.get_resource_vars())

    def test_scss_factory(self):
        @provider(ISCSSResourceFactory)
        def resource_factory(context, request):
            return SCSSResource('foo', source='$color = red;')

        ftw.theming.tests.resource_factory = resource_factory
        self.load_zcml('<theme:scss_factory factory=".resource_factory" />')

        self.assertDictContainsSubset(
            {'name': 'foo',
             'slot': 'addon',
             'before': None,
             'after': None},
            self.get_resource_vars())

    def test_scss_factory_must_provide_interface(self):
        def bad_resource_factory(context, request):
            return None
        ftw.theming.tests.resource_factory = bad_resource_factory
        with self.assertRaises(ZopeXMLConfigurationError) as cm:
            self.load_zcml('<theme:scss_factory factory=".resource_factory" />')
        self.assertEquals('add_scss: factory must provide ISCSSResourceFactory',
                          str(cm.exception.evalue))

    def load_zcml(self, *lines):
        self.layer.load_zcml_string('\n'.join((
                    '<configure ',
                    '    xmlns:theme="http://namespaces.zope.org/ftw.theming"',
                    '    i18n_domain="my.package"',
                    '    package="ftw.theming.tests"''>',
                    ) + lines + (
                    '</configure>',
                    )))

    def get_resources(self, context=CONTEXT, request=REQUEST,
                      profileinfo=ProfileInfoStub(),
                      include_unavailable=True):
        registry = getUtility(ISCSSRegistry)
        return registry.get_resources(context, request,
                                      profileinfo=profileinfo,
                                      include_unavailable=include_unavailable)

    def get_resource(self, **kwargs):
        resource, = self.get_resources(**kwargs)
        return resource

    def get_resource_vars(self):
        return vars(self.get_resource())


def attrs(name, resources):
    return map(attrgetter(name), resources)
