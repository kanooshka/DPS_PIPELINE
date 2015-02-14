#!/usr/bin/python

""" Creates reusable Qt window components. """

# define authorship information:
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#---------------------------------------------------------------------------

import logging
import os.path
import shutil
import zipfile

import projex.text

from xml.etree import ElementTree

from PyQt4.QtCore import QSize, QDir, Qt
from PyQt4.QtGui import QIcon,\
                              QTreeWidgetItem,\
                              QApplication

from projexui.widgets.xtreewidget import XTreeWidgetItem

import projexui.resources

logger = logging.getLogger(__name__)

TITLE_MAP = {
    'functions':    'All Functions',
    'classes':      'All Classes',
    'modules':      'All Modules',
    'api':          'API Manual',
    'user':         'User Manual'
}

class XdkEntryItem(XTreeWidgetItem):
    TITLE_MAP = {}
    
    def __init__( self, parent, filepath, title=None ):
        super(XdkEntryItem, self).__init__(parent)
        
        # set custom properties
        self._isFolder = os.path.isdir(filepath)
        self._filepath = str(filepath).replace('\\', '/')
        self._url      = ''
        self._loaded   = False
        
        self.setFixedHeight(22)
        
        # define custom properties
        if self._isFolder:
            icon = projexui.resources.find('img/folder.png')
            self.setChildIndicatorPolicy(self.ShowIndicator)
            self._url = 'file:///%s/index.html' % self._filepath.strip('/')
        else:
            icon = projexui.resources.find('img/file.png')
            self._url    = 'file:///%s' % self._filepath
            self._loaded = True
        
        if title is not None:
            self.TITLE_MAP[self._url] = title
            self.setText(0, title)
        else:
            self.setText(0, self.titleForFilepath(self._url))
        
        # set default properties
        self.setIcon(0,     QIcon(icon))
        self.setSizeHint(0, QSize(20, 18))
        self.setText(1, os.path.basename(os.path.splitext(self._filepath)[0]))
    
    def filepath( self ):
        """
        Returns the filepath for this item.
        
        :return     <str>
        """
        return self._filepath
    
    def gotoItem(self, path):
        self.load()
        if not path:
            tree = self.treeWidget()
            tree.setCurrentItem(self)
            return
        
        path = str(path).split('/')
        check = projex.text.underscore(path[0])
        for i in range(self.childCount()):
            child = self.child(i)
            if projex.text.underscore(child.text(1)) == check:
                child.gotoItem('/'.join(path[1:]))
    
    def isFolder( self ):
        """
        Returns whether or not this instance is a folder.
        
        :return     <bool>
        """
        return self._isFolder
    
    def isLoaded( self ):
        """
        Return whether or not this item is currently loaded.
        
        :return     <bool>
        """
        return self._loaded
    
    def load( self ):
        """
        Loads this item.
        """
        if self._loaded:
            return
        
        self._loaded = True
        self.setChildIndicatorPolicy(self.DontShowIndicatorWhenChildless)
        
        if self.isFolder():
            for name in os.listdir(self.filepath()):
                # ignore 'hidden' folders
                if ( name.startswith('_') and not name.startswith('__') ):
                    continue
                
                # ignore special cases (only want modules for this)
                if ( '-' in name ):
                    continue
                
                # use the index or __init__ information
                if ( name in ('index.html', '__init__.html') ):
                    self._url = 'file:///%s/%s' % (self.filepath(), name)
                    continue
                
                # otherwise, load a childitem
                XdkEntryItem(self, os.path.join(self.filepath(), name))
    
    def loadFromXml(self, xml, basepath):
        self._loaded = True
        for xchild in xml:
            filepath = os.path.join(basepath, xchild.get('basename', ''))
            filepath = filepath.replace('\\', '/').replace('.wiki', '.html')
            title = xchild.get('title', '')
            item = XdkEntryItem(self, filepath, title)
            item.loadFromXml(xchild, filepath)
    
    def url( self ):
        """
        Returns the url for this instance.
        
        :return     <str>
        """
        return self._url
    
    def xdkItem( self ):
        root = self
        while ( root.parent() ):
            root = root.parent()
        
        if ( isinstance(root, XdkItem) ):
            return root
        return None
    
    @staticmethod
    def titleForFilepath( url ):
        """
        Returns a gui title for this url.
        
        :return     <str>
        """
        url = str(url)
        if url in XdkEntryItem.TITLE_MAP:
            return XdkEntryItem.TITLE_MAP.get(url)
        
        url      = str(url).replace('\\', '/')
        basename = os.path.basename(url)
        title    = os.path.splitext(basename)[0]
        
        if title == 'index':
            title = url.split('/')[-2]
        
        if title.endswith('-allmembers'):
            title = 'List of All Members for %s' % title.split('-')[-2]
        elif title.endswith('-source'):
            title = 'Source Code for %s' % title.split('-')[-2]
        elif len(str(url).split('/')) <= 2 and title in TITLE_MAP:
            title = TITLE_MAP[title]
        elif not 'api/' in url:
            title = projex.text.pretty(title)
        
        return title
    
