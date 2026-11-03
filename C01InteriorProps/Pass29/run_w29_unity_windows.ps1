[CmdletBinding()]
param([ValidateSet('Preflight','Execute')][string]$Mode='Preflight',
      [string]$ProjectRoot=(Get-Location).Path,
      [string]$UnityExe='C:\Program Files\Unity\Hub\Editor\6000.3.14f1\Editor\Unity.exe')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$ProjectRoot=(Resolve-Path $ProjectRoot).Path
$folder=Join-Path $ProjectRoot 'C01InteriorProps_QA\PASS29\WindowsUnity'
New-Item -Force -ItemType Directory $folder|Out-Null
$state=[ordered]@{unity='NOT_RUN';source='NOT_RUN';build='NOT_RUN';editmode='NOT_RUN';playmode='NOT_RUN';
 screenshots='OWNER_ACTION_REQUIRED';authored_motion='NOT_APPROVED';release='HOLD'}
$receipt=Join-Path $folder 'W29_REAL_UNITY_RESULT.json'
function Save{$state|ConvertTo-Json -Depth 8|Set-Content $receipt -Encoding utf8}
function Invoke-UnityEditor([string[]]$CommandArgs,[string]$Tag){
 & $UnityExe @CommandArgs
 if($LASTEXITCODE -ne 0){throw "$Tag real Unity process failed $LASTEXITCODE"}
}
function CheckXml([string]$f){
 if(!(Test-Path $f)){throw 'Real Unity XML missing'}
 [xml]$xml=Get-Content $f -Raw
 if($xml.DocumentElement.Name -ne 'test-run' -or
  [int]$xml.DocumentElement.GetAttribute('passed') -lt 1 -or
  [int]$xml.DocumentElement.GetAttribute('failed') -ne 0 -or
  $xml.DocumentElement.GetAttribute('result') -ne 'Passed'){throw 'Unity tests did not pass'}
 return @{passed=[int]$xml.DocumentElement.GetAttribute('passed');failed=0}
}
try {
 $stage=Join-Path $ProjectRoot 'C01InteriorProps\Pass29\stage_w29_nine.py'
 if($Mode -eq 'Preflight'){
  & python $stage --repo $ProjectRoot
  if($LASTEXITCODE -ne 0){throw 'Manifest preview failed'}
  Save;Write-Host 'UNITY_NOT_RUN';exit 0
 }
 if(!(Test-Path -LiteralPath $UnityExe)){throw 'Licensed Unity Editor missing'}
 & python $stage --repo $ProjectRoot --apply
 if($LASTEXITCODE -ne 0){throw 'Signed binary source stage failed'}
 $state.source='NINE_PHYSICAL_SIGNED_FBX'
 $state.unity='EDITOR_STARTED';Save
 Invoke-UnityEditor -CommandArgs @('-batchmode','-quit','-projectPath',$ProjectRoot,
 '-executeMethod','C01.InteriorProps.Pass29.W29Room.Build',
 '-logFile',(Join-Path $folder 'Build-Editor.log')) -Tag 'BUILD'
 $scene=Join-Path $ProjectRoot 'Assets\C01InteriorProps\Pass29\Generated\Scenes\W29_NONDOOR_ROOM_4x4_CORRIDOR_2x4.unity'
 if(!(Test-Path $scene)){throw 'Real scene not generated'}
 $state.build='NATIVE_UNITY_SCENE_SAVED';Save
 $edit=Join-Path $folder 'EditMode-results.xml'
 Invoke-UnityEditor -CommandArgs @('-batchmode','-quit','-projectPath',$ProjectRoot,'-runTests','-testPlatform','editmode',
 '-testFilter','C01.InteriorProps.Pass29.W29EditTests','-testResults',$edit,
 '-logFile',(Join-Path $folder 'EditMode-Editor.log')) -Tag 'EDITMODE'
 $state.editmode=CheckXml $edit;Save
 $play=Join-Path $folder 'PlayMode-results.xml'
 Invoke-UnityEditor -CommandArgs @('-batchmode','-quit','-projectPath',$ProjectRoot,'-runTests','-testPlatform','playmode',
 '-testFilter','C01.InteriorProps.Pass29.W29Play','-testResults',$play,
 '-logFile',(Join-Path $folder 'PlayMode-Editor.log')) -Tag 'PLAYMODE'
 $state.playmode=CheckXml $play
 $state.unity='EDITOR_EDITMODE_PLAYMODE_SMOKE_PASS'
 $state.screenshots='REAL_1080P_SCENE_GAME_NOT_YET_SIGNED'
 $state.release='HOLD';Save
 Write-Host 'Unity QA smoke completed; authored materials/PhysX/visual/RC remain HOLD'
 exit 0
}catch{
 $state.failure=$_.Exception.Message
 if($state.unity -eq 'EDITOR_STARTED'){$state.unity='EDITOR_ATTEMPTED_NO_PASS'}
 Save
 Write-Error ('UNITY_RC_HOLD '+$state.failure)
 exit 29
}
