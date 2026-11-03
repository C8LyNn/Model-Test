# C01-03 — DETAIL PASS13 / KONKRETNE BRAKI MONTAŻOWE W ŹRÓDŁOWYCH SIATKACH

**Zlecenie:** [#36](https://github.com/C8LyNn/Model-Test/issues/36); **blokady natywnego eksportu:** [#33](https://github.com/C8LyNn/Model-Test/issues/33). Oryginalne modele bez zmian w gałęzi C01-03; nie łączono PR.

## P0: aktualny C01-18 PR #18, źródłowe OBJ

Model | Rozłączona część | Oś i odległość najbliższego obrysu źródłowych wierzchołków | Konkretna korekta producenta
---|---|---|---
P18-01 | `Lower_Rim` → `Crate_Shell` | Y = 10 mm | Osadzić cokół w korpusie lub dodać ukryte, rzeczywiste mocowania; nie usuwać 0.9m obrysu skrzyni
P18-02 | `Back_Support_0.6` → `Rack_Post_-1.015_-0.365` | X = 30 mm | Dociągnąć obie końcówki belki do ramy lub dodać wsporniki w istniejącym obrysie regału
P18-02 | `Back_Support_1.48` → `Rack_Post_-1.015_-0.365` | X = 30 mm | Jak wyżej, bez losowych ozdobników
P18-03 | `Cart_Shelf_Lip_0_-0.48` → `Cart_Shelf_0` | Y = 5 mm | Zlikwidować rzeczywistą szczelinę geometrii listwa-półka lub podłożyć konstrukcyjny uchwyt
P18-03 | `Cart_Shelf_Lip_0_0.48` → `Cart_Shelf_0` | Y = 5 mm | Jak wyżej
P18-03 | `Cart_Shelf_Lip_1_-0.48` → `Cart_Shelf_1` | Y = 5 mm | Jak wyżej
P18-03 | `Cart_Shelf_Lip_1_0.48` → `Cart_Shelf_1` | Y = 5 mm | Jak wyżej

**Weryfikacja faktyczna:** czytane wierzchołki OBJ w rewizji producenta `24b03911ee423240d03a5de5b39a1655b257b131`, blob SHA-1 P18-01 `3147fbc11da4ad2c4cac9f4c8a520d921d1cd6b7`, P18-02 `2878f4c20a5dc8a51fe31659662f9835b5e451f2`, P18-03 `df5a68c87fd49597c79bbb6f70735f32543489bf`. Rozłączność wykryta z **całą** resztą części każdego modelu (nie tylko z wybranym sąsiadem). Stwierdzone rozłączne AABB nie mogą mieć rzeczywistego kontaktu siatek, choć nakładające się AABB wymagają dodatkowej kontroli trójkątów. Szczegółowy wynik [P18_SOURCE_7_DISJOINT_PARTS_ACTUAL_VERTEX_QA.json](./P18_SOURCE_7_DISJOINT_PARTS_ACTUAL_VERTEX_QA.json).

## P0: P17-02 czytnik — co naprawdę jest rozłączone

Na identycznym pliku glTF `7f183922dab2b5e416af7a8dc30a46c1b6990286` wykonano pełny odczyt zakodowanych pozycji FLOAT32 i translacji + skali instancji, nie tylko metadata accessors.

- Każda z **czterech** śrub ma rzeczywisty wymiar **9 × 9 × 3 mm**. Wszystkie **9 wierzchołków tylnego pierścienia każdej śruby** jest wewnątrz objętości MountBacking, głębokość osadzenia 0.5 mm. Nie są 2-metrowymi ani 0.81-milimetrowymi śrubami. Nie należy ich przeskalowywać bez nowego dowodu.
- Keybed z tyłu: **Z = 0.058 m**, Housing z przodu: **Z = 0.0575 m**. Pozytywna przerwa **0.500 mm**. Rozłączność AABB 38 instancji: **2 grupy, 13 części korpusu ze śrubami i 25 części płyty klawiszy + przyciski + prowadnice**.
- Potrzebna celowana poprawka rzeczywistego źródła P17-02: minimalny kontakt obudowa-płyta przycisków lub realna blacha montażowa. Bez scalania ruchomych części, bez nowych ID. Potem kontrola rzeczywistych trójkątów, normalnych i widoczności.

Dowód [P17_02_ACTUAL_GLTF_BUFFERS_SCREW_AND_KEYBED_CONTACT.json](./P17_02_ACTUAL_GLTF_BUFFERS_SCREW_AND_KEYBED_CONTACT.json). P17-02 obecny producer PR #17 HEAD `cf405ed6636c9788cfd4c9d4d35e99a8683902dc`; autorski source SHA-256 `3fba39e0e5813e6abc486c8ca5685247b59b0614a4186a545dd57903ed51e077`.

## Pozostałe aktywne pakiety

- **C01-15 P15-03:** aktualna autorska specyfikacja + 6 elementów zawiasów; wykonanie Blender, nowy FBX i odczyt w Unity nie istnieje (kandydaci offline, nie produkcja).
- **C01-16 P16-01–07:** 7 plików dodatkowej geometrii OBJ potwierdzone SHA w PASS12, ale 7 nowych natywnych `.blend` i źródłowe eksporty Blender FBX nadal niezatwierdzone.
- **C01-19 P19-02/05:** producent deklaruje rzeczywiste binarne pliki `.blend` i FBX jako kandydatów w ZIP poza repo; natywne otwarcie/zapis przez aplikację Blender, eksport/ponowny import i C01-02 nieprzeprowadzone. P19-01/02/05/07/08 wymagają także zakończenia wcześniejszej poprawy triangulacji.

## Release gate

Źródłowy PASS dla 3 P18 w PASS12 oznacza brak błędnych indeksów/degeneratów, **nie** poprawny montaż; dla tych trzech modeli nowy PASS13 `FAIL_SOURCE_CONTACT`. P17-02 również `FAIL_SOURCE_CONTACT` (Keybed). W sumie **4 modele z 8 potwierdzonymi rozłączeniami**.

36/36 modeli pozostaje `BLOCKED`; nowe Blender 4.x open→save→FBX export→import, prefab/Unity6 oraz ostateczne podpisane QA na nowych SHA `NOT RUN`. C01 Actions run [41119479370](https://github.com/C8LyNn/Model-Test/actions/runs/41119479370) zakończył się przed startem runnera, job `steps=[]`, źródło błędu bez potwierdzenia. Lokalne środowisko C01-03 nie ma Blender/bpy, Git LFS i Unity.

**NEEDS_OWNER_ACTION:** odblokować runner bez zmian płatności albo użyć uprawnionego Windows Blender 4.x+Git LFS. Najpierw producent C01-18 usuwa 7 rozłącznych styków i C01-17 usuwa 0.5mm przerwę Keybed; potem fizyczny zapis `.blend`, nowy FBX, wireframe i render BEFORE/AFTER w Blenderze, dokładny SHA256, niezależne C01-02 i realne Unity 6. Nie merge.
