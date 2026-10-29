# C01 v3.1 — większy statek, dłuższe boczne korytarze

Scena: `Assets/C01ShipV3/Scenes/C01_Ship_FromPlan.unity`.
Prefab nadrzędny: `Assets/C01ShipV3/Prefabs/C01_SHIP_FROM_PLAN_MASTER.prefab`.

## Wymiary

| Element | v3.0 | v3.1 |
|---|---:|---:|
| Szerokość nominalna wszystkich korytarzy | 3 m | 3 m |
| Długość każdej z 6 bocznych odnóg | 3 m | 9 m |
| Korpus | 45 × 21 m | 45 × 33 m |
| Kajuta | 6 × 3 m | 6 × 9 m |
| Powierzchnia podłóg, z mostkiem, rufą i podestami | 1161 m² | 1845 m² |

Dodano moduły siatki 3 m; skale wszystkich instancji pozostają równe 1. Sześć sektorów ma nadal 15 × 6 m. Zachowano 12 kajut, 36 drzwi, 4 śluzy i 5 silników. Wejścia do kajut leżą w środkowej części dłuższych odnóg.

## Otwieranie i sterowanie

**Tools → C01 Ship → Open imported ship**, następnie Play i zakładka Game.
**1**: podgląd całości; **2**: chodzenie; **WASD + PPM**: ruch i rozglądanie; **E**: drzwi do 3,5 m; **R**: dach; **L**: podpisy; **O/K**: zwykłe drzwi. Śluzy obsługuj indywidualnie przez E.

**Tools → C01 Ship → Verify imported project** powtarza audyt i wszystkie testy. **Rebuild and verify expanded ship** odtwarza prefab/scenę z bieżącego manifestu, wykonuje audyt, testy i eksport paczki. Najpierw zapisz sceny. Generator zachowuje nazwę projektu, jego profile URP, przestrzeń koloru i istniejącą listę scen.

## Źródła

- `Tools/build_ship.py`: domyślnie 9 m bocznej odnogi, dopuszczalne długości w wielokrotnościach 3 m.
- `Assets/C01ShipV3/Data/ship.json`: wspólne dane montażowe dla Unity, Blendera i audytów.
- `Tools/validate_ship.py`, `Tests/`: niezależna walidacja geometrii oraz wymiarów zatwierdzonej konfiguracji 9 m.
- `Tools/blender_ship.py`: rzeczywisty eksport Blender, FBX/OBJ/GLB oraz testy powrotnego importu FBX.
- `C01Source/C01_Ship_FromPlan.blend` i `.glb`: zaktualizowane źródło i złożony statek.
- `Assets/C01ShipV3/Models`: 62 aktualnie używane modele niestandardowe; bazowe moduły w C01Modular. Starsze nieużywane warianty pozostały zachowane.

Uruchomienie generatora wymaga Pythona, a eksportu Blender — zainstalowanego Blendera. Walidacja Python jest przypięta do wymiarów dostarczonej wersji v3.1; zmiana długości wymaga dostosowania oczekiwań projektu i ponownego audytu.

## QA w Unity 6000.3.14f1

11 testów Python, 15 EditMode i 5 PlayMode. Test ruchu przechodzi pełne sześć bocznych odnóg do sektorów oraz korytarz główny, kajutę i wyjście rufowe. Testy brakującej podłogi i sufitu sprawdzają kontrolowane FAIL z konkretnym ID, a nie awarię walidatora. 13 rzeczywistych podglądów Unity w `C01Ship_QA/Screenshots`.

Wynik bieżącego pełnego przebiegu: `C01Ship_QA/integration_status.txt`. Raport: `C01Ship_QA/QA_REPORT_PL.md`; dowody NUnit: `model_test_editmode.xml`, `model_test_playmode.xml`. Pliki negative i red zawierają celowo wyniki nieudane; dokumentują wykrywanie braków oraz wcześniejszą reprodukcję naprawionego problemu.

NOT RUN: samodzielny build aplikacji, ręczna sesja klawiaturą/myszą, opcjonalny import GLB/OBJ do Unity. Źródło Blender, FBX/OBJ/GLB wykonano rzeczywiście ponownie dla v3.1. Zapisany NavMesh służy audytowi otwartych drzwi; ruch gracza używa colliderów.

Poprzednie wersje pozostają w historii Git i w paczce Desktop v3.0. Przed zmianą wykonano dodatkowo kopię `C01_Ship_Expanded_v3.1/Previous_ModelTest_v3.0_assets.zip` na Pulpicie.
