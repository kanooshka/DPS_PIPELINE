""" 
Defines the templates for this build.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

NSISHORTCUT = """
    ; create a new shortcut
    CreateShortCut '$DESKTOP\\{product}.lnk' '$INSTDIR\\{product}\\{exname}.exe'
"""

NSISAPP = """
    ; install the product
    SetOutPath '$INSTDIR\\{product}\\'
    
    ; install application code
    File /nonfatal /r /x .svn /x *.pyc {srcpath}\*
"""

NSISPACKAGE = """
    ; install the product
    SetOutPath '$INSTDIR\\{product}\\'
    
    ; install python source code
    File /nonfatal /r /x .svn /x *.pyc {srcpath}\*
    
    ; install the auto-generated documentation
    SetOutPath '$INSTDIR\\{product}\\resources\\docs\\'
    File /nonfatal /r /x .svn /x *.pyc {buildpath}\\docs\\*
    
    ; install the license
    SetOutPath '$INSTDIR\\{product}\\'
    File /nonfatal {buildpath}\\license.txt
    
    SetOutPath '$INSTDIR\\{product}\\resources\\'
    File /nonfatal {buildpath}\\{product}.xdk
"""

NSISMODULE = """
    ; install the product
    SetOutPath '$INSTDIR'
    
    ; install python module
    File /nonfatal {srcpath}
"""

NSIFILE = """\
!include "MUI2.nsh"
!include LogicLib.nsh

; defined by the obuild system
!define MUI_ABORTWARNING
!define MUI_PRODUCT                     '{product}'
!define MUI_VERSION                     '{version}'
!define MUI_COMPANY                     '{company}'
!define MUI_ICON                        '{logo}'
!define MUI_UNICON                      '{logo}'
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_BGCOLOR                     'ffffff'
!define MUI_INSTFILESPAGE_PROGRESSBAR   'colored'

!define MUI_HEADERIMAGE 
!define MUI_HEADERIMAGE_BITMAP          '{header_image}'
!define MUI_WELCOMEFINISHPAGE_BITMAP    '{finish_image}'

BrandingText "{product} {version} from {company}"

InstallDir '{instpath}'

; define the name of the product
Name '{product} {version}'

; define the generated output file
OutFile '{outpath}\\{instname}-{platform}.exe'

#SilentInstall silent

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE 'license.txt'
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE '{language}'

; include the customized install and uninstall files
Section 'Install'
    {install}
    
    ; register the product
    WriteRegStr HKLM 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{company}\\{product}' 'DisplayName' '{product} (remove only)'
    WriteRegStr HKLM 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{company}\\{product}' 'UninstallString' '$INSTDIR\\{product}\\uninstall-{exname}.exe'
    
    {distopts}
    
    ; create the uninstaller
    WriteUninstaller '$INSTDIR\\{product}\\uninstall-{exname}.exe '
    
SectionEnd

Section 'Uninstall'
    ; call the uninstaller
    RMDir /r '$INSTDIR'
    Delete '$DESKTOP\\{product}.lnk'
    
    ; remove the registry information
    DeleteRegKey HKLM 'SOFTWARE\\{company}\\{product}'
    DeleteRegKey HKLM 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{company}\\{product}'

SectionEnd
"""

SETUPFILE = """\
import os
try:
    from setuptools import setup
except ImportError:
    try:
        from distutils.core import setup
    except ImportError:
        raise ImportError('Could not find setuptools.')

setup(
    name = '{name}',
    version = '{version}',
    author = '{author}',
    author_email = '{author_email}',
    maintainer = '{author}',
    maintainer_email = '{author_email}',
    description = '''{brief}''',
    license = '{license}',
    keywords = '{keywords}',
    url = '{url}',
    include_package_data=True,
    long_description='''{description}''',
    classifiers=[{classifiers}],
    packages = [{packages}],
    package_data = {{{package_data}}}
)"""

SPECTREE = """\
dataset += Tree(r'{path}', prefix='{prefix}', excludes=[{excludes}])
"""

SPECFILE = """\
# -*- mode: python -*-
import logging
import os
import sys

logger = logging.getLogger(__name__)

# define analysis options
hookpaths = [{hookpaths}]
hiddenimports = [{hiddenimports}]
excludes = [{excludes}]

# generate the analysis for our executable
results = Analysis([r'{runtime}'],
                   pathex=[r'{srcpath}/..'],
                   hiddenimports=hiddenimports,
                   hookspath=hookpaths,
                   excludes=excludes)

dataset = results.datas

# load any additional data information
{datasets}

pyz = PYZ(results.pure)
exe = EXE(pyz,
          results.scripts,
          exclude_binaries={excludeBinaries},
          name=os.path.join(os.path.join(r'build',
                                         r'pyi.{platform}',
                                         r'{exname}',
                                         r'{exname}.exe')),
          debug={debug},
          strip={strip},
          icon=r'{logo}',
          upx={upx},
          console={debug})

coll = COLLECT(exe,
               results.binaries,
               results.zipfiles,
               dataset,
               strip={strip},
               upx={upx},
               name=os.path.join(r'{distpath}', r'{exname}'))
"""