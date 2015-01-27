#!/usr/bin/python

""" Defines the reusable build system that will build all of the \
projects created as part of the projex suite. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import logging
import os
import re
import shutil
import subprocess
import sys
import zipfile

from optparse               import OptionParser
from xml.etree.ElementTree  import ElementTree

NSI_EXE = os.getenv('NSIS_EXE', r'c:\Program Files (x86)\NSIS\makensis.exe')
NSI_EXE = os.getenv('NSIS_EXE', r'c:\Program Files (x86)\NSIS\makensis.exe')

BASE_PATH = os.path.dirname(__file__)

PLATFORM_PYTHON_PATHS = {
    'win32':  os.environ.get('PROJEX_BUILD_PYWIN32', 
                            r'C:\Python%(py_major)s%(py_minor)s\lib\site-packages'),
    'win64':  os.environ.get('PROJEX_BUILD_PYWIN64',
                            r'C:\Python%(py_major)s%(py_minor)s_64\lib\site-packages'),
    'linux2': os.environ.get('PROJEX_BUILD_PYLINUX',
                             '/usr/lib/python%(py_major)s%(py_minor)s/site-packages/'),
    'osx':    os.environ.get('PROJEX_BUILD_PYOSX',
                             '/usr/lib/python%(py_major)s%(py_minor)s/site-packages/'),
    'darwin': os.environ.get('PROJEX_BUILD_DARWIN',
                             '/Library/Frameworks/Python.framework/Versions/%(py_major)s.%(py_minor)s/'\
                             'lib/python%(py_major)s.%(py_minor)s/site-packages/')
}

PLATFORM_APP_PATHS = {
    'win32':  os.environ.get('PROJEX_BUILD_APPWIN32',
                            r'$PROGRAMFILES\%(company)s'),
    'win64':  os.environ.get('PROJEX_BUILD_APPWIN64',
                            r'$PROGRAMFILES64\%(company)s'),
    'linux2': os.environ.get('PROJEX_BUILD_APPLINUX',
                            r'/usr/bin/'),
    'osx':    os.environ.get('PROJEX_BUILD_APPOSX',
                            r'/usr/bin/'),
    'darwin': os.environ.get('PROJEX_BUILD_DARWIN',
                            r'/usr/bin/')
}

APP_INSTALLER = r"""SetOutPath '$INSTDIR\${MUI_PRODUCT}\bin\Python%(PY_VERSION)s\'
    File /nonfatal /r /x .svn %(DEV_PATH)s\common\%(PLATFORM)s\Python%(PY_VERSION)s\*
    
    ; create a new shortcut
    CreateShortCut '$DESKTOP\${MUI_PRODUCT}.lnk' '"${PYTHON_INSTDIR}\pythonw.exe"' '"$INSTDIR\${MUI_PRODUCT}\main.py"' '$INSTDIR\${MUI_PRODUCT}\resources\img\icon.ico'
    """

SETUP_FILE = """\
import os
try:
    from setuptools import setup
except ImportError:
    try:
        from distutils.core import setup
    except ImportError:
        raise ImportError('Could not find setuptools.')

