import zope.interface
import zope.component

import os
import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import zope.component.testing
import zope.configuration.xmlconfig

import z3c.pt
import five.pt

class TestParticipation(object):
    principal = 'foobar'
    interaction = None

def setUp(test):
    zope.component.testing.setUp(test)
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', five.pt)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    
def tearDown(test):
    zope.component.testing.tearDown(test)

def test_suite():
    import five.pt.tests
    path = five.pt.tests.__path__[0]

    globs = dict(
        os=os,
        path=path,
        interface=zope.interface,
        component=zope.component)
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
        "zcml.txt",
        optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp,
        tearDown=tearDown,
        package="five.pt")])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
