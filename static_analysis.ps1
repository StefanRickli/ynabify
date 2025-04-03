Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

get-command hatch > $null

$ErrorActionPreference = "Continue"

hatch fmt
hatch run types:check