#------------------------------------------------------------------------------

class XdkItem(XdkEntryItem):
    """ """
    def __init__( self, xdk_filename ):
        # create the new XdkItem
        super(XdkItem, self).__init__(None, xdk_filename)
        
        # creates the new XdkItem
        basename = os.path.basename(str(xdk_filename))
        name     = os.path.splitext(basename)[0]
        
        temppath  = str(QDir.tempPath())
        temp_path = os.path.join(temppath, 'xdk/%s' % name)
        
        # define custom properties
        self._tempFilepath  = temp_path
        self._searchurls    = {}
        
        # set the options
        self.setChildIndicatorPolicy(self.ShowIndicator)
        self.setIcon(0, QIcon(projexui.resources.find('img/sdk.png')))
        
        toc_file = os.path.join(temp_path, 'toc.xml')
        toc_xml = None
        if toc_file:
            try:
                toc_xml = ElementTree.parse(toc_file).getroot()
            except:
                pass
        
        if toc_xml is not None:
            self._url = 'file:///%s/index.html' % temp_path.strip('/')
            self.setText(0, toc_xml.get('name', self.text(0)))
            self.loadFromXml(toc_xml, temp_path)
        else:
            # load the url information for this entry
            for name in sorted(os.listdir(temp_path)):
                # ignore 'hidden' folders
                if name.startswith('_') and not name.startswith('__'):
                    continue
                
                # ignore special cases (only want modules for this)
                if '-' in name or name == 'toc.xml':
                    continue
                
                # use the index or __init__ information
                if name == '__init__.html':
                    self._url = 'file:///%s/%s' % (temp_path, name)
                    continue
                
                elif name == 'index.html':
                    self._url = 'file:///%s/%s' % (temp_path, name)
                
                # otherwise, load a childitem
                XdkEntryItem(self, os.path.join(temp_path, name))
    
    def isFolder(self):
        """
        Returns whether or not this item is a folder.
        
        :return     <bool>
        """
        return True
    
    def indexlist( self ):
        """
        Returns the list of files in alphabetical order for index lookups.
        
        :return     [(<str> name, <str> url), ..]
        """
        # load the index information from the filename
        zfile = zipfile.ZipFile(self.filepath(), 'r')
        namelist = zfile.namelist()
        zfile.close()
        
        # extract the index information
        output = []
        temppath = self.tempFilepath()
        for name in namelist:
            name_splt = os.path.basename(name).split('.')[0].split('-')
            
            # ignore undesired information
            if name_splt[-1] in ('allmembers', 'source'):
                continue
            
            elif name.startswith('_static'):
                continue
            
            # ignore any private information
            ignore = False
            for part in name_splt:
                if ( part.startswith('_') ):
                    ignore = True
                    break
            
            if ( ignore ):
                continue
            
            title = self.titleForFilepath(os.path.join(temppath, name))
            url = 'file:///%s/%s' % (self.tempFilepath(), name)
            output.append((title, url))
        
        return output
    
    def search( self, terms ):
        """
        Seraches the documents for the inputed terms.
        
        :param      terms
        
        :return     [{'url': <str>, 'title': <str>', 'strength': <int>}]
        """
        # load the search information
        if not self._searchurls:
            prefix = 'file:///' + self.tempFilepath().rstrip('/') + '/'
            # load the html contents
            zfile = zipfile.ZipFile(self.filepath(), 'r')
            for name in zfile.namelist():
                # ignore static resources
                if name.startswith('_static'):
                    continue
                
                url = prefix + name
                url = url.replace('\\', '/')
                self._searchurls[url] = zfile.read(name)
            zfile.close()
        
        # search for the contents
        output = [] # [(<int> strength>
        term_list = str(terms).split(' ')
        for url, html in self._searchurls.items():
            title           = self.titleForFilepath(url)
            strength        = 0
            all_title_found = True
            all_found       = True
            
            for term in term_list:
                if ( term == title ):
                    strength += 5
                
                elif ( term.lower() == title.lower() ):
                    strength += 4
                    
                elif ( term in title ):
                    strength += 3
                
                elif ( term.lower() in title.lower() ):
                    strength += 2
                
                else:
                    all_title_found = False
                
                if ( not term in html ):
                    all_found = False
                else:
                    strength += 1
            
            if ( all_title_found ):
                strength += len(terms) * 2
            
            if ( all_found ):
                strength += len(terms)
            
            # determine the strength
            if ( strength ):
                output.append({'url': url, 
                               'title': self.titleForFilepath(url),
                               'strength': strength})
        
        return output
    
    def tempFilepath(self):
        """
        Returns the location being used for the temporary extraction of the
        XDK docs.
        
        :return     <str>
        """
        return self._tempFilepath