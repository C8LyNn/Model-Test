# C01-10 W20: exact signed real-FBX + licensed Unity 6000.3.14f1 Windows runner.
# Default Preflight: NO Unity launched, NO prefab claim. Execute: actual Unity Editor tests.
# Never supplies, reads or logs Unity license secrets; activate ONLY in Unity Hub.
[CmdletBinding()]
param(
  [ValidateSet('Preflight','Execute')][string]$Mode = 'Preflight',
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$UnityExe = 'C:\Program Files\Unity\Hub\Editor\6000.3.14f1\Editor\Unity.exe',
  [string]$EvidenceDirectory = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$assets = @(
  [pscustomobject]@{ Id='P16-01'; Sha256='c0a782a17a0047e0d578a41e42ac714c0fa0f86c7c4960f4bc10e21a24a278fd'; Bytes=48380 },
  [pscustomobject]@{ Id='P17-02'; Sha256='db49121a520f16ca636626795550b83e8a4df94ded56a7ccb76308520bb7c3f6'; Bytes=77420 },
  [pscustomobject]@{ Id='P18-01'; Sha256='f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c'; Bytes=140460 }
)
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if ([string]::IsNullOrWhiteSpace($EvidenceDirectory)) {
  $EvidenceDirectory = Join-Path $ProjectRoot 'C01InteriorProps_QA\PASS20\WindowsUnity'
}
New-Item -ItemType Directory -Force -Path $EvidenceDirectory | Out-Null
$state = [ordered]@{
  schema = 'C01-10-PASS20-LICENSED-WINDOWS-UNITY-GATE-v1'
  mode = $Mode
  project = $ProjectRoot
  unity_version_required = '6000.3.14f1'
  unity_urp_version_required = '17.3.0'
  checked_inputs = @()
  physical_fbx_sha_pass = $false
  unity = 'UNITY_NOT_RUN'
  editmode = 'NOT_RUN'
  playmode = 'NOT_RUN'
  prefabs = 'NOT_RUN'
  scene = 'NOT_RUN'
  final_release = 'HOLD_INDEPENDENT_C01_02'
}

function Write-Receipt {
  $out = Join-Path $EvidenceDirectory 'C01_10_PASS20_ACTUAL_WINDOWS_RESULT.json'
  $state | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $out -Encoding utf8
  Write-Host ('Evidence: ' + $out)
}
function Require-TestRunXml([string]$Path, [string]$Name) {
  if (!(Test-Path -LiteralPath $Path)) { throw "$Name did not write a real Unity test-results XML" }
  [xml]$doc = Get-Content -LiteralPath $Path -Raw
  $root = $doc.DocumentElement
  if ($null -eq $root -or $root.Name -ne 'test-run') { throw "$Name XML root is not test-run" }
  $total = [int]$root.GetAttribute('total')
  $passed = [int]$root.GetAttribute('passed')
  $failed = [int]$root.GetAttribute('failed')
  $status = $root.GetAttribute('result')
  if ($total -lt 1 -or $passed -lt 1 -or $failed -ne 0 -or $status -ne 'Passed') {
    throw "$Name no successful Unity tests: total=$total passed=$passed failed=$failed result=$status"
  }
  return [ordered]@{result=$status;total=$total;passed=$passed;failed=$failed}
}

try {
  $versionFile = Join-Path $ProjectRoot 'ProjectSettings\ProjectVersion.txt'
  $packagesFile = Join-Path $ProjectRoot 'Packages\manifest.json'
  if (!(Test-Path $versionFile) -or !(Test-Path $packagesFile)) {
    throw 'Not a real Unity project root: missing ProjectSettings or Packages'
  }
  $version = Get-Content -LiteralPath $versionFile -Raw
  if ($version -notmatch '(?m)^m_EditorVersion: 6000\.3\.14f1\s*$') {
    throw 'Wrong Unity project version (requires 6000.3.14f1)'
  }
  $packages = Get-Content -LiteralPath $packagesFile -Raw | ConvertFrom-Json
  $urp = $packages.dependencies.'com.unity.render-pipelines.universal'
  if ($urp -ne '17.3.0') { throw "Wrong URP package version: $urp" }

  foreach($asset in $assets) {
    $file = Join-Path $ProjectRoot ("Assets\C01InteriorProps\Pass04Incoming\" + $asset.Id + "\" + $asset.Id + ".fbx")
    if (!(Test-Path -LiteralPath $file -PathType Leaf)) { throw ('Missing original hydrated FBX: '+$file) }
    $actualSize = (Get-Item -LiteralPath $file).Length
    if ($actualSize -ne $asset.Bytes) { throw ('Wrong FBX byte size: '+$asset.Id) }
    $reader = [System.IO.File]::OpenRead($file)
    try {
      $header = New-Object byte[] 18
      $read = $reader.Read($header,0,$header.Length)
    } finally { $reader.Dispose() }
    if ($read -ne 18 -or [Text.Encoding]::ASCII.GetString($header) -ne 'Kaydara FBX Binary') {
      throw ('Not an actual binary Blender FBX: ' + $asset.Id)
    }
    $digest = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $asset.Sha256) { throw ('Exact FBX SHA256 mismatch: ' + $asset.Id) }
    $state.checked_inputs += [ordered]@{
      id=$asset.Id;sha256=$digest;bytes=$actualSize;real_binary_fbx=$true
    }
  }
  $state.physical_fbx_sha_pass = $true
  Write-Host 'PASS20 WINDOWS PHYSICAL 3/3 FBX: FULL SHA256+MAGIC+SIZE PASS'

  if ($Mode -eq 'Preflight') {
    Write-Host 'Preflight verified. UNITY_NOT_RUN (intentional; no licensed Editor invoked).'
    Write-Receipt
    exit 0
  }

  if (!(Test-Path -LiteralPath $UnityExe -PathType Leaf)) {
    $state.unity = 'UNITY_NOT_RUN_EDITOR_NOT_INSTALLED'
    throw ('Unity 6000.3.14f1 Editor not installed: ' + $UnityExe)
  }

  $state.unity = 'UNITY_EDITOR_INVOCATION_STARTED'
  Write-Receipt
  $editXml = Join-Path $EvidenceDirectory 'EditMode-results.xml'
  $editLog = Join-Path $EvidenceDirectory 'EditMode-Editor.log'
  $playXml = Join-Path $EvidenceDirectory 'PlayMode-results.xml'
  $playLog = Join-Path $EvidenceDirectory 'PlayMode-Editor.log'

  $editArguments = @(
    '-batchmode','-quit','-projectPath',$ProjectRoot,
    '-runTests','-testPlatform','editmode',
    '-testFilter','C01.InteriorProps.Pass19.ThreeNativeEditModeTests',
    '-testResults',$editXml,'-logFile',$editLog
  )
  Write-Host 'RUNNING REAL Unity EditMode - license must already be active via Unity Hub'
  & $UnityExe @editArguments
  $editExit = $LASTEXITCODE
  if ($editExit -ne 0) { throw ('Unity EditMode process exit code '+$editExit) }
  $state.editmode = Require-TestRunXml $editXml 'EditMode'

  $prefabDir = Join-Path $ProjectRoot 'Assets\C01InteriorProps\Pass19\Resources\Pass19QA'
  foreach($asset in $assets) {
    if (!(Test-Path -LiteralPath (Join-Path $prefabDir ($asset.Id+'.prefab')) -PathType Leaf)) {
      throw ('REAL Unity prefab not persisted: '+$asset.Id)
    }
  }
  $scenePath = Join-Path $ProjectRoot 'Assets\C01InteriorProps\Pass19\Generated\Scenes\C01_PASS19_NATIVE_3FBX_QA_ONLY.unity'
  if (!(Test-Path -LiteralPath $scenePath -PathType Leaf)) {
    throw 'REAL Unity isolated QA scene not persisted'
  }
  $state.prefabs = '3_REAL_NATIVE_PREFABS_CREATED_AND_PERSISTED'
  $state.scene = 'ISOLATED_REAL_UNITY_SCENE_CREATED_AND_PERSISTED'

  $playArguments = @(
    '-batchmode','-quit','-projectPath',$ProjectRoot,
    '-runTests','-testPlatform','playmode',
    '-testFilter','C01.InteriorProps.Pass19.RealNativePhysicsTests',
    '-testResults',$playXml,'-logFile',$playLog
  )
  Write-Host 'RUNNING REAL Unity PlayMode on three signed FBX-derived QA prefabs'
  & $UnityExe @playArguments
  $playExit = $LASTEXITCODE
  if ($playExit -ne 0) { throw ('Unity PlayMode process exit code '+$playExit) }
  $state.playmode = Require-TestRunXml $playXml 'PlayMode'
  $state.unity = 'UNITY_6000_3_14f1_REAL_EDITOR_EDITMODE_PLAYMODE_PASS'
  Write-Receipt
  Write-Host 'SUCCESS real signed FBX => Unity prefabs + scene => EditMode + PlayMode. C01-02 final release STILL HOLD.'
  exit 0
}
catch {
  $state.failure = [string]$_.Exception.Message
  if ($state.unity -eq 'UNITY_EDITOR_INVOCATION_STARTED') {
    $state.unity = 'UNITY_EDITOR_ATTEMPTED_NO_PASS'
  }
  Write-Receipt
  Write-Error ('W20 HOLD: '+$state.failure)
  exit 20
}
