; ------------------------------------------------------------
; Inno Setup — Flash-Excel installer
; User-scope install (no admin required)
; ------------------------------------------------------------

#define MyAppName "Flash-Excel"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppPublisher "Neuraaak"
#define MyAppExeName "flash-excel.exe"
#define MyAppId "{{F3A2C1B4-8E5D-4F9A-B2C7-1D3E6F8A0C5B}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; User-scope : pas de droits admin, install dans %LocalAppData%
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Sortie
OutputDir=..\..\dist
OutputBaseFilename=Flash-Excel-{#MyAppVersion}-Setup

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Icône
SetupIconFile=..\..\bin\assets\images\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Pas de redémarrage nécessaire
RestartIfNeededByRun=no

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Files]
; Tout le contenu de dist/Flash-Excel/ (structure plate PyInstaller)
Source: "..\..\dist\Flash-Excel\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Nettoie les fichiers générés à l'exécution (config user, logs)
Type: filesandordirs; Name: "{app}\bin\config\app.config.yaml"
