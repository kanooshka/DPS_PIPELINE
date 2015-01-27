#!/usr/bin/python

""" Parses through the python source code to generate HTML documentation.  """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import datetime
import distutils.dir_util
import logging
import os
import shutil
import sys
import time

from xml.etree import ElementTree

import projex
import projex.text
import projex.wikitext

from projex.enum import enum

from projex        import resources
from projex.docgen import templates
from projex.docgen import commands

logger = logging.getLogger(__name__)

#----------------------------------------------------------------------

class DoxEntry(object):
    def __cmp__(self, other):
        if not type(other) == DoxEntry:
            return -1
        
        return cmp(self.order(), other.order())
        
    def __init__(self, **kwds):
        self._title = kwds.get('title', '')
        self._basename = kwds.get('basename', '')
        self._order = kwds.get('order', 0)
        self._children = kwds.get('children', [])
    
    def basename(self):
        return self._basename
    
    def children(self):
        return self._children
    
    def order(self):
        return self._order
    
    def setBasename(self, basename):
        self._basename = str(basename)
    
    def setOrder(self, order):
        self._order = order
    
    def setTitle(self, title):
        self._title = str(title)
    
    def sync(self, filepath):
        """
        Syncs the contents of this entry based on the given filepath.
        
        :param      filepath | <str>
        """
        child_names = [child.basename() for child in self.children()]
        filenames   = list(os.listdir(str(filepath)))
        
        rem_paths = set(child_names).difference(filenames)
        new_paths = set(filenames).difference(child_names)
        
        # remove the deleted filepaths
        if rem_paths:
            kids = [c for c in self.children() if c.basename() not in rem_paths]
            for i, kid in enumerate(kids):
                kid.setOrder(i)
        else:
            kids = self.children()[:]
        
        # add new paths
        for path in sorted(new_paths):
            childpath = os.path.join(filepath, path)
            if os.path.isdir(childpath):
                title = projex.text.pretty(path)
            else:
                title = projex.text.pretty(os.path.splitext(path)[0])
            
            order = len(kids)
            child = DoxEntry(title=title, basename=path, order=order)
            kids.append(child)
        
        self._children = kids
        
        # sync sub-folders
        for child in self.children():
            childpath = os.path.join(filepath, child.basename())
            if os.path.isdir(childpath):
                child.sync(childpath)
    
    def title(self):
        return self._title
    
    def toXml(self, xml):
        """
        Converts this source information to xml data.
        
        :param      xml | <ElementTree.Element>
        
        :return     <ElementTree.SubElement>
        """
        xentry = ElementTree.SubElement(xml, 'entry')
        xentry.set('title', self.title())
        xentry.set('basename', self.basename())
        
        for entry in sorted(self.children()):
            entry.toXml(xentry)
        
        return xentry
    
    @staticmethod
    def fromXml(xml):
        """
        Generates a new source entry based on the inputed xml node.
        
        :param      xml | <ElementTree.Element>
        
        :return     <DoxSource>
        """
        opts = {}
        opts['title'] = xml.get('title', '')
        opts['basename'] = xml.get('basename', '')
        
        children = []
        for xchild in xml:
            child = DoxEntry.fromXml(xchild)
            child.setOrder(len(children))
            children.append(child)
        
        opts['children'] = children
        
        return DoxEntry(**opts)

#----------------------------------------------------------------------

