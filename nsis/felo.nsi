;       $Id$    
; ======================================================================
;     felo.nsi - Part of the Felo Program
; 
;    Copyright © 2006 Torsten Bronger <bronger@physik.rwth-aachen.de>
;
;    This file is part of the Felo program.
;
;    Felo is free software; you can redistribute it and/or modify it under
;    the terms of the MIT licence:
;
;    Permission is hereby granted, free of charge, to any person obtaining a
;    copy of this software and associated documentation files (the "Software"),
;    to deal in the Software without restriction, including without limitation
;    the rights to use, copy, modify, merge, publish, distribute, sublicense,
;    and/or sell copies of the Software, and to permit persons to whom the
;    Software is furnished to do so, subject to the following conditions:
;
;    The above copyright notice and this permission notice shall be included in
;    all copies or substantial portions of the Software.
;
;    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
;    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
;    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
;    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
;    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
;    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
;    DEALINGS IN THE SOFTWARE.
;
; ======================================================================

; NOTE: this .nsi script is designed for NSIS v2

########################################################################
#
# Header information
#
########################################################################

;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  Name "Felo"
  OutFile "Felo-1.0.exe"

  BrandingText "Felo -- http://felo.sourceforge.net"

  InstallDir "$PROGRAMFILES\Felo"
  InstallDirRegKey HKCU "Software\Felo" ""

  SetCompressor /SOLID lzma

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING
  !define MUI_UNABORTWARNING
  !define MUI_ICON "..\src\felo.ico"
  !define MUI_UNICON "..\src\felo-uninstall.ico"
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "..\src\felo-header.bmp"
  !define MUI_WELCOMEFINISHPAGE_BITMAP "..\src\felo-welcome.bmp"
  
;--------------------------------
;Language Selection Dialog Settings

  ;Remember the installer language
  !define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
  !define MUI_LANGDLL_REGISTRY_KEY "Software\Felo" 
  !define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

;--------------------------------
;Finish Page Settings

  !define MUI_FINISHPAGE_RUN "$INSTDIR\felo.exe"
  !define MUI_FINISHPAGE_NOREBOOTSUPPORT


!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE $(MUILicense)
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!include "translations.nsi"

;--------------------------------
;Reserve Files
  
  ;These files should be inserted before other files in the data block
  ;Keep these lines before any File command
  ;Only for solid compression (by default, solid compression is enabled for BZIP2 and LZMA)
  
  !insertmacro MUI_RESERVEFILE_LANGDLL

Function .onInit
  UserInfo::GetAccountType
  Pop $1
  StrCmp $1 "Admin" 0 noadmin
    SetShellVarContext all
    Goto exit
  noadmin:
    SetShellVarContext current
    StrCpy $INSTDIR "$PROFILE\Felo"
  exit:
FunctionEnd

Section "Felo"
  SetOutPath "$INSTDIR"
  File /r "..\dist\*"
  File "..\src\felo.ico"
  WriteRegStr SHCTX "Software\Felo" "" "$INSTDIR"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "DisplayName" "Felo"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "DisplayIcon" "$INSTDIR\felo.ico"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "Publisher" "Torsten Bronger, Aachen"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" \
              "HelpLink" "http://sourceforge.net/forum/forum.php?forum_id=638727"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "URLInfoAbout" "http://felo.sourceforge.net"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "DisplayVersion" "1.0"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "VersionMajor" 1
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "VersionMinor" 0
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "NoModify" 1
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo" "NoRepair" 1
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ;Create shortcuts
  CreateDirectory "$SMPROGRAMS\Felo"
  CreateShortCut "$SMPROGRAMS\Felo\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortCut "$SMPROGRAMS\Felo\Felo.lnk" "$INSTDIR\felo.exe"

  ;Create file association
  !define Index "Line${__LINE__}"
    ReadRegStr $1 HKCR ".felo" ""
    StrCmp $1 "" "${Index}-NoBackup"
      StrCmp $1 "FeloFile" "${Index}-NoBackup"
      WriteRegStr HKCR ".felo" "backup_val" $1
  "${Index}-NoBackup:"
    WriteRegStr HKCR ".felo" "" "FeloFile"
    ReadRegStr $0 HKCR "FeloFile" ""
    StrCmp $0 "" 0 "${Index}-Skip"
          WriteRegStr HKCR "FeloFile" "" "Felo bouts file"
          WriteRegStr HKCR "FeloFile\shell" "" "open"
          WriteRegStr HKCR "FeloFile\DefaultIcon" "" "$INSTDIR\felo.exe,0"
  "${Index}-Skip:"
    WriteRegStr HKCR "FeloFile\shell\open\command" "" '$INSTDIR\felo.exe "%1"'
    WriteRegStr HKCR "FeloFile\shell\edit" "" "Edit Felo File"
    WriteRegStr HKCR "FeloFile\shell\edit\command" "" '$INSTDIR\felo.exe "%1"'

    System::Call 'Shell32::SHChangeNotify(i 0x8000000, i 0, i 0, i 0)'
  !undef Index
