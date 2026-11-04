# Deck zero logistics implementation plan

**Goal:** Align engineering with its control room and put cargo at the freight dock while keeping food nearer the galley and hydroponics.

**Architecture:** Reassign four existing same-sized sectors and translate their existing reusable equipment. Keep the modular architecture and gate controller IDs stable; update zone IDs, labels and connectivity metadata to reflect the new functions.

**Constraints:** Preserve the v7.1 bridge, lift behaviour, emergency hangar, door clearances, symmetry of architectural layout and earlier scenes. Test real Unity access and gate behaviour as well as source geometry.

- [ ] Check old layout fails purpose-specific proximity tests.
- [ ] Build a data-driven zone and equipment remapping; test full source geometry and access.
- [ ] Create a separate scene and editable master prefab from v7.1.
- [ ] Verify the sector functions, freight passage and existing ship interactions in Unity.
- [ ] Capture the layout and deliver the verified project without overwriting previous versions.
