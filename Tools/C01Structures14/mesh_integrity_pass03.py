"""C01-14 PASS03. Audits REAL v001 .blend files; conservative per-mesh repairs.
Never rebuilds objects from primitives. No cosmetic modifications or forced welding.
Requires Blender 4.0+ / numpy.
"""
import bpy, bmesh, json, math, hashlib, sys, argparse, collections
from pathlib import Path
from mathutils import Vector

IDS=("RMP-01","RAI-01")
EPS=1e-7
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def mesh_names(): return [o for o in bpy.data.objects if o.type=="MESH"]
def quant(v,nd=5): return tuple(round(float(x),nd) for x in v)
def statistics(obj):
    me=obj.data
    me.calc_loop_triangles()
    verts=me.vertices; edges=me.edges; polys=me.polygons
    usage=collections.defaultdict(list)
    neighbors=[set() for _ in verts]
    face_signatures=collections.Counter()
    for p in polys:
        ids=list(p.vertices)
        face_signatures[tuple(sorted(ids))]+=1
        for i,a in enumerate(ids):
            b=ids[(i+1)%len(ids)]
            usage[tuple(sorted((a,b)))].append((a,b))
            neighbors[a].add(b);neighbors[b].add(a)
    loose_vertices=[v.index for v in verts if not neighbors[v.index]]
    loose_edges=[e.index for e in edges if tuple(sorted(e.vertices)) not in usage]
    boundary=[k for k,v in usage.items() if len(v)==1]
    nonmanifold=[k for k,v in usage.items() if len(v)>2]
    bad_winding=[k for k,v in usage.items() if len(v)==2 and v[0]==v[1]]
    duplicates=sum(n-1 for n in face_signatures.values() if n>1)
    degenerates=[p.index for p in polys if p.area<=EPS*EPS]
    coordinate_map=collections.defaultdict(list)
    for v in verts:coordinate_map[quant(v.co,7)].append(v.index)
    colocated=[[a for a in ids] for ids in coordinate_map.values() if len(ids)>1]
    seen=set(); components=0
    for v in verts:
        if v.index in seen:continue
        components+=1; todo=[v.index];seen.add(v.index)
        while todo:
            for n in neighbors[todo.pop()]:
                if n not in seen:seen.add(n);todo.append(n)
    # Edge/vertex T-junctions: only inside the SAME Blender Mesh object.
    junctions=[]
    for v in verts:
        for e in edges:
            a,b=verts[e.vertices[0]].co,verts[e.vertices[1]].co
            if v.index in e.vertices: continue
            d=b-a;denom=d.length_squared
            if denom<EPS*EPS: continue
            t=(v.co-a).dot(d)/denom
            if EPS<t<1-EPS and (a+d*t-v.co).length<EPS:
                junctions.append([v.index,e.index])
    bm=bmesh.new();bm.from_mesh(me)
    signed_volume=float(bm.calc_volume(signed=True)) if not boundary and not nonmanifold else None
    bm.free()
    uv=me.uv_layers.active
    uv_errors=0
    if uv is None:uv_errors=len(me.loops)
    else:
        uv_errors=sum(not all(math.isfinite(v) for v in dat.uv) for dat in uv.data)
    invalid_normals=sum(not all(math.isfinite(v) for v in p.normal) for p in polys)
    return dict(name=obj.name, collider_reference=obj.name.startswith("COL_"),
      vertices=len(verts),edges=len(edges),faces=len(polys),triangles=len(me.loop_triangles),
      connected_components=components,loose_vertices=len(loose_vertices),loose_edges=len(loose_edges),
      boundary_edges=len(boundary),nonmanifold_edges=len(nonmanifold),
      inconsistent_shared_edge_winding=len(bad_winding),degenerate_faces=len(degenerates),
      duplicate_faces=duplicates,colocated_vertices=len(colocated),t_junction_candidates=len(junctions),
      zero_length_edges=sum((verts[e.vertices[0]].co-verts[e.vertices[1]].co).length<EPS for e in edges),
      signed_volume=signed_volume,uv0_present=uv is not None,invalid_uv=uv_errors,
      invalid_face_normals=invalid_normals,
      triangles_with_invalid_uv=sum(1 for tr in me.loop_triangles if uv is not None and abs(
        (uv.data[tr.loops[1]].uv-uv.data[tr.loops[0]].uv).x * (uv.data[tr.loops[2]].uv-uv.data[tr.loops[0]].uv).y -
        (uv.data[tr.loops[1]].uv-uv.data[tr.loops[0]].uv).y * (uv.data[tr.loops[2]].uv-uv.data[tr.loops[0]].uv).x)<1e-12),
      materials=[mat.name if mat else None for mat in me.materials],
      vertex_pair_candidates=colocated[:20],t_junction_samples=junctions[:20])
