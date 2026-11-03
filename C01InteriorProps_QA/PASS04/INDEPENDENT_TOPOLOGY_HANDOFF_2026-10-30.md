# C01-02 — PASS 04 / niezależne QA 36 FBX

**Data:** 2026-10-30 · **Zakres:** #33 / #30 · **PR QA:** #13 (DRAFT)

## Rzeczywiście wykonane

- Pobrano GitHub Actions ZIP z 6 poprawnych przebiegów produkcyjnych C01-17/18/19, dodatkowo starszy komplet P19-W01. Zweryfikowano ZIP CRC, fizyczny nagłówek FBX Binary, odczytano rzeczywistą tablicę wierzchołków/PolygonVertexIndex/warstwy normalnych i UV0.
- **22/36 oryginalnych binarnych FBX** przeszły niezależny indeksowy audyt geometrii: brak loose vertices, duplicate/degenerate native polygons, zero-length lub >2-use polygon edges. Wykryte 5 potencjalnie niebezpiecznych n-gonowych triangulacji jest opisane osobno.
- Każdy zapis z indeksem V/E/F/T i skróconym SHA znajduje się w `36_MODELS_GATE.csv`; pełne SHA-256 22 binariów, źródłowe nazwy artefaktów oraz SHA ZIP w pobieralnej paczce C01-02 PASS04. **Artefakt CI ma własny commit SHA; nie wolno traktować HEAD PR producenta jako SHA przetestowanego binarium.**
- Testy regresyjne QA uruchomione **10/10 PASS na prawdziwych FBX**, bez mocków. To nie oznacza zatwierdzenia modeli.
- **Blender independent opening/reimport: NOT RUN. Unity import/PlayMode: NOT RUN.** Programy nie są dostępne w środowisku QA.

## P0 — P19-05/07/08 (rzeczywiste FBX przed→po PASS03)

| ID | V | E | F | Trójkąty sum(n−2) | n-gony >4 | Degenerate w teście fan | Krawędzie użyte >2× przez fan |
|---|---|---|---|---|---:|---:|---:|
| P19-05 | 88→88 | 132→140 | 66→66 | 132→148 | 3 | 1 | 1 |
| P19-07 | 104→136 | 156→204 | 78→78 | 156→252 | 16 | 19 | 2 |
| P19-08 | 96→149 | 144→241 | 72→100 | 144→282 | 35 | 7 | 3 |

**Stan PASS04:** trzy nowe próby workflow C01-19 triangulation `41094095740`, `41094682073`, `41094703040` zakończyły się **FAILURE**. Nie ma zaakceptowanego nowego eksportu eliminującego n-gony. **P19-05/07/08: FAIL — kompatybilność triangulacji**, nie faktyczny Unity importer FAIL. Producent powinien wykonać kontrolowaną triangulację w Blenderze i po udanym CI udostępnić dokładny finalny FBX wraz z SHA. Nie stosować naiwnego fan jako metody naprawy.

**Nowe kandydaty:** P19-01 (13 degeneratów w stres-teście fan, 1 potencjalne T-junction), P19-02 (11 degeneratów i 5 fan edges o >2 użyciach). Także kierujemy do C01-19; nie udajemy rzeczywistych błędów Unity. W P19-07 znaleziono 8 kandydatów vertex-on-edge; P19-08 nie wykazał kandydatów w obrębie tej samej siatki. Dla wszystkich modeli niewykonane pozostają testy cross-part intersections i pełna topologia w Blenderze.

## Pozostałe blokady

- **C01-16 — P16-01..07:** dwie ostatnie próby CI z Blender binary export `41094504957` i `41094525422` zakończyły się FAILURE. W QA brak autentycznych natywnych binarnych FBX, status 7× BLOCKED.
- **C01-15 — P15-01..07:** istnieją manifesty/LFS oraz udane starsze CI producenta, ale brak w tej sesji niezależnie pobranych/zweryfikowanych finalnych fizycznych 7 FBX, 7× BLOCKED.
- **C01-17/18/19 — 22 FBX:** pozytywne wyniki dotyczą zidentyfikowanych dokładnych archiwów GitHub Actions, a nie automatycznie aktualnych HEAD producentów; nie ma potwierdzenia Unity/Blender i szerszego audytu z-fighting/cross-part.

## Release gate

**0 FULL APPROVED / 5 FAIL (ryzyko triangulacji / static export preflight) / 31 BLOCKED.**

Żadnego modelu nie naprawiał C01-02; właściciele modeli w istniejących PR odpowiadają za zmianę siatek. Nie modyfikowano konstrukcji statku. Brak merge. #33/#30 pozostają otwarte. Kolejne kroki: C01-19 poprawia 5 wskazanych eksportów i uruchamia Blender CI PASS04, C01-16 uzupełnia 7 natywnych źródeł, C01-15 publikuje 7 dostępnych binariów, C01-02 wykonuje retest SHA, C01-10 potwierdza import rzeczywistych prefabów w Unity 6 URP.

**Zasada:** statyczny PASS na pliku FBX nie zastępuje testu importera Blender ani Unity.
