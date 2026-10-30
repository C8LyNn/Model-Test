# Plan implementacji C01 v3.1

1. `Tests/test_expansion.py`: test czerwony dla sześciu odnóg 3 × 9 m, korpusu 45 × 33 m, kajut 6 × 9 m i pola pokładu 1845 m². Uruchomić unittest przed zmianą generatora.
2. `Tools/build_ship.py`: parametr długości odnogi (wielokrotność 3 m), spójne pasma Z i przesunięcia drzwi/wyposażenia. Przebudować podłogi, sufity, ściany, wspólne węzły i kadłub; zaktualizować niezależny `validate_ship.py` i testy usuwania fragmentów nowej odnogi. Zachować 36 drzwi, wspólne moduły bez zmiany skali.
3. `Tools/blender_ship.py`: obsługa projektu bezpośrednio w root oraz starego układu UnityProject, kamera z nowych wymiarów. Wykonać prawdziwy eksport .blend, FBX/OBJ/GLB i testy powrotnego importu.
4. Unity `ShipBuilder.cs`, `ShipValidation.cs`, `ShipExplorer.cs`: zachować ustawienia hosta, wyprowadzać kamerę, start gracza, NavMesh i ujęcia z danych. Test PlayMode musi przejść pełne północne i południowe odnogi oraz sektor, a istniejące testy nadal sprawdzać drzwi i śluzy.
5. Bezpiecznie zachować kopię aktualnych folderów C01 poza Assets; zaktualizować dane, modele i skrypty w Model Test. Przebudować scenę/prefab w otwartym edytorze poprzez jednorazowe żądanie, uruchomić pełne EditMode/PlayMode, obejrzeć render z góry i przekrój.
6. Uaktualnić raport, paczkę Unity i dokumentację wymiarów; commitować tylko własne pliki, wysłać do bieżącej gałęzi i zaktualizować PR #1. Testy niedostępne oznaczyć NOT RUN.