def audit(id):
    rows=[statistics(o) for o in mesh_names()]
    collider=[o.name for o in mesh_names() if o.name.startswith("COL_")]
    return {"asset_id":id,"source":"REAL_NATIVE_BLEND","mesh_parts":rows,
       "intentional_exceptions":[{"type":"COLLIDER_DUPLICATES_VISIBLE_GEOMETRY",
        "meshes":collider,"reason":"Dedicated non-rendered collider proxy, separate asset object, not z-fighting in Unity"}] if collider else
        [{"type":"SEPARATE_PARTS","reason":"Guardrail posts/rails intentionally separate editable objects and their assembly contacts overlap"}],
       "total":{"vertices":sum(r["vertices"] for r in rows),"edges":sum(r["edges"] for r in rows),
       "faces":sum(r["faces"] for r in rows),"triangles":sum(r["triangles"] for r in rows)}}
def defect_count(r):
    keys=["loose_vertices","loose_edges","nonmanifold_edges","inconsistent_shared_edge_winding",
          "degenerate_faces","duplicate_faces","t_junction_candidates","zero_length_edges",
          "invalid_uv","invalid_face_normals"]
    # The two reference meshes are intentionally closed triangle shells; no boundary allowed.
    return sum(sum(int(part[k]) for k in keys)+part["boundary_edges"]+
               int(part["signed_volume"] is not None and part["signed_volume"]<=0)
               for part in r["mesh_parts"])
def repair_one(obj):
    """Only remove ACTUAL detected defects; preserve UV split, sharp edges, part ownership."""
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
    changes=[]
    dangling=[v for v in bm.verts if not v.link_edges and not v.link_faces]
    if dangling:
        bmesh.ops.delete(bm,geom=dangling,context="VERTS");changes.append(["remove_loose_vertices",len(dangling)])
    loose=[e for e in bm.edges if not e.link_faces]
    if loose:
        bmesh.ops.delete(bm,geom=loose,context="EDGES");changes.append(["remove_loose_edges",len(loose)])
    deg=[f for f in bm.faces if f.calc_area()<EPS*EPS]
    if deg:
        bmesh.ops.delete(bm,geom=deg,context="FACES");changes.append(["remove_zero_area_faces",len(deg)])
    seen=set();dup=[]
    for f in bm.faces:
        key=tuple(sorted(v.index for v in f.verts))
        if key in seen:dup.append(f)
        else:seen.add(key)
    if dup:
        bmesh.ops.delete(bm,geom=dup,context="FACES");changes.append(["remove_duplicate_faces",len(dup)])
    # NO blanket merge-by-distance: preserve hard edges and UV boundaries.
    # NO recalc of already correctly oriented normals.
    if changes:
        bm.to_mesh(obj.data);obj.data.update()
    bm.free()
    return changes
def tri_signature():
    c=collections.Counter()
    for obj in mesh_names():
        if obj.name.startswith("COL_"): continue
        me=obj.data;me.calc_loop_triangles()
        for tr in me.loop_triangles:
            c[(obj.name,tuple(sorted(quant(obj.matrix_world @ me.vertices[i].co,4) for i in tr.vertices)))]+=1
    return c
