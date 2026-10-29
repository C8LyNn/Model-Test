# C01 — statek z planu v3.0 / raport QA

29.10.2026, Europe/Warsaw. **Wynik dostępnych testów: PASS.**

## Dostarczona scena

Native Unity: `Assets/C01ShipV3/Scenes/C01_Ship_FromPlan.unity`. Master: `Assets/C01ShipV3/Prefabs/C01_SHIP_FROM_PLAN_MASTER.prefab`.

Układ odpowiada przekazanemu rzutowi: mostek, 12 kajut, sześć sektorów, korytarze poprzeczne, D1/D2 na głównej osi, D3/D4 na rufie, dwa wyjścia i pięć napędów. Zachowano wyłączne wejścia kajutowe z poprzecznych korytarzy i połączenia boczne sektorów. Szczegóły pozycji i przyjętego metrażu są w PLAN_MAPPING_PL.md.

614 edytowalnych instancji montażowych, 5393 bryły z colliderami, 137 odcinków ścian i 112 współdzielone węzły. 132 płytki podłogi, dokładnie 1161.00 m² powierzchni pokładu z mostkiem, rufą i podestami. Powierzchnie techniczne osłony dziobu są osobnymi częściami kadłuba.

## Rzeczywiste testy i dowody

| Kontrola | Wynik | Dowód |
|---|---|---|
| Python — topologia, podłogi, usterki, geometra i ruch drzwi | PASS, 6 testów | layout_tests.log |
| 12 kajut i dokładnie 12 wejść z poprzecznych korytarzy | PASS | layout_qa.json; layout_mutations.json |
| 36 osobnych drzwi i 5 napędów | PASS | ship.json; layout_qa.json |
| Wszystkie bryły, drzwi zamknięte i otwarte | PASS, 0 penetracji | geometry_qa.json |
| Pełny ruch pojedynczych drzwi co 1° | PASS, 3276 pozycji | sweep_qa.json |
| Niezależne kąty sąsiadujących skrzydeł co 1° | PASS, 132496 kombinacji | sweep_qa.json |
| Unity — kompilacja, natywna scena/prefab, collidery, źródłowe części | PASS, 6000.3.14f1 URP | unity_ship.log; unity_ship_qa.json |
| Unity — fizyka ruchu i kapsuła człowieka w przejściach | PASS, 3276 pozycji drzwi | unity_ship_qa.json |
| Unity — pokrycie powierzchni | PASS, 1788 rzeczywistych promieni | unity_ship_qa.json |
| Unity NavMesh — rzeczywiste trasy od mostka | PASS, 35/35 stref | unity_ship_qa.json, routes |
| Unity EditMode — nowe i zachowane testy C01 | PASS, 12 | unity_editmode.xml |
| Unity PlayMode — nowe i zachowane testy C01 | PASS, 4 | unity_playmode.xml |
| Blender — zapis źródła, FBX/OBJ/GLB | PASS, 54 nowych modeli | blender_ship.log; Source/; Models/ |
| FBX → Blender, każda część: wierzchołki i ściany | PASS | blender_ship_qa.json |
| Nowe FBX → Unity: części, skala i osie | PASS, 54 modeli | unity_ship_qa.json |
| Ocena wizualna względem planu | PASS w zapisanych ujęciach | Screenshots/; visual_review.md |
| Zachowanie poprzedniej v2.0 | PASS, 586 plików | previous_version_preservation.json |

Testy PlayMode obejmują: otwieranie kolejnych par czterech śluz z kontrolą, że drugie skrzydło pozostaje zamknięte; niezależne ustawienia bliskich drzwi w rzeczywistej fizyce; ruch CharacterController przez mostek, główny korytarz, D1, D2, wejście rufowe, kajutę i wyjściową śluzę D3. Zachowany test starego zestawu również został wykonany.

