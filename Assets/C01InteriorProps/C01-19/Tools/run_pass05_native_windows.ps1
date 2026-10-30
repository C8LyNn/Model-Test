param(
  [ValidateSet('W01','W02')][string]$Wave='W02',
  [string]$BlenderPath='blender.exe',
  [string]$RepoPath=(Get-Location).Path,
  [switch]$Push
)
$ErrorActionPreference='Stop'
$branch=if($Wave -eq 'W01'){'c01/props-19-furniture'}else{'c01/props-19-furniture-wave02'}
$rel=if($Wave -eq 'W01'){'Assets/C01InteriorProps/C01-19'}else{'Assets/C01InteriorProps/C01-19-W02'}
Push-Location $RepoPath
try {
  $active=(git branch --show-current).Trim()
  if($LASTEXITCODE -ne 0 -or $active -ne $branch){throw "Wrong branch: expected $branch got $active"}
  git lfs pull
  if($LASTEXITCODE -ne 0){throw "git lfs pull failed"}
  $src=Join-Path $RepoPath ($rel+'/Source/pass04_triangulate.py')
  if(-not (Test-Path $src)){throw "Missing Blender native source script $src"}
  & $BlenderPath --version
  if($LASTEXITCODE -ne 0){throw "Blender 4.x unavailable"}
  & $BlenderPath -b --factory-startup --python-exit-code 1 --python $src
  if($LASTEXITCODE -ne 0){throw "Native Blender triangulation failed, DO NOT COMMIT"}
  $root=Join-Path $RepoPath $rel
  $summary=Get-Content (Join-Path $root 'QA/PASS04/SUMMARY.json') -Raw | ConvertFrom-Json
  if(@($summary.models).Count -ne 4){throw "Four real mesh reports required"}
  foreach($m in $summary.models){
    if($m.fbx_roundtrip.status -ne 'PASS' -or $m.after.degenerate_triangles -ne 0){
      throw "Model $($m.id) failed Blender source/FBX verification"
    }
    $f=Join-Path $root "Models/$($m.id)/$($m.id).fbx"
    $b=Join-Path $root "Models/$($m.id)/$($m.id).blend"
    $magic=[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($f),0,21)
    $bmagic=[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($b),0,7)
    if(-not $magic.StartsWith('Kaydara FBX Binary') -or $bmagic -ne 'BLENDER'){throw "Invalid native binaries $($m.id)"}
    Write-Host "VALIDATED $($m.id) FBX SHA256=$((Get-FileHash $f -Algorithm SHA256).Hash)"
  }
  if($Push){
    git add -- "$rel/Models" "$rel/QA/PASS04"
    if($LASTEXITCODE -ne 0){throw "git add failed"}
    git commit -m "fix(C01-19 PASS05): native Blender triangulation $Wave"
    if($LASTEXITCODE -ne 0){throw "git commit failed"}
    git push origin "HEAD:$branch"
    if($LASTEXITCODE -ne 0){throw "Push rejected; do not force-push"}
  } else {
    Write-Host 'Real native sources validated locally; run again with -Push to update existing draft PR.'
  }
} finally {Pop-Location}
