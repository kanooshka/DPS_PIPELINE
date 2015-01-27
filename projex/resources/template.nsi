!include "MUI2.nsh"
!include LogicLib.nsh

; defined by the obuild system
!define PROJECT_PATH '%(PROJECT_PATH)s'
!define PLATFORM '%(PLATFORM)s'
!define RESOURCE_PATH "%(PROJEXCORE_PATH)s\projex\resources"

!define MUI_ABORTWARNING
!define MUI_PRODUCT                     '%(MUI_PRODUCT)s'
!define PYTHON_INSTDIR                  '%(PYTHON_INSTDIR)s'
!define MUI_VERSION                     '%(MUI_VERSION)s'
!define MUI_COMPANY                     '%(MUI_COMPANY)s'
!define MUI_ICON                        '${RESOURCE_PATH}\img\logo.ico'
!define MUI_UNICON                      '${RESOURCE_PATH}\img\logo.ico'
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_BGCOLOR                     'ffffff'
!define MUI_INSTFILESPAGE_PROGRESSBAR   'colored'

!define MUI_HEADERIMAGE 
!define MUI_HEADERIMAGE_BITMAP          '${RESOURCE_PATH}\img\installer.bmp'
!define MUI_WELCOMEFINISHPAGE_BITMAP    '${RESOURCE_PATH}\img\installer-side.bmp'

BrandingText "${MUI_PRODUCT} ${MUI_VERSION} from ${MUI_COMPANY}"

InstallDir '%(INSTALL_DIR)s'

; define the name of the product
Name '${MUI_PRODUCT} ${MUI_VERSION}'

; define the generated output file
OutFile         '%(OUTPUT_FILE)s'

#SilentInstall silent

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE 'license.txt'
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE 'English'

; include the customized install and uninstall files
Section 'Install'
    ; install the product
    SetOutPath '$INSTDIR\${MUI_PRODUCT}\'
    
    ; install the python code
    File /nonfatal /r /x .svn /x *.pyc ${PROJECT_PATH}\code\${MUI_PRODUCT}\*
    
    ; install the auto-generated documentation
    SetOutPath '$INSTDIR\${MUI_PRODUCT}\resources\docs\'
    File /nonfatal /r /x .svn /x *.pyc ${PROJECT_PATH}\_build\docs\*
    
    ; install the license
    SetOutPath '$INSTDIR\${MUI_PRODUCT}\'
    File /nonfatal ${PROJECT_PATH}\_build\license.txt
    
    SetOutPath '$INSTDIR\${MUI_PRODUCT}\resources\'
    File /nonfatal ${PROJECT_PATH}\_build\${MUI_PRODUCT}.xdk
    
    ; install the external logic
    %(APP_INSTALLER)s
    
    ; register the product
    WriteRegStr HKLM 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_COMPANY}\${MUI_PRODUCT}' 'DisplayName' '${MUI_PRODUCT} (remove only)'
    WriteRegStr HKLM 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_COMPANY}\${MUI_PRODUCT}' 'UninstallString' '$INSTDIR\${MUI_PRODUCT}\uninstall.exe'
    
    ; create the uninstaller
    WriteUninstaller '$INSTDIR\${MUI_PRODUCT}\uninstall.exe '
    
SectionEnd

Section 'Uninstall'
    ; call the uninstaller
    RMDir /r '$INSTDIR'
    Delete '$DESKTOP\${MUI_PRODUCT}.lnk'
    
    ; remove the registry information
    DeleteRegKey HKLM 'SOFTWARE\${MUI_COMPANY}\${MUI_PRODUCT}'
    DeleteRegKey HKLM 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${MUI_COMPANY}\${MUI_PRODUCT}'

SectionEnd