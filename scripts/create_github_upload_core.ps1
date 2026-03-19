Param(
    [string]$OutputDir = "github-upload-core"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path ".").Path
$outPath = Join-Path $root $OutputDir

if (Test-Path $outPath) {
    Remove-Item $outPath -Recurse -Force
}
New-Item -ItemType Directory -Path $outPath | Out-Null

# Include only core source/docs folders for a minimal public repo.
$includeDirs = @(
    ".github",
    "config",
    "core",
    "docs",
    "jessica",
    "memory",
    "scripts",
    "tests",
    "tools"
)

# Exclude generated/heavy content even inside included folders.
$excludeDirs = @(
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".vscode",
    "logs",
    "llama.cpp",
    "Voice",
    "jessica_data_embeddings",
    "node_modules",
    "build",
    "dist",
    "archive"
)

$excludeFiles = @(
    ".env",
    ".jessica_consent.json",
    "jessica_data.db",
    "jessica_robot_memory.db",
    "user_profile.db",
    "memory.json",
    "jessica_memory.json",
    "jessica_schedule.json",
    "jessica_world_state.json",
    "*.pyc",
    "*.pyo",
    "*.bak",
    "*.bak.bak",
    "run_output*.txt",
    "demo_output*.txt",
    "demo_out*.txt",
    "autodidactic_report.txt"
)

foreach ($dir in $includeDirs) {
    $src = Join-Path $root $dir
    if (-not (Test-Path $src)) {
        continue
    }

    $dst = Join-Path $outPath $dir
    New-Item -ItemType Directory -Path $dst -Force | Out-Null

    $args = @(
        $src,
        $dst,
        "/E",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/NP",
        "/XD"
    ) + $excludeDirs + @("/XF") + $excludeFiles

    robocopy @args | Out-Null
    if ($LASTEXITCODE -ge 8) {
        throw "robocopy failed while copying $dir (exit code $LASTEXITCODE)"
    }
}

# Include key top-level files needed to run and understand the project.
$includeFiles = @(
    ".gitignore",
    "README.md",
    "START_HERE.md",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-optional.txt",
    "run_jessica.py",
    "main.py",
    "config.py",
    "build_llama_cpp_windows.ps1",
    "pytest.ini"
)

foreach ($file in $includeFiles) {
    $srcFile = Join-Path $root $file
    if (Test-Path $srcFile) {
        Copy-Item $srcFile (Join-Path $outPath $file) -Force
    }
}

# Remove any nested cache/build dirs that slipped in.
Get-ChildItem $outPath -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @("node_modules", "build", "dist", "__pycache__", ".pytest_cache") } |
    Remove-Item -Recurse -Force

$sizeMB = [math]::Round(((Get-ChildItem $outPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum) / 1MB, 2)
$fileCount = (Get-ChildItem $outPath -Recurse -File -ErrorAction SilentlyContinue).Count
Write-Host "Created $OutputDir ($sizeMB MB, $fileCount files)"
