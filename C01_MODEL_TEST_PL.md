# C01 — statek w projekcie Model Test

Scena: `Assets/C01ShipV3/Scenes/C01_Ship_FromPlan.unity`.
Prefab nadrzędny: `Assets/C01ShipV3/Prefabs/C01_SHIP_FROM_PLAN_MASTER.prefab`.

Otwieranie: **Tools → C01 Ship → Open imported ship**. Scena jest też pierwszą w Build Scenes. SampleScene zachowano; scena ThreeRooms jest dodana dla testów biblioteki.

Po Play wybierz zakładkę Game. Klawisz **1** pokazuje cały statek, **2** włącza chodzenie, **WASD + prawy przycisk myszy** sterują postacią, **E** obsługuje drzwi w zasięgu 3,5 m, **R** przełącza dach, **L** podpisy. **O/K** otwierają/zamykają zwykłe drzwi. Śluzy obsługuj indywidualnie przez E.

Statek zawiera 12 kajut, 6 sektorów, mostek, korytarze, 4 śluzy i 5 silników według dostarczonego planu. 614 instancji pozostaje osobnymi edytowalnymi elementami powiązanymi z prefabami. Modele FBX/OBJ: `Assets/C01ShipV3/Models` i `Assets/C01Modular/Models`. Źródło Blender i GLB: `C01Source` (poza Assets, aby Unity nie wymagało importera Blender).

## Weryfikacja w tym projekcie — 2026-10-29

Unity 6000.3.14f1, URP 17.3.0, Input System 1.19.0. Zachowano ustawienia i nazwę projektu Model Test.

- EditMode: **12/12 PASS**, PlayMode: **4/4 PASS**.
- Statek: 614 instancji, 5393 colliderów, 36 drzwi, 3276 pozycji drzwi 0–90°, 1788 promieni sprawdzających powierzchnie, 54 importy nowych FBX.
- 35/35 stref osiągalnych w audycie NavMesh; 0 wykrytych błędów i penetracji.
- Rzeczywisty CharacterController przeszedł korytarz przez D1/D2, wejście do kajuty i wyjście rufowe. Testy sprawdziły niezależne kąty sąsiednich drzwi oraz sekwencję czterech śluz.
- 12 obrazów z Camera.Render w tym projekcie: `C01Ship_QA/Screenshots`.

Powtórzenie pełnej kontroli: **Tools → C01 Ship → Verify imported project**. Najpierw zapisz zmienione sceny. Po testach narzędzie przywraca scenę statku.

Dowody: `C01Ship_QA/model_test_editmode.xml`, `model_test_playmode.xml`, `unity_ship_qa.json`, `integration_progress.txt` i `QA_REPORT_PL.md`. Raporty `unity_negative_*` celowo zawierają FAIL: testy usuwają framugę lub silnik i sprawdzają, czy audyt wykrywa brak geometrii. Wyniki wcześniejszych prób są zachowane w historii postępu; końcowy pełny przebieg ma DONE PASS.

**NOT RUN w tej integracji:** build samodzielnej aplikacji, ręczny spacer klawiaturą i myszą, ponowny eksport w Blenderze oraz import opcjonalnego OBJ/GLB do Unity. Dostarczone pliki Blender/FBX/GLB pochodzą z rzeczywiście wykonanych eksportów paczki v3.0.

NavMesh jest zapisem audytu przy wszystkich otwartych drzwiach. Ruch gracza korzysta z colliderów; nie jest to dynamiczny system nawigacji AI.

Generator geometrii i prefabów: `Assets/C01ShipV3/Editor/ShipBuilder.cs`, wspólne dane montażowe: `Assets/C01ShipV3/Data/ship.json`. Oryginalne polecenie Build odtwarza scenę i ustawia dostarczony profil C01 URP; do bieżącego testowania używaj poleceń Open/Verify powyżej.
