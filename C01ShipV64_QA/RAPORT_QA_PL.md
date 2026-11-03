# C01 v6.4 — raport QA

Jednostka siatki: 3 m. Korytarze: 1 kratka szerokości. Kondygnacje 1 i 2: zwykłe pomieszczenia 1 kratka wysokości; sektory 2 kratki. Poziom 0: 2 kratki wysokości. Podłogi: -6,4 / 0 / 3,4 m.

## Analiza danych montażowych

- 19 testów źródłowych, w tym testy wykrywające celowo usuniętą podłogę, sufit i ścianę: PASS (`source_tests.txt`).
- Korytarze: 27, 198 pól, brak wykrytych braków podłogi (`corridor_floor_coverage.json`).
- Podłogi: 4458 regionów, sufit: 4410 regionów; brak wykrytych braków w pomiarze powierzchni (`floor_coverage.json`, `ceiling_coverage.json`).
- Pełna geometria bazowa, w tym detale, pięć pozycji bram: 0 wykrytych przenikań (`geometry_*.json`).
- Obudowy czterech wind w pełnym zakresie pionowym i pięciu pozycjach bram: 0 wykrytych przenikań (`cabin_swept_clearance.json`).
- Przybliżone próbkowanie tras dla otwartych bram: znaleziono dojście do wszystkich oznaczonych pomieszczeń i przystanków (`routes.json`). To nie zastępuje pełnego ręcznego przejścia.

## Unity i Blender

Eksport Blender 5.2.3 LTS: 394 modeli FBX i OBJ, 13 próbek ponownie zaimportowanych i porównanych z geometrią źródłową — PASS (`../C01SourceV64/QA/blender_models_v64.json`). Unity 6000.3.14f1, URP, PlayMode: 10/10 PASS (`playmode_v64.xml`), w tym pomiar korytarzy i wysokości, wejście do czterech wind z trzech pokładów, jazda postaci, przyciski, brama, schody, drabina, wentylacja, kolizje mostka i wyrównanie linii ścian. Osobna kompilacja projektu Windows i pełne ręczne przejście całego statku: NOT RUN. Plik `.blend` opisuje montaż bazowy; końcowe wykończenie jest osobną warstwą Unity.

`C01SourceV64/PolishSource/bridge_screen_report.json`: osobny ekran mostka 2,98 m, eksport FBX i kontrola liczby części po ponownym imporcie — PASS.

Pierwszy pomiar bocznego korytarza (`dimensions_initial_door_sample.xml`) trafił w zamknięte skrzydła bram po bokach, co dało 2,858 m prześwitu zamiast 2,7 m przy pełnych ścianach. Poprawiony pomiar jest wykonywany między pełnymi panelami. Pierwszy zestaw PlayMode (`playmode_before_bridge_fix.xml`) wykrył ekran mostka przecinający strop; ekran został przebudowany, a zestaw uruchomiono ponownie.


Zrzuty wykonane w Unity: `Screenshots/corridor_main.png`, `corridor_branch.png`, `sector_access.png`, `bridge.png`, `lift.png` oraz `deck_plan.png`. Kontrola wizualna obejmowała wskazane ujęcia, a nie wszystkie połączenia statku.
Import FBX v6.4 do czystego projektu Unity: NOT RUN. Scena korzysta z prefabów i siatek generowanych bezpośrednio w Unity z danych montażowych; próbki FBX sprawdzono ponownym importem w Blenderze. Samodzielny build Windows i pełne ręczne przejście wszystkich pomieszczeń: NOT RUN.
