Param(
  [ValidateSet('Release','Debug')] [string]$Config = 'Release'
)

$ErrorActionPreference = 'Stop'

$Root = $PSScriptRoot
$LlamaDir = Join-Path $Root 'llama.cpp'
$BuildDir = Join-Path $LlamaDir 'build'

Write-Host "Building llama.cpp in $BuildDir ($Config)..."

if (-not (Test-Path $LlamaDir)) {
  throw "llama.cpp folder not found at: $LlamaDir"
}

if (-not (Test-Path $BuildDir)) {
  New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

# If this build folder was generated from a different absolute path, CMake will error.
# Clear the cache so we can reconfigure cleanly.
$cacheFile = Join-Path $BuildDir 'CMakeCache.txt'
if (Test-Path $cacheFile) {
  $cacheText = Get-Content $cacheFile -ErrorAction SilentlyContinue | Out-String
  if ($cacheText -and ($cacheText -match 'CMAKE_HOME_DIRECTORY') -and ($cacheText -notmatch [regex]::Escape($LlamaDir))) {
    Write-Warning "Stale CMake cache detected (different source path). Clearing $BuildDir ..."
    Remove-Item -LiteralPath $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
  }
}

Push-Location $BuildDir
try {
  # Disable CURL by default to avoid needing libcurl dev packages on Windows.
  cmake .. -DLLAMA_CURL=OFF
  cmake --build . --config $Config

  $binDir = Join-Path -Path $BuildDir -ChildPath 'bin'
  $exe1 = Join-Path -Path $binDir -ChildPath $Config
  $candidates = @(
    (Join-Path -Path $exe1 -ChildPath 'llama-cli.exe')
    (Join-Path -Path $exe1 -ChildPath 'main.exe')
    (Join-Path -Path $binDir -ChildPath 'llama-cli.exe')
    (Join-Path -Path $binDir -ChildPath 'main.exe')
  )

  $found = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($found) {
    Write-Host "OK: Found llama executable at: $found"
  } else {
    Write-Warning "Build finished but no llama-cli.exe/main.exe found under $binDir. Your llama.cpp version may use different binary names."
  }
} finally {
  Pop-Location
}
