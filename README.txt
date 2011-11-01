Overview
========

This package brings the Chameleon template engine to the Zope 2
platform. Five is supported.

It works using monkey-patching onto the existing API (specifically,
the ``TALInterpreter`` and ``PageTemplate`` classes). In simple terms,
what the patching does is to replace the TAL interpreter class and
make sure that the so-called "cooking" routine uses the Chameleon
parser and compiler instead of the ``zope.*`` reference
implementation.


Usage
~~~~~

To enable Chameleon, configure the package using ZCML::

  <include package="five.pt" />

For more information on Chameleon, see http://www.pagetemplates.org/.
