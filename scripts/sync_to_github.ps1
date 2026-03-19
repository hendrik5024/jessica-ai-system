<#
.SYNOPSIS
    Syncs the cleaned Jessica AI source to your local GitHub repo folder and pushes.

.USAGE
    From Jessica_clean root:
        .\scripts\sync_to_github.ps1

    With a custom commit message:
        .\scripts\sync_to_github.ps1 -Message "Add new skill"
#>

Param(
    [string]$Source  = "C:\Users\hendr\Documents\Jessica_clean",
    [string]$Target  = "C:\Users\hendr\OneDrive\Documents\GitHub\jessica-ai-system",
    [string]$Message = ""
)

if (-not $Message) {
    $Message = "Sync Jessica AI core - " + (Get-Date -Format 'yyyy-MM-dd HH:mm')
}

$ErrorActionPreference = "Stop"

# --- 1. Validate paths ---
if (-not (Test-Path $Source)) { throw "Source not found: $Source" }
if (-not (Test-Path $Target)) { throw "Target not found: $Target" }

Write-Host "`n[1/4] Source : $Source"
Write-Host "      Target : $Target"

# --- 2. Build a temp clean bundle from the source ---
Write-Host "`n[2/4] Building clean bundle..."

$tmpBundle = Join-Path $env:TEMP "jessica_sync_bundle"
if (Test-Path $tmpBundle) { Remove-Item $tmpBundle -Recurse -Force }
New-Item -ItemType Directory -Path $tmpBundle | Out-Null

# Folders to include in the GitHub repo.
$includeDirs = @(
    ".github", "config", "core", "docs", "jessica",
    "memory", "scripts", "tests", "tools"
)

# Directories to always exclude (even inside included folders).
$excludeDirs = @(
    ".venv", ".pytest_cache", "__pycache__", ".vscode",
    "logs", "llama.cpp", "Voice", "jessica_data_embeddings",
    "node_modules", "build", "dist", "archive",
    "github-upload", "github-upload-core"
)

# Individual files to exclude.
$excludeFiles = @(
    ".env", ".jessica_consent.json",
    "jessica_data.db", "jessica_robot_memory.db",
    "user_profile.db", "memory.json", "jessica_memory.json",
    "jessica_schedule.json", "jessica_world_state.json",
    "*.pyc", "*.pyo", "*.bak", "*.bak.bak",
    "run_output*.txt", "demo_output*.txt", "demo_out*.txt",
    "autodidactic_report.txt"
)

foreach ($dir in $includeDirs) {
    $src = Join-Path $Source $dir
    if (-not (Test-Path $src)) { continue }
    $dst = Join-Path $tmpBundle $dir
    New-Item -ItemType Directory -Path $dst -Force | Out-Null
    $rcArgs = @($src, $dst, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP", "/XD") `
              + $excludeDirs + @("/XF") + $excludeFiles
    robocopy @rcArgs | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed for $dir (exit $LASTEXITCODE)" }
}

# Key top-level root files.
$includeFiles = @(
    ".gitignore", "README.md", "START_HERE.md",
    "requirements.txt", "requirements-dev.txt", "requirements-optional.txt",
    "run_jessica.py", "main.py", "config.py",
    "build_llama_cpp_windows.ps1", "pytest.ini"
)
foreach ($f in $includeFiles) {
    $sf = Join-Path $Source $f
    if (Test-Path $sf) { Copy-Item $sf (Join-Path $tmpBundle $f) -Force }
}

# Remove any nested cache/build dirs that slipped in.
Get-ChildItem $tmpBundle -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @("node_modules","build","dist","__pycache__",".pytest_cache") } |
    Remove-Item -Recurse -Force

$bundleMB = [math]::Round(((Get-ChildItem $tmpBundle -Recurse -File | Measure-Object Length -Sum).Sum)/1MB,2)
Write-Host "      Bundle  : $bundleMB MB"

# --- 3. Mirror bundle into target repo (preserve .git) ---
Write-Host "`n[3/4] Mirroring into target repo..."

# Delete everything in target except .git and LICENSE.
Get-ChildItem $Target -Force |
    Where-Object { $_.Name -notin @('.git','LICENSE') } |
    Remove-Item -Recurse -Force

# Copy bundle into target.
$rcArgs2 = @($tmpBundle, $Target, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP")
robocopy @rcArgs2 | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy mirror failed (exit $LASTEXITCODE)" }

Remove-Item $tmpBundle -Recurse -Force

# --- 4. Commit and push ---
Write-Host "`n[4/4] Committing and pushing..."
Set-Location $Target

git add -A

$changed = (git status --porcelain)
if (-not $changed) {
    Write-Host "      Nothing changed - already in sync."
} else {
    $numChanged = ($changed | Measure-Object).Count
    Write-Host "      Changed files: $numChanged"
    git commit -m $Message
    git push origin main
    Write-Host "      Pushed to origin/main."
}

Write-Host ""; Write-Host "Done! Repo at: $Target"; Write-Host ""
