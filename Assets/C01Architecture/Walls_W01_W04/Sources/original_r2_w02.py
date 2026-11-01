"""Lossless W02 original-r2 authoring topology, not a new model.

Frozen source: C01_WALLS_WAVE02_r2/Sources/mesh_data.json.
This exact 12x12 stepped surface reproduces ALL 288 original vertex records
and ALL 572 original oriented triangle records, in the SAME index order.
No FBX, Blender, network or package dependencies are needed to rebuild it.
Units/meters, Unity Y-up; local pivot at (0,0,0).
"""
from __future__ import annotations
import hashlib
import json

ORIGINAL_SOURCE_FBX_SHA256 = "3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037"
TOPOLOGY_SHA256 = "6774ef24535abf56c9f3c6cb1d28ede342f6dd9a1db284cb5bcafa01b2f83995"
X = (0.0, .08, .12, .16, .43, .47, .53, .57, .84, .88, .92, 1.0)
Y = (0.0, .16, .23, .30, 1.38, 1.45, 1.55, 1.62, 2.70, 2.77, 2.84, 3.0)


def build_exact():
    vertices = []
    for rear in (False, True):
        for j, y in enumerate(Y):
            for i, x in enumerate(X):
                z = .2 if rear else (
                    .042 if 4 <= j <= 7 and 4 <= i <= 7 else
                    (.025 if 3 <= j <= 8 and 3 <= i <= 8 else 0.0))
                vertices.append([x, y, z])

    triangles = []
    for j in range(11):
        for i in range(11):
            p = j * 12 + i
            q = p + 144
            triangles.extend((
                [p, p+13, p+1], [p, p+12, p+13],
                [q, q+1, q+13], [q, q+13, q+12]))
    for i in range(11):
        p, t = i, 132+i
        triangles.extend((
            [p, p+1, p+145], [p, p+145, p+144],
            [t, t+145, t+1], [t, t+144, t+145]))
    for j in range(11):
        left, right = j*12, j*12+11
        triangles.extend((
            [left, left+156, left+12], [left, left+144, left+156],
            [right, right+12, right+156], [right, right+156, right+144]))

    assert len(vertices) == 288 and len(triangles) == 572
    identity = {"vertices": vertices, "triangles": triangles}
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    actual_sha = hashlib.sha256(canonical).hexdigest()
    if actual_sha != TOPOLOGY_SHA256:
        raise ValueError("W02 source topology identity drift: " + actual_sha)
    return vertices, triangles


if __name__ == "__main__":
    vertices, triangles = build_exact()
    print("W02 original r2 source VERIFIED: 288 vertices / 572 triangles")
    print("Topology SHA256: " + TOPOLOGY_SHA256)
