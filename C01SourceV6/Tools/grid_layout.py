"""Topology in nominal floor squares; one square is 3 metres."""


def build():
    zones, corridors = [], []

    def zone(ident, kind, deck, x0, x1, z0, z1, **kwargs):
        zones.append(dict(id=ident, kind=kind, deck=deck, x0=x0, x1=x1,
                          z0=z0, z1=z1, **kwargs))

    for deck in (0, 1, 2):
        zone(f"L{deck}_MAIN", "corridor", deck, 0, 42, 14, 15)
        corridors.append(dict(id=f"L{deck}_MAIN", deck=deck, width=1))
        for name, x in (("D1", 13), ("D2", 27)):
            zone(f"L{deck}_{name}", "airlock", deck, x, x+2, 14, 15,
                 parent=f"L{deck}_MAIN")
        if deck == 0:
            for i, name in enumerate(("ENGINE_ROOM", "PURIFICATION", "EVAC_HANGAR")):
                zone(f"L0_{name}", "sector", 0, 14*i, 14*(i+1), 15, 30)
            zone("L0_CARGO", "sector", 0, 0, 14, 0, 14)
            zone("L0_HYDROPONICS", "sector", 0, 14, 42, 0, 14)
            continue
        for i in range(6):
            x = i * 7
            for side, z0 in (("S", 11), ("N", 15)):
                branch = f"L{deck}_{side}_BRANCH_{i+1}"
                zone(branch, "corridor", deck, x+3, x+4, z0, z0+3)
                corridors.append(dict(id=branch, deck=deck, width=1))
                for j, cx in enumerate((x, x+4)):
                    kind = "cabin" if i % 2 == 0 else "support"
                    ident = f"L{deck}_{side}_{kind.upper()}_{2*i+j+1:02}"
                    zone(ident, kind, deck, cx, cx+3, z0, z0+3)
                    if kind == "cabin":
                        zone(ident+"_BATH", "bathroom", deck, cx, cx+2, z0+2, z0+3, parent=ident)
        for i, (north, south) in enumerate(zip(("GYM", "LAB", "MED"),
                                                ("CARGO", "ENGINE_CONTROL", "TECH"))):
            kind = "sector" if deck == 1 else "void"
            zone(f"L{deck}_{north}", kind, deck, 14*i, 14*(i+1), 18, 30)
            zone(f"L{deck}_{south}", kind, deck, 14*i, 14*(i+1), 0, 11)
    lifts = [
        dict(id="BRIDGE_PASSENGER", kind="passenger", x0=-4, x1=-3, z0=8, z1=9),
        dict(id="STERN_PASSENGER", kind="passenger", x0=46, x1=47, z0=20, z1=21),
        dict(id="STERN_CARGO_S", kind="cargo", x0=43, x1=45, z0=3, z1=5),
        dict(id="STERN_CARGO_N", kind="cargo", x0=43, x1=45, z0=25, z1=27),
    ]
    # Connections are nominal adjacency, not evidence of physical walkability.
    links = []
    for i, a in enumerate(zones):
        for b in zones[i+1:]:
            if a["deck"] != b["deck"] or "void" in (a["kind"], b["kind"]):
                continue
            if a.get("parent") == b["id"] or b.get("parent") == a["id"]:
                links.append((a["id"], b["id"]))
                continue
            if a.get("parent") or b.get("parent"):
                continue
            vertical = (a["x1"] == b["x0"] or b["x1"] == a["x0"]) and max(a["z0"], b["z0"]) < min(a["z1"], b["z1"])
            horizontal = (a["z1"] == b["z0"] or b["z1"] == a["z0"]) and max(a["x0"], b["x0"]) < min(a["x1"], b["x1"])
            if not (vertical or horizontal):
                continue
            kinds = {a["kind"], b["kind"]}
            if kinds in ({"cabin", "corridor"}, {"support", "corridor"}):
                corridor = a if a["kind"] == "corridor" else b
                if "_MAIN" in corridor["id"]:
                    continue
            if kinds in ({"cabin"}, {"support"}, {"cabin", "support"}, {"sector", "cabin"}, {"sector", "support"}):
                continue
            links.append((a["id"], b["id"]))
    return dict(grid_metres=3, ship_bounds=[-16, 58, -2, 32],
                body_bounds=[0, 42, 0, 30], elevations=[-12.4, 0, 6.4],
                zones=zones, corridors=corridors, lifts=lifts, links=links)
