# QA — dwa pokłady v7.7

Nowa scena usuwa poziom 0, jego 39 bram, podłogi, niższe ściany i przyciski wind prowadzące do niego. Pozostawia poziomy 1 i 2. Przeniesiono dwa reaktory, cztery moduły oczyszczania, 15 z 40 roślin, osiem skrzyń oraz prom; poprzednia kompletna wersja pozostaje w scenie v7.6. Nowy wylot promu znajduje się w ładowni poziomu 1. Pod sześcioma szybami wind dodano 12 modułowych płyt.

- `source_audit.json`: niezależne pokrycie podłóg i sufitów oraz dostępność stref na dwóch pozostałych poziomach; analiza kolizji dla trzech pozycji bram. Zero penetracji nie zastępuje testów prześwitu.
- `C01SourceV77/test_two_decks.py`: usunięcie dolnego pokładu i kontroli, zachowanie najważniejszych funkcji, geometria całego promu na drodze przez otwartą i zamkniętą bramę; testy wykrywają celowo usuniętą kratkę oraz celową przeszkodę.
- `blender_reopened.json` i `blender_exports.json`: rzeczywisty montaż źródła Blender i trzy eksporty FBX/OBJ z ponownym importem FBX.
- Unity 6000.3.14f1 Play Mode: `final.xml` — 13/13 testów, w tym jazda gracza windą pasażerską i towarową, odrzucenie poziomu 0, fizyczne wejścia do sektorów, pościg, prześwit promu oraz poprzednia scena z działającym poziomem 0. Zrzuty: `Screenshots`.
- `dynamic_cargo.xml` — osobny test transportu ruchomej skrzyni windą towarową z poziomu 1 na 2.

Wylot promu nie symuluje ciśnienia i nie blokuje automatycznie innych drzwi hangaru; prom nie ma sterowania lotem. Pełna ręczna rozgrywka, osobny build Windows i AI potwora: NOT RUN.
