#Requires -Version 5.1
# Regression checks for the mandatory pre-download gate; no network or install.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProjectRoot = Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot\install-common.ps1"

function Assert-True($Condition, [string]$Message) {
    if (!$Condition) { throw $Message }
}

$Valid = @{
    version = @(3, 12, 3); releaselevel = 'final'; implementation = 'CPython'
    bits = 64; machine = 'AMD64'; platform = 'win32'; executable = 'test-python.exe'
}
Assert-True (Test-CompatiblePython ([pscustomobject]$Valid)) '3.12.3 x64 must pass.'
$NewPatch = $Valid.Clone()
$NewPatch.version = @(3, 12, 12)
Assert-True (Test-CompatiblePython ([pscustomobject]$NewPatch)) 'Newer 3.12 patch must pass.'
Assert-True (!(Test-CompatiblePython $null)) 'Missing Python must fail.'
foreach ($Change in @(
    @{version = @(3, 11, 9)}, @{version = @(3, 12, 2)},
    @{version = @(3, 13, 0)}, @{version = @(3, 14, 8)},
    @{bits = 32}, @{machine = 'ARM64'}, @{implementation = 'PyPy'},
    @{platform = 'linux'}, @{releaselevel = 'candidate'}
)) {
    $Invalid = $Valid.Clone()
    foreach ($Key in $Change.Keys) { $Invalid[$Key] = $Change[$Key] }
    Assert-True (!(Test-CompatiblePython ([pscustomobject]$Invalid))) "Must reject $($Change | ConvertTo-Json -Compress)"
}

# Exercise real native argument quoting, including under Windows PowerShell 5.1.
$Python = Get-Command python.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if ($Python -and $Python.Source -notlike '*\Microsoft\WindowsApps\*') {
    Assert-True ($null -ne (Invoke-PythonProbe $Python.Source)) 'Python probe failed to return JSON.'
}

# A successful probe must preserve launcher settings and return the exact selection.
$OriginalProbe = ${function:Invoke-PythonProbe}
try {
    function Invoke-PythonProbe {
        param([string]$Executable, [string[]]$PrefixArguments)
        Assert-True ($Executable -eq 'selected-python.exe') 'Explicit selection was replaced.'
        Assert-True (!$env:PYLAUNCHER_ALLOW_INSTALL) 'Launcher install must be disabled.'
        Assert-True ($env:PYTHON_MANAGER_AUTOMATIC_INSTALL -eq 'false') 'Manager install must be disabled.'
        return [pscustomobject]$Valid
    }
    $Before = @($env:PYLAUNCHER_ALLOW_INSTALL, $env:PYTHON_MANAGER_AUTOMATIC_INSTALL)
    $Result = Assert-CompatiblePython 'selected-python.exe'
    Assert-True ($Result.executable -eq $Valid.executable) 'Accepted Python metadata missing.'
    Assert-True ($env:PYLAUNCHER_ALLOW_INSTALL -eq $Before[0]) 'Launcher setting was not restored.'
    Assert-True ($env:PYTHON_MANAGER_AUTOMATIC_INSTALL -eq $Before[1]) 'Manager setting was not restored.'
} finally { ${function:Invoke-PythonProbe} = $OriginalProbe }

# Install into a new isolated fixture, so any accidental download/setup is observable.
$Fixture = Join-Path $ProjectRoot ('tmp\python-gate-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path "$Fixture\scripts" -Force | Out-Null
Copy-Item -LiteralPath "$ProjectRoot\install.ps1" -Destination "$Fixture\install.ps1"
Copy-Item -LiteralPath "$PSScriptRoot\install-common.ps1" -Destination "$Fixture\scripts\install-common.ps1"
$OriginalEnvironment = @{}
foreach ($Name in @('ROS_DISTRO', 'CONDA_PREFIX', 'VIRTUAL_ENV')) {
    $OriginalEnvironment[$Name] = [Environment]::GetEnvironmentVariable($Name, 'Process')
    [Environment]::SetEnvironmentVariable($Name, $null, 'Process')
}
try {
    foreach ($Component in @('ROS2', 'MoveIt', 'All')) {
        try {
            $ErrorActionPreference = 'Continue' # Expected native stderr is data in PS 5.1.
            $Output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Fixture\install.ps1" -Component $Component -SkipVerification -PythonExecutable "$Fixture\missing-python.exe" 2>&1 | Out-String
        } finally { $ErrorActionPreference = 'Stop' }
        Assert-True ($LASTEXITCODE -eq 1) "$Component must exit 1. $Output"
        Assert-True ($Output -match 'Required Python is missing or incompatible') "$Component did not fail at Python gate. $Output"
        Assert-True ($Output -match 'https://www.python.org/downloads/release/python-3123/') 'Installation guidance missing.'
    }
} finally {
    foreach ($Name in $OriginalEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($Name, $OriginalEnvironment[$Name], 'Process')
    }
}
foreach ($Directory in @('downloads', 'tools', '.cache', 'lyrical', 'moveit', 'logs')) {
    Assert-True (!(Test-Path -LiteralPath "$Fixture\$Directory")) "Preflight created $Directory."
}
Write-Host 'PASS: Python acceptance/rejection, explicit selection, launcher settings and all installer modes before downloads.'
