# T2 runtime review

Reviewed the task brief, implementation report, specification and contract, and the packaged `7954b17..b6abb512` diff. Focused source checks covered button dispatch/raycasting, airlock and lift state transitions, rider detection/carrying, gate caching and scene-based tests. No source, index or HEAD changes were made by this review.

## Spec verdict

**APPROVE for integration, with Unity execution pending.** Runtime APIs and confirmed deck elevations (-12.4, 0, 6.4 m) match the contract. Left-click interaction resolves an actual `ShipButtonV4` on the first collider hit; panel hits have no gate fallback. Lift buttons dispatch before gate handling. Airlock cancellation clears the relevant pending request, and replacement requests close the opposite gate before opening. Lift requests close all landings before continuous travel, preserve that requirement during redirects/repeated calls, and permit opening only at the stopped, aligned current floor. QA reset does not move the player.

The gate implementation caches closed positions per leaf, serializes those origins across reloads, converts manifest world travel through the parent transform, and synchronizes current/target/physics in `SetImmediate`. Only referenced leaves move. Rider detection requires the nearest non-player ground-ray hit to belong to the car, with an additional footprint filter; carrying uses `CharacterController.Move` with each car delta rather than assigning the player transform. Overview visibility changes renderers without disabling colliders, and walking restores geometry.

## Quality verdict

**APPROVE: no actionable correctness or maintainability finding in the reviewed scope.** The interlock state transitions are small and explicit, and the tests exercise the delivered scene rather than substitute geometry. The report accurately separates successful C# compilation from unexecuted Unity scene/physics checks. The previously identified marker filename issue is already fixed separately and is not an outstanding finding here.

## Findings

None requiring a code change from this static review.

## Recommendation and validation limits

Proceed with primary's actual Unity import and scene PlayMode run before final delivery. This review did not execute Unity or independently repeat the reported compilation. Confirm the authored button collision, gate pocket/passage, and both-lift continuous transport checks against the assembled scene. Also exercise a lift while the explorer remains enabled in normal walking mode: `ShipRuntimePlayTests.LoadShip` disables explorer updates for controlled tests, so its transport test does not cover concurrent walking gravity and lift carrying. Verify this as an integration check; static review alone cannot establish CharacterController contact behavior or physical clearances.