SectionEnd

;--------------------------------
;Uninstaller Functions

Function un.onInit
  UserInfo::GetAccountType
  Pop $1
  StrCmp $1 "Admin" 0 noadmin
    SetShellVarContext all
    Goto exit
  noadmin:
    SetShellVarContext current
  exit:
FunctionEnd

Section "Uninstall"
  # I do everything separately because an RMDir /r "$INSTDIR" seems to dangerous to me.
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$INSTDIR\felo.ico"
  Delete "$INSTDIR\auf10.dat"
  Delete "$INSTDIR\auf15.dat"
  Delete "$INSTDIR\auf5.dat"
  Delete "$INSTDIR\boilerplate*.felo"
  Delete "$INSTDIR\boilerplate.felo"
  Delete "$INSTDIR\bz2.pyd"
  Delete "$INSTDIR\_controls_.pyd"
  Delete "$INSTDIR\_core_.pyd"
  Delete "$INSTDIR\felo.exe"
  Delete "$INSTDIR\felo-icon.png"
  Delete "$INSTDIR\felo-logo.png"
  Delete "$INSTDIR\felo-logo-small.png"
  Delete "$INSTDIR\_gdi_.pyd"
  Delete "$INSTDIR\_grid.pyd"
  Delete "$INSTDIR\_html.pyd"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\licence*.html"
  Delete "$INSTDIR\licence.html"
  Delete "$INSTDIR\_misc_.pyd"
  Delete "$INSTDIR\MSVCR71.dll"
  Delete "$INSTDIR\python24.dll"
  Delete "$INSTDIR\select.pyd"
  Delete "$INSTDIR\_socket.pyd"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\_stc.pyd"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\_windows_.pyd"
  Delete "$INSTDIR\wxmsw26u_stc_vc_enthought.dll"
  Delete "$INSTDIR\wxmsw26u_vc_enthought.dll"
  Delete "$INSTDIR\zlib.pyd"
  RMDir /r "$INSTDIR\po"
  RMDir "$INSTDIR"

  UserInfo::GetAccountType
  Pop $1
  StrCmp $1 "Admin" 0 noadmin
    SetShellVarContext all
  noadmin:

  Delete "$SMPROGRAMS\Felo\Uninstall.lnk"
  Delete "$SMPROGRAMS\Felo\Felo.lnk"
  RMDir "$SMPROGRAMS\Felo"

  DeleteRegKey /ifempty SHCTX "Software\Felo"
  DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\Felo"

  ;Uninstall file association
  !define Index "Line${__LINE__}"
    ReadRegStr $1 HKCR ".felo" ""
    StrCmp $1 "FeloFile" 0 "${Index}-NoOwn" ; only do this if we own it
      ReadRegStr $1 HKCR ".felo" "backup_val"
      StrCmp $1 "" 0 "${Index}-Restore" ; if backup="" then delete the whole key
        DeleteRegKey HKCR ".felo"
      Goto "${Index}-NoOwn"
  "${Index}-Restore:"
        WriteRegStr HKCR ".felo" "" $1
        DeleteRegValue HKCR ".felo" "backup_val"

      DeleteRegKey HKCR "FeloFile" ;Delete key with association settings

      System::Call 'Shell32::SHChangeNotify(i 0x8000000, i 0, i 0, i 0)'
  "${Index}-NoOwn:"
  !undef Index
SectionEnd

