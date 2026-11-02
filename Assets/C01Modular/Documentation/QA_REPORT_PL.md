# C01 PASS 02 v2.0 — raport QA

Data lokalna: 29.10.2026, Europe/Warsaw. **Wynik dostępnych testów: PASS**. Status nie obejmuje etapów NOT RUN opisanych niżej.

## Wynik i pliki

Gotowy master zawiera 83 pozycje źródłowe: 18 podłóg pomieszczeń, dodatkowy podest wejścia, 18 sufitów, 24 odcinki ścian i 22 współdzielone węzły. Trzy W04 zawierają zagnieżdżone framugi i skrzydła. W scenie jest 820 pełnych brył z detalami i colliderami.

Biblioteka: 15 osobnych modeli źródłowych, po jednym FBX i OBJ, odpowiadające im prefabrykaty oraz master. W00 ma fizycznie pełną szerokość 3 m; infille systemu grafowego mają 2,70 m plus współdzielone końcówki węzłów. Sceny: ThreeRooms oraz JointLab.

## Audyt v1.3 — przyczyny

Pomierzono 10 rzeczywistych OBJ i porównano ich obrysy z JSON. Wykryto 59 części niepołączonych powierzchniowo z główną bryłą modelu. Podłoga miała uniesione nakładki do 9 mm nad poziomem chodu i przerwy od 1 mm; detale ścian miały warstwy powietrza 1–2 mm. Słupek 0,28 m tworzył uskok względem rdzenia 0,20 m i wykończenia 0,266 m. Listwa słupka była w całości schowana w jego objętości. Dotychczasowa walidacja pomijała dekoracje, pary części wewnątrz jednego modelu i brakujące powierzchnie. Ramy i skrzydła nie dziedziczyły transformacji ściany; jedno E przełączało wszystkie drzwi.

Dowody: `QA/baseline_audit.json`, `QA/regression_RED_v13.log`. Wszystkie 3 nowe testy regresyjne wykazały błędy w starej paczce. Oryginalnego ZIP i Baseline nie zmieniono.

## Wykonane kontrole

| Kontrola | Wynik | Rzeczywisty dowód |
|---|---|---|
| Python — regresje i akceptacja | PASS, 12 testów | python_tests.log |
| Celowe uszkodzenia | PASS, 17 odrzuconych wariantów | mutation_evidence.json |
| Pełna objętość każdego modelu | PASS; dokładne przekroje wszystkich istotnych warstw | static_qa.json; validate_kit.py |
| Pole brakującej podłogi / sufitu | 0 / 0 m² | static_qa.json |
| Niepożądane penetracje wszystkich brył | 0 w Unity; 0 w Python | unity_geometry_qa.json; static_qa.json |
| Drzwi 0–90°, co 1° | 273 pozycji; bez kolizji | oba raporty geometrii |
| Sockety i transformacje Unity | 179 kontroli; warianty w 4 orientacjach | unity_geometry_qa.json; unity_editmode.xml |
| Powierzchnie podłogi i sufitu w Unity | 297 promieni na rzeczywistych colliderach | unity_geometry_qa.json |
| Blender 5.2.2 — zapis .blend, FBX, OBJ, GLB | PASS | blender_final.log; Source/; Models/ |
| FBX → Blender | 15 pełnych modeli, każda część i ściany | blender_export.json |
| FBX → Unity | 15 pełnych modeli, tożsamość/ilość części, osie, obrysy i trójkąty | unity_geometry_qa.json |
| Kompilacja i generowanie Unity | PASS, 6000.3.14f1, URP 17.3.0 | unity_final.log; natywne .prefab/.unity |
| Unity EditMode | PASS, 7 testów | unity_editmode.xml |
| Unity PlayMode | PASS, 1 test | unity_playmode.xml |
| Zapisane rendery Unity + ocena wizualna | 10 rzeczywistych ujęć; PASS w sprawdzonych ujęciach | Screenshots/; visual_review.md |

