; Inno Setup Script for Organizador de Terapias
; Requires Inno Setup 6.0 or later - https://jrsoftware.org/isdl.php
; v3.0.0: Modo claro/oscuro, Word sin bloqueo, tooltips, atajos, elegir archivo, config en %APPDATA%

#define MyAppName "Organizador de Terapias"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "SCRIPS"
#define MyAppExeName "terapias.exe"

[Setup]
AppId={{A5B3C7D9-1E2F-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=README.md
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer_output
OutputBaseFilename=OrganizadorTerapias_Setup_v{#MyAppVersion}
SetupIconFile=image-removebg-preview.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Instalador de {#MyAppName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "image-removebg-preview.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "organizar_config.ini.ejemplo"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "CONTRIBUTING.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "BUILD_INSTRUCTIONS.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\image-removebg-preview.ico"
Name: "{group}\Documentación"; Filename: "{app}\README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\image-removebg-preview.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DataDirPage: TInputDirWizardPage;
  SourceFolder, DestFolder, BackupFolder: String;

procedure InitializeWizard;
begin
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Configuración de Carpetas', 'Seleccione las ubicaciones de las carpetas de trabajo',
    'Carpeta Origen: documentos Word para organizar' + #13#10 +
    'Carpeta Destino: organización por fecha y paciente' + #13#10 +
    'Carpeta Respaldo: Word después de convertir a PDF',
    False, '');
  SourceFolder := ExpandConstant('{userdocs}\TERAPIAS\DOCUMENTOS PARA ARMAR');
  DestFolder := ExpandConstant('{userdocs}\TERAPIAS\TERAPIAS');
  BackupFolder := ExpandConstant('{userdocs}\TERAPIAS\Respaldo');
  DataDirPage.Add('Carpeta Origen:');
  DataDirPage.Add('Carpeta Destino:');
  DataDirPage.Add('Carpeta Respaldo:');
  DataDirPage.Values[0] := SourceFolder;
  DataDirPage.Values[1] := DestFolder;
  DataDirPage.Values[2] := BackupFolder;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = DataDirPage.ID then
  begin
    SourceFolder := DataDirPage.Values[0];
    DestFolder := DataDirPage.Values[1];
    BackupFolder := DataDirPage.Values[2];
    if (SourceFolder = DestFolder) or (SourceFolder = BackupFolder) or (DestFolder = BackupFolder) then
    begin
      MsgBox('Las carpetas deben ser diferentes entre sí.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    if not DirExists(SourceFolder) then CreateDir(SourceFolder);
    if not DirExists(DestFolder) then CreateDir(DestFolder);
    if not DirExists(BackupFolder) then CreateDir(BackupFolder);
    if not DirExists(ExpandConstant('{userappdata}\OrganizadorTerapias')) then
      CreateDir(ExpandConstant('{userappdata}\OrganizadorTerapias'));
    ConfigFile := ExpandConstant('{userappdata}\OrganizadorTerapias\organizar_config.ini');
    SetArrayLength(ConfigContent, 8);
    ConfigContent[0] := '[RUTAS]';
    ConfigContent[1] := 'source = ' + SourceFolder;
    ConfigContent[2] := 'base_dest = ' + DestFolder;
    ConfigContent[3] := 'backup = ' + BackupFolder;
    ConfigContent[4] := 'logfile = ' + ExpandConstant('{userdocs}\TERAPIAS\organizar_log.txt');
    ConfigContent[5] := 'word_path = winword.exe';
    ConfigContent[6] := '[UI]';
    ConfigContent[7] := 'appearance = Dark';
    SaveStringsToFile(ConfigFile, ConfigContent, False);
  end;
end;

[UninstallDelete]
Type: files; Name: "{userappdata}\OrganizadorTerapias\organizar_config.ini"
Type: dirifempty; Name: "{userappdata}\OrganizadorTerapias"

[Messages]
spanish.WelcomeLabel2=Esto instalará [name/ver] en su computadora.%n%nLe ayudará a organizar documentos de terapias, convertirlos a PDF y mantener un respaldo automático.
spanish.FinishedLabel=La instalación de [name] ha finalizado.%n%nPuede ejecutar la aplicación desde los accesos directos instalados.
