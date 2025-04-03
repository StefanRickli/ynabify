Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

get-command hatch > $null

hatch fmt
hatch env run types:check
