# Ceiling-junction geometry prototype

## Diagnosis

V5 `vertical_modules` starts at the bottom of each uninterrupted wall run, emits 3 m lengths, and emits the remaining length as a final module. `join_deck_intervals` can join the full run from -12.4 to 12.4 m: 24.8 m = 8 × 3 m + 0.8 m. A 12.4 m run gives 4 × 3 m + 0.4 m. Each generated wall module receives separate metal top and bottom rails. Thus a short remainder can produce an extra visible framed band at the roof. V5 also has legitimate short spans at gate openings and deck junctions, so a height-only global replacement is unsafe. The existing V5 manifest has 82 `W3_H800` and 209 `W3_H400` wall instances across all elevations; those counts are not a count of roof defects.

## Candidate integration

`vertical_partition.py` is a standalone partition/classification prototype, not an integrated generator or a finished mesh solution. On wall segments ending at a verified ceiling underside it retains each complete 3 m panel exactly and labels a final segment no more than 1 m high as `trim`. For each trim generate an unframed, uniformly finished fascia, filling exactly the same 3D footprint and interval as the replaced wall. Keep wall collision/obstacle coverage, deck elevations, ceiling surfaces, and all gate cuts unchanged. Exact 3 m spans never create a trim.

Do not globally replace V5's shared `vertical_modules`: it is also used for gates, bow hull pieces, and other geometry. Apply the classification only to wall spans whose endpoint is actually a ceiling for that location and side. If a wall continues through or above a ceiling or if neighboring spaces have different ceiling heights, a roof-end flag alone is insufficient; derive spatial ceiling intersections from the actual ceiling geometry and design transitions explicitly. Do not mistake a gate cut endpoint for a ceiling. The 1 m threshold is a visual design choice, not a safety guarantee.

A visually continuous fascia needs matching material, coplanar visible surfaces, and matching vertical extents at the 0.3 m corner/intersection nodes and along neighboring wall runs. V5 nodes are independently partitioned and are metal. Compute common fascia intervals along the complete connected wall/node edge, split node meshes at the same elevations, and select the same finish; applying the helper independently to each node is not sufficient. Shared walls can have different visual requirements on each face. Ensure trim meshes do not introduce gaps, duplicates, z-fighting, or collision changes, and verify apertures and roof steps. If compatible alignment cannot be established, leave that junction unchanged and flag it for review.

Keep the full panel's existing 0.12 m top metal rail in its original location. Begin the fascia exactly at the panel top and give the fascia no additional top or bottom rails: the standard panel edge remains a single intentional line, rather than a second frame around the remainder. Choose its finish and depth alongside the node treatment so the meeting is visually deliberate; confirm the result in Unity. At the 12.4 m ceiling underside, the existing 0.2 m ceiling slab continues upward to 12.6 m: do not extend or change either wall or slab to hide the remainder.

## Alternatives

- Recommended: retain 3 m panels and expose the unavoidable remainder as a plain ceiling fascia. This preserves elevations and module size but the fascia remains physically visible.
- Redistribute the remainder among shorter panels: exact coverage but repeated square modules are lost.
- Conceal the entire remainder inside the existing ceiling: not generally geometrically possible without moving the ceiling or changing the story envelope; 0.4/0.8 m of wall exists below the fixed ceiling underside.

## Validation and limitations

Run `python -m unittest -v test_vertical_partition` from this folder. Six tests cover 24.8 m, 6.4 m and exact-grid spans, gate cuts, a short intrinsic run, and a non-narrow remainder. Tests exercise mathematical labeling only, not geometry, materials, collisions, gate operation, or visual appearance. No Unity run or V5 project mutation was performed. V6 integration requires generator-specific tests for actual walls and nodes and visual review in Unity before claiming the strip is removed.
