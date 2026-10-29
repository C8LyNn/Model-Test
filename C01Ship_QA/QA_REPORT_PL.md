# QA — C01 v3.1 / wydłużone boczne korytarze

Projekt: Model Test, Unity 6000.3.14f1, URP 17.3.0, Input System 1.19.0, DX12.

Konfiguracja: korpus 45 × 33 m, sześć bocznych odnóg 3 × 9 m, główny i rufowy korytarz nominalnie 3 m, kajuty 6 × 9 m. 858 instancji w skali 1; 7343 pełne bryły/collidery; 36 drzwi; 62 aktualne modele niestandardowe FBX. 1845 m² ciągłych podłóg.

## Dowody

- `python_tests_target.log`: 11 testów wymiarów, topologii, pełnego pokrycia, braków i geometrii.
- `model_test_editmode.xml`: 15 testów; sockety, rotacje, spójność importu i sceny, brakujące framugi, silnik, podłoga i sufit w wydłużonej odnodze.
- `model_test_playmode.xml`: 5 testów; przejście przez wszystkie 6 odnóg do sektorów, korytarz, kajutę i rufę; 4 śluzy; niezależne kąty drzwi; zachowanie kadru po spacerze.
- `unity_ship_qa.json`: 0 błędów, 0 penetracji, 3276 pozycji drzwi, 2832 promienie powierzchni, 35/35 dostępnych stref, 62 zaimportowane FBX.
- `geometry_qa.json`, `sweep_qa.json`: 7343 bryły we wszystkich detalach; brak penetracji przy 0° i 90°, brak kolizji w 3276 pozycjach pojedynczych drzwi i 16562 niezależnych kombinacjach dwóch bliskich drzwi.
- `blender_ship_qa.json`: rzeczywisty eksport Blender/FBX/OBJ/GLB, 62/62 testy powrotnego importu FBX PASS.
- `Screenshots/`: 13 rzeczywistych renderów Unity, w tym rzut, przekrój i wnętrze dłuższej odnogi. Obejrzano rzut, przekrój i ujęcie 13; końcowy kadłub ma ciągły obrys, a przejścia, podłogi i sufity są widoczne.
- `host_settings_qa.txt`: zachowane nazwa Model Test, profile PC_RPAsset, Linear i poprzednie sceny.

Aktualny status pełnego przebiegu jest w `integration_status.txt`; historia prób w `integration_progress.txt`. Wcześniejsze red i negative FAIL są oczekiwane: wykazały brak długości w v3.0 oraz błąd słownika przy celowym usuwaniu podłogi/sufitu. Walidator teraz zapisuje raport z brakującym ID i kończy kontrolowanym błędem. Podczas pierwszej przebudowy zaobserwowano też stary podgląd kadłuba w buforach siatki; zapis generowanych siatek teraz jawnie aktualizuje dane geometrii i bufor GPU.

## NOT RUN i zakres

Samodzielny build aplikacji, ręczna sesja użytkownika oraz opcjonalny import OBJ/GLB do Unity: NOT RUN. Automatyczny CharacterController faktycznie przeszedł odnogi i przejścia w PlayMode. NavMesh dotyczy drzwi otwartych. Symulacja lotu/ciśnienia nie należy do tego zestawu.

Nie zwiększano szczegółowości wyposażenia. Poprzednia wersja zachowana w Git, paczce v3.0 i dodatkowej kopii ZIP sprzed przebudowy.
