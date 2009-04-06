Overview
========

The five.pt package brings the Chameleon template engine to Zope 2. It's a
drop-in replacement, providing bridges to the most common API.

Support for browser pages, viewlets and viewlet managers is included.

Usage
-----

To enable Chameleon, simply include the ZCML configuration::

  <include package="five.pt" />

Tempates may be instantiated directly. Here's an example of a browser view
which uses a view page template::

  from Products.Five import BrowserView
  from five.pt.pagetemplate import ViewPageTemplateFile

  class SimpleView(BrowserView):
      index = ViewPageTemplateFile('simple.pt')

Other template classes are available, see the ``pagetemplate`` module.

For general information about Chameleon, see http://chameleon.repoze.org/.
