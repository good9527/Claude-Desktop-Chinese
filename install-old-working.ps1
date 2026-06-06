# Legacy entry point kept for compatibility.

$ErrorActionPreference = "Stop"
$installer = Join-Path $PSScriptRoot "install.ps1"
if (-not (Test-Path -LiteralPath $installer)) {
    throw "install.ps1 was not found next to this legacy entry point."
}

& $installer
