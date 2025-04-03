Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

get-command hatch > $null

$ErrorActionPreference = "Continue"

hatch run pre-commit run --all-files
hatch run types:check
