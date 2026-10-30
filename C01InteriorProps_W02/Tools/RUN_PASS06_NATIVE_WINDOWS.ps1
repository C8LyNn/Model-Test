# C01-17 PASS06 — run on owner's Windows desktop WITH Blender 4.x and Git LFS.
# Does not commit, push or merge. Fails closed on any source SHA mismatch.
param([string]$BlenderExe = "", [string]$Repo = "")
$ErrorActionPreference = "Stop"
if (-not $Repo) { $Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path }
$Repo = (Resolve-Path $Repo).Path
if (-not $BlenderExe) {
  $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
  if ($cmd) { $BlenderExe = $cmd.Source }
}
if (-not $BlenderExe) {
  $candidates = @(
    "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
  )
  $BlenderExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { throw "NEEDS_OWNER_ACTION: install Blender 4.x or pass -BlenderExe path" }
Push-Location $Repo
try {
  $branch = (& git branch --show-current).Trim()
  if ($LASTEXITCODE -ne 0 -or $branch -ne "c01/props-17-wave02") { throw "Wrong branch: $branch. Must use existing Draft PR #23" }
  $dirty = & git status --porcelain
  if ($LASTEXITCODE -ne 0 -or $dirty) { throw "Working tree must be clean before binary overwrite; safeguard user edits." }
  & git lfs version
  if ($LASTEXITCODE -ne 0) { throw "NEEDS_OWNER_ACTION: Git LFS missing" }
  & git lfs pull --include="C01InteriorProps_W02/Blender/P17-05.blend,Assets/C01InteriorProps/W02/Models/P17-05.fbx"
  if ($LASTEXITCODE -ne 0) { throw "Git LFS hydration failed. No Blender execution." }
  & $BlenderExe --version
  if ($LASTEXITCODE -ne 0) { throw "Blender version command failed" }
  $source = Join-Path $Repo "C01InteriorProps_W02\Tools\pass06_native_p1705.py"
  & $BlenderExe -b -t 2 --factory-startup --python-exit-code 1 --python $source -- $Repo
  if ($LASTEXITCODE -ne 0) { throw "FAIL: native Blender source/FBX repair or roundtrip, do not commit!" }
  $roundtrip = Join-Path $Repo "C01InteriorProps_W02\Tools\fbx_roundtrip.py"
  & $BlenderExe -b -t 2 --factory-startup --python-exit-code 1 --python $roundtrip -- $Repo
  if ($LASTEXITCODE -ne 0) { throw "FAIL: independent reimport of all 4 W02 FBX" }
  $result = Join-Path $Repo "C01InteriorProps_W02\QA\PASS06\P17-05_NATIVE_REPAIR_RESULT.json"
  if (-not (Test-Path $result)) { throw "Missing actual generated native result JSON" }
  $r = Get-Content $result -Raw | ConvertFrom-Json
  if ($r.blender_source -ne "PASS" -or $r.fbx_roundtrip -ne "PASS") { throw "PASS06 native validation failed" }
  Write-Host "SUCCESS: real Blender repaired and reimported P17-05 source+FBX"
  Write-Host "BLEND AFTER SHA256: $($r.source_after_blend_sha256)"
  Write-Host "FBX AFTER SHA256: $($r.fbx_after_sha256)"
  & git status --short
  Write-Host "IMPORTANT: NO automatic Git commit/push, and NO QA self-approval. Review real images and results, then commit only on existing PR #23."
} finally { Pop-Location }
