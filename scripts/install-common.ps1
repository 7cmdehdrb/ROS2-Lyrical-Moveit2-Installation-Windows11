function Assert-InstallHost {
    if ($env:OS -ne 'Windows_NT' -or ![Environment]::Is64BitProcess -or $env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
        throw 'Use 64-bit PowerShell on Windows 11 x64.'
    }
    $OsInfo = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
    if ([int]$OsInfo.CurrentBuildNumber -lt 22000 -or $OsInfo.InstallationType -ne 'Client') {
        throw 'Windows 11 x64 is required.'
    }
    if ($env:ROS_DISTRO -or $env:CONDA_PREFIX -or $env:VIRTUAL_ENV) {
        throw 'Open a fresh PowerShell without ROS, Conda, or a Python virtual environment activated.'
    }
    if ($ProjectRoot -match '[\s!%&^()\x27]') {
        throw 'Use a short project path without spaces or shell metacharacters, e.g. C:\python_ws\ros2.'
    }
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
}

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Executable $($Arguments -join ' ')" }
}

function Get-VerifiedDownload {
    param([string]$Url, [string]$Sha256)
    $Directory = Join-Path $ProjectRoot 'downloads'
    New-Item -ItemType Directory -Force -Path $Directory | Out-Null
    $Destination = Join-Path $Directory ([IO.Path]::GetFileName(([Uri]$Url).AbsolutePath))
    if (Test-Path -LiteralPath $Destination) {
        if ((Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash -ne $Sha256) {
            throw "Checksum mismatch: $Destination. Remove this file and rerun; it was not used."
        }
        Write-Host "Verified cached download: $Destination"
        return $Destination
    }
    $Partial = "$Destination.partial"
    Write-Host "Downloading $Url"
    # Windows 11 includes curl.exe. Retries replace the partial file; no global cache.
    Invoke-Checked "$env:SystemRoot\System32\curl.exe" @('--fail', '--location', '--retry', '3', '--connect-timeout', '30', '--output', $Partial, $Url)
    if ((Get-FileHash -LiteralPath $Partial -Algorithm SHA256).Hash -ne $Sha256) {
        throw "Checksum mismatch: $Partial. The download was not extracted."
    }
    Move-Item -LiteralPath $Partial -Destination $Destination
    return $Destination
}

function Expand-ProjectArchive {
    param([string]$ArchivePath)
    # A unique staging folder allows a failed extraction to be retried safely.
    $Stage = Join-Path $ProjectRoot ('tmp\extract-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Stage | Out-Null
    # Windows' bundled bsdtar reads ZIPs and avoids very slow per-file extraction
    # observed with .NET ZipFile on Windows PowerShell 5.1.
    Invoke-Checked "$env:SystemRoot\System32\tar.exe" @('-xf', $ArchivePath, '-C', $Stage)
    return $Stage
}

function Move-ProjectDirectory {
    param([string]$Source, [string]$Destination)
    $Boundary = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\') + '\'
    foreach ($Candidate in @($Source, $Destination)) {
        $Resolved = [IO.Path]::GetFullPath($Candidate)
        if (!$Resolved.StartsWith($Boundary, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Directory move outside project refused: $Resolved"
        }
        if ((Test-Path -LiteralPath $Resolved) -and ((Get-Item -LiteralPath $Resolved).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Directory move through a reparse point refused: $Resolved"
        }
    }
    if (Test-Path -LiteralPath $Destination) { throw "Destination already exists: $Destination" }
    Move-Item -LiteralPath $Source -Destination $Destination
}

function Install-ProjectPixi {
    param($Source)
    $Zip = Get-VerifiedDownload $Source.url $Source.sha256
    $Exe = Join-Path $ProjectRoot 'tools\pixi\pixi.exe'
    if (!(Test-Path -LiteralPath $Exe)) {
        $Stage = Expand-ProjectArchive $Zip
        New-Item -ItemType Directory -Force -Path (Split-Path $Exe -Parent) | Out-Null
        Copy-Item -LiteralPath "$Stage\pixi.exe" -Destination $Exe
    }
    $Version = & $Exe --version
    if ($LASTEXITCODE -ne 0 -or $Version.Trim() -ne "pixi $($Source.version)") {
        throw "Expected Pixi $($Source.version), found: $Version. Use a clean tools\pixi directory."
    }
    Write-Host "Using $Version"
    return $Exe
}

function Install-OfficialRos {
    param($Source, [string]$PixiExe)
    $Zip = Get-VerifiedDownload $Source.url $Source.sha256
    $Target = Join-Path $ProjectRoot 'lyrical'
    if (!(Test-Path -LiteralPath $Target)) {
        Write-Host 'Extracting official ROS 2 binaries...'
        $Stage = Expand-ProjectArchive $Zip
        Move-ProjectDirectory (Join-Path $Stage $Source.archive_root) $Target
    }
    # Check even an existing installation against the pinned archive before reuse.
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Archive = [IO.Compression.ZipFile]::OpenRead($Zip)
    try {
        foreach ($Name in @('pixi.toml', 'pixi.lock')) {
            $Entry = $Archive.GetEntry("$($Source.archive_root)/$Name")
            if ($null -eq $Entry -or !(Test-Path -LiteralPath "$Target\$Name")) {
                throw "Incomplete ROS installation: $Target. Preserve it separately and rerun."
            }
            $Stream = $Entry.Open()
            $HashAlgorithm = [Security.Cryptography.SHA256]::Create()
            try { $Expected = [BitConverter]::ToString($HashAlgorithm.ComputeHash($Stream)).Replace('-', '') }
            finally { $Stream.Dispose(); $HashAlgorithm.Dispose() }
            if ((Get-FileHash -LiteralPath "$Target\$Name" -Algorithm SHA256).Hash -ne $Expected) {
                throw "Existing $Target\$Name differs from the pinned release; it will not be overwritten."
            }
        }
    } finally { $Archive.Dispose() }
    Invoke-Checked $PixiExe @('install', '--locked', '--manifest-path', "$Target\pixi.toml")
    Push-Location $Target
    try { Invoke-Checked $PixiExe @('run', '--locked', 'python', 'preinstall_setup_windows.py') }
    finally { Pop-Location }
}

function Invoke-ActivatedPython {
    param([string]$Activation, [string]$Script, [string[]]$Arguments = @())
    # Paths are validated above; only internal, fixed script names/flags are accepted.
    $Command = 'call "{0}\{1}" && python "{0}\{2}" {3}' -f $ProjectRoot, $Activation, $Script, ($Arguments -join ' ')
    Invoke-Checked $env:ComSpec @('/d', '/c', $Command)
}
