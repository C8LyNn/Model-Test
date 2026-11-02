# C01 v6.2 – raport QA

## Zmiany

- Na 4523 modułach ściennych wykończenie poziome jest częścią powierzchni siatki, a jego wysokości wynikają ze wspólnej siatki 3 m. Stare początki modułów różniły się m.in. o 0,4 m po wycięciu otworu bramy.
- W czterech szybach dodano kabiny ze ścianami i dachem, z podziałem na osobne moduły do 3 m. Kabiny mają luz od ścian szybu i otwór wejściowy. Trzy przyciski pięter zamontowano od wewnątrz, a zewnętrzne przyciski wywołania pozostają na każdym poziomie. Usunięto dwanaście dawnych paneli wystających do szybów.
- Mostek otrzymał fotel dowódcy, dwa fotele załogi, sześć konsol i modułowy ekran przedni. Układ jest inspirowany konwencją Star Treka; modele są oddzielnymi prefabami.

## Wykonane testy

- Unity 6000.3.14f1 PlayMode: `playmode_v62.xml`, 6/6 — wejście do każdej z czterech kabin na trzech pokładach (12 wejść), dostępność przycisków wywołania i przycisków wewnętrznych, ruch kabin, wykończenie ścian oraz kolizje wyposażenia mostka.
- Unity PlayMode: `ride_v62.xml`, 1/1 — rzeczywista postać wjeżdża na górny pokład w każdej z czterech wind.
- Unity PlayMode: `gate_v62.xml`, 1/1 — otwarcie przyciskiem oraz fizyczne przejście przez bramę między siłownią i laboratorium. `gate_before.json` i `gate_after.json` potwierdzają tę samą liczbę i pozycję widocznych skrzydeł w porównywanym miejscu.
- `cabin_swept_clearance.json`: analityczny test pełnego zakresu pionowego czterech kabin wobec oryginalnych brył sceny, dla pięciu położeń bram, wykrył 0 przenikań. `cabin_clearance_old_buttons.json` wykrywa 240 kolizji, jeżeli przywrócić usunięte panele; `cabin_clearance_mutation.json` wykrywa 843 kolizje po celowym przesunięciu kabiny. Wynik odnosi się do badanych brył i nie zastępuje pełnego testu rozgrywki.
- 4/4 testy generatora dotyczą wysokości, luzów, pokrycia kabin oraz układu mostka. Sprawdzają też, czy panele kabin nie przenikają się wzajemnie.
- Blender 5.2.3: zapisano źródła nowych modułów i wyeksportowano 18 FBX; ponowny import 18/18 zachował wymiary. Unity zaimportowało te same 18 FBX, z wymiarami zgodnymi z modułami sceny: `unity_fbx_import.json`.
- W `Screenshots/` znajdują się rzeczywiste rendery Unity: mostek, kabina i porównanie fragmentu ściany przed/po.

## Ograniczenia

Nie przeprowadzono pełnego ręcznego przejścia całego statku, testu FPS ani buildu Windows. Nie powtórzono kompletnego audytu wszystkich wcześniejszych podłóg, sufitów i połączeń statku. Kanały wentylacyjne nadal kończą się kratkami, a część istniejących podestów nie ma pełnych barierek. Plik Blender v6.2 zawiera źródła nowych modułów; kompletna wcześniejsza konstrukcja Blender pochodzi z v6.