def scene_bounds():
    points=[o.matrix_world @ v.co for o in mesh_names() if not o.name.startswith("COL_") for v in o.data.vertices]
    return [tuple(min(v[i] for v in points) for i in range(3)),tuple(max(v[i] for v in points) for i in range(3))]
def setup_camera(bounds,zoom=1):
    # Render actual mesh; wire image uses edges read from the loaded native source.
    mid=Vector([(a+b)/2 for a,b in zip(*bounds)])
    max_size=max((b-a for a,b in zip(*bounds)))
    cam_data=bpy.data.cameras.new("QA_OrthographicCamera")
    camera=bpy.data.objects.new("QA_Camera",cam_data);bpy.context.collection.objects.link(camera)
    camera.location=mid+Vector((max_size*1.25,-max_size*1.8,max_size*1.15))
    direction=mid-camera.location;camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
    cam_data.type="ORTHO";cam_data.ortho_scale=max_size*1.5*zoom
    bpy.context.scene.camera=camera
    for pt,power,size in [((3,-5,8),800,4),((-4,3,5),550,5)]:
        ld=bpy.data.lights.new("QA_Light","AREA");l=bpy.data.objects.new("QA_Light",ld)
        bpy.context.collection.objects.link(l);l.location=mid+Vector(pt)
        l.rotation_euler=(mid-l.location).to_track_quat("-Z","Y").to_euler()
        ld.energy=power;ld.shape="DISK";ld.size=size
    scene=bpy.context.scene;scene.render.engine="CYCLES";scene.cycles.samples=8
    scene.render.resolution_x=600;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    if scene.world is None: scene.world=bpy.data.worlds.new("QA_World")
    scene.world.color=(.12,.12,.12)
def render_png(path,wire=False):
    overlay=[]
    if wire:
        cr=bpy.data.curves.new("QA_ActualMeshEdges","CURVE");cr.dimensions="3D";cr.resolution_u=1
        cr.bevel_depth=.004;cr.resolution_u=1;cr.resolution_u=1;cr.bevel_resolution=0
        for ob in mesh_names():
            if ob.name.startswith("COL_"):continue
            for ed in ob.data.edges:
                sp=cr.splines.new("POLY");sp.points.add(1)
                for idx,vi in enumerate(ed.vertices):
                    co=ob.matrix_world @ ob.data.vertices[vi].co
                    sp.points[idx].co=(*co,1)
        edgeobj=bpy.data.objects.new("QA_ActualTopologyEdgeOverlay",cr)
        bpy.context.collection.objects.link(edgeobj);overlay=[edgeobj]
        mat=bpy.data.materials.new("QA_WireInk");mat.diffuse_color=(.01,.02,.025,1)
        mat.use_nodes=True;bsdf=mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:bsdf.inputs["Base Color"].default_value=(.01,.02,.025,1)
        cr.materials.append(mat)
    bpy.context.scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    for obj in overlay:bpy.data.objects.remove(obj,do_unlink=True)
def import_roundtrip(path,before):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path),use_custom_normals=True)
    after=tri_signature()
    diff=before-after;missing=after-before
    data={"fbx_import_executed":True,"imported_objects":[o.name for o in mesh_names()],
          "original_triangles":sum(before.values()),"imported_triangles":sum(after.values()),
          "triangle_positions_exact_at_1e-4":not diff and not missing,
          "missing_triangles":sum(diff.values()),"unexpected_triangles":sum(missing.values()),
          "uv0_by_mesh":{o.name:bool(o.data.uv_layers) for o in mesh_names()},
          "bounds_after_import":scene_bounds()}
    # Blender may rename objects / split vertices for hard/UV edges: compare geometry without naming.
    unname=lambda counter:collections.Counter({k[1]:v for k,v in counter.items()})
    def positions(counter):
        return collections.Counter({k[1]:sum(n for (name,points),n in counter.items() if points==k[1]) for k in counter})
    aa=positions(before);bb=positions(after)
    data["triangulated_surface_positions_equal"]=aa==bb
    data["roundtrip_pass"]=aa==bb and all(data["uv0_by_mesh"].values())
    return data
