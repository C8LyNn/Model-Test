import unittest
import grid_layout


class GridLayoutTests(unittest.TestCase):
    def test_ship_and_decks(self):
        layout = grid_layout.build()
        self.assertEqual(layout["ship_bounds"], [-16, 58, -2, 32])
        self.assertEqual(layout["grid_metres"], 3)
        self.assertEqual(layout["elevations"], [-12.4, 0, 6.4])

    def test_cabins_and_corridors_remain_unstretched(self):
        layout = grid_layout.build()
        for deck in (1, 2):
            cabins = [z for z in layout["zones"] if z["deck"] == deck and z["kind"] == "cabin"]
            self.assertEqual(len(cabins), 12)
            self.assertTrue(all(z["x1"]-z["x0"] == 3 and z["z1"]-z["z0"] == 3 for z in cabins))
            self.assertTrue(all(c["width"] == 1 for c in layout["corridors"] if c["deck"] == deck))
            for c in cabins:
                baths = [b for b in layout["zones"] if b.get("parent") == c["id"]]
                self.assertEqual(len(baths), 1)
                self.assertEqual((baths[0]["x1"]-baths[0]["x0"], baths[0]["z1"]-baths[0]["z0"]), (2, 1))

    def test_lifts_and_zone_ownership(self):
        layout = grid_layout.build()
        lifts = layout["lifts"]
        self.assertEqual(len([l for l in lifts if l["kind"] == "cargo"]), 2)
        self.assertEqual(len([l for l in lifts if l["kind"] == "passenger"]), 2)
        self.assertTrue(all(l["x0"] >= 42 for l in lifts if l["kind"] == "cargo"))
        self.assertTrue(all(l["z0"] not in (14, 15) for l in lifts if l["kind"] == "passenger"))
        for deck in (0, 1, 2):
            zones = [z for z in layout["zones"] if z["deck"] == deck and not z.get("parent")]
            cells = {}
            for z in zones:
                for x in range(z["x0"], z["x1"]):
                    for y in range(z["z0"], z["z1"]):
                        self.assertNotIn((x, y), cells, (z["id"], cells.get((x, y))))
                        cells[x, y] = z["id"]
            self.assertEqual(len(cells), 42 * 30, "Every body cell must have exactly one owner")

    def test_all_rooms_have_a_path_from_main_corridor(self):
        layout = grid_layout.build()
        for deck in (0, 1, 2):
            start = f"L{deck}_MAIN"
            reached = {start}
            while True:
                expanded = reached | {b for a, b in layout["links"] if a in reached} | {a for a, b in layout["links"] if b in reached}
                if expanded == reached:
                    break
                reached = expanded
            rooms = {z["id"] for z in layout["zones"] if z["deck"] == deck and z["kind"] not in ("void",)}
            self.assertTrue(rooms <= reached, (deck, sorted(rooms-reached)))


if __name__ == "__main__":
    unittest.main()
