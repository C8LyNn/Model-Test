# C01 — PASS 02 / Modular Repair v2.0

Naprawiony zestaw konstrukcyjny Space Horror Interiors. Bazowa paczka v1.3 pozostaje w `Baseline/`; nie należy mieszać jej generatora z nowymi assetami.

## Otwieranie

1. Otwórz `UnityProject/` w **Unity 6000.3.14f1**. Projekt zawiera gotowe assety, sceny i ustawiony URP 17.3.0 oraz Input System 1.17.0.
2. Otwórz `Assets/C01Modular/Scenes/C01_PASS02_ThreeRooms.unity`.
3. Master: `Assets/C01Modular/Prefabs/C01_PASS02_ThreeRooms_MASTER.prefab`.
4. W Play użyj osobnych przycisków drzwi w lewym górnym rogu. Prawy przycisk myszy + WASD/Q/Z przesuwa kamerę; E przełącza drzwi wskazane środkiem widoku z odległości do 4 m. Przycisk `Toggle ceilings` pokazuje wnętrze.
5. Scena `C01_PASS02_JointLab.unity` zawiera END, STRAIGHT, CORNER, T i CROSS z tymi samymi prefabami oraz obrotami we wszystkich ćwiartkach.

Alternatywnie zaimportuj `QA/C01_PASS02_v2.0.unitypackage` do projektu Unity 6.3 URP z Input System 1.17.0 i Unity Test Framework 1.6.0. Biblioteki Unity nie są kopiowane do paczki assetów; pełny projekt zawiera manifest zależności i lockfile.

## Wymiary i wymiana wariantów

- Jednostka: 1 m. Krok konstrukcyjny: 1 m. Rozstaw portów architektury: 3 m. Poziom podłogi: y=0; spód sufitu: y=3.
- Trzy **nominalne** pokoje 6×9 m na osiach x=0/6/12/18, z=0/9; cała siatka pomieszczeń 18×9 m. Grubość ściany 0,30 m zmniejsza wymiary w świetle do 5,70×8,70 m. Obrys zewnętrznych ścian wynosi 18,30×9,30 m. Podest wejściowy 3×3 m znajduje się dodatkowo przed wejściem.
- W systemie grafowym ściana składa się z wypełnienia **2,70 m** i dwóch połówek współdzielonych węzłów po 0,15 m. Rozstaw Start–End to dokładnie **3 m**. Nie dodawaj osobnych słupków do każdej ściany.
- Fizycznie pełny, samodzielny model ściany 3×3×0,30 m to `W00_Complete_Wall_3m_STANDALONE` — dostępny także jako FBX, OBJ i źródło Blender. Ma własne półwęzły; do mastera używaj modułów W01/W02/W05/W04 i wspólnych węzłów.
- W01, W02 i W05 można podmieniać bez korekty pozycji, obrotu lub skali. W04 ma te same porty, lecz wnosi funkcję przejścia. Framuga i skrzydło są zagnieżdżone w W04; podążają za nim przy przemieszczeniu.
- F01/F02 mają pełne 3×3 m i wspólną górną płaszczyznę y=0. Sufit C01 ma lokalną podstawę y=0, a jego prefab umieszcza się na y=3. Wszystkie materiały/dekoracje są podziałami bryły; nie tworzą unoszących się nakładek.

## Źródła i regeneracja

`UnityProject/Assets/C01Modular/Data/kit.json` zawiera geometrię, materiały, sockety i wszystkie pozycje. Python QA, Blender i Unity korzystają z tych samych danych. Definicję generuje `Tools/build_kit.py`.

`Source/C01_PASS02_Source.blend` zawiera osobne edytowalne części i instancje całej konstrukcji. Kolekcja `SOURCE_MODULES_editable_origin_at_socket` jest domyślnie ukryta; włącz ją, aby edytować źródła. `CEILINGS_toggle_visibility` przełącza sufit. Osobne modele FBX/OBJ są w `UnityProject/Assets/C01Modular/Models/`; dodatkowy GLB całej konstrukcji jest w `Source/`.

Nie nadpisuj geometrii przez ręczne przesuwanie części w prefabie. Zmień specyfikację i uruchom generator; ręczne odchylenia prefabów są wykrywane przez QA. Edycje źródła Blender nie przepisują automatycznie JSON — źródłem montażu pozostaje manifest.

W Unity menu `Tools > C01 PASS02` buduje prefabrykaty, uruchamia walidację i eksportuje paczkę. Skrypt `Tools/run_all.ps1` odtwarza pełną sekwencję z podanymi ścieżkami Unity i Blender. Generowanie ponowne nadpisuje wyłącznie pliki wersji PASS02, zachowując GUID istniejących assetów Unity.

Szczegóły: `docs/STANDARD_PL.md`, `docs/QA_REPORT_PL.md`, `QA/verification_summary.json`. Logi niepowodzeń z audytu i wcześniejszych prób pozostają jako dowody; końcowy status wynika z raportu zbiorczego i ostatnich wyników XML, nie z wyszukiwania dowolnego słowa FAIL we wszystkich historycznych logach.

## Integracja repozytorium

Wejście było archiwum ZIP bez `.git` i bez wskazanego repozytorium/remote. Nie utworzono gałęzi ani PR w cudzym projekcie. Dostarczona paczka i źródła są gotowe do umieszczenia w docelowym repozytorium.
