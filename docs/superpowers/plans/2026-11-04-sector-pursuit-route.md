# Sector pursuit route implementation plan

**Goal:** Route the upper-deck pursuit through multiple sectors rather than only along the straight main corridor.

**Architecture:** Add 3 m modular guarded catwalks above the existing gym, engine-control and medical sectors. Connect each end to a side branch using usable gates, and close three main-corridor sections so the route actually traverses the sectors. Keep the ground-level sector functions and prior decks intact.

**Constraints:** Upper deck remains at 3.4 m, sector ceilings and modular structure remain intact; floor/railing details, gate operation, player clearance and uninterrupted route from bridge to exit must be tested in Unity and source data. Existing versions and user changes remain.

- [ ] Verify that the previous scene lacks the planned sector route.
- [ ] Build and audit modular catwalks, gates, guardrails and obstacles.
- [ ] Create the separate scene and editable master prefab with working gates.
- [ ] Test the complete forced route, blocked corridor, gate buttons and existing transport systems.
- [ ] Capture visual evidence and deliver scene, project and QA.
