"""C01-15 PASS26: per-loop UV mapper for unchanged cabinet lid and hollow hinge sleeve.

Only UV0 on pre-existing mesh faces; source vertex/edge/face topology, normals,
materials, hierarchy, pivots and other original assets are preserved.
"""
from math import atan2, pi, hypot

def layout_custom_mesh_uv(data, shape, part):
    if shape not in {'notched_box', 'hollow_cylinder'}:
        raise ValueError('Unsupported P15 PASS26 UV shape: ' + str(shape))
    layer = data.uv_layers.active or data.uv_layers.new(name='UVMap')
    if layer.name != 'UVMap':
        raise AssertionError('Original UV0 layer is not UVMap')
    verts = data.vertices
    if shape == 'notched_box':
        axes = range(3)
        mins = [min(v.co[d] for v in verts) for d in axes]
        spans = [max(v.co[d] for v in verts)-mins[d] for d in axes]
        if any(x <= 1e-8 for x in spans):
            raise RuntimeError('DoorSkin became dimensionless')
        for poly in data.polygons:
            dominant = max(axes, key=lambda d: abs(poly.normal[d]))
            free = [d for d in axes if d != dominant]
            sign = 1 if poly.normal[dominant] >= 0 else 0
            for lid in poly.loop_indices:
                co = verts[data.loops[lid].vertex_index].co
                u = (dominant + (co[free[0]] - mins[free[0]])/spans[free[0]])/3
                v = (sign + (co[free[1]] - mins[free[1]])/spans[free[1]])/2
                layer.data[lid].uv = (u,v)
    else:
        R=float(part['radius'])
        inner=float(part['inner_radius'])
        H=float(part['depth'])
        if not 0 < inner < R or H <= 0:
            raise RuntimeError('Invalid hinge cylinder section')
        for poly in data.polygons:
            lids=list(poly.loop_indices)
            coords=[verts[data.loops[lid].vertex_index].co for lid in lids]
            if abs(poly.normal.z) > .7:
                positive=sum(co.z for co in coords) >= 0
                for lid,co in zip(lids,coords):
                    u=(.5 if positive else 0) + .25*(co.x/R + 1)
                    v=.5 + .25*(co.y/R + 1)
                    layer.data[lid].uv=(u,v)
            else:
                avg=sum(hypot(co.x,co.y) for co in coords)/len(coords)
                inside=avg < .5*(R+inner)
                angles=[(atan2(co.y,co.x)/(2*pi))%1 for co in coords]
                if max(angles)-min(angles)>.5:
                    angles=[a+1 if a<.5 else a for a in angles]
                for lid,co,theta in zip(lids,coords,angles):
                    u=(.5 if inside else 0) + theta*.5
                    v=(co.z/H+.5)*.5
                    layer.data[lid].uv=(u,v)
    data.update()
