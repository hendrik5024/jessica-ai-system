Param(
    [string]$OutputDir = "github-upload"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path ".").Path
$outPath = Join-Path $root $OutputDir

if (Test-Path $outPath) {
    Remove-Item $outPath -Recurse -Force
}
New-Item -ItemType Directory -Path $outPath | Out-Null

# Exclude heavy local/generated folders.
$excludeDirs = @(
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".vscode",
    "logs",
    "jessica_data_embeddings",
    "Voice",
    "llama.cpp",
    "node_modules",
    "build",
    "dist",
    "github-upload"
)

# Exclude local runtime files.
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

$robocopyArgs = @(
    $root,
    $outPath,
    "/E",
    "/NFL",
    "/NDL",
    "/NJH",
    "/NJS",
    "/NP",
    "/XD"
) + $excludeDirs + @("/XF") + $excludeFiles

robocopy @robocopyArgs | Out-Null

# Robocopy exit codes < 8 are success states.
if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE"
}

# Remove nested node_modules/build folders that may still appear in some layouts.
Get-ChildItem $outPath -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @("node_modules", "build", "dist", "__pycache__") } |
    Remove-Item -Recurse -Force

$sizeMB = [math]::Round(((Get-ChildItem $outPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum) / 1MB, 2)
Write-Host "Created $OutputDir ($sizeMB MB)"
