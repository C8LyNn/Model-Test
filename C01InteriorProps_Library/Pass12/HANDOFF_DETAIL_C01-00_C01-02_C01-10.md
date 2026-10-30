# C01-03 DETAIL PASS12 — RZECZYWISTE ZMIANY ŹRÓDEŁ I BRAMKI QA

Zlecenie: https://github.com/C8LyNn/Model-Test/issues/36 ; problem eksportów https://github.com/C8LyNn/Model-Test/issues/33 . Istniejący Draft PR #27, bez merge.

## Realne edycje źródeł OBJ/glTF w PR producentów

| Model | Przed (części/V/F/T) | Po (części/V/F/T) | Source SHA-256 | Status |
|---|---|---|---|---|
| P18-03 wózek | 17/208/270/348 | 53/872/1110/1532 | 3996be33105a17163d4c8a753012aca891c1b19b156abf32ddab02d8fbca50e0 | Source PASS, binary STALE |
| P18-02 regał | 17/136/102/204 | 47/600/666/1012 | d37f3347dabf84bf315b27b1d24bc517dda77265bb60da2c086d28bdcf3e3472 | Source PASS, binary STALE |
| P18-01 skrzynia | 15/120/90/180 | 37/416/426/684 | 7e353b62210df2cdefc03e85a11c109dcf4ca5d51b776c2ab45452ae8239be79 | Source PASS, binary STALE |
| P17-02 czytnik | 20 instancji / 240T | 38 instancji / 536T | 3fba39e0e5813e6abc486c8ca5685247b59b0614a4186a545dd57903ed51e077 | C01-02 disputed source FAIL; binary STALE |

P18-03: 36 nowych części, po dziewięć na koło (widełki, mocowanie ramy, wzmocnienie, oś, piasty, śruba). Cztery oryginalne ruchome koła i kontakt na Y=0 zachowane. Odchyłka osi od słupków 50mm X/45mm Z nie została ukryta arbitralnym przesunięciem; funkcjonalne połączenia pomostowe dodano w oryginalnym OBJ. Realna kinematyka i kolizje NOT RUN.

P18-02: 30 nowych części (12 wsporników, 12 śrub półek, 2 mocowania etykiet, 4 śruby). Oryginalne etykiety: 50mm powyżej górnej półki i 10mm powyżej listwy. Nowe blachy montażowe w zakresie Y=1.960..2.072 łączą półkę/listwę i dolną część etykiet. Source AABB contact PASS, Blender BVH NOT RUN.

P18-01: 22 nowe części, w tym 8 podkładów listew, 2 zespoły zawiasów, 2 zespoły zatrzasków i 4 śruby wieka. Nowa bryła wystaje o 15mm przed poprzedni obrys i 7mm wyżej: C01-01 musi potwierdzić tolerancję rozmiaru.

P16-01..07: siedem dodatkowych realnych plików OBJ w PR #12/#28, łącznie 57 nowych części i 1280 trójkątów (160/160/160/240/196/216/148). Sprawdzono rzeczywiste v/vt/vn/f, wszystkie indeksy poprawne, zero trójkątów zerowego pola. W P16-06 źródło rozróżnia STATIC i ROTOR. Natomiast kompletna nowa natywna .blend i Blender binary FBX NIE istnieje w tych PR.

## P17-02: niezależny QA wymaga sprostowania analizy skalowania

Raport C01-02 FOUR_PILOT_INDEPENDENT_SOURCE_QA.json oznaczył P17-02 FAIL_SOURCE_GEOMETRY_SEVERE jako rzekomo wielometrowe śruby. Dokładnie ten sam glTF Git blob 7f183922dab2b5e416af7a8dc30a46c1b6990286 jawnie zawiera scale=[0.0045,0.0045,0.003] przy każdej instancji śruby. Po poprawnym przekształceniu śruba ma 9x9x3mm, a obrys całego czytnika pozostaje 180x280x70mm. Prowadnice też używają legalnego skalowania i instancjonowania mesh4. Dowód: ./P17_02_INDEPENDENT_QA_TRANSFORM_REVIEW.json oraz zgłoszenie https://github.com/C8LyNn/Model-Test/issues/8#issuecomment-6532212951 . C01-03 NIE NADPISUJE formalnego QA. Nadal pełny BLOCKED; wymagany ponowny przegląd rzeczywistych kontaktów po transformacji.

## Archiwum i wersje

Machine registry 36 modeli: ./asset_registry_36.json
Rzeczywiste SHA i V/F/T pilota: ./PILOT_LATEST_SOURCE_SHA256.json
Siedem źródeł P16: ./P16_ALL_SEVEN_DETAIL_SOURCE_SHA256.json
Dokładne źródłowe BEFORE P18: ./pilot_source_baseline.json

## Odbiór rzeczywistych plików

Nowe edytowalne źródła modeli: 11. Statyczne source checks C01-03: 11. Niezależna QA source P18: 3 PASS. P17-02: 1 kontestowany FAIL źródła. Nowe .blend zapisane przez Blendera 4.x: 0. Nowe binary FBX wyeksportowane i reimportowane przez Blendera: 0. Pełne C01-02 QA końcowego FBX: 0/36. Realne Unity 6 URP prefab PASS: 0. Wszystkie 36 wydaniowo BLOCKED.

NEEDS_OWNER_ACTION: GitHub-hosted CI C01 nie przydziela wykonujących runnerów; lokalnie brak Blender 4.x, bpy, git-lfs i Unity. Wymagane rzeczywiste środowisko Blender na Windows z Git LFS albo odblokowane Actions, natywne eksporty SHA-256, wireframe/shaded BEFORE/AFTER, reimport, podpis C01-02 i test Unity. Nie wykonywano merge, zmian statku ani nowych asset ID.
