.. contents:: Table of Contents


Installation
============

Add the package as dependency to your setup.py:

.. code:: python

  setup(...
        install_requires=[
          ...
          'ftw.theming',
        ])

or to your buildout configuration:

.. code:: ini

  [instance]
  eggs += ftw.theming

and rerun buildout.


SCSS Registry
=============

The SCSS registry is configured with ZCML and contains all SCSS resources from
``ftw.theming``, addons, the theme and policy packages.


Inspecting the SCSS registry
----------------------------

The ``@@theming-resources`` (on any navigation root) lists all resources.


Resource slots
--------------

The registry allows to register resources to a list of fix slots.
These are the available slots, sorted by inclusion order:

- ``top``
- ``variables``
- ``mixins``
- ``ftw.theming``
- ``addon``
- ``theme``
- ``policy``
- ``bottom``

Adding resources
----------------

Adding SCSS resources is done in the ZCML of a package.
The SCSS should always go into the same package where the styled templates are.

Registering a resource
~~~~~~~~~~~~~~~~~~~~~~

.. code:: xml

    <configure
        xmlns:theme="http://namespaces.zope.org/ftw.theming"
        xmlns:zcml="http://namespaces.zope.org/zcml"
        i18n_domain="ftw.tabbedview">

        <configure zcml:condition="installed ftw.theming">
          <include package="ftw.theming" />

          <theme:scss
              file="resources/tabbed.scss"
              slot="addon"
              profile="ftw.tabbedview:default"
              />
        </configure>

    </configure>


Options for standalone ``theme:scss``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``file``: relative path to the SCSS file (required)
- ``slot``: name of the slot (see slots section, default: ``addon``)
- ``profile``: Generic Setup profile required to be installed (default:
  no profile, e.g. ``my.package:default``)
- ``for``: context interface (default: ``INavigationRoot``)
- ``layer``: request layer interface (default: ``Interface``)
- ``before``: name of the resource after which this resource should be ordered
  (within the same slot).
- ``after``: name of the resource before which this resource should be ordered
  (within the same slot)


Registering multiple resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: xml

    <configure
        xmlns:theme="http://namespaces.zope.org/ftw.theming"
        xmlns:zcml="http://namespaces.zope.org/zcml"
        i18n_domain="plonetheme.fancy">

        <include package="ftw.theming" />

        <theme:resources
            slot="theme"
            profile="plonetheme.fancy:default"
            layer="plonetheme.fancy.interfaces.IFancyTheme">

            <theme:scss file="resources/foo.scss" />
            <theme:scss file="resources/bar.scss" />

        </theme:resources>

    </configure>

Options for ``theme:resources``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``slot``: name of the slot (see slots section, default: ``addon``)
- ``profile``: Generic Setup profile required to be installed (default:
  no profile, e.g. ``my.package:default``)
- ``for``: context interface (default: ``INavigationRoot``)
- ``layer``: request layer interface (default: ``Interface``)

Options for ``theme:scss`` within ``theme:resources``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``file``: relative path to the SCSS file (required)
- ``before``: name of the resource after which this resource should be ordered
  (within the same slot).
- ``after``: name of the resource before which this resource should be ordered
  (within the same slot)


Resource names
~~~~~~~~~~~~~~

Each resource has an automatically generated name, which can be looked up in the
``@@theming-resources``-view.
The resource has the format ``[package]:[relative path]``.


Resource Ordering
-----------------

The SCSS resources are ordered when retrieved from the registry, so that the
order is as consistent as possible.

Ordering priority:

1. the resource's ``slot`` (see the slot section below)
1. the ``before`` and ``after`` options (topological graph sorting), within each slot.
1. the ZCML load order of the resources

Be aware that the ZCML load order is usally random.


Resource factories for dynamic resources
----------------------------------------

A resource factory is a callable (accepting context and request) which returns
a ``DynamicSCSSResource`` object.
Since the callable instantiates the resource, it's content can be created dynamically.


.. code:: xml

    <configure
        xmlns:theme="http://namespaces.zope.org/ftw.theming"
        xmlns:zcml="http://namespaces.zope.org/zcml"
        i18n_domain="plonetheme.fancy">

        <include package="ftw.theming" />

        <theme:scss_factory factory=".dynamic_resource_factory" />

    </configure>


.. code:: python

    from ftw.theming.interfaces import ISCSSResourceFactory
    from ftw.theming.resource import DynamicSCSSResource
    from zope.interface import provider

    @provider(ISCSSResourceFactory)
    def dynamic_resource_factory(context, request):
        return DynamicSCSSResource('dynamic.scss', slot='addon', source='$color: blue;',
                                   cachekey='1')


When generating the SCSS is expensive in time, you should subclass the
``DynamicSCSSResource`` class and implement custom ``get_source`` and ``get_cachekey``
methods.
The ``get_cachekey`` should be very lightweight and cheap: it is called on every pageview.
It should return any string and only change the return value when the ``get_source`` result
will change.