class DoxSource(object):
    Type = enum('Wiki', 'Module', 'Group')
    
    def __init__(self, dox, typ, name, filepath):
        self._dox = dox
        self._type = typ
        self._name = name
        self._filepath = filepath
        self._entries = []
    
    def addEntry(self, entry):
        """
        Adds a new entry to this entry.  Entries can be grouped
        together to create custom hierarchies.
        
        :param      entry | <DoxEntry>
        """
        entry._order = len(self._entries)
        self._entries.append(entry)
    
    def entries(self):
        """
        Returns the list of entries associated with this dox file.
        
        :return     [<DoxEntry>, ..]
        """
        return self._entries
    
    def export(self, outpath, breadcrumbs=None):
        """
        Exports this source to the given output path location.
        
        :param      outpath | <str>
        """
        if breadcrumbs is None:
            breadcrumbs = ['Home']
        
        # save the toc
        xtoc = ElementTree.Element('toc')
        xtoc.set('name', self.name())
        for entry in sorted(self.entries()):
            entry.toXml(xtoc)
        
        projex.text.xmlindent(xtoc)
        toc_file = open(os.path.join(outpath, 'toc.xml'), 'w')
        toc_file.write(ElementTree.tostring(xtoc))
        toc_file.close()
        
        # generate an arbitrary group
        if self.type() == DoxSource.Type.Group:
            key = self.name().replace(' ', '_').lower()
            target = os.path.join(outpath, key)
            if not os.path.exists(target):
                os.mkdir(target)
            
            breadcrumbs.append(self.name())
            for source in self.sources():
                source.export(target, breadcrumbs)
        
        # generate user docs
        elif self.type() == DoxSource.Type.Wiki:
            for entry in sorted(self._entries):
                self.exportEntry(self.filepath(),
                                 outpath,
                                 entry,
                                 breadcrumbs)
            
        # generate module docs
        elif self.type() == DoxSource.Type.Module:
            pass
    
    def exportEntry(self, src, target, entry, breadcrumbs):
        """
        Exports the entry to HTML.
        
        :param      srcpath     | <str>
                    targetpath  | <str>
                    entry       | <DoxEntry>
        """
        src_path    = os.path.join(src, entry.basename())
        target_path = os.path.join(target, entry.basename())
        
        # export a folder
        if os.path.isdir(src_path):
            os.makedirs(target_path)
            crumbs = breadcrumbs + [entry.title()]
            for child in entry.children():
                self.exportEntry(src_path, target_path, child, crumbs)
        
        # export a wiki file
        elif entry.basename().endswith('.wiki'):
            count = len(breadcrumbs) - 1
            
            base_url = '.' + '/..' * count
            static_url = base_url + '/_static'
            
            # extract wiki information
            wiki_file = open(src_path, 'r')
            wiki_contents = wiki_file.read()
            wiki_file.close()
            
            # generate the contents
            
            # generate the breadcrumbs for this file
            incl = entry.basename() != 'index.wiki'
            html = self._dox.render(entry.title(),
                                    wiki_contents,
                                    breadcrumbs,
                                    filepath=src_path,
                                    baseUrl=base_url,
                                    staticUrl=static_url,
                                    includeTitleInCrumbs=incl)
            
            # generate the new html file
            target_path = target_path.replace('.wiki', '.html')

            html_file = open(target_path, 'w')
            html_file.write(html)
            html_file.close()
    
    def filepath(self):
        """
        Returns the filepath for the source of this source.
        
        :return     <str>
        """
        path = os.path.expandvars(self._filepath)
        if os.path.isabs(path):
            return path
        
        elif self._dox.filename():
            basepath = os.path.dirname(self._dox.filename())
            basepath = os.path.join(basepath, path)
        
        else:
            basepath = path
        
        return os.path.abspath(basepath)
    
    def name(self):
        """
        Returns the name for this source.
        
        :return     <str>
        """
        return self._name
    
    def sources(self):
        """
        Returns a list of the sub-sources this instance holds.  Sources
        can be nested together in groups to create custom hierarchies.
        
        :return     [<DoxSource>, ..]
        """
        return self._sources
    
    def sync(self):
        """
        Syncs the contents of this entry based on the given filepath.
        
        :param      filepath | <str>
        """
        if self.type() != DoxSource.Type.Wiki:
            return
        
        filepath = self.filepath()
        entry_names = [entry.basename() for entry in self.entries()]
        filenames   = list(os.listdir(str(filepath)))
        
        rem_paths = set(entry_names).difference(filenames)
        new_paths = set(filenames).difference(entry_names)
        
        # remove the deleted filepaths
        if rem_paths:
            kids = [c for c in self.entries() if c.basename() not in rem_paths]
            for i, kid in enumerate(kids):
                kid.setOrder(i)
        else:
            kids = self.entries()[:]
        
        # add new paths
        for path in sorted(new_paths):
            entrypath = os.path.join(filepath, path)
            if os.path.isdir(entrypath):
                title = projex.text.pretty(path)
            else:
                title = projex.text.pretty(os.path.splitext(path)[0])
            
            order = len(kids)
            entry = DoxEntry(title=title, basename=path, order=order)
            kids.append(entry)
        
        self._entries = kids
        
        # sync sub-folders
        for entry in self.entries():
            entrypath = os.path.join(filepath, entry.basename())
            if os.path.isdir(entrypath):
                entry.sync(entrypath)
    
    def toXml(self, xml):
        """
        Converts this source information to xml data.
        
        :param      xml | <ElementTree.Element>
        
        :return     <ElementTree.SubElement>
        """
        xsource = ElementTree.SubElement(xml, 'source')
        xsource.set('type', DoxSource.Type[self.type()])
        xsource.set('name', self.name())
        xsource.set('path', self._filepath)
        
        for source in sorted(self._entries):
            source.toXml(xsource)
        
        return xsource
    
    def type(self):
        """
        Returns the type of source this source is.
        
        :return     <DoxSource.Type>
        """
        return self._type
    
    @staticmethod
    def fromXml(dox, xml):
        """
        Generates a new source based on the inputed xml node.
        
        :param      xml | <ElementTree.Element>
        
        :return     <DoxSource>
        """
        typ = DoxSource.Type[xml.get('type')]
        rsc = DoxSource(dox, typ, xml.get('name', ''), xml.get('path', ''))
        
        # load entries
        for xentry in xml:
            rsc.addEntry(DoxEntry.fromXml(xentry))
        
        return rsc
        

