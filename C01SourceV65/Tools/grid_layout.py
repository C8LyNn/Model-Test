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
            zone("L0_CARGO", "sector", 0, 0, 14, -1, 14)
            zone("L0_HYDROPONICS", "sector", 0, 14, 28, -1, 14)
            zone("L0_FOOD_RESERVE", "sector", 0, 28, 42, -1, 14, role="FOOD_STORAGE", label="ZAPASY ZYWNOSCI")
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
                    roles = {
                        (1,"N",3):("GYM_CHANGING","SZATNIA TRENINGOWA"), (1,"N",4):("GYM_EQUIPMENT","SPRZET TRENINGOWY"),
                        (1,"N",7):("SAMPLE_STORAGE","PROBKI I MATERIALY"), (1,"N",8):("RESEARCH_PREP","PRZYGOTOWANIE BADAN"),
                        (1,"N",11):("MEDICAL_RECEPTION","REJESTRACJA MEDYCZNA"), (1,"N",12):("MEDICAL_SUPPLIES","ZAPASY MEDYCZNE"),
                        (1,"S",3):("CARGO_OFFICE","EWIDENCJA LADUNKU"), (1,"S",4):("CARGO_TOOLS","NARZEDZIA LADUNKOWE"),
                        (1,"S",7):("ENGINE_MONITORING","NADZOR MASZYNOWNI"), (1,"S",8):("POWER_CONTROL","KONTROLA ZASILANIA"),
                        (1,"S",11):("WORKSHOP","WARSZTAT"), (1,"S",12):("SPARE_PARTS","CZESCI ZAMIENNE"),
                        (2,"N",3):("GALLEY","KUCHNIA"), (2,"N",4):("MESS","JADALNIA"),
                        (2,"N",7):("LAUNDRY","PRALNIA"), (2,"N",8):("LINEN_STORAGE","POSCIEL I ODZIEZ"),
                        (2,"N",11):("QUIET_ROOM","SALA WYCISZENIA"), (2,"N",12):("TELEMEDICINE","TELEMEDYCYNA"),
                        (2,"S",3):("CREW_LOUNGE","SALON ZALOGI"), (2,"S",4):("RECREATION","REKREACJA"),
                        (2,"S",7):("HYGIENE_SUPPLIES","SRODKI HIGIENY"), (2,"S",8):("CLOTHING_REPAIR","NAPRAWA ODZIEZY"),
                        (2,"S",11):("COMMUNICATIONS","LACZNOSC"), (2,"S",12):("WATER_CONTROL","NADZOR WODY I POWIETRZA")}
                    role, label = roles.get((deck,side,2*i+j+1),("", "")) if kind == "support" else ("", "")
                    zone(ident, kind, deck, cx, cx+3, z0, z0+3, role=role, label=label)
                    if kind == "cabin":
                        bath_z = z0 if side=="N" else z0+2
                        zone(ident+"_BATH", "bathroom", deck, cx, cx+2, bath_z, bath_z+1, parent=ident)
        for i, (north, south) in enumerate(zip(("GYM", "LAB", "MED"),
                                                ("CARGO", "ENGINE_CONTROL", "TECH"))):
            kind = "sector" if deck == 1 else "void"
            zone(f"L{deck}_{north}", kind, deck, 14*i, 14*(i+1), 18, 30)
            zone(f"L{deck}_{south}", kind, deck, 14*i, 14*(i+1), -1, 11)
    lifts = [
        dict(id="BRIDGE_PASSENGER", kind="passenger", x0=-4, x1=-3, z0=8, z1=9),
        dict(id="BRIDGE_PASSENGER_N", kind="passenger", x0=-4, x1=-3, z0=20, z1=21),
        dict(id="STERN_PASSENGER", kind="passenger", x0=46, x1=47, z0=20, z1=21),
        dict(id="STERN_PASSENGER_S", kind="passenger", x0=46, x1=47, z0=8, z1=9),
        dict(id="STERN_CARGO_S", kind="cargo", x0=43, x1=45, z0=3, z1=5),
        dict(id="STERN_CARGO_N", kind="cargo", x0=43, x1=45, z0=24, z1=26),
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
    return dict(grid_metres=3, ship_bounds=[-16, 58, -3, 32],
                body_bounds=[0, 42, -1, 30], elevations=[-6.4, 0, 3.4],
                zones=zones, corridors=corridors, lifts=lifts, links=links)