def run(args):
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=True)
    for id in IDS:
        src=Path(args.input).resolve()/"Blender"/("C01_14_"+id+"_v001.blend")
        if not src.is_file():raise FileNotFoundError(src)
        bpy.ops.wm.open_mainfile(filepath=str(src))
        originals=tri_signature()
        before=audit(id);before["sha256_original_blend"]=sha(src)
        base=output/"QA"/id;base.mkdir(parents=True,exist_ok=True)
        (base/"mesh_topology_before.json").write_text(json.dumps(before,indent=2))
        render_dir=output/"Previews"/id;render_dir.mkdir(parents=True,exist_ok=True)
        bounds=scene_bounds();setup_camera(bounds)
        render_png(render_dir/"wireframe_before.png",wire=True)
        changes={}
        for ob in mesh_names():changes[ob.name]=repair_one(ob)
        after=audit(id);after["repairs"]=changes
        after["repair_verdict"]="REPAIRED" if any(changes.values()) else "NO_SOURCE_TOPOLOGY_REPAIR_NEEDED"
        after["visual_surface_unchanged"]=tri_signature()==originals
        after["bounds_before"]=bounds;after["bounds_after"]=scene_bounds()
        (base/"mesh_topology_after.json").write_text(json.dumps(after,indent=2))
        if not after["visual_surface_unchanged"]:raise RuntimeError(id+" visual triangle topology changed")
        render_png(render_dir/"wireframe_after.png",wire=True)
        render_png(render_dir/"shaded_after.png",wire=False)
        # Connection detail is a zoom of ACTUAL inspected mesh, not a reconstructed geometry.
        bpy.context.scene.camera.data.ortho_scale*=.55
        render_png(render_dir/"joint_inspection_after.png",wire=True)
        src_dir=output/"Sources";fbx_dir=output/"FBX"
        src_dir.mkdir(exist_ok=True);fbx_dir.mkdir(exist_ok=True)
        blend=src_dir/("C01_14_"+id+"_v002.blend")
        fbx=fbx_dir/("C01_14_"+id+"_v002.fbx")
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        bpy.ops.object.select_all(action="DESELECT")
        for ob in mesh_names():ob.select_set(True)
        bpy.context.view_layer.objects.active=mesh_names()[0]
        bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,
            object_types={"MESH"},axis_forward="-Z",axis_up="Y",global_scale=1,
            apply_unit_scale=True,bake_anim=False,mesh_smooth_type="FACE")
        if not blend.read_bytes().startswith(b"BLENDER"):raise RuntimeError("Invalid BLEND "+id)
        if not fbx.read_bytes().startswith(b"Kaydara FBX Binary"):raise RuntimeError("Invalid FBX "+id)
        roundtrip=import_roundtrip(fbx,originals)
        roundtrip["sha256_after_blend"]=sha(blend);roundtrip["sha256_after_fbx"]=sha(fbx)
        roundtrip["before_defect_count"]=defect_count(before)
        roundtrip["after_defect_count"]=defect_count(after)
        roundtrip["geometry_still_suspect"]=roundtrip["after_defect_count"]!=0
        (base/"fbx_roundtrip.json").write_text(json.dumps(roundtrip,indent=2))
        print(id,"BEFORE",before["total"],"AFTER",after["total"],
              "DEFECTS",roundtrip["before_defect_count"],roundtrip["after_defect_count"],
              "FBX_ROUNDTRIP",roundtrip["roundtrip_pass"],"CHANGES",changes)
        # Invalid geometry or failed import comparison cannot be silently called PASS.
        if roundtrip["geometry_still_suspect"] or not roundtrip["roundtrip_pass"]:
            raise RuntimeError("PASS03 gate failed for "+id+": "+json.dumps(roundtrip))
if __name__=="__main__":
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    run(p.parse_args(argv))