#----------------------------------------------------------------------

class DoxFile(object):
    _current = None
    
    def __init__(self):
        self._filename = ''
        
        # configuration info
        self._config = {}
        self._config['company'] = 'Projex Software, LLC'
        self._config['companyUrl'] = 'http://www.projexsoftware.com/'
        self._config['theme'] = 'base'
        self._config['themePath'] = ''
        self._config['title'] = 'Dox Documentation'
        self._config['version'] = '0.0'
        self._config['copyright'] = ''
        self._config['resourcePath'] = ''
        
        # additional properties
        self._defaultEnvironment = {}
        self._navigation = []
        self._sources = []
    
    def addNavigation(self, title, url):
        """
        Adds a navigation link to the main navigation menu bar for the
        documentation.
        
        :param      title | <str>
                    url   | <str>
        """
        self._navigation.append((title, url))
    
    def addSource(self, source):
        """
        Adds the inputed source to the list of sources for this instance.
        
        :param      source | <DoxSource>
        """
        self._sources.append(source)
    
    def config(self, key, default=None):
        """
        Returns the configuration value for the inputed key.
        
        :param      key | <str>
        """
        return self._config.get(key, default)
    
    def company(self):
        """
        Returns the company name for this dox file.
        
        :return     <str>
        """
        return self.config('company')
    
    def companyUrl(self):
        """
        Returns the company url for this dox file.
        
        :return     <str>
        """
        return self.config('companyUrl')
    
    def copyright(self):
        """
        Returns the copyright information for this dox file.
        
        :return     <str>
        """
        copyright = self.config('copyright')
        
        if not copyright:
            copyright = 'generated by <a href="%s">docgen</a> '\
                        'copyright &copy; <a href="%s">%s</a> %s'
            
            opts = (projex.website(),
                    self.companyUrl(),
                    self.company(),
                    datetime.date.today().year)
            
            copyright %= opts
        
        return copyright
    
    def defaultEnvironment(self):
        """
        Returns the default environment variables for the dox file.
        
        :return     <dict>
        """
        return self._defaultEnvironment
    
    def export(self, outpath=None, xdkpath=None):
        """
        Builds the files that will be used to generate the different help
        documentation from the dox sources within this configuration file.
        
        :param      outpath | <str>
        """
        dirpath = os.path.dirname(self.filename())
        filename = os.path.basename(self.filename()).split('.')[0]
        if outpath is None:
            outpath = os.path.join(dirpath, 'dist/html')
        if xdkpath is None:
            xdkpath = os.path.join(dirpath, 'dist/%s.xdk' % filename)
        
        basepath = outpath
        self.initEnviron()
        
        #----------------------------------------------------------------------
        
        # clear the output location
        if os.path.exists(outpath):
            distutils.dir_util.remove_tree(outpath)
        
        # create the output location
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        
        # generate the source files
        for source in self.sources():
            source.export(outpath)
        
        # copy the resources and syntax code
        static_path = os.path.join(outpath, '_static')
        paths = []
        paths.append(resources.find('ext/prettify'))
        paths.append(templates.path('javascript'))
        paths.append(templates.path('css'))
        paths.append(templates.path('images'))
        paths.append(templates.path('img'))
        
        if not os.path.exists(static_path):
            os.makedirs(static_path)
        
        # copy static resources
        for path in paths:
            if not os.path.exists(path):
                continue
            
            basename = os.path.basename(path)
            target   = os.path.join(static_path, basename)
            
            try:
                distutils.dir_util.copy_tree(path, target, update=1)
            except IOError:
                pass
        
        # include dynamic resources
        for resource in self.resourcePaths():
            for subpath in os.listdir(resource):
                filepath = os.path.join(resource, subpath)
                outpath = os.path.join(static_path, subpath)
                
                if os.path.isdir(filepath):
                    try:
                        distutils.dir_util.copy_tree(filepath, outpath, update=1)
                    except IOError:
                        pass
                else:
                    shutil.copyfile(filepath, outpath)
        
        if xdkpath:
            commands.generateXdk(basepath, xdkpath)
        
        return basepath
    
    def filename(self):
        """
        Returns the filename associated with this dox file.
        
        :return     <str>
        """
        return self._filename
    
    def initEnviron(self):
        """
        Initializes the docgen build environment settings with this
        dox file's configuration information.
        """
        # setup the templating
        templates.setTheme(self.theme())
        templates.setThemePath(self.themePath())
        
        # initialize navigation
        templ = templates.template('link_navigation.html')
        nav = []
        for title, url in self.navigation():
            nav.append(templ % {'title': title, 'url': url})
        
        # set the environment variables
        commands.ENVIRON.clear()
        commands.ENVIRON['module_title'] = self.title()
        commands.ENVIRON['module_version'] = self.version()
        commands.ENVIRON['copyright'] = self.copyright()
        commands.ENVIRON['navigation'] = ''.join(nav)
        
        # setup rendering options
        commands.RENDER_OPTIONS.clear()
        commands.RENDER_OPTIONS['TITLE'] = self.title()
        commands.RENDER_OPTIONS['VERSION'] = self.version()
        commands.RENDER_OPTIONS['COMPANY'] = self.company()
        commands.RENDER_OPTIONS['COMPANY_URL'] = self.companyUrl()
        
        split_ver = self.version().split('.')
        for i, key in enumerate(('MAJOR', 'MINOR', 'REVISION')):
            try:
                commands.RENDER_OPTIONS[key] = split_ver[i]
            except:
                continue
        
        # include additional environment options
        for key, value in self.defaultEnvironment().items():
            env_key = 'DOX_%s' % key
            value = os.environ.get(env_key, value)
            commands.ENVIRON[key] = value
            commands.RENDER_OPTIONS[key] = value
    
    def navigation(self):
        """
        Returns the navigation links for this dox file.
        
        :return     [(<str> title, <str> url), ..]
        """
        return self._navigation[:]
    
    def render(self,
               title,
               contents,
               breadcrumbs=None,
               baseUrl=None,
               staticUrl=None,
               filepath='',
               includeTitleInCrumbs=False,
               debug=False):
        """
        Renders the inputed text to HTML for this dox, including the
        inputed breadcrumbs when desired.
        
        :param      title | <str>
                    contents | <DoxSource.Type>
                    breadcrumbs | [<str>, ..] || None
        
        :return     <str>
        """
        self.initEnviron()
        
        curdir = os.curdir
        if self.filename():
            os.chdir(os.path.dirname(self.filename()))
        
        # generate temp breadcrumbs
        offset = 1
        if breadcrumbs is None:
            filepath = str(filepath)
            breadcrumbs = []
            dir_name = os.path.dirname(filepath)
            fname = os.path.basename(filepath).split('.')[0]
            
            if fname.lower() != 'index':
                breadcrumbs.append(projex.text.pretty(fname))
                offset = 2
            
            index_file = os.path.abspath(os.path.join(dir_name, '../index.wiki'))
            while os.path.exists(index_file):
                crumb = os.path.normpath(dir_name).split(os.path.sep)[-1]
                dir_name = os.path.abspath(os.path.join(dir_name, '..'))
                breadcrumbs.append(projex.text.pretty(crumb))
                index_file = os.path.abspath(os.path.join(dir_name, '../index.wiki'))
            
            breadcrumbs.append('Home')
            breadcrumbs.reverse()
        
        count = len(breadcrumbs) - offset
        if baseUrl is None:
            baseUrl = '.' + '/..' * count
        
        if staticUrl is None:
            staticUrl = baseUrl + '/_static'
        
        page_templ  = templates.template('page.html')
        crumb_templ = templates.template('link_breadcrumbs.html')
        nav_templ   = templates.template('link_navigation.html')
        
        # extract the mako template information
        templatePaths = self.templatePaths()
        rem_paths = []
        for path in templatePaths:
            if not path in sys.path:
                sys.path.insert(0, path)
                rem_paths.append(path)
        
        options = commands.RENDER_OPTIONS.copy()
        options['FILENAME'] = filepath
        options['ROOT'] = baseUrl
        
        if debug:
            dir_name = os.path.dirname(filepath)
            url = os.path.abspath(dir_name + baseUrl + '/../resources')
            
            commands.url_handler.setReplaceWikiSuffix(False)
            commands.url_handler.setStaticUrl('file:///' + url)
        else:
            commands.url_handler.setStaticUrl(baseUrl + '/_static')
        
        contents = projex.wikitext.render(contents,
                                          commands.url_handler,
                                          options=options,
                                          templatePaths=templatePaths)
        
        if debug:
            commands.url_handler.setStaticUrl(None)
            commands.url_handler.setReplaceWikiSuffix(True)
        
        # generate the breadcrumb links
        crumbs = []
        for i, crumb in enumerate(breadcrumbs):
            url = '.' + '/..' * (count - i) + '/index.html'
            opts = {'text': crumb, 'url': url}
            crumbs.append(crumb_templ % opts)
        
        if includeTitleInCrumbs:
            crumbs.append(crumb_templ % {'text': title, 'url': ''})
        
        # generate the environ data
        environ = commands.ENVIRON.copy()
        environ['base_url']       = baseUrl
        environ['static_url']     = staticUrl
        environ['title']          = title
        environ['contents']       = contents
        environ['breadcrumbs']    = ''.join(crumbs)
        environ['module_title']   = self.title()
        environ['module_version'] = self.version()
        environ['copyright']      = self.copyright()
        
        # create navigation links
        nav = []
        for title, url in self.navigation():
            href = url % environ
            nav.append(nav_templ % {'title': title, 'url': href})
        
        environ['navigation'] = ''.join(nav)
        
        os.chdir(curdir)
        
        # generate the html
        result = page_templ % environ
        
        sys.path = sys.path[len(rem_paths):]
        
        return result
    
    def resourcePath(self):
        """
        Returns the path to the resources for this doxfile
        
        :return     <str>
        """
        return self.config('resourcePath', '')
    
    def resourcePaths(self):
        """
        Returns a list of the resource paths for this doxfile.
        
        :return     <str>
        """
        resource_path = self.resourcePath()
        if not resource_path:
            return []
        
        output   = []
        basepath = os.path.dirname(self.filename())
        for path in resource_path.split(os.path.pathsep):
            path = os.path.expandvars(path)
            if os.path.isabs(path):
                output.append(path)
            else:
                path = os.path.abspath(os.path.join(basepath, path))
                output.append(path)
        
        return output
    
    def save(self):
        """
        Saves the doxfile to the current filename.
        
        :return     <bool> | success
        """
        return self.saveAs(self.filename())
    
    def saveAs(self, filename):
        """
        Saves this doxfile out to a file in XML format.
        
        :param      filename | <str>
        
        :return     <bool> | success
        """
        if not filename:
            return False
        
        elem = self.toXml()
        projex.text.xmlindent(elem)
        
        content = ElementTree.tostring(elem)
        
        try:
            f = open(filename, 'w')
            f.write(content)
            f.close()
        except IOError:
            logger.exception('Could not save DoxFile')
            return False
        return True
    
    def setCompany(self, company):
        """
        Sets the company for this dox file.
        
        :param      company | <str>
        """
        self.setConfig('company', company)
    
    def setCompanyUrl(self, url):
        """
        Sets the company url this dox file.
        
        :param      company | <str>
        """
        self.setConfig('companyUrl', url)
    
    def setCopyright(self, copyright):
        """
        Sets the copyright values for this dox file to the inputed value.
        
        :param      copyright | <str>
        """
        self.setConfig('copyright', copyright)
    
    def setConfig(self, key, value):
        """
        Sets the configuration value for this dox file to the inputed data.
        
        :param      key | <str>
                    value | <str>
        """
        self._config[key] = value
    
    def setDefaultEnvironment(self, env):
        """
        Sets the default environment variables for this dox file.
        
        :param      env | <dict>
        """
        self._defaultEnvironment = env
    
    def setFilename(self, filename):
        """
        Sets the filename for this dox file to the inputed file.
        
        :param      filename | <str>
        """
        self._filename = str(filename)
    
    def setNavigation(self, navigation):
        """
        Sets the navigation to the inputed list of navigation urls and titles.
        
        :param      navigation | [(<str> title, <str> url), ..]
        """
        self._navigation = navigation
    
    def setResourcePath(self, path):
        """
        Sets the resource path for this dox file to the inputed path.
        
        :param      path | <str>
        """
        self.setConfig('resourcePath', path)
    
    def setResourcePaths(self, paths):
        """
        Sets the resource path information for this dox file to the inputed
        list of files.
        
        :param      paths | [<str>, ..]
        """
        self.setResourcePath(os.path.pathsep.join(map(str, paths)))
    
    def setTemplatePath(self, path):
        """
        Sets the template path for this doxfile to the inputed path.
        
        :param      path | <str>
        """
        self.setConfig('templatePath', path)
    
    def setTemplatePaths(self, paths):
        """
        Sets the string of template paths for this dox file to the inputed
        list of paths.  This list will be used when rendering mako files
        to have as templatable options.
        
        :param      paths | <str>
        """
        self.setTemplatePath(os.path.pathsep.join(map(str, paths)))
    
    def setTheme(self, theme):
        """
        Sets the theme that will be used for this dox file.
        
        :param      theme | <str>
        """
        self.setConfig('theme', theme)
    
    def setThemePath(self, themePath):
        """
        Sets the theme path that will be used when loading the theme of
        this dox file.  If a blank string is specified, then the default theme
        locations will be used.
        
        :param      themePath | <str>
        """
        self.setConfig('themePath', themePath)
    
    def setTitle(self, title):
        """
        Sets the title for this dox file to the inputed title.
        
        :param      title | <str>
        """
        self.setConfig('title', title)
    
    def setVersion(self, version):
        """
        Sets the vesion for this dox file to the inputed version.
        
        :param      version | <str>
        """
        self.setConfig('version', version)
    
    def sources(self):
        """
        Returns a list of the sources for this dox file.
        
        :return     [<DoxSource>, ..]
        """
        return self._sources
    
    def templatePath(self):
        """
        Returns the template path linked with this dox file.
        
        :return     <str>
        """
        return self.config('templatePath', '')
    
    def templatePaths(self):
        """
        Returns a string with path separated template path locations for
        additional mako templates.
        
        :return     <str>
        """
        output = [src.filepath() for src in self.sources()]
        
        template_path = self.templatePath()
        if not template_path:
            return output
        
        basepath = os.path.dirname(self.filename())
        for path in template_path.split(os.path.pathsep):
            path = os.path.expandvars(path)
            if os.path.isabs(path):
                output.append(path)
            else:
                path = os.path.abspath(os.path.join(basepath, path))
                output.append(path)
        return output
    
    def theme(self):
        """
        Returns the theme for this dox file.
        
        :return     <str>
        """
        return self.config('theme')
    
    def themePath(self, abspath=True):
        """
        Returns the theme path for this dox file.
        
        :return     <str>
        """
        path = self.config('themePath')
        if not path:
            return resources.find('docgen/%s/' % self.theme())
        elif not abspath:
            return path
        
        if not path.startswith('.'):
            return path
        return os.path.abspath(os.path.join(os.path.dirname(self.filename()), path))
    
    def toXml(self):
        """
        Converts this dox file to XML.
        
        :return     <ElementTree.Element>
        """
        xml = ElementTree.Element('dox')
        xml.set('version', '1.0')
        
        # store the configuration data
        xconfig = ElementTree.SubElement(xml, 'config')
        
        for key, value in self._config.items():
            xattr = ElementTree.SubElement(xconfig, key)
            xattr.text = value
        
        # store environment data
        xenv = ElementTree.SubElement(xml, 'environment')
        
        for key, value in self._defaultEnvironment.items():
            xattr = ElementTree.SubElement(xenv, key)
            xattr.text = value
        
        # store the navigation data
        xnavigation = ElementTree.SubElement(xml, 'navigation')
        for title, url in self.navigation():
            xlink = ElementTree.SubElement(xnavigation, 'link')
            xlink.set('title', title)
            xlink.text = url
        
        # store source data
        xsources = ElementTree.SubElement(xml, 'sources')
        for source in self.sources():
            source.toXml(xsources)
        
        return xml
    
    def title(self):
        """
        Returns the title for this dox file.
        
        :return     <str>
        """
        return self.config('title')
    
    def version(self):
        """
        Returns the version for this dox file.
        
        :return     <str>
        """
        return self.config('version')
    
    @staticmethod
    def current():
        """
        Returns the current instance of this dox file.
        
        :return     <DoxFile> || None
        """
        return DoxFile._current
    
    @staticmethod
    def load(filename):
        """
        Loads the dox file from the inputed filename.
        
        :param      filename | <str>
        
        :return     <DoxFile>
        """
        try:
            xml = ElementTree.parse(filename)
        except:
            return DoxFile()
        
        dox = DoxFile()
        dox.setFilename(filename)
        
        # update configuration information
        xconfig = xml.find('config')
        if xconfig is not None:
            for xattr in xconfig:
                dox.setConfig(xattr.tag, xattr.text)
        
        env = {}
        xenv = xml.find('environment')
        if xenv is not None:
            for xattr in xenv:
                env[xattr.tag] = xattr.text
        
        dox.setDefaultEnvironment(env)
        
        # update navigation information
        xnavigation = xml.find('navigation')
        if xnavigation is not None:
            for xlink in xnavigation:
                dox.addNavigation(xlink.get('title'), xlink.text)
        
        # load source information
        xsources = xml.find('sources')
        if xsources is not None:
            for xsource in xsources:
                dox.addSource(DoxSource.fromXml(dox, xsource))
        
        return dox
    
    @staticmethod
    def setCurrent(doxfile):
        """
        Returns the current instance of this dox file.
        
        :param      doxfile | <DoxFile> || None
        """
        DoxFile._current = doxfile
    