setup(
    name = "%(dist_name)s",
    version = "%(version)s",
    author = "%(author)s",
    author_email = "%(email)s",
    maintainer = "%(author)s",
    maintainer_email = "%(email)s",
    description = '''%(brief)s''',
    license = "%(license)s",
    keywords = "%(keywords)s",
    url = "%(url)s",
    include_package_data=True,
    long_description='''%(description)s''',
    classifiers=[
        "Development Status :: %(dev_status)s",
    ],
    packages = [
        %(packages)s
    ],
    package_data = {
        "%(dist_name)s": [
%(package_data)s
        ]
    }
)
"""

logger = logging.getLogger(__name__)

def build( module, 
           typ          = 'root', 
           platform     = 'win64',
           company      = 'Projex Software',
           userpath     = '',
           doc_config   = '',
           license      = 'GPL',
           language     = 'Englight'):
    """
    Runs an nsi installer for building exe files.  The typ parameter will
    drive where the default install location will be.  Possible values would
    be root (default python site-packages), lib (projex/lib), stdplug
    (projex/stdplug), userplug (projex/userplug), app (projex/app).
    
    :param      module      |  <module>
    :param      typ         |  <str>
    :param      platform    |  <str>
    :param      company     |  <str>
    
    :return     <bool>
    """
    project_path = os.path.join( os.path.dirname(module.__file__), '../..' )
    project_path = os.path.abspath(project_path)
    code_path    = os.path.join( os.path.dirname(module.__file__), '..' )
    code_path    = os.path.abspath(code_path)
    
    # define the default install location
    platform_path = PLATFORM_PYTHON_PATHS.get( platform )
    if ( not platform_path ):
        logger.error('There is no python path defined for %s platform' \
                     % platform)
        return False
    
    # determine the installation location
    py_major    = sys.version_info[0]
    py_minor    = sys.version_info[1]
    
    if ( typ == 'app' ):
        install_dir = PLATFORM_APP_PATHS.get( platform ) % {'company': company}
        py_install_dir = os.environ.get('PYTHON_INSTDIR',
                                     r'$INSTDIR\${MUI_PRODUCT}\bin\Python%(PY_VERSION)s')
    else:
        install_dir = platform_path % {'py_major': py_major, 'py_minor': py_minor}
        py_install_dir = ''
    
    vdata = getattr(module, '__version_info__', (0, 0, 0))
    vname = getattr(module, '__version__', '0.0 (r 0)')
    
    # create the nsi information
    opt = {}
    opt['MUI_PRODUCT']   = module.__name__
    opt['MUI_COMPANY']   = company
    opt['MUI_VERSION']   = vname
    opt['VERSION']       = '%s.%s.%s' % vdata
    opt['PROJECT_PATH']  = project_path
    opt['PLATFORM']      = platform
    opt['LICENSE']       = license
    opt['DEV_PATH']      = os.path.normpath(os.environ.get('PROJEX_DEVPATH', ''))
    opt['PROJEXCORE_PATH'] = os.path.abspath(os.path.dirname(__file__) + '/..')
    opt['OUTPUT_PATH']   = r'%(PROJECT_PATH)s\bin\%(PLATFORM)s' % opt
    opt['OUTPUT_NAME']   = r'%(MUI_PRODUCT)s-%(VERSION)s-%(PLATFORM)s.exe' % opt
    opt['OUTPUT_FILE']   = os.path.join(opt['OUTPUT_PATH'], opt['OUTPUT_NAME'])
    opt['PYTHON_INSTDIR'] = py_install_dir
    opt['LANGUAGE']      = language
    opt['INSTALL_DIR']   = os.path.normpath(install_dir)
    opt['PY_VERSION']    = '%s%s' % (py_major, py_minor)
    
    if ( os.environ.get('PROJEX_COMMON_NOBUILD') != '1' ):
        opt['APP_INSTALLER'] = (APP_INSTALLER if typ == 'app' else '') % opt
    else:
        opt['APP_INSTALLER'] = ''
    
    build_path = opt['OUTPUT_PATH'].replace('\\', '/')
    if ( not os.path.exists(build_path) ):
        os.mkdir(build_path)
    
    build_path = os.path.join(project_path,'_build')
    
    # try to clear out the build folder before continuing
    if ( os.path.exists(build_path) ):
        try:
            shutil.rmtree(build_path)
        except Exception:
            pass
    
    # create the autogen file
    if ( not os.path.exists(build_path) ):
        os.mkdir(build_path)
    
    # create the autogen information
    fname = os.path.join(project_path,'_build/autogen.nsi')
    
    # load the template installer file
    templ_path = os.path.join(BASE_PATH, 'resources/template.nsi')
    templ_read = open(templ_path, 'r')
    data = templ_read.read()
    templ_read.close()
    
    # save the template file for the given version
    templ_write = open(fname, 'w')
    templ_write.write(data % opt)
    templ_write.close()
    
    # copy the resource file to the build directory
    src   = os.path.join(BASE_PATH,  'resources/licenses/%s.txt' % license)
    targ  = os.path.join(build_path, 'license.txt')
    shutil.copyfile(src, targ)
    
    # generate the documentation
    if ( os.getenv('PROJEX_DOCGEN_NOBUILD') != '1' ):
        import projex.docgen
        
        filename = os.path.abspath(doc_config)
        dirname  = os.path.dirname(filename)
        docpath  = os.path.join(project_path, '_build/docs/')
        modname  = os.path.basename(filename).split('.')[0]
        
        sys.path.insert(0, dirname)
        
        try:
            conf = __import__(modname)
        
        except ImportError:
            conf = None
            msg = 'Could not import %s from %s file for documentation.'
            logger.error(msg, modname, dirname)
        
        projex.docgen.generate(module, docpath, userpath, config = conf)
        
    # generate the setup file
    if ( os.getenv('PROJEX_SETUP_NOBUILD') != '1' ):
        generate_setup(module, code_path, license)
    
    # build package zip file
    if ( os.getenv('PROJEX_ZIP_NOBUILD') != '1' ):
        output_path     = opt['OUTPUT_PATH']
        output_fname    = r'%(MUI_PRODUCT)s-%(VERSION)s.zip' % opt
        output_name     = os.path.join(output_path, output_fname)
        output_filepath = os.path.join(output_path, output_name)
        output_filepath = os.path.normpath(output_filepath).replace('\\', '/')
        
        # clear out the existing archive
        if ( os.path.exists(output_filepath) ):
            try:
                os.remove(output_filepath)
            except OSError:
                logger.warning('Could not remove zipfile: %s' % output_filepath)
        
        zfile = zipfile.ZipFile(output_filepath, 'w')
        
        # zip up all the relavent files from the code base
        for root, folders, filenames in os.walk(code_path):
            # ignore .svn folders
            if ( '.svn' in root ):
                continue
            
            for filename in filenames:
                if ( filename.endswith('.pyc') ):
                    continue
                
                arcname = os.path.join(root.replace(code_path, '').lstrip('/'),
                                       filename)
                
                logger.info('Archiving %s...' % arcname)
                zfile.write(os.path.join(root, filename), arcname)
        
        # zip up all the source documentation for the build
        if ( os.path.exists(userpath) ):
            userpath = os.path.abspath(userpath)
            for root, folders, filenames in os.walk(userpath):
                if ( '.svn' in root ):
                    continue
                
                for filename in filenames:
                    base_path = root.replace(userpath, '').lstrip('/')
                    arcname = os.path.join('wiki', base_path, filename)
                    arcname = arcname.replace('\\', '/').strip('/')
                    
                    logger.info('Archiving %s...' % arcname)
                    zfile.write(os.path.join(root, filename), arcname)
        
        # zip up all the documentation from the build
        for root, folders, filenames in os.walk(build_path):
            if ( '.svn' in root ):
                continue
                
            for filename in filenames:
                if ( filename == 'autogen.nsi' ):
                    continue
                
                base_path = root.replace(build_path, '').lstrip('/')
                arcname = os.path.join(module.__name__, base_path, filename)
                arcname = arcname.replace('\\', '/').strip('/')
                
                if ( not arcname.startswith(module.__name__) ):
                    arcname = module.__name__ + '/' + arcname
                
                logger.info('Archiving %s...' % arcname)
                zfile.write(os.path.join(root, filename), arcname)
        
        # zip up the .xdk file
        xdk_filename = '_build/%s.xdk' % module.__name__
        xdk_filepath = os.path.join(project_path, xdk_filename)
        if ( os.path.exists(xdk_filepath) ):
            arcname = r'%s/resources/%s.xdk' % (module.__name__, module.__name__)
            logger.info('Archiving %s...' % arcname)
            zfile.write(xdk_filepath, arcname)
        
        zfile.close()
        
        logger.info('Archiving Completed.')
    
    # build NSI/windows exe
    if ( sys.platform.startswith('win') and 
         os.getenv('PROJEX_NSI_NOBUILD') != '1' ):
        
        # run the installer
        cmd = '"%s" %s' % (NSI_EXE, fname)
        
        # build the project
        os.system(cmd)
        os.system(opt['OUTPUT_FILE'])

def generate_setup_for_path(path, license='GPL'):
    """
    Adds the path to the sys path and then imports the package, creating a \
    setup.py file for it.
    
    :param      path | <str>
    
    :return     <bool> | success
    """
    package_path    = os.path.normpath(path)
    base_path       = os.path.dirname(package_path)
    
    if ( not base_path in sys.path ):
        sys.path.insert(0, base_path)
    
    package_name    = package_path.split(os.path.sep)[-1]
    
    try:
        __import__(package_name)
    except ImportError:
        logger.error('Could not import %s from %s' % (package_name, base_path))
        return False
    
    module = sys.modules.get(package_name)
    if ( not module ):
        logger.error('Could not find %s module.' % package_name)
        return False
        
    generate_setup(module, base_path, license)
    return True

def generate_setup(module, output_path, license='GPL'):
    """
    Generates a setup.py file for the inputed python module/package.
    
    :param      module      | <module> || <package>
                output_path | <str>
    """
    setuppath = os.path.join(output_path, 'setup.py')
        
    options                 = {}
    
    dist_name               = module.__name__
    if ( hasattr(module, '__bdist_name__') ):
        dist_name           = module.__bdist_name__
    
    brief = getattr(module, '__doc__', '').split('.')[0]
    if brief:
        brief += '.'
    
    if len(brief) > 103:
        brief = brief[:100] + '...'
    
    options['dist_name']    = dist_name
    options['project_name'] = module.__name__
    options['version']      = getattr(module, '__version__', '0.0.0')
    options['author']       = getattr(module, '__maintainer__', '')
    options['email']        = getattr(module, '__email__' '')
    options['keywords']     = ''
    options['license']      = license
    options['brief']        = brief.strip()
    options['description']  = getattr(module, '__doc__', '').strip()
    options['url']          = 'http://www.projexsoftware.com/'
    
    deps = map(lambda x: "'%s'" % x, getattr(module, '__depends__', []))
    options['dependencies'] = ','.join(deps)
    options['dev_status']   = '3 - Alpha'
    
    packages = []
    package_data = {}
    
    base_path = os.path.normpath(os.path.dirname(module.__file__))
    
    for path, folders, files in os.walk(base_path):
        if ( '.svn' in path ):
            continue
        
        path = os.path.normpath(path).replace(base_path, '')
        path = path.strip('"').strip(os.path.sep)
        path = ('%s/%s' % (module.__name__, path)).strip('/\\')
        path = path.replace('\\', '/')
        
        # include package paths
        packages.append('"%s"' % path)
        
        data_files = []
        
        # include orb file data
        for file in files:
            ext = os.path.splitext(file)[1]
            if ( ext.startswith('.py') and ext != '.pytempl' ):
                continue
            
            data_files.append(file)
        
        package_data[path] = data_files
        
    options['packages']     = ',\n        '.join(packages)
    
    # format the package data
    pkg_data = []
    for path, data_files in package_data.items():
        path = path[len(dist_name)+1:].replace('\\', '/')
        
        for data_file in data_files:
            pkg_data.append('            "%s/%s",' % (path, data_file))
    
    options['package_data'] = '\n'.join(pkg_data)
    
    setup_data = SETUP_FILE % options
    
    # generate the setup file
    setup_file = open(setuppath, 'w')
    setup_file.write(setup_data)
    setup_file.close()

def main():
    """
    Processes and runs the code from the command line.
    
    :param      argv  |  [ <str>, .. ]
    
    :return     <int>
    """
    logging.basicConfig()
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    usage  = 'usage: xbuild [buildfile].xbuild'
    parser = OptionParser(usage=usage)
    args   = parser.parse_args()[1]
    
    # make sure we have a build file to process
    if ( not args ):
        parser.print_help()
        sys.exit(1)
    
    tree = ElementTree()
    root = tree.parse(args[0])
    
    # grab the relative path from the build file
    relpath = os.path.dirname(args[0])
    modtype = root.get('type')
    company = root.get('company', 'Projex Software')
    license = root.get('license', 'GPL')
    lang    = root.get('lang', 'English')
    modelem = root.find('module')
    modname = modelem.get('name')
    modpath = modelem.get('path')
    
    platform = os.getenv('PROJEX_BUILD_PLATFORM', sys.platform)
    
    docs        = root.find('docs')
    doc_config  = os.getenv('PROJEX_DOCGEN_CONFIG', '')
    userpath    = os.getenv('PROJEX_DOCGEN_USREPATH', '')
    
    if ( docs is not None ):
        if ( not doc_config ):
            doc_config = docs.get('config', '')
        if ( not userpath ):
            userpath   = os.path.dirname(docs.get('config', ''))
    
    # import the module
    modpath  = modpath.replace('.', relpath)
    
    # generate revision file
    rev_file = os.path.join(modpath, modname, '__revision__.py')
    try:
        proc = subprocess.Popen(['svn', 'info', modpath], stdout=subprocess.PIPE)
    except WindowsError:
        proc = None
    
    rev = None
    if proc:
        for line in proc.stdout:
            data = re.match('^Revision: (\d+)', line)
            if data:
                rev = int(data.group(1))
                break
    
    if rev is not None:
        f = open(rev_file, 'w')
        f.write('__revision__ = %i\n' % rev)
        f.close()
    
    if ( not modpath in sys.path ):
        sys.path.insert(0, modpath)
    
    __import__(modname)
    mod = sys.modules[modname]
    
    # build NSI installers
    return build( mod, 
                  typ = modtype,
                  platform = platform,
                  company = company,
                  userpath = userpath,
                  doc_config = doc_config,
                  license = license,
                  language = lang)

if ( __name__ == '__main__' ):
    sys.exit(main())