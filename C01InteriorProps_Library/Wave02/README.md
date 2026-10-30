# C01-03 — WAVE 02 Asset Registry (20 planned, no fabricated models)

**Scope:** C01 — 3D Asset Factory; production owned only by C01-15–19; independent QA by C01-02; scene integration by C01-10; final signoff by C01-00.

**Stacked PR:** this branch targets `c01/props-03-asset-library` (Wave01 PR #10). It does not change ship scene or supplier geometry. Once Wave01 registry PR merges, retarget this library PR to the approved integration branch.

## Catalog

| ID | Owner | Planned asset | Dependencies | Status |
|---|---|---|---|---|
| P15-04 | C01-15 | Ceiling cable tray straight 3 m | None | PLANNED |
| P15-05 | C01-15 | Cable tray elbow 90 degrees | P15-04 | PLANNED |
| P15-06 | C01-15 | Technical wire bundle with brackets | P15-04, P15-05 | PLANNED |
| P15-07 | C01-15 | Wall coolant manifold with pipes and pressure gauges | None | PLANNED |
| P16-04 | C01-16 | Large ceiling illumination panel | None | PLANNED |
| P16-05 | C01-16 | Backlit corridor directional sign | None | PLANNED |
| P16-06 | C01-16 | Rotating alarm beacon | None | PLANNED |
| P16-07 | C01-16 | Entry availability/lock/error indicator | None | PLANNED |
| P17-04 | C01-17 | Large bridge operator station with two screens | P17-01 | PLANNED |
| P17-05 | C01-17 | Laboratory and medical diagnostic terminal | None | PLANNED |
| P17-06 | C01-17 | Emergency cutoff panel with cover and switch | None | PLANNED |
| P17-07 | C01-17 | Fuse module with removable cartridge | None | PLANNED |
| P18-04 | C01-18 | Technical materials transport cylinder | None | PLANNED |
| P18-05 | C01-18 | Locking equipment case | None | PLANNED |
| P18-06 | C01-18 | Hazardous specimen containment container | None | PLANNED |
| P18-07 | C01-18 | Portable toolbox | None | PLANNED |
| P19-05 | C01-19 | Two-person crew bench | None | PLANNED |
| P19-06 | C01-19 | Fold-down wall table | None | PLANNED |
| P19-07 | C01-19 | Medical diagnostic bed | None | PLANNED |
| P19-08 | C01-19 | Cabin washbasin / sanitation module | None | PLANNED |

**Exact canonical distribution:** 4 new models per production group, 20 IDs total. The full catalog is Wave02/catalog.json. Different wave numbers do not recycle existing Wave01 identifiers.

## Evidence semantics

- Proposed version is 0.1.0; delivered version is NULL until a real asset is actually received.
- Dimensions, pivot, triangle count, socket and material/collider fields are NULL because producers and C01-01 have not established measured/approved values. No imaginary meshes, exports, SHA hashes or source paths have been created here.
- Dependencies link assets by stable IDs (not duplicate files), e.g. P15-05 corner references P15-04 straight cable tray; P17-04 maintains style continuity with P17-01.
- Approved versions must be immutable: new source geometry or interop contract means new SemVer version and new hash, never overwrite of the previously approved export.
- Every approved model needs a real .blend, .fbx, .prefab with .meta, three views, and documented independent Blender/Unity QA, not just a static manifest.

## Test commands

```bash
python C01InteriorProps_Library/Wave02/validate_wave02.py audit
python -m unittest discover -s C01InteriorProps_Library/Wave02/tests -v
python C01InteriorProps_Library/Wave02/validate_wave02.py release
```

Successful metadata audit is not production acceptance; `release` must exit 2 BLOCKED until every model passes C01-02 and real import/clearance evidence exists.

## Handoff

Producer models for P15–P19 stay in independent producer branches/PRs. C01-03 registers real paths and SHA256 only when physical files are accessible. C01-02 performs independent QA; C01-10 assembles demonstrators after approval. C01-00 alone closes the release gate.

**Current result:** Wave02 library metadata READY; 0/20 producer files accepted; 0/20 models approved; Blender/Unity NOT RUN by C01-03.
