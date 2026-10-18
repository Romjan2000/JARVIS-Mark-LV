# ==============================================================================
# JARVIS Mark-LV : Windows Automated One-Click Installer
# ==============================================================================
$ErrorActionPreference = "Stop"

if (-not $InstallDir) { $InstallDir = "$HOME\JARVIS-Mark-LV" }
if (-not $RepoUrl) { $RepoUrl = "https://github.com/Romjan2000/JARVIS-Mark-LV.git" }

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   JARVIS MARK-LV : ONE-CLICK CROSS-PLATFORM INSTALLER    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Determine target directory
$IsLocalRepo = $false
if ((Test-Path ".\main.py") -and (Test-Path ".\setup.py")) {
    $WorkspaceDir = (Get-Location).Path
    $IsLocalRepo = $true
    Write-Host "[+] Running in current JARVIS directory: $WorkspaceDir" -ForegroundColor Green
} elseif ((Test-Path ".\Mark-IV\main.py") -and (Test-Path ".\Mark-IV\setup.py")) {
    $WorkspaceDir = (Join-Path (Get-Location).Path "Mark-IV")
    $IsLocalRepo = $true
    Write-Host "[+] Found JARVIS in Mark-IV folder: $WorkspaceDir" -ForegroundColor Green
} else {
    $WorkspaceDir = $InstallDir
    Write-Host "[i] Remote execution detected. Target directory: $WorkspaceDir" -ForegroundColor Yellow
}

# 2. Check Git if cloning is needed
if (-not $IsLocalRepo) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "[!] Git is not installed or not in PATH." -ForegroundColor Red
        Write-Host "    Please install Git from https://git-scm.com/download/win and re-run this command." -ForegroundColor Yellow
        exit 1
    }

    if (-not (Test-Path $WorkspaceDir)) {
        Write-Host "[*] Cloning JARVIS Mark-LV repository..." -ForegroundColor Cyan
        git clone $RepoUrl $WorkspaceDir
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[!] Failed to clone repository from $RepoUrl" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[+] Target directory already exists: $WorkspaceDir" -ForegroundColor Green
    }
}

Set-Location $WorkspaceDir

# 3. Detect and verify Python
Write-Host "[*] Detecting Python interpreter..." -ForegroundColor Cyan
$PythonExe = $null

$PyCandidates = @("py -3.12", "py -3.11", "py -3.13", "python", "py")
foreach ($cand in $PyCandidates) {
    try {
        $parts = $cand -split " "
        $cmd = $parts[0]
        $cmdArgs = if ($parts.Length -gt 1) { $parts[1..($parts.Length-1)] } else { @() }
        $verStr = & $cmd @cmdArgs -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($verStr -eq "3.11" -or $verStr -eq "3.12" -or $verStr -eq "3.13") {
            $PythonExe = $cand
            Write-Host "[+] Found supported Python ($verStr) via: $cand" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $PythonExe) {
    Write-Host "[!] Compatible Python (3.11, 3.12, or 3.13) was not found." -ForegroundColor Red
    Write-Host "    JARVIS requires Python 3.11, 3.12, or 3.13 on Windows." -ForegroundColor Yellow
    Write-Host "    Download Python 3.12: https://www.python.org/downloads/release/python-3128/" -ForegroundColor Yellow
    Write-Host "    *IMPORTANT*: Make sure to check 'Add python.exe to PATH' during installation!" -ForegroundColor Yellow
    exit 1
}

# 4. Create Virtual Environment
$VenvDir = Join-Path $WorkspaceDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[*] Creating isolated virtual environment in .venv..." -ForegroundColor Cyan
    $parts = $PythonExe -split " "
    $cmd = $parts[0]
    $cmdArgs = if ($parts.Length -gt 1) { $parts[1..($parts.Length-1)] } else { @() }
    & $cmd @cmdArgs -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "[+] Virtual environment created successfully." -ForegroundColor Green
} else {
    Write-Host "[+] Virtual environment (.venv) already present." -ForegroundColor Green
}

# 5. Upgrade pip and run setup.py
Write-Host "[*] Upgrading pip..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip --quiet

Write-Host "[*] Running JARVIS setup (installing dependencies and Playwright browsers)..." -ForegroundColor Cyan
& $VenvPython setup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Setup encountered an error while installing dependencies." -ForegroundColor Red
    Write-Host "    You can retry manually: .venv\Scripts\python.exe setup.py" -ForegroundColor Yellow
    exit 1
}

# 6. Create Desktop Shortcut
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [System.Environment]::GetFolderPath("Desktop")
    $ShortcutPath = Join-Path $DesktopPath "JARVIS Mark-LV.lnk"
    $BatchPath = Join-Path $WorkspaceDir "run_jarvis.bat"
    $IconPath = Join-Path $WorkspaceDir "config\jarvis.ico"

    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $BatchPath
    $Shortcut.WorkingDirectory = $WorkspaceDir
    if (Test-Path $IconPath) {
        $Shortcut.IconLocation = $IconPath
    }
    $Shortcut.Description = "JARVIS Mark-LV AI Assistant"
    $Shortcut.Save()
    Write-Host "[+] Desktop shortcut created: $ShortcutPath" -ForegroundColor Green
} catch {
    Write-Host "[i] Note: Could not create desktop shortcut (non-critical)." -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   [+] JARVIS MARK-LV SETUP FINISHED SUCCESSFULLY!        " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Launch commands:" -ForegroundColor Cyan
Write-Host "  Double click: run_jarvis.bat (or Desktop Shortcut)" -ForegroundColor White
Write-Host "  From Terminal: .venv\Scripts\python.exe main.py" -ForegroundColor White
Write-Host ""

if (-not $NoLaunch) {
    Write-Host "[*] Launching JARVIS Mark-LV..." -ForegroundColor Cyan
    & $VenvPython main.py
}