132 496 kombinacji niezależnych kątów (liczba aktualnego modelu: 132496) sprawdzono dokładnym SAT w Python dla pełnych obrysów skrzydeł i segmentów zawiasów. Test PlayMode osobno kontroluje kolizje rzeczywistych colliderów sąsiednich drzwi przy wybranych krytycznych kątach, w tym kątach odtwarzających znalezione wcześniej błędy. Nie deklaruje się wykonania wszystkich kombinacji przez silnik fizyki Unity.

`doorCandidates` jest liczbą par po odrzuceniu nieprzecinających się AABB; może wynosić 0 w naprawionym układzie. Każda z 3276 pozycji ma aktualizowane rzeczywiste collidery. Uzupełnia to dokładny SAT, testy kapsuły, niezależne pozy drzwi oraz test fizycznego ruchu gracza. Sam wynik „0 kolizji” nie stanowi całej walidacji.

NavMesh zbudowano rzeczywiście z colliderów. Parametry: promień 0,28 m, wysokość 1,80 m, schodek 0,18 m, voxel 0,07 m. Sprawdzono PathComplete do wszystkich 33 stref wewnętrznych i dwóch podestów zewnętrznych. Jest to konfiguracja **ze wszystkimi drzwiami otwartymi**. Zapisany NavMesh nie jest dynamicznie aktualizowany przez interakcję gracza; gracz porusza się przy użyciu CharacterController i fizycznych colliderów.

## Naprawy podczas integracji

Pierwsza rzeczywista kontrola Unity wykryła zderzenie skrzydła z ładunkiem, zbyt ciasny narożnik poprzecznego przejścia (3 kajuty nieosiągalne) oraz luki walidacji niezależnych kątów. Dodano pełne testy ruchu, zmieniono orientację standardowych modułów drzwiowych i położenie wyposażenia poza pełnym zakresem ruchu. Nie zmniejszano promienia agenta ani grubości ścian. Zachowano raporty sprzed napraw: unity_before_handing_fix.json, sweep_before_handing_fix.json i logi regresji RED.

Dodatkowy test bajtów pliku NavMesh ujawnił nadpisywanie dostawy przez test negatywny z usuniętą framugą. Obecnie audyty negatywne pracują na tymczasowym NavMesh; regresję odtworzono jako FAIL przed poprawką i potwierdzono w końcowej zielonej serii. Przegląd niezależnego recenzenta i poprawki opisano w code_review.md.

## Ograniczenia

- Skala jest decyzją wykonawczą: środek statku 45×21 m, kajuty 6×3 m, sektory 15×6 m, korytarze nominalnie 3 m. Wymiary są osiowe; światło jest mniejsze o grubość ścian. D1/D2 mają długość 6 m. Nie deklaruje się odtworzenia pikselowych proporcji bezwymiarowego rysunku.
- To jedna wyposażona scena w stylu C01, z prostymi modelami funkcjonalnymi. Zbudowano pełny układ, nie dziesięć wariantów stylistycznych.
- Śluzy mają działającą blokadę par drzwi. Nie symulują ciśnienia, próżni, uszczelek ani dekompresji. Pięć napędów to osobne edytowalne instancje modelu wizualnego; brak symulacji lotu.
- **NOT RUN:** osobny build/uruchomienie playera poza Edytorem; ręczna sesja myszy i klawiatury przez człowieka; import dodatkowych OBJ/GLB do Unity. Eksporty OBJ/GLB rzeczywiście wykonano; FBX rzeczywiście zaimportowano w obu programach.
- Nie dostarczono repozytorium/remote. Nie tworzono gałęzi ani PR w innym projekcie.

Nie stwierdzono pozostałej kolizji lub nieosiągalnej wymaganej strefy w zweryfikowanym układzie. Wynik nie obejmuje przyszłych ręcznych zmian sceny, dowolnej skali ani pozasiatkowych połączeń.

## Integralność

SHA-256 manifestu: `07d02ddb115aecc57940f37a21a416e16403e50311f47cd330ae8dbac0a61ab4`. Plan źródłowy zachowano w Reference/. `QA/file_hashes.json` służy do sprawdzenia zawartości ZIP; wynik ponownego odczytu plików archiwum zapisuje package_verification.json.
