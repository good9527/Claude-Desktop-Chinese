param(
    [Parameter(Mandatory=$false)][switch]$Check,
    [Parameter(Mandatory=$false)][switch]$Restore,
    [Parameter(Mandatory=$false)][switch]$Daemon
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
$installScript = Join-Path $scriptDir "install.ps1"

function Show-Menu {
    Clear-Host
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "          Claude Desktop 中文汉化管理面板 (Elite Toolkit)              " -ForegroundColor Yellow
    Write-Host "          永久自愈 · 零依赖原生注入 · 20000+ 词条全量覆盖             " -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. [Install/Update] 一键安装 / 更新中文语言包 (Install Patch)" -ForegroundColor Green
    Write-Host "  2. [Check Status]   环境与健康状态诊断 (Health Diagnostics)" -ForegroundColor Blue
    Write-Host "  3. [Toggle Daemon]  开启 / 关闭后台自动守护 (Auto-Healing Daemon)" -ForegroundColor Magenta
    Write-Host "  4. [Restore Backup] 一键恢复官方原版英文 (One-Click Rollback)" -ForegroundColor Yellow
    Write-Host "  5. [Exit]           退出控制台 (Exit)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Cyan
    $choice = Read-Host "请输入选项 [1-5]"

    switch ($choice) {
        "1" { powershell -ExecutionPolicy Bypass -File $installScript; Pause }
        "2" { powershell -ExecutionPolicy Bypass -File $installScript -Check; Pause }
        "3" {
            $cur = powershell -ExecutionPolicy Bypass -File $installScript -Daemon status
            $target = if ($LASTEXITCODE -eq 0) { "disable" } else { "enable" }
            powershell -ExecutionPolicy Bypass -File $installScript -Daemon $target
            Write-Host "守护状态已切换为: $target" -ForegroundColor Green
            Pause
        }
        "4" { powershell -ExecutionPolicy Bypass -File $installScript -Restore; Pause }
        "5" { exit 0 }
        default { Show-Menu }
    }
    Show-Menu
}

Show-Menu
