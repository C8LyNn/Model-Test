# Scoped Unity re-review

Scope: fixes `0b9f3da` and `a1f69c4`, the Editor changes in `c902e88`, and the primary's subsequent working-tree `canRestore` correction in ShipV4Batch. Source/index/HEAD were left unchanged by this reviewer. No Unity process, broad tests, or asset mutations were performed by this reviewer.

**Spec verdict: APPROVE for the scoped source changes.** Both previous review findings and the preservation error path identified during re-review are addressed in source.

**Quality verdict: APPROVE for the scoped source changes.** No remaining actionable findings. The primary must commit/sync the reviewed `canRestore` correction before final delivery.

**Actual Unity results: NOT VERIFIED by this review.** Initial execution is now underway with the primary. No passing generation/import, EditMode/PlayMode, callback/domain-reload, rendered-image, or export result is asserted here; the primary must supply that evidence. This source approval does not convert pending checks into PASS.

## Preservation error-path follow-up

The initial `c902e88` path called Restore after snapshot failure before capturing the current request's scene setup. The primary corrected this during re-review: `ShipV4Batch.cs:44` initializes `canRestore` from an active runner stage, `:52` enables it for a new request only after successful preservation and setup capture, and `:57` guards Restore with it. Snapshot failures for either `open` or `preserve-rebuild` now leave the dirty scene setup open rather than consuming absent/stale restoration state. The corrected source path is approved; actual failure-injection behavior remains unverified in Unity. The existing dirty-scene guard is not a finding.

## Previous findings

- **Projection integration: addressed in source.** Walking explicitly selects perspective/FOV 65. Serialized overview projection/size/FOV restore through ResetView, and repeated walking calls do not overwrite them. The real-scene PlayMode regression asserts both projections and return framing.
- **Saved NavMesh negative test: addressed in source.** A uniquely named real NavMeshData sentinel is saved, checked for nonempty bytes/GUID, and deleted in `finally`. The missing-bed fixture invokes exhaustive validation, requires a route entry per zone plus four transport links, and compares saved asset bytes/GUID afterward. Thus the navigation path can no longer be bypassed by this test.

Successful snapshot SaveAs uses a unique path outside the v4 asset root and does not overwrite the original scene file. The new material setup chooses the host's built-in/URP shader, applies emission and transparent glass state, and leaves host pipeline settings alone. Added text is source-parented. Deck plans derive their center/extent from solid renderer bounds at the output aspect ratio, slice above the selected floor, and restore near clipping afterward. These paths still require actual visual and integration verification in Unity.
