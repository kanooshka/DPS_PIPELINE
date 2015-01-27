""" 
Defines the builder class for building versions.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import logging
import os
import re
import shutil
import subprocess
import sys
import zipfile

from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

import projex
import projex.pyi
from projex.enum import enum
from projex.xbuild import templ
from projex.xbuild import errors

import projex.resources

logger = logging.getLogger(__name__)

wrap_str = lambda x: map(lambda y: "r'{0}'".format(y.replace('\\', '/')), x)


class Builder(object):
    Options = enum('GenerateRevision',
                   'GenerateDocs',
                   'GenerateExecutable',
                   'GenerateInstaller',
                   'GenerateSetupFile',
                   'GenerateZipFile',
                   'SignExecutable',)
    
    _plugins = {}
    
    def __init__(self):
        # set general information
        self._name = ''
        self._version = ''
        self._revision = ''
        self._license = ''
        self._environment = {}
        self._options = Builder.Options.all()
        self._ignoreFileTypes = ['.pyc', '.pyo']
        self._language = 'English'
        
        # set meta information
        self._company = ''
        self._companyUrl = ''
        self._author = ''
        self._authorEmail = ''
        
        # set build paths
        self._distributionPath = ''
        self._sourcePath = ''
        self._outputPath = ''
        self._buildPath = ''
        self._licenseFile = ''
        
        # set executable options
        opts = {}
        opts['excludeBinaries'] = 1
        opts['debug'] = False
        opts['strip'] = None
        opts['logo'] = projex.resources.find('img/logo.ico')
        opts['upx'] = True
        opts['cmd'] = 'python -O /pyinstaller/pyinstaller.py "{spec}"'
        
        self._runtime = ''
        self._specfile = ''
        self._hookPaths = []
        self._hiddenImports = []
        self._executableData = []
        self._executableExcludes = []
        self._executableName = ''
        self._executablePath = ''
        self._productName = ''
        self._executableOptions = opts
        
        # set installation options
        opts = {}
        opts['logo'] = projex.resources.find('img/logo.ico')
        opts['header_image'] = projex.resources.find('img/installer.bmp')
        opts['finish_image'] = projex.resources.find('img/installer-side.bmp')
        
        for k, v in opts.items():
            opts[k] = os.path.abspath(v)
        
        opts['cmd'] = r'makensis.exe "{script}"'
        
        self._installName = ''
        self._installPath = ''
        self._installerOptions = opts
        
        # set documentation options
        self._doxfile = ''
        
        # set revision options
        self._revisionFilename = '__revision__.py'
        
        # set setuptools options
        self._distributionName = ''
        self._keywords = ''
        self._brief = ''
        self._description = ''
        self._dependencies = []
        self._classifiers = []

    def author(self):
        """
        Returns the author associated with this builder.
        
        :return     <str>
        """
        return self._author

    def authorEmail(self):
        """
        Returns the author email associated with this builder.
        
        :return     <str>
        """
        return self._authorEmail

    def brief(self):
        """
        Returns the brief associated with this builder.
        
        :return     <str>
        """
        return self._brief

    def build(self):
        """
        Builds this object into the desired output information.
        """
        # remove previous build information
        buildpath = self.buildPath()
        if not buildpath:
            raise errors.InvalidBuildPath(buildpath)
        
        # setup the environment
        for key, value in self.environment().items():
            os.environ[key] = value
        
        if os.path.exists(buildpath):
            shutil.rmtree(buildpath)
        
        # generate the build path for the installer
        os.makedirs(buildpath)
        
        # create the output path
        outpath = self.outputPath()
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        
        # copy license information
        src = self.licenseFile()
        if src and os.path.exists(src):
            targ = os.path.join(buildpath, 'license.txt')
            shutil.copyfile(src, targ)
        
        # generate revision information
        if self.options() & Builder.Options.GenerateRevision:
            self.generateRevision()
        
        # generate documentation information
        if self.options() & Builder.Options.GenerateDocs:
            self.generateDocumentation(buildpath)
        
        # generate setup file
        if self.options() & Builder.Options.GenerateSetupFile:
            self.generateSetupFile(os.path.join(self.sourcePath(), '..'))
        
        # generate executable information
        if self.options() & Builder.Options.GenerateExecutable:
            self.generateExecutable()
        
        # generate zipfile information
        if self.options() & Builder.Options.GenerateZipFile:
            self.generateZipFile(self.outputPath())
        
        # generate installer information
        if self.options() & Builder.Options.GenerateInstaller:
            self.generateInstaller(buildpath)

    def buildPath(self):
        """
        Returns the root path for building this instance.
        
        :return     <str>
        """
        return self._buildPath

    def classifiers(self):
        """
        Returns the classifiers associated with this builder.
        
        :return     [<str>, ..]
        """
        return self._classifiers

    def company(self):
        """
        Returns the company associated with this builder.
        
        :return     <str>
        """
        return self._company

    def companyUrl(self):
        """
        Returns the company url associated with this builder.
        
        :return     <str>
        """
        return self._companyUrl

    def dependencies(self):
        """
        Returns the dependencies associated with this builder.
        
        :return     [<str>, ..]
        """
        return self._dependencies

    def description(self):
        """
        Returns the description associated with this builder.
        
        :return     <str>
        """
        return self._description

    def distributionName(self):
        """
        Returns the name to be used in the setup distribution within
        python's setup tools for this builder.
        
        :return     <str>
        """
        if self._distributionName:
            return self._distributionName
        else:
            return self.name()

    def distributionPath(self):
        """
        Returns the name to be used in the setup distribution within
        python's setup tools for this builder.
        
        :return     <str>
        """
        return self._distributionPath

    def doxfile(self):
        """
        Returns the dox file for this builder.
        
        :return     <str>
        """
        return self._doxfile

    def environment(self):
        """
        Returns the environment variables for this builder.
        
        :return     {<str> key: <str> value, ..}
        """
        return self._environment

    def executableExcludes(self):
        """
        Returns the exclude packages for this executable.
        
        :return     [<str>, ..]
        """
        return self._executableExcludes

    def executableData(self):
        """
        Returns a list of the executable data that will be collected for this
        pyinstaller.
        
        :return     [(<str> type, {<str> option: <str> value})]
        """
        return self._executableData

    def productName(self):
        """
        Returns the folder for the executable this builder will generate.
        
        :return     <str>
        """
        if self._productName:
            return self._productName
        else:
            return self.name()

    def executableName(self):
        """
        Returns the name for the executable this builder will generate.
        
        :return     <str>
        """
        if self._executableName:
            return self._executableName
        else:
            return self.name()

    def executablePath(self):
        """
        Returns the default executable path for this builder.
        
        :return     <str>
        """
        return self._executablePath

    def executableOption(self, key, default=''):
        """
        Returns the executable option for given key to the inptued value.
        
        :param      key | <str>
                    default | <variant>
        """
        return self._executableOptions.get(key, default)

    def keywords(self):
        """
        Returns the keywords associated with this builder.
        
        :return     <str>
        """
        return self._keywords

    def generateDocumentation(self, outpath='.'):
        """
        Generates the documentation for this builder in the output path.
        
        :param      outpath | <str>
        """
        pass

    def generateExecutable(self, outpath='.'):
        """
        Generates the executable for this builder in the output path.
        
        :param      outpath | <str>
        """
        if not (self.runtime() or self.specfile()):
            return False
        
        if not self.distributionPath():
            return
        
        if os.path.exists(self.distributionPath()):
            shutil.rmtree(self.distributionPath())
        
        # generate the specfile if necessary
        specfile = self.specfile()
        if not specfile:
            # generate the spec file options
            opts = {}
            opts['name'] = self.name()
            opts['exname'] = self.executableName()
            opts['product'] = self.productName()
            opts['runtime'] = self.runtime()
            opts['srcpath'] = self.sourcePath()
            opts['buildpath'] = self.buildPath()
            opts['hookpaths'] = ',\n'.join(wrap_str(self.hookPaths()))
            opts['hiddenimports'] = ',\n'.join(wrap_str(self.hiddenImports()))
            opts['distpath'] = self.distributionPath()
            opts['platform'] = sys.platform
            opts['excludes'] = ',\n'.join(wrap_str(self.executableExcludes()))
            
            datasets = []
            for typ, data in self.executableData():
                if typ == 'tree':
                    args = {}
                    args['path'] = data[0]
                    args['prefix'] = data[1]
                    args['excludes'] = ','.join(wrap_str(data[2]))
                    
                    datasets.append(templ.SPECTREE.format(**args))
            
            opts['datasets'] = '\n'.join(datasets)
            
            opts.update(self._executableOptions)
            
            data = templ.SPECFILE.format(**opts)
            
            # generate the spec file for building
            specfile = os.path.join(self.buildPath(), self.name() + '.spec')
            f = open(specfile, 'w')
            f.write(data)
            f.close()
        
        cmd = self.executableOption('cmd')
        os.system(cmd.format(spec=specfile))
        
        return True

    def generateRevision(self):
        """
        Generates the revision file for this builder.
        """
        revpath = self.sourcePath()
        if not os.path.exists(revpath):
            return
        
        # determine the revision location
        revfile = os.path.join(revpath, self.revisionFilename())
        mode = ''
        # test for svn revision
        try:
            args = ['svn', 'info', revpath]
            proc = subprocess.Popen(args, stdout=subprocess.PIPE)
            mode = 'svn'
        except WindowsError:
            try:
                args = ['git', 'rev-parse', 'HEAD', revpath]
                proc = subprcoess.Popen(args, stdout=subprocess.PIPE)
                mode = 'git'
            except WindowsError:
                return
        
        # process SVN revision
        rev = None
        
        if mode == 'svn':
            for line in proc.stdout:
                data = re.match('^Revision: (\d+)', line)
                if data:
                    rev = int(data.group(1))
                    break
        elif mode == 'git':
            rev = '"' + proc.stdout.read().strip() + '"'
        
        if rev is not None:
            f = open(revfile, 'w')
            f.write('__revision__ = {0}\n'.format(rev))
            f.close()

    def generateInstaller(self, outpath='.'):
        """
        Generates the installer for this builder.
        
        :param      outpath | <str>
        """
        # generate the options for the installer
        opts = {}
        opts['name'] = self.name()
        opts['exname'] = self.executableName()
        opts['version'] = self.version()
        opts['company'] = self.company()
        opts['language'] = self.language()
        opts['license'] = self.license()
        opts['platform'] = sys.platform
        opts['product'] = self.productName()
        opts['outpath'] = self.outputPath()
        opts['instpath'] = self.installPath()
        opts['instname'] = self.installName()
        opts['buildpath'] = self.buildPath()
        
        distopts = []
        if self.runtime() and os.path.exists(self.distributionPath()):
            opts['srcpath'] = os.path.join(self.distributionPath(), self.name())
            distopts.append(templ.NSISHORTCUT.format(**opts))
            opts['install'] = templ.NSISAPP.format(**opts)
        elif os.path.isfile(self.sourcePath()):
            opts['srcpath'] = self.sourcePath()
            opts['install'] = templ.NSISMODULE.format(**opts)
        else:
            opts['srcpath'] = self.sourcePath()
            opts['install'] = templ.NSISPACKAGE.format(**opts)
        
        opts['distopts'] = '\n'.join(distopts)
        
        opts.update(self._installerOptions)
        
        data = templ.NSIFILE.format(**opts)
        
        # create the output file
        outfile = os.path.join(os.path.abspath(outpath), 'autogen.nsi')
        f = open(outfile, 'w')
        f.write(data)
        f.close()
        
        installerfile = os.path.join(self.outputPath(), self.installName())
        installerfile += '-{0}.exe'.format(sys.platform)
        
        # run the installer
        cmd = self.installerOption('cmd').format(script=outfile)
        os.system(cmd)
        os.system(installerfile)

    def generateSetupFile(self, outpath='.'):
        """
        Generates the setup file for this builder.
        """
        outfile = os.path.join(os.path.abspath(outpath), 'setup.py')
        
        opts = {}
        opts['name'] = self.distributionName()
        opts['version'] = self.version()
        opts['author'] = self.author()
        opts['author_email'] = self.authorEmail()
        opts['keywords'] = self.keywords()
        opts['license'] = self.license()
        opts['brief'] = self.brief()
        opts['description'] = self.description()
        opts['url'] = self.companyUrl()
        
        wrap_dict = lambda x: map(lambda k: "r'{0}': [{1}]".format(k[0],
                                  ',\n'.join(wrap_str(k[1]))),
                                  x.items())
        
        opts['dependencies'] = ',\n'.join(wrap_str(self.dependencies()))
        opts['classifiers'] = ',\n'.join(wrap_str(self.classifiers()))
        
        packages = []
        package_data = {}
        
        if os.path.isfile(self.sourcePath()):
            basepath = os.path.normpath(os.path.dirname(self.sourcePath()))
        else:
            basepath = os.path.normpath(self.sourcePath())
        
        baselen = len(basepath) + 1
        rootdir = os.path.basename(basepath)
        basepkg = None
        basepkgpath = ''
        package_data = {}
        
        for root, folders, files in os.walk(basepath):
            if '.svn' in root or '.git' in root:
                continue
            
            data_types = set()
            
            # generate the package information
            pkg = projex.packageFromPath(root)
            if pkg:
                packages.append(pkg)
                
                if basepkg is None:
                    basepkg = pkg
                    basepkgpath = root
            
            # load the modules
            for file in files:
                modname, ext = os.path.splitext(file)
                # ignore standard ignore files
                if ext in self.ignoreFileTypes():
                    continue
                
                # ignore non-data files
                elif ext.startswith('.py') and ext != '.pytempl':
                    if not basepkg:
                        packages.append(modname)
                    continue
                
                data_types.add('*' + ext)
            
            if data_types:
                subpath = os.path.join(basepkgpath, root[len(basepkgpath):])
                subpath = subpath.strip(os.path.sep)
                
                data_paths = []
                for data_type in data_types:
                    type_path = os.path.join(subpath, data_type)
                    data_paths.append(type_path)
                
                package_data.setdefault(basepkg, [])
                package_data[basepkg] += data_paths
        
        opts['packages'] = ',\n'.join(wrap_str(packages))
        opts['package_data'] = ',\n'.join(wrap_dict(package_data))
        
        text = templ.SETUPFILE.format(**opts)
        
        # generate the file
        f = open(outfile, 'w')
        f.write(text)
        f.close()

    def generateZipFile(self, outpath='.'):
        """
        Generates the zip file for this builder.
        """
        fname = self.installName() + '.zip'
        outfile = os.path.abspath(os.path.join(outpath, fname))
        
        # clears out the exiting archive
        if os.path.exists(outfile):
            try:
                os.remove(outfile)
            except OSError:
                logger.warning('Could not remove zipfile: %s', outfile)
                return False
        
        # generate the zip file
        zfile = zipfile.ZipFile(outfile, 'w')
        
        # zip up all relavent fields from the code base
        if os.path.isfile(self.sourcePath()):
            zfile.write(self.sourcePath(), os.path.basename(self.sourcePath()))
        else:
            basepath = os.path.abspath(os.path.join(self.sourcePath(), '..'))
            baselen = len(basepath) + 1
            for root, folders, filenames in os.walk(basepath):
                # ignore hidden folders
                if '.svn' in root or '.git' in root:
                    continue
                
                # include files
                for filename in filenames:
                    ext = os.path.splitext(filename)[1]
                    if ext in self.ignoreFileTypes():
                        continue
                    
                    arcroot = root[baselen:].replace('\\', '/')
                    arcname = os.path.join(arcroot, filename)
                    logger.info('Archiving %s...', arcname)
                    zfile.write(os.path.join(root, filename), arcname)
        zfile.close()
        return True

    def hiddenImports(self):
        """
        Returns a list of the hidden imports that are associated with this
        builder.  This is used with PyInstaller when generating a build.
        
        :return     [<str>, ..]
        """
        return self._hiddenImports

    def hookPaths(self):
        """
        Returns the path that contains additional hooks for this builder.
        This provides the root location that PyInstaller will use when
        generating installater information.
        
        :return     [<str>, ..]
        """
        return self._hookPaths

    def ignoreFileTypes(self):
        """
        Returns the file types to ignore for this builder.
        
        :return     [<str>, ..]
        """
        return self._ignoreFileTypes

    def installName(self):
        """
        Returns the name for the installer this builder will generate.
        
        :return     <str>
        """
        if self._installName:
            return self._installName
        elif self.revision():
            return '{0}-{1}.{2}'.format(self.name(),
                                            self.version(),
                                            self.revision())
        else:
            return '{0}-{1}'.format(self.name(), self.version())

    def installPath(self):
        """
        Returns the default installation path for this builder.
        
        :return     <str>
        """
        return self._installPath

    def installerOption(self, key, default=''):
        """
        Returns the installer option for given key to the inptued value.
        
        :param      key | <str>
                    default | <variant>
        """
        return self._installerOptions.get(key, default)

    def name(self):
        """
        Returns the name for this builder.
        
        :return     <str>
        """
        return self._name

    def language(self):
        """
        Returns the language associated with this builder.
        
        :return     <str>
        """
        return self._language

    def license(self):
        """
        Returns the license for this builder.
        
        :return     <str>
        """
        return self._license

    def licenseFile(self):
        """
        Returns the license file for this builder.
        
        :return     <str>
        """
        if self._licenseFile:
            return self._licenseFile
        elif self._license:
            f = projex.resources.find('licenses/{0}.txt'.format(self.license()))
            return f
        else:
            return ''

    def loadXml(self, xdata, filepath=''):
        """
        Loads properties from the xml data.
        
        :param      xdata | <xml.etree.ElementTree.Element>
        """
        # build options
        opts = {}
        opts['platform'] = sys.platform
        
        mkpath = lambda x: os.path.abspath(os.path.join(filepath, 
                                                        x.format(**opts)))
        
        # lookup environment variables
        xenv = xdata.find('environment')
        if xenv is not None:
            env = {}
            for xkey in xenv:
                env[xkey.tag] = xenv.text
            self.setEnvironment(env)
        
        # lookup general settings
        xsettings = xdata.find('settings')
        if xsettings is not None:
            for xsetting in xsettings:
                key = xsetting.tag
                val = xsetting.text
                attr = '_' + key
                if hasattr(self, attr):
                    setattr(self, attr, val)
        
        # lookup path options
        xpaths = xdata.find('paths')
        if xpaths is not None:
            for xpath in xpaths:
                key = xpath.tag
                path = xpath.text
                
                if key.endswith('Paths'):
                    path = map(mkpath, path.split(';'))
                else:
                    path = mkpath(path)
                
                setattr(self, '_' + key, path)
        
        # lookup executable options
        xexe = xdata.find('executable')
        if xexe is not None:
            exe_tags = {'runtime':'_runtime',
                        'name': '_executableName',
                        'folder': '_productName'}
            
            for tag, prop in exe_tags.items():
                xtag = xexe.find(tag)
                if xtag is not None:
                    setattr(self, prop, xtag.text)
            
            # load exclude options
            xexcludes = xexe.find('excludes')
            if xexcludes is not None:
                excludes = []
                for xexclude in xexcludes:
                    excludes.append(xexclude.text)
                self.setExecutableExcludes(excludes)
            
            # load build data
            xexedata = xexe.find('data')
            if xexedata is not None:
                data = []
                for xentry in xexedata:
                    if xentry.tag == 'tree':
                        path = xentry.get('path', '')
                        if path:
                            path = mkpath(path)
                        else:
                            path = self.sourcePath()
                        
                        prefix = xentry.get('prefix', os.path.basename(path))
                        excludes = xentry.get('excludes', '').split(';')
                        
                        if excludes:
                            data.append(('tree', (path, prefix, excludes)))
                
                self.setExecutableData(data)
            
            # load hidden imports
            xhiddenimports = xexe.find('hiddenimports')
            if xhiddenimports is not None:
                imports = []
                for ximport in xhiddenimports:
                    imports.append(ximport.text)
                self.setHiddenImports(imports)
            
            # load options
            xopts = xexe.find('options')
            if xopts is not None:
                for xopt in xopts:
                    if xopt.tag == 'logo':
                        value = mkpath(xopt.text)
                    else:
                        value = xopt.text
                    self._executableOptions[xopt.tag] = value
        
        # lookup installer options
        xexe = xdata.find('installer')
        if xexe is not None:
            exe_tags = {'runtime':'_runtime',
                        'name': '_executableName',
                        'folder': '_productName'}
            
            for tag, prop in exe_tags.items():
                xtag = xexe.find(tag)
                if xtag is not None:
                    setattr(self, prop, xtag.text)
            
            xopts = xexe.find('options')
            if xopts is not None:
                for xopt in xopts:
                    if xopt.tag == 'logo':
                        value = mkpath(xopt.text)
                    else:
                        value = xopt.text
                    
                    self._installerOptions[xopt.tag] = value

    def options(self):
        """
        Returns the build options for this instance.
        
        :return     <Builder.Options>
        """
        return self._options

    def outputPath(self):
        """
        Returns the output path for this builder.
        
        :return     <str>
        """
        return self._outputPath

    def revision(self):
        """
        Returns the revision associated with this builder instance.
        
        :return     <str>
        """
        return self._revision

    def revisionFilename(self):
        """
        Returns the filename that will be generated for automatic
        revision tracking.
        
        :return     <str>
        """
        return self._revisionFilename

    def runtime(self):
        """
        Returns the runtime script for this executable.
        
        :return     <str>
        """
        return self._runtime

    def setAuthor(self, author):
        """
        Returns the author associated with this builder.
        
        :param      author | <str>
        """
        self._author = author

    def setAuthorEmail(self, email):
        """
        Returns the author email associated with this builder.
        
        :param      email | <str>
        """
        self._authorEmail = email

    def setDistributionName(self, name):
        """
        Sets the name for this builder that will be used for distribution within
        Python's setuptools.
        
        :param      name | <str>
        """
        self._distributionName = name

    def setBrief(self, brief):
        """
        Returns the brief associated with this builder.
        
        :param      brief | <str>
        """
        self._brief = brief

    def setBuildPath(self, buildPath):
        """
        Sets the build path for this instance to the given path.
        
        :param      buildPath | <str>
        """
        self._buildPath = buildPath

    def setClassifiers(self, classifiers):
        """
        Returns the classifiers associated with this builder.
        
        :param      classifiers | [<str>, ..]
        """
        self._classifiers = classifiers

    def setCompany(self, company):
        """
        Returns the company associated with this builder.
        
        :param      company | <str>
        """
        self._company = company

    def setCompanyUrl(self, companyUrl):
        """
        Returns the company url associated with this builder.
        
        :param      companyUrl | <str>
        """
        self._companyUrl = companyUrl

    def setDistributionName(self, distname):
        """
        Sets the distribution name associated with this builder.
        
        :param      distname | <str>
        """
        self._distributionName = distname

    def setDistributionPath(self, distpath):
        """
        Sets the distribution path associated with this builder.
        
        :param      distpath | <str>
        """
        self._distributionPath = distpath

    def setDependencies(self, dependencies):
        """
        Returns the dependencies associated with this builder.
        
        :param      dependencies | [<str>, ..]
        """
        self._dependencies = dependencies

    def setDescription(self, description):
        """
        Returns the description associated with this builder.
        
        :param      description | <str>
        """
        self._description = description

    def setDoxfile(self, doxfile):
        """
        Sets the dox file for the builder.
        
        :param      doxfile | <str>
        """
        self._doxfile = doxfile

    def setEnvironment(self, environ):
        """
        Sets the environment for this builder to the inputed environment.
        
        :param      environ | {<str> key: <str> value, ..}
        """
        self._environ = environ

    def setExecutableExcludes(self, excludes):
        """
        Sets the exclude packages for this executable.
        
        :param     excludes | [<str>, ..]
        """
        self._executableExcludes = excludes

    def setExecutableData(self, data):
        """
        Sets a list of the executable data that will be collected for this
        pyinstaller.
        
        :param      data | [(<str> type, {<str> option: <str> value})]
        """
        self._executableData = data

    def setProductName(self, product):
        """
        Sets the folder for the executable this builder will generate.
        
        :param     folder | <str>
        """
        self._productName = product

    def setExecutableName(self, name):
        """
        Sets the name for the executable for this builder to the
        given name.
        
        :param      name | <str>
        """
        self._executableName = name

    def setExecutablePath(self, path):
        """
        Sets the exectuable path for this builder to the given path.
        
        :param      path | <str>
        """
        self._executablePath = path

    def setExecutableOption(self, key, value):
        """
        Sets the executable option for given key to the inptued value.
        
        :param      key | <str>
                    value | <str>
        """
        self._executableOptions[key] = value

    def setHiddenImports(self, imports):
        """
        Sets the hidden imports for this builder to the given list of imports.
        
        :param      imports | [<str>, ..]
        """
        self._hiddenImports = imports

    def setHookPaths(self, paths):
        """
        Sets the location for the hooks path for additional PyInstaller hook
        information.
        
        :param      path | <str>
        """
        self._hookPaths = paths

    def setIgnoreFileTypes(self, ftypes):
        """
        Sets the file types to ignore for this builder.
        
        :param      ftypes | [<str>, ..]
        """
        self._ignoreFileTypes = ftypes

    def setInstallName(self, name):
        """
        Sets the name for the installer for this builder to the
        given name.
        
        :param      name | <str>
        """
        self._installName = name

    def setInstallPath(self, path):
        """
        Sets the installation path for this builder to the given path.
        
        :param      path | <str>
        """
        self._installPath = path

    def setInstallerOption(self, key, value):
        """
        Sets the installer option for given key to the inptued value.
        
        :param      key | <str>
                    value | <str>
        """
        self._installerOptions[key] = value

    def setKeywords(self, keywords):
        """
        Returns the keywords associated with this builder.
        
        :param      keywords | <str>
        """
        self._keywords = keywords

    def setLanguage(self, language):
        """
        Sets the language is associated with this builder.
        
        :param      language | <str>
        """
        self._language = language

    def setLicense(self, license):
        """
        Returns the license associated with this builder.
        
        :param      license | <str>
        """
        self._license = license

    def setLicenseFile(self, filename):
        """
        Sets the filename for the license file that will be included
        with the build system.
        
        :param      filename | <str>
        """
        self._licenseFile = filename

    def setName(self, name):
        """
        Sets the name for this instance.
        
        :param      name | <str>
        """
        self._name = name

    def setOptions(self, options):
        """
        Sets the options for this builder instance.
        
        :param      options | <Builder.Options>
        """
        self._options = options

    def setOutputPath(self, outpath):
        """
        Sets the output path for this builder.
        
        :param      outpath | <str>
        """
        self._outputPath = outpath

    def setRevision(self, rev):
        """
        Sets the revision information for this builder.
        
        :param      rev | <str>
        """
        self._revision = rev

    def setRevisionFilename(self, filename):
        """
        Sets the revision filename for this instance.
        
        :param      filename | <str>
        """
        self._revisionFilename = filename

    def setRuntime(self, runtime):
        """
        Sets the runtime script for this builder to the given path.  This is
        ussed in conjunction with generateExecutable to determine what paths
        to use for building a runtime file.
        
        :param      runtime | <str>
        """
        self._runtime = runtime

    def setSpecfile(self, specfile):
        """
        Sets the specfile for the builder for this instance.
        
        :param      specfile | <str>
        """
        self._specfile = specfile

    def setSourcePath(self, path):
        """
        Sets the path for the revision for this builder object.
        
        :param      path | <str>
        """
        self._sourcePath = path

    def setVersion(self, version):
        """
        Sets the version information for this builder.
        
        :param      version | <str>
        """
        self._version = version

    def specfile(self):
        """
        Returns the specfile for generating pyInstaller information.
        
        :return     <str>
        """
        return self._specfile

    def sourcePath(self):
        """
        Returns the path for generating the revision information.
        
        :return     <str>
        """
        return self._sourcePath

    def version(self):
        """
        Returns the version associated with this builder.
        
        :return     <str>
        """
        return self._version
 
    @staticmethod
    def plugin(name):
        """
        Returns the plugin for the given name.  By default, the
        base Builder instance will be returned.
        
        :param      name | <str>
        """
        return Builder._plugins.get(name, Builder)
 
    @staticmethod
    def register(plugin, name=None):
        """
        Registers the given builder as a plugin to the system.
        
        :param      plugin | <subclass of PackageBuilder>
                    name   | <str> || None
        """
        if name is None:
            name = plugin.__name__
        
        Builder._plugins[name] = plugin
    
    @classmethod
    def fromXml(cls, xdata, filepath=''):
        """
        Generates a new builder from the given xml data and then
        loads its information.
        
        :param      xdata | <xml.etree.ElementTree.Element>
        
        :return     <Builder> || None
        """
        builder = cls()
        builder.loadXml(xdata, filepath=filepath)
        return builder
    
    @staticmethod
    def fromFile(filename):
        """
        Parses the inputed xml file information and generates a builder
        for it.
        
        :param      filename | <str>
        
        :return     <Builder> || None
        """
        try:
            xdata = ElementTree.parse(filename).getroot()
        except ExpatError:
            return None
        
        builder = Builder.plugin(xdata.get('type'))
        if builder:
            return builder.fromXml(xdata, os.path.dirname(filename))
        return None
 
#----------------------------------------------------------------------

class PackageBuilder(Builder):
    """ A builder for an individual package. """
    def __init__(self, pkg):
        super(PackageBuilder, self).__init__()
        
        # set build information from the package
        filepath = getattr(pkg, '__file__', '')
        if '__init__' in filepath:
            srcpath = os.path.dirname(filepath)
            product = pkg.__name__
        else:
            if filepath.endswith('.pyc'):
                filepath = filepath[:-1]
            
            srcpath = filepath
            product = os.path.basename(srcpath)
        
        buildpath = os.path.join(srcpath, '..', '.build')
        distpath = os.path.join(srcpath, '..', '.dist')
        outpath = os.path.join(srcpath, '..', '.bin', sys.platform)
        
        instpath = os.path.dirname(sys.executable)
        instpath = os.path.join(instpath, 'Lib', 'site-packages')
        
        self.setProductName(product)
        self.setDistributionPath(os.path.abspath(distpath))
        self.setSourcePath(os.path.abspath(srcpath))
        self.setBuildPath(os.path.abspath(buildpath))
        self.setOutputPath(os.path.abspath(outpath))
        self.setInstallPath(instpath)
        
        if hasattr(pkg, '__bdist_name__'):
            self.setName(getattr(pkg, '__bdist_name__', ''))
        else:
            self.setName(getattr(pkg, '__name__', ''))
        
        self.setVersion(getattr(pkg, '__version__', '0.0'))
        self.setRevision(getattr(pkg, '__revision__', ''))
        self.setAuthor(getattr(pkg, '__maintainer__', ''))
        self.setAuthorEmail(getattr(pkg, '__email__', ''))
        self.setDescription(getattr(pkg, '__doc__', ''))
        self.setBrief(getattr(pkg, '__brief__', ''))
        self.setLicense(getattr(pkg, '__license__', ''))
        self.setCompany(getattr(pkg, '__company__', ''))
        self.setCompanyUrl(getattr(pkg, '__company_url__', ''))

    @classmethod
    def fromXml(cls, xdata, filepath=''):
        """
        Generates a new builder from the given xml data and then
        loads its information.
        
        :param      xdata | <xml.etree.ElementTree.Element>
        
        :return     <Builder> || None
        """
        module = None
        pkg_data = xdata.find('package')
        if pkg_data is not None:
            path = pkg_data.find('path').text
            name = pkg_data.find('name').text
            
            if filepath:
                path = os.path.join(filepath, path)
            
            path = os.path.abspath(path)
            sys.path.insert(0, path)
            sys.modules.pop(name, None)
            
            try:
                __import__(name)
                module = sys.modules[name]
            except ImportError, KeyError:
                return None
        else:
            return None
        
        # generate the builder
        builder = cls(module)
        builder.loadXml(xdata, filepath=filepath)
        return builder

Builder.register(PackageBuilder)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: projex/xbuild/builder [buildfile]'
        sys.exit(0)
    
    builder = Builder.fromFile(sys.argv[1])
    if builder:
        builder.build()