Overview
========

The five.pt package brings the z3c.pt package into the Zope 2 world,
using Zope 2 conventions.

You can use z3c.pt out of the box with Zope 2 as well.

Use
===

It's very easy. To define a view which use a five.pt template::

  from Products.Five import BrowserView
  from five.pt.pagetemplate import ViewPageTemplateFile

  class SimpleView(BrowserView):

      index = ViewPageTemplateFile('simple.pt')


``ViewPageTemplate`` is defined as well and takes a string as template
code. For more information, please refer to z3c.pt documentation.
