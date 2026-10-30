param(
    [Parameter(Mandatory = $true)]
    [string]$BlenderExecutable
)
$ErrorActionPreference = 'Stop'
$SourceRoot = Split-Path -Parent $PSScriptRoot
$ScriptFile = Join-Path $PSScriptRoot 'ci_pass04_native.py'
$ObjDirectory = Join-Path $SourceRoot 'OBJ'
$BlenderDirectory = Join-Path $SourceRoot 'Blender'
$FBXDirectory = Join-Path $SourceRoot 'FBX'
if (-not (Test-Path -LiteralPath $BlenderExecutable -PathType Leaf)) { throw "Blender executable not found: $BlenderExecutable" }
if (-not (Test-Path -LiteralPath $ScriptFile)) { throw "Missing actual Blender runner" }
$Assets = @(Get-ChildItem -LiteralPath $ObjDirectory -Filter 'P16-*.obj' -File | ForEach-Object { $_.BaseName } | Sort-Object)
$Expected = if ($SourceRoot -match 'LightingW02$') { @('P16-04','P16-05','P16-06','P16-07') } else { @('P16-01','P16-02','P16-03') }
if (@(Compare-Object $Assets $Expected).Count -ne 0) { throw "Unexpected source asset list: $($Assets -join ',')" }
& $BlenderExecutable --version
if ($LASTEXITCODE -ne 0) { throw 'Blender binary failed version check' }
foreach ($Asset in $Expected) {
    Write-Host "C01-16: native Blender import/FBX roundtrip $Asset"
    & $BlenderExecutable -b --factory-startup --python-exit-code 1 --python $ScriptFile -- $Asset
    if ($LASTEXITCODE -ne 0) { throw "Actual Blender test FAILED for $Asset ($LASTEXITCODE)" }
    $Blend = Join-Path $BlenderDirectory "$Asset.blend"
    $FBX = Join-Path $FBXDirectory "$Asset.fbx"
    $ReportFile = Join-Path (Join-Path $PSScriptRoot $Asset) 'blender_binary_fbx_roundtrip.json'
    if (-not (Test-Path -LiteralPath $Blend)) { throw "Missing native .blend for $Asset" }
    if (-not (Test-Path -LiteralPath $FBX)) { throw "Missing binary FBX for $Asset" }
    if (-not (Test-Path -LiteralPath $ReportFile)) { throw "Missing Blender roundtrip QA for $Asset" }
    $BlendBytes = [System.IO.File]::ReadAllBytes($Blend)
    $FBXBytes = [System.IO.File]::ReadAllBytes($FBX)
    $BlendMagic = [System.Text.Encoding]::ASCII.GetString($BlendBytes,0,[Math]::Min(7,$BlendBytes.Length))
    $FBXMagic = [System.Text.Encoding]::ASCII.GetString($FBXBytes,0,[Math]::Min(18,$FBXBytes.Length))
    if ($BlendMagic -ne 'BLENDER-') { throw "$Asset source is not a native Blender file" }
    if (-not $FBXMagic.StartsWith('Kaydara FBX Binary')) { throw "$Asset file is not a binary FBX" }
    $Report = Get-Content -LiteralPath $ReportFile -Raw | ConvertFrom-Json
    if ($Report.result -ne 'PASS') { throw "$Asset roundtrip is not PASS" }
    if ((Get-FileHash -LiteralPath $Blend -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Report.blend_sha256) { throw "BLEND SHA256 mismatch for $Asset" }
    if ((Get-FileHash -LiteralPath $FBX -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Report.binary_fbx_sha256) { throw "FBX SHA256 mismatch for $Asset" }
    Write-Host ("VERIFIED {0}: blender={1}, binaryFBX={2}" -f $Asset,$Report.blend_sha256,$Report.binary_fbx_sha256)
}
Write-Host "BLENDER SOURCE AND BINARY FBX ALL $($Expected.Count) PASS. Unity and independent QA NOT RUN."
