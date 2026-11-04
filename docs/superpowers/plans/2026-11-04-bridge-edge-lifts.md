# Bridge edge lifts implementation plan

**Goal:** Move the bridge's two passenger lifts symmetrically towards the outer hull and reorganize command stations around a clear central axis.

**Architecture:** Derive a new version from the existing modular assembly. Rebuild each shaft and its landings using the 3 m grid, replace affected floors and galleries, and preserve independently editable elements and previous scenes. Store layout data separately from the Unity scene and verify connectivity across all decks.

**Constraints:** Preserve v7.0 seam and roof fixes, working gate/lift interlocks, player routes, room heights, previous versions, and the user's local changes.

- [ ] Establish failing checks for the old lift locations, symmetry and accessible landings.
- [ ] Generate the new bridge and lift layout with complete wall/floor connections.
- [ ] Create a new Unity scene and master prefab using reusable modules.
- [ ] Test geometry, player access and lift travel on all decks, and inspect screenshots.
- [ ] Deliver verified scene and report without overwriting previous work.
