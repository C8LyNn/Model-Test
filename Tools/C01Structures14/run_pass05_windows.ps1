# C01-14 PASS05 — offline native Blender fallback for Windows
# Requires checked-out Model-Test branch and Blender 4.x; NEVER mutates mesh sources.
param(
  [Parameter(Mandatory=$true)][string] $BlenderExe,
  [string] $PythonExe = "python"
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
function Assert-LastExit([string]$label) {
  if ($LASTEXITCODE -ne 0) { throw "$label failed with exit code $LASTEXITCODE" }
}
if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
  throw "Blender 4.x executable not found: $BlenderExe"
}
$repo = (git rev-parse --show-toplevel).Trim()
Assert-LastExit "git rev-parse"
Set-Location -LiteralPath $repo
$branch = (git branch --show-current).Trim()
Assert-LastExit "git branch"
if ($branch -ne "c01/structures-14-prototypes-w02") {
  throw "Wrong branch: $branch (must be c01/structures-14-prototypes-w02)"
}
& $BlenderExe --background --python-expr "import bpy; assert bpy.app.version >= (4,0,0); print('PASS real Blender:',bpy.app.version_string)"
Assert-LastExit "Blender version check"
& git lfs pull
Assert-LastExit "git lfs pull"
$srcDir = Join-Path $repo "Assets/C01StructuralPrototypes/P14/Pass03"
$tmp = Join-Path $env:TEMP "C01_14_PASS05_SHA_PINNED"
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
foreach ($id in @("RMP-01","RAI-01")) {
  Copy-Item -LiteralPath (Join-Path $srcDir ("Sources/C01_14_" + $id + "_v002.blend")) -Destination $tmp -Force
  Copy-Item -LiteralPath (Join-Path $srcDir ("FBX/C01_14_" + $id + "_v002.fbx")) -Destination $tmp -Force
}
$dest = Join-Path $repo "Assets/C01StructuralPrototypes/P14/Pass05"
New-Item -ItemType Directory -Path $dest -Force | Out-Null
& $PythonExe "Tools/C01Structures14/fbx_raw_pass05.py" $tmp (Join-Path $dest "QA_Windows_binary_fbx.json")
Assert-LastExit "Exact binary FBX check"
& $BlenderExe --background --python-exit-code 1 --python "Tools/C01Structures14/verify_pass04_exact_sources.py" -- --input $srcDir --out (Join-Path $dest "Native_Windows")
Assert-LastExit "Native Blender source + FBX import"
Write-Host "Local PASS05 outputs saved in: $dest"
Write-Host "Unity 6 URP and independent C01-02 QA: NOT RUN, require separate execution."
