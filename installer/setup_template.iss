; =====================================================================
; Broadcast Playroom 3 — Inno Setup Installer Script Template
; Supports: Lite & FULL Editions, Coexistence Detection,
; Shared Data Directory, Mandatory Windows Defender Exclusion with UAC Warning,
; Verification Check, and Edition Desktop Shortcuts.
; =====================================================================

#define AppName "Broadcast Playroom 3"
#define AppVersion "3.0.0"
#define AppPublisher "Zepiam"
#define AppURL "https://github.com/zepiam/broadcast-playroom-3"

; เปลี่ยนเป็น FULL หรือ LITE ตอนสั่งคอมไพล์
#ifndef Edition
  #define Edition "FULL"
#endif

#if Edition == "FULL"
  #define ExeName "BroadcastPlayroom-Full.exe"
  #define ShortcutName "Broadcast Playroom"
  #define IconFile "..\assets\icons\bp-full-icon.ico"
  #define SubDir "full"
#else
  #define ExeName "BroadcastPlayroom-Lite.exe"
  #define ShortcutName "Broadcast Playroom Lite"
  #define IconFile "..\assets\icons\bp-lite-icon.ico"
  #define SubDir "lite"
#endif

[Setup]
AppId={{D41A132E-72E0-7AA2-9463-45C0A99E69FC}}
AppName={#AppName} ({#Edition})
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
DefaultDirName=C:\BroadcastPlayroom
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=..\dist_installer
OutputBaseFilename=BroadcastPlayroom-{#Edition}-Setup
SetupIconFile={#IconFile}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "thai"; MessagesFile: "compiler:Languages\Thai.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\{#SubDir}"

[Files]
; ตัวอย่างการคัดลอกไฟล์โปรแกรมเข้าโฟลเดอร์รุ่นย่อย
Source: "..\{#SubDir}\*"; DestDir: "{app}\{#SubDir}"; Flags: ignoreversion recursesubdirs createallsubdirs
; ไอคอนสำหรับ Shortcut
Source: "{#IconFile}"; DestDir: "{app}\{#SubDir}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\{#ShortcutName}"; Filename: "{app}\{#SubDir}\{#ExeName}"; IconFilename: "{app}\{#SubDir}\{#IconFile}"; WorkingDir: "{app}\{#SubDir}"
Name: "{group}\{#ShortcutName}"; Filename: "{app}\{#SubDir}\{#ExeName}"; IconFilename: "{app}\{#SubDir}\{#IconFile}"; WorkingDir: "{app}\{#SubDir}"

[Registry]
Root: HKCU; Subkey: "Software\BroadcastPlayroom"; ValueType: string; ValueName: "InstallRoot"; ValueData: "{app}"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\BroadcastPlayroom"; ValueType: string; ValueName: "DataDir"; ValueData: "{app}\data"; Flags: uninsdeletekeyifempty
#if Edition == "FULL"
Root: HKCU; Subkey: "Software\BroadcastPlayroom"; ValueType: dword; ValueName: "FullInstalled"; ValueData: 1
Root: HKCU; Subkey: "Software\BroadcastPlayroom"; ValueType: string; ValueName: "FullPath"; ValueData: "{app}\full\{#ExeName}"
#else
Root: HKCU; Subkey: "Software\BroadcastPlayroom"; ValueType: dword; ValueName: "LiteInstalled"; ValueData: 1
Root: HKCU; Subkey: "Software\BroadcastPlayroom"; ValueType: string; ValueName: "LitePath"; ValueData: "{app}\lite\{#ExeName}"
#endif

[Code]
var
  ExclusionPage: TWizardPage;
  LblExclusionDesc: TLabel;
  BtnAddExclusion: TButton;
  LblExclusionStatus: TLabel;
  ExclusionVerified: Boolean;

// -------------------------------------------------------------
// ตรวจสอบว่าเคยติดตั้งอีกเวอร์ชันหนึ่งไว้แล้วหรือไม่
// -------------------------------------------------------------
function InitializeSetup(): Boolean;
var
  ExistingRoot: String;
begin
  Result := True;
  if RegQueryStringValue(HKCU, 'Software\BroadcastPlayroom', 'InstallRoot', ExistingRoot) then
  begin
    if DirExists(ExistingRoot) then
    begin
      // ถ้าพบโฟลเดอร์หลักเดิม ให้แนะนำและล็อกโฟลเดอร์ให้ตรงกัน
      MsgBox('ตรวจพบว่าเครื่องนี้เคยติดตั้ง Broadcast Playroom ไว้แล้วที่:' + #13#10 +
             ExistingRoot + #13#10#13#10 +
             'ตัวติดตั้งจะนำเวอร์ชัน {#Edition} ไปติดตั้งไว้ในโฟลเดอร์หลักเดียวกัน เพื่อแชร์ข้อมูลการใช้งานร่วมกันครับ', mbInformation, MB_OK);
    end;
  end;
end;

// -------------------------------------------------------------
// ตรวจสอบสถานะการยกเว้นใน Windows Defender จริงผ่าน PowerShell
// -------------------------------------------------------------
function CheckDefenderExclusion(TargetFolder: String): Boolean;
var
  ResultCode: Integer;
  ScriptCmd: String;
begin
  ScriptCmd := 'if ((Get-MpPreference).ExclusionPath -contains ''' + TargetFolder + ''') { exit 0 } else { exit 1 }';
  Result := Exec('powershell.exe', '-NoProfile -ExecutionPolicy Bypass -Command "' + ScriptCmd + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// -------------------------------------------------------------
// ปลุกสิทธิ์ UAC และสั่งเพิ่มโฟลเดอร์ลงใน Defender Exclusion
// -------------------------------------------------------------
procedure BtnAddExclusionClick(Sender: TObject);
var
  InstallFolder: String;
  ErrorCode: Integer;
begin
  InstallFolder := ExpandConstant('{app}');
  
  MsgBox('ระบบกำลังจะขอสิทธิ์ผู้ดูแลระบบ (UAC)' + #13#10#13#10 +
         '*** กรุณากด "Yes" (ใช่) หรือ "OK" ในหน้าต่างที่กำลังจะปรากฏขึ้นมา ***' + #13#10 +
         'หากกด No หรือยกเลิก จะถือว่าการติดตั้งโปรแกรมไม่สมบูรณ์ครับ', mbInformation, MB_OK);

  LblExclusionStatus.Caption := 'กำลังเพิ่มสิทธิ์ยกเว้นใน Windows Defender...';
  LblExclusionStatus.Font.Color := clBlue;

  // รันคำสั่งเพิ่ม Exclusion ด้วยสิทธิ์ผู้ดูแลระบบ (runas)
  ShellExec('runas', 'powershell.exe',
            '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Add-MpPreference -ExclusionPath ''' + InstallFolder + '''"',
            '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);

  // ตรวจสอบว่าได้รับการยกเว้นจริงแล้วหรือไม่
  if CheckDefenderExclusion(InstallFolder) then
  begin
    ExclusionVerified := True;
    LblExclusionStatus.Caption := '✓ ได้รับการยกเว้นความปลอดภัยใน Windows Defender เรียบร้อยแล้ว';
    LblExclusionStatus.Font.Color := clGreen;
    WizardForm.NextButton.Enabled := True;
    MsgBox('ได้รับการยกเว้นความปลอดภัยเรียบร้อยแล้ว สามารถกด "Next (ถัดไป)" ได้เลยครับ', mbInformation, MB_OK);
  end
  else
  begin
    ExclusionVerified := False;
    LblExclusionStatus.Caption := '✗ ยังไม่ได้รับการยกเว้น กรุณากดปุ่มเพื่อขอสิทธิ์อีกครั้ง และกดยืนยัน UAC';
    LblExclusionStatus.Font.Color := clRed;
    WizardForm.NextButton.Enabled := False;
    MsgBox('การขอสิทธิ์ยกเว้นไม่สำเร็จ (อาจเกิดจากการกด No หรือปฏิเสธ UAC)' + #13#10 +
           'กรุณากดปุ่มขอสิทธิ์ใหม่อีกครั้งเพื่อความปลอดภัยในการอัปเดตโปรแกรมครับ', mbError, MB_OK);
  end;
end;

// -------------------------------------------------------------
// สร้าง Custom Wizard Page สำหรับขั้นตอน Mandatory Exclusion
// -------------------------------------------------------------
procedure InitializeWizard;
begin
  ExclusionVerified := False;

  ExclusionPage := CreateCustomPage(wpInstalling,
    'ความปลอดภัยของโปรแกรม (Windows Defender Exclusion)',
    'ขั้นตอนสำคัญ: บังคับเพิ่มโฟลเดอร์โปรแกรมลงในรายการยกเว้นความปลอดภัย');

  LblExclusionDesc := TLabel.Create(WizardForm);
  LblExclusionDesc.Parent := ExclusionPage.Surface;
  LblExclusionDesc.Left := 0;
  LblExclusionDesc.Top := 0;
  LblExclusionDesc.Width := ExclusionPage.SurfaceWidth;
  LblExclusionDesc.WordWrap := True;
  LblExclusionDesc.Caption :=
    'เนื่องจากโปรแกรมมีระบบสังเคราะห์เสียง AI และระบบ Auto-Update อัตโนมัติ ' +
    'โปรแกรมป้องกันไวรัส Windows Defender อาจตรวจจับผิดพลาดและลบไฟล์ของโปรแกรมทิ้ง' + #13#10#13#10 +
    '*** คำเตือน: กรุณากดปุ่มด้านล่าง และกด "Yes / OK" เมื่อมีหน้าต่างขอสิทธิ์ UAC ปรากฏขึ้นมา ***' + #13#10 +
    'หากไม่กด จะถือว่าการติดตั้งไม่สมบูรณ์ และจะไม่สามารถกดถัดไปได้';

  BtnAddExclusion := TButton.Create(WizardForm);
  BtnAddExclusion.Parent := ExclusionPage.Surface;
  BtnAddExclusion.Left := 0;
  BtnAddExclusion.Top := 110;
  BtnAddExclusion.Width := 280;
  BtnAddExclusion.Height := 36;
  BtnAddExclusion.Caption := '🛡️ ขอสิทธิ์ยกเว้น Windows Defender';
  BtnAddExclusion.OnClick := @BtnAddExclusionClick;

  LblExclusionStatus := TLabel.Create(WizardForm);
  LblExclusionStatus.Parent := ExclusionPage.Surface;
  LblExclusionStatus.Left := 0;
  LblExclusionStatus.Top := 160;
  LblExclusionStatus.Width := ExclusionPage.SurfaceWidth;
  LblExclusionStatus.WordWrap := True;
  LblExclusionStatus.Caption := 'สถานะ: ยังไม่ได้รับการยกเว้น (กรุณากดปุ่มด้านบน)';
  LblExclusionStatus.Font.Style := [fsBold];
  LblExclusionStatus.Font.Color := clRed;
end;

// -------------------------------------------------------------
// บล็อกปุ่ม Next ไว้จนกว่าจะได้รับการยกเว้นความปลอดภัยจริง
// -------------------------------------------------------------
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = ExclusionPage.ID then
  begin
    WizardForm.NextButton.Enabled := ExclusionVerified;
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;