Test PlayMode otwiera kolejno każde drzwi, czeka na rzeczywiste Update i FixedUpdate, potwierdza bezruch pozostałych, sprawdza przejście kapsuły przy otwarciu i blokowanie przy zamknięciu, a następnie powrót zawiasu do socketu. Jedno zaliczenie tego testu obejmuje wszystkie trzy drzwi.

`doorSolidTests` w raporcie Unity liczy tylko kandydatów po konserwatywnym odrzucaniu AABB. Może wynosić 0, gdy żadna bryła skrzydła nie ma wspólnego AABB z nieruchomą konstrukcją w żadnej z 273 pozycji. Dodatkowo wykonano niezależny SAT w Python i rzeczywiste testy kapsuły w Unity. Brak kolizji nie jest jedyną podstawą wyniku: osobno badana jest kompletność objętości i powierzchni.

## Poprawki po niezależnym przeglądzie

Usunięcie rdzenia podłogi/sufitu, części skrzydła lub zawiasu nie mogło być akceptowane przez kontrolę samej powierzchni. Dodano pełne wymagane objętości i testy negatywne (najpierw rzeczywiste FAIL, później PASS). Unity kontroluje również istnienie oraz transformacje całych zagnieżdżonych modułów. Eksporty są porównywane część po części. Przegląd opisano w `QA/code_review.md`.

Pierwszy rzeczywisty import Unity wykazał odbicie osi X FBX — naprawiono konwersję prawoskrętną/lewoskrętną w kopiach siatek eksportera, bez korekt pozycji modeli w scenie. Pierwsza kompilacja ujawniła niezgodny Input System 1.12.0 pochodzący z szablonu; projekt używa przetestowanej wersji 1.17.0. Historyczne logi FAIL zachowano, a końcowe wyniki są w plikach wskazanych w tabeli.

## Zakres i pozostałe ograniczenia

Nie stwierdzono pozostałego błędu P0 w dostarczonym układzie i sprawdzonym kontrakcie. Nie oznacza to walidacji dowolnej przyszłej geometrii lub konfiguracji.

- Pokoje 6×9 m i cały układ 18×9 m są wymiarami osi konstrukcyjnych. Przy ścianie 0,30 m światło pokoju wynosi 5,70×8,70 m; zewnętrzne ściany wystają 0,15 m poza osie. Podest wejścia jest poza prostokątem pomieszczeń.
- Światło drzwi 1,80×2,40 m; luzy ruchowe są jawne, dość duże i zamierzone (szczegóły w STANDARD_PL.md). Nie dodawano uszczelek, zamków, szczegółowych zawiasów ani deklaracji hermetyczności.
- Docelowy zakres testów architektury to jednostkowa skala i obroty co 90°. Skalowanie całego zestawu, dowolne kąty ścian oraz dowolne sceny użytkownika nie są objęte zaliczeniem.
- Warianty wyglądu zachowano jako płaskie podziały materiałów. Nie zwiększano szczegółowości przed naprawą modularności.

**NOT RUN:** osobny build i uruchomienie samodzielnego playera Windows; ręczny test myszy/klawiatury przez człowieka; import dodatkowych GLB/OBJ do Unity. GLB i OBJ rzeczywiście wyeksportowano, a FBX rzeczywiście zaimportowano i zmierzono w Unity oraz Blenderze. Nie deklaruje się testu playera na podstawie PlayMode.

## Repozytorium

Archiwum wejściowe i folder roboczy nie zawierają `.git`; nie wskazano repozytorium ani remote. Gałąź i PR: **NOT RUN — repozytorium niedostępne**. Nie użyto innego projektu z pulpitu jako zastępczego repozytorium.

## Integralność i odtwarzanie

Hash manifestu: `b1f6831bb79f992746c68b536008faf4796d39aae2a4135f295b2d44e746a4a8`. `QA/file_hashes.json` obejmuje pliki dostawy, a ZIP jest ponownie czytany i porównywany z tymi hashami. `Tools/run_all.ps1` odtwarza generowanie i dostępne testy. Wersję v1.3 zachowano w Baseline.

Odniesienie do zgodności Input System z gałęzią Unity: [oficjalne informacje wydania 6000.3.1f1](https://unity.com/releases/editor/whats-new/6000.3.1f1).
