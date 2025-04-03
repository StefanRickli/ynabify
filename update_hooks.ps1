Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

get-command hatch > $null
hatch run pre-commit autoupdate
