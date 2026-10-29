# C01 — statek z planu / v3.0

Gotowa scena statku oparta na przekazanym rzucie. Zawiera mostek, 12 kajut, sześć sektorów, korytarze poprzeczne, cztery śluzy D1–D4, dwa wyjścia rufowe i pięć napędów. Zachowano naprawione moduły C01; dorobiono dziób, osłony kadłuba i proste wyposażenie. Poprzedni folder `C01_PASS02_v2.0` pozostaje osobno.

## Otwórz scenę

1. Otwórz `UnityProject/` w **Unity 6000.3.14f1** (URP 17.3.0, Input System 1.17.0).
2. Otwórz `Assets/C01ShipV3/Scenes/C01_Ship_FromPlan.unity`.
3. Prefab całej konstrukcji: `Assets/C01ShipV3/Prefabs/C01_SHIP_FROM_PLAN_MASTER.prefab`.
4. Włącz Play. Początkowo pokazany jest cały pokład ze zdjętym sufitem i etykietami pomieszczeń.

Pełna paczka assetów do importu: `QA/C01_Ship_FromPlan_v3.0.unitypackage`. Zawiera zarówno potrzebny C01, jak i nowe assety. W istniejącym projekcie wymagane są URP, Input System, moduł AI i Unity Test Framework; pełny projekt ma gotowy manifest i lockfile. Przed importem do własnego projektu wykonaj standardową kopię tego projektu — nazwy bazowej biblioteki C01 są zachowane.

## Sterowanie

| Klawisz | Działanie |
|---|---|
| 1 | Widok całego statku |
| 2 | Spacer, początek na mostku |
| WASD + prawy przycisk myszy | Ruch i rozglądanie |
| Q / Z w trybie lotu | Wysokość kamery |
| E | Drzwi wskazane środkiem obrazu, do 3,5 m |
| R | Pokaż/ukryj sufit |
| L | Pokaż/ukryj etykiety |
| O / K | Otwórz/zamknij zwykłe drzwi wewnętrzne |

Osiem drzwi śluz obsługuje się indywidualnie przez E. Otwieranie jednych najpierw zamyka drugie. Jest to blokada drzwi; nie symulacja atmosfery lub ciśnienia. Napędy są modelami wizualnymi. Scena służy do oglądania i eksploracji układu.

## Skala i zgodność z planem

Rysunek nie podawał wymiarów. Przyjęto siatkę 3 m: środkowa część pokładu 45×21 m, kajuty 6×3 m, duże sektory 15×6 m, główny i poprzeczne korytarze szerokości nominalnej 3 m. Są to wymiary osiowe; ściany mają grubość 0,30 m.

Zachowano topologię rysunku, w szczególności wejścia do kajut wyłącznie z korytarzy poprzecznych. D1 leży pomiędzy parami 02/03 i 08/09, a D2 pomiędzy 04/05 i 10/11. D1/D2 mają długość 6 m, aby zachować wspólny raster oraz środki przy x=15 i x=30. Dodano niewielkie zewnętrzne podesty przy wyjściach. Zbudowano jeden wariant stylistyczny C01.

Mapa szczegółowa: `docs/PLAN_MAPPING_PL.md`. Dowody testów: `docs/QA_REPORT_PL.md` i `QA/verification_summary.json`.

## Edycja i źródła

- Każdy z 614 elementów montażowych pozostaje osobnym obiektem / instancją prefabu. Ściany, podłogi i sufity bazowe zachowują oryginalną skalę i sockety C01.
- Manifest całej sceny: `Assets/C01ShipV3/Data/ship.json`. Generator: `Tools/build_ship.py`. Unity i Blender odczytują tę samą geometrię oraz transformacje.
- Nowe modele/prefaby: `Assets/C01ShipV3/Models/` i `Prefabs/`. Zawierają 54 definicje nowych elementów geometrycznych, w tym fragmenty kadłuba, kliny podłogi/sufitu i wyposażenie. Model napędu jest wspólnym źródłem pięciu osobnych instancji.
- Edytowalny Blender: `Source/C01_Ship_FromPlan.blend`. Kolekcja `SOURCE_MODULES_editable` zawiera źródła; jest ukryta. Kolekcja `Ceilings` przełącza dach.
- Dodatkowy złożony GLB: `Source/C01_Ship_FromPlan.glb`.
- `Assets/C01ShipV3/Data/Ship_OpenDoors_NavMesh.asset` to wynik kontroli tras w konfiguracji ze wszystkimi drzwiami otwartymi. Nie jest dynamiczną nawigacją aktualizowaną przy każdym ruchu drzwi. Gracz korzysta z rzeczywistych colliderów.

Menu `Tools > C01 Ship` odtwarza scenę. `Tools/run_ship.ps1` uruchamia generowanie danych, eksport Blender, Unity QA, testy, raport i pakowanie. Ręczne zmiany sceny nie są automatycznie przenoszone z powrotem do manifestu — generator odtwarza układ z JSON.

Prawdziwe rendery Unity znajdują się w `QA/Screenshots/`: rzut, przekrój, zamknięty kadłub i wnętrza. Obraz źródłowy zachowano w `Reference/ship_plan.png`.
