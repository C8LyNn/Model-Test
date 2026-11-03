# C01-17 / DETAIL PASS14 — P17-02 physical binary FBX candidate

**Existing Draft PR #17, not merged.** Authoring source from PASS12/13 unchanged. Physically wrote an actual 147,186-byte **Kaydara FBX Binary 7400** containing 38 existing parts and 536 triangles. New FBX SHA-256: `028aac19cfe3bb7ff873a08c948a95cfa31344cee2e87347f636030620e1ebe1`.

The FBX was constructed offline, from the actual historic Blender-PASS03 binary FBX. **All 20 original Geometry nodes remain precisely identical**. Added 18 previously authored mechanical parts as 18 Mesh Model/Geometry pairs and kept 4 real screws mounted and the corrected Keybed/Housing contact. No new asset IDs, no ship file edits, no uncontrolled welding, no merge.

**Real executed static QA:** two FBX readers, original FBX byte-identity reserialization preflight, 38 meshes/536 triangles, 536/536 actual authoring OBJ world triangles identical to 1µm, no missing/extra triangles, 0 zero-area triangles, valid UV0/normal indices in all 38 meshes, original 20 mesh arrays preserved, 18 new root/material connections present.

**Physical binary distribution:** ChatGPT PASS14 conversation file `C01-17_PASS14_P17-02_REAL_BINARY_FBX_CANDIDATE.zip`, 1,135,669 bytes, SHA256 `4b7648797f7b4c266f701a32fe744f60cfef28fb22c3be8d78077d9340152db3`, CRC PASS. Contains actual new binary candidate FBX, original genuine but **STALE** .blend, full 536-triangle source OBJ, historical real BEFORE shaded PNG, analytical AFTER diagram (not Blender), checks and an unexecuted real Blender 4.x import→new .blend save→binary FBX reexport→reimport Windows gate.

**CRITICAL:** This is an **offline FBX candidate** and **NOT a genuine Blender exporter artifact**. New 38-part Blender-saved native `.blend` has not been produced. Existing LFS `.blend` and `.fbx` in PR #17 still contain historical old 20/240 bytes, not latest. Blender 4.x runtime load/save/export/reimport **NOT_RUN**, independent C01-02 final acceptance **PENDING**, Unity 6 URP **NOT_RUN**. C01 Actions no runner allocated. **NEEDS_OWNER_ACTION**: run bundled `RUN_WINDOWS.ps1` on authorized Windows Blender 4.x, then have QA independently verify freshly Blender-origin BLEND and FBX SHA, and Unity integration separately. Do not promote the offline candidate or falsely mark full PASS.

Machine receipt: `C01InteriorProps_Source/QA/PASS14/P17-02_OFFLINE_BINARY_FBX_CANDIDATE_QA.json`.
