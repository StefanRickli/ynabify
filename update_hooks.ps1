Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

get-command hatch > $null
hatch env run pre-commit autoupdate