.. code:: python

    from Products.CMFCore.utils import getToolByName
    from ftw.theming.interfaces import ISCSSResourceFactory
    from ftw.theming.resource import DynamicSCSSResource
    from zope.annotation import IAnnotations
    from zope.interface import provider


    class CustomSCSSResource(DynamicSCSSResource):

          def get_source(self, context, request):
              return 'body { background-color: $primary-color; }'

          def get_cachekey(self, context, request):
              portal = getToolByName(context, 'portal_url').getPortalObject()
              config = IAnnotations(portal).get('my-custom-config', {})
              return config.get('last-change-timestamp', '1')

    @provider(ISCSSResourceFactory)
    def dynamic_resource_factory(context, request):
        return CustomSCSSResource('my.package:custom.scss', slot='addon')



Control Panel
=============

When ``ftw.theming`` is installed, a control panel is added, listing the
SCSS resources and the default SCSS variables.
The controlpanel views are available on any navigation root.


Icons
=====

``ftw.theming`` provides a portal type icon registry.
The default iconset is `font-awesome`_.


Declare icon for portal types
-----------------------------

Portal type icons are declared in the scss file of the addon package.
It is possible to support multiple icon sets by declaring icons for each iconset:

.. code:: scss

    @include portal-type-font-awesome-icon(repository-folder, leaf);
    @include portal-type-icon(repository-folder, "\e616", customicons);

Using those mixins does not generate any CSS yet, nor does it introduce dependency
to those iconset.
It simply stores this information in a list to be processed later.


Switching iconset
-----------------

A theme or policy package may change the iconset.
The standard iconset is ``font-awesome``.
Changing the iconset should be done in an SCSS file in the ``variables`` slot.

.. code:: scss

    $standard-iconset: customicons;


Custom iconsets
---------------

The default iconset is ``font-awesome``, which is automatically loaded and the
necessary CSS is generated when the ``$standard-iconset`` variable is ``font-awesome``.

For having custom iconsets an SCSS file must be registered in the ``bottom`` slot.
This is usually done by a theme or policy package.

The SCSS file should apply the necessary CSS only when the ``$standard-iconset`` is set
to this iconset:

.. code:: scss

    @if $standard-iconset == customicons {

      @font-face {
        font-family: 'customicons';
        src:url('#{$portal-url}/++theme++foo/fonts/customicons.eot?-fa99j8');
        src:url('#{$portal-url}/++theme++foo/fonts/customicons.eot?#iefix-fa99j8') format('embedded-opentype'),
        url('#{$portal-url}/++theme++foo/fonts/customicons.woff?-fa99j8') format('woff'),
        url('#{$portal-url}/++theme++foo/fonts/customicons.ttf?-fa99j8') format('truetype'),
        url('#{$portal-url}/++theme++foo/fonts/customicons.svg?-fa99j8#opengever') format('svg');
        font-weight: normal;
        font-style: normal;
      }

      .icons-on [class^="contenttype-"],
      .icons-on [class*=" contenttype-"] {
        &:before {
          font-family: 'customicons';
          content: "x";
          text-align:center;
          position: absolute;
        }
      }

      @each $type, $value in get-portal-type-icons-for-iconset(font-awesome) {
        body.icons-on .contenttype-#{$type} {
          &:before {
            content: $value;
          }
        }
      }
    }



Functions
=========

embed-resource
--------------

The ``embed-resource`` function embeds a resource (e.g. svg) as
base64 encoded url.

Example:

.. code:: scss

    .something {
        background: embed-resource("images/foo.svg");
    }

The function is able to fill colors in SVGs.
This can be done with either XPath or CSS selectors.

Since lxml is used for filling the SVGs and SVGs are namespaced
XML documents, the expressions must be namespaced as well.
This leads to problems when converting certain CSS selectors
since CSS does not support namespaces.

Example:

.. code:: scss

    .foo {
        background: embed-resource("soccer.svg", $fill-css:['#pentagon': red]);
    }

    .bar {
        background: embed-resource("soccer.svg", $fill-xpath:['//*[@id="black_stuff"]/*[local-name()="g"][1]': red]);
    }



SCSS Mixins
===========

Using media queries Mixins
--------------------------

``ftw.theming`` provides mixins for most common media queries:

- phone (800px)
- tablet (1024px)
- desktop-M (1360px) - HD
- desktop-L (1920px) - Full HD
- desktop-XL (2560px) - WQHD

Example usage:

.. code:: scss

    #container {
        width: 1600px;

        @include tablet {
            width:1000px;
        }
        @include phone {
            width:500px;
        }
    }


Links
=====

- Github: https://github.com/4teamwork/ftw.theming
- Issues: https://github.com/4teamwork/ftw.theming/issues
- Pypi: http://pypi.python.org/pypi/ftw.theming
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.theming

Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.theming`` is licensed under GNU General Public License, version 2.

.. _font-awesome: http://fortawesome.github.io/Font-Awesome/
