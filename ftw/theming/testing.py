from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from ftw.testing.layer import ComponentRegistryLayer
from ftw.testing.layer import TEMP_DIRECTORY
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class MetaZCMLLayer(ComponentRegistryLayer):

    def setUp(self):
        super(MetaZCMLLayer, self).setUp()
        import ftw.theming
        self.load_zcml_file('meta.zcml', ftw.theming)


META_ZCML = MetaZCMLLayer()


class ThemingLayer(PloneSandboxLayer):
    defaultBases = (COMPONENT_REGISTRY_ISOLATION,
                    BUILDER_LAYER,
                    TEMP_DIRECTORY)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.theming:default')


THEMING_FIXTURE = ThemingLayer()
THEMING_FUNCTIONAL = FunctionalTesting(
    bases=(THEMING_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.theming:functional")
