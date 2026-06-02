# Auto-elevate
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Requesting admin..." -ForegroundColor Yellow
    $tempScript = Join-Path $env:TEMP "debug_write.ps1"
    $content = [IO.File]::ReadAllText($MyInvocation.MyCommand.Path, [Text.Encoding]::UTF8)
    [IO.File]::WriteAllText($tempScript, $content, [Text.UTF8Encoding]::new($true))
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$tempScript`"" -Verb RunAs -Wait
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    exit 0
}

$logFile = Join-Path ([Environment]::GetFolderPath('Desktop')) "claude-debug-log.txt"
Start-Transcript -Path $logFile -Force | Out-Null

$claude = Get-AppxPackage -Name 'Claude'
$dir = $claude.InstallLocation
$enUsFile = Join-Path $dir "app\resources\ion-dist\i18n\en-US.json"
$resultFile = Join-Path ([Environment]::GetFolderPath('Desktop')) "claude-system-result.txt"

Write-Host "Target: $enUsFile"
Write-Host ""

# Test 15: Windows Backup API (SeBackupPrivilege / FILE_FLAG_BACKUP_SEMANTICS)
Write-Host "=== Test 15: Backup API Write ==="
Add-Type @"
using System;
using System.IO;
using System.Runtime.InteropServices;
public class BackupWriter {
    [DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
    static extern IntPtr CreateFile(string lpFileName, uint dwDesiredAccess, uint dwShareMode,
        IntPtr lpSecurityAttributes, uint dwCreationDisposition, uint dwFlagsAndAttributes, IntPtr hTemplateFile);

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern bool CloseHandle(IntPtr hObject);

    [DllImport("kernel32.dll", SetLastError=true)]
    static extern bool WriteFile(IntPtr hFile, byte[] lpBuffer, uint nNumberOfBytesToWrite,
        out uint lpNumberOfBytesWritten, IntPtr lpOverlapped);

    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges,
        ref TOKEN_PRIVILEGES NewState, int BufferLength, IntPtr PreviousState, IntPtr ReturnLength);

    [DllImport("advapi32.dll", SetLastError=true)]
    static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

    [DllImport("kernel32.dll")]
    static extern IntPtr GetCurrentProcess();

    [StructLayout(LayoutKind.Sequential)]
    struct TOKEN_PRIVILEGES {
        public uint PrivilegeCount;
        public LUID Luid;
        public uint Attributes;
    }

    [StructLayout(LayoutKind.Sequential)]
    struct LUID {
        public uint LowPart;
        public int HighPart;
    }

    const uint FILE_FLAG_BACKUP_SEMANTICS = 0x02000000;
    const uint GENERIC_WRITE = 0x40000000;
    const uint CREATE_ALWAYS = 2;
    const uint SE_PRIVILEGE_ENABLED = 0x00000002;
    const uint TOKEN_ADJUST_PRIVILEGES = 0x0020;

    public static string TryWrite(string path, byte[] content) {
        try {
            // Try to enable backup privilege
            IntPtr hToken;
            if (OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, out hToken)) {
                var tp = new TOKEN_PRIVILEGES();
                tp.PrivilegeCount = 1;
                tp.Attributes = SE_PRIVILEGE_ENABLED;
                // SE_BACKUP_NAME = 17, SE_RESTORE_NAME = 18
                var luid = new LUID();
                // LookupPrivilegeValue for SeRestorePrivilege
                var tp2 = new TOKEN_PRIVILEGES { PrivilegeCount = 1, Attributes = SE_PRIVILEGE_ENABLED };
                AdjustTokenPrivileges(hToken, false, ref tp2, 0, IntPtr.Zero, IntPtr.Zero);
                CloseHandle(hToken);
            }

            IntPtr handle = CreateFile(path, GENERIC_WRITE, 1, IntPtr.Zero, CREATE_ALWAYS, FILE_FLAG_BACKUP_SEMANTICS, IntPtr.Zero);
            if (handle == new IntPtr(-1)) {
                return "CreateFile failed: " + Marshal.GetLastWin32Error();
            }
            uint written;
            bool ok = WriteFile(handle, content, (uint)content.Length, out written, IntPtr.Zero);
            CloseHandle(handle);
            if (ok) return "SUCCESS: wrote " + written + " bytes";
            return "WriteFile failed: " + Marshal.GetLastWin32Error();
        } catch (Exception ex) {
            return "Exception: " + ex.Message;
        }
    }
}
"@ -ErrorAction SilentlyContinue

$testContent = [Text.Encoding]::UTF8.GetBytes("BACKUP_API_TEST")
$r15 = [BackupWriter]::TryWrite($enUsFile, $testContent)
Write-Host "Result: $r15"
Write-Host ""

# Test 16: PowerShell FileStream with Backup flag via .NET
Write-Host "=== Test 16: .NET FileStream with FileOptions ==="
try {
    $fs = [IO.FileStream]::new($enUsFile, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
    $bytes = [Text.Encoding]::UTF8.GetBytes("FILESTREAM_TEST")
    $fs.Write($bytes, 0, $bytes.Length)
    $fs.Close()
    Write-Host "FileStream: SUCCESS"
} catch {
    Write-Host "FileStream: FAILED - $($_.Exception.Message)"
}
Write-Host ""

# Restore original content
$backupDir = Join-Path $env:USERPROFILE "AppData\Local\Claude-Chinese-Patch"
$backupFile = Join-Path $backupDir "en-US-original.json"
if (Test-Path $backupFile) {
    $origBytes = [IO.File]::ReadAllBytes($backupFile)
    $restoreResult = [BackupWriter]::TryWrite($enUsFile, $origBytes)
    Write-Host "Restore: $restoreResult"
}

Stop-Transcript | Out-Null
Write-Host ""
Write-Host "Log saved to: $logFile" -ForegroundColor Green
Read-Host "Press Enter to close"
