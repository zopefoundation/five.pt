import Globals

from Products.CMFCore.FSObject import FSObject
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions

from Products.CMFFormController.BaseControllerPageTemplate import \
     BaseControllerPageTemplate as BaseCPT
from Products.CMFFormController.FSControllerBase import FSControllerBase

from Shared.DC.Scripts.Script import Script
from AccessControl import ClassSecurityInfo
from RestrictedPython import Utilities

from pagetemplate import BaseTemplateFile

class FSPageTemplate(BaseTemplateFile, FSObject, Script):
    meta_type = 'Filesystem Page Template'
    
    security = ClassSecurityInfo()
    security.declareObjectProtected(permissions.View)

    _default_bindings = {'name_subpath': 'traverse_subpath'}

    utility_builtins = Utilities.utility_builtins
    
    def __init__(self, id, filepath, fullname=None, properties=None):
        FSObject.__init__(self, id, filepath, fullname, properties)
        self.ZBindings_edit(self._default_bindings)

        # instantiate page template
        BaseTemplateFile.__init__(self, filepath)
        
    def _readFile(self, reparse):
        # templates are lazy
        if reparse:
            self.read()

    def __call__(self, *args, **kwargs):
        kwargs['args'] = args
        return BaseTemplateFile.__call__(self, self, **kwargs)    
    
class FSControllerPageTemplate(FSPageTemplate, FSControllerBase, BaseCPT):
    def __init__(self, id, filepath, fullname=None, properties=None):
        FSPageTemplate.__init__(self, id, filepath, fullname, properties)  
        self.filepath = filepath
      
        self._read_action_metadata(self.getId(), filepath)
        self._read_validator_metadata(self.getId(), filepath)

    def _readFile(self, reparse):
        FSPageTemplate._readFile(self, reparse)
        self._readMetadata()

    def _updateFromFS(self):
        # workaround for Python 2.1 multiple inheritance lameness
        return self._baseUpdateFromFS()

    def _readMetadata(self):
        # workaround for Python 2.1 multiple inheritance lameness
        return self._baseReadMetadata()

    def __call__(self, *args, **kwargs):
        return self._call(FSPageTemplate.__call__, *args, **kwargs)

Globals.InitializeClass(FSPageTemplate)
Globals.InitializeClass(FSControllerPageTemplate)

DirectoryView.registerFileExtension('pt', FSPageTemplate)
DirectoryView.registerFileExtension('zpt', FSPageTemplate)
DirectoryView.registerFileExtension('html', FSPageTemplate)
DirectoryView.registerFileExtension('htm', FSPageTemplate)
DirectoryView.registerFileExtension('cpt', FSControllerPageTemplate)

DirectoryView.registerMetaType('Page Template', FSPageTemplate)
DirectoryView.registerMetaType('Controller Page Template', FSControllerPageTemplate)
