# C01 v5 — raport QA

## Zakres

Siatka ma kratkę 3 m. Ściany i węzły dzielą się na osobne, powtarzalne segmenty do 3 m wysokości. Standardowy moduł ma nominalnie 3 × 3 m wraz ze wspólnymi węzłami; wkładka między węzłami ma 2,7 m. Przy płytach pokładów i otworach występują krótkie uzupełnienia. Podzielono także poszycie dziobu, ramy i ruchome panele bram. Instancje są osobnymi prefabami i mają skalę 1.

Jedenaście sektorów na pokładach 0 i 1 ma antresole 6 m nad podłogą, schody z czterech powtarzanych odcinków, dwie części drabiny i dwa moduły kanału wentylacyjnego dostępnego z podestu. Kanały kończą się kratką; nie łączą jeszcze sektorów. Piony mostka i rufy nadal łączą pokłady fizycznymi windami. Antresole i schody mają otwarte krawędzie bez poręczy.

Scena uruchamia się w trybie spaceru: WASD, PPM obrót, Shift bieg, Spacja skok, E drabina, W/S wspinanie, LPM panel, 1 podgląd, 2 spacer. Instrukcja jest w `C01_SHIP_V5_PL.md` i `C01SourceV5/README_PL.md`.

## Dostępne dowody

- **Python: 14/14 PASS**, w tym rozmiary, powtarzalność, wypełnienie połączeń przy płytach i miejsce dla postaci przy schodach, drabinach, podestach i wejściach do kanałów we wszystkich 11 sektorach. Raport: `C01SourceV5/QA/python_v5.log`.
- **Pokrycie posadzek/sufitów:** 2250 obszarów, 0 braków. Pełna geometria źródłowa ma 31 383 bryły i 0 przenikań przy pięciu pozycjach bram. Raporty: `layout_v5.json`, `geometry_v5_0.json`, `geometry_v5_1.json`, `gate_intermediate_poses.json`.
- **Ściany i poszycie:** porównanie rzeczywistych brył do v4 próbkowało po 410 350 punktów dla bram zamkniętych i otwartych, nie wykrywając utraty starej geometrii. Kontrolne usunięcie modułu ściany zostało wykryte. Jest to próbkowanie, a nie matematyczny dowód szczelności wszystkich ścian. `structure_v4_to_v5.json`, `structure_negative.json`.
- **Unity 6000.3.14f1 / URP 17.3.0:** audyt PASS, 9767 instancji, 31 383 collidery, 0 przenikań w stanach otwartym i zamkniętym, 16 087 promieni kontroli powierzchni, 357 prawidłowo zaimportowanych FBX i 98 dostępnych stref z czterema jawnymi połączeniami wind. `C01ShipV5_QA/unity_v5_qa.json`.
- **Unity EditMode:** 8/8 PASS w drugim pełnym przebiegu. Obejmuje testy uszkodzonych podłóg, sufitów, łóżka, przycisku, collidera, socketów i zachowania ustawień. `C01ShipV5_QA/editmode.xml`.
- **Unity PlayMode:** siedem wcześniejszych testów przeszło w pełnym przebiegu (bramy, śluzy, windy, grawitacja i kamera). Po poprawce zejścia z drabiny dwa ukierunkowane testy przeszły osobno: fizyczny ruch po schodach, wejście do kanału i drabina w sektorze treningowym oraz wejście i zejście z drabiny dolnej maszynowni. `C01SourceV5/QA/Unity_second/playmode.xml` i `C01ShipV5_QA/playmode.xml`. Kompletnego zestawu po ostatniej poprawce nie uruchomiono ponownie.
- `C01ShipV5_QA/status.txt` zawiera status ostatniego żądania `verify-ladders`, czyli wyłącznie dwóch ukierunkowanych testów, a nie całego zestawu PlayMode.
- **Blender 5.2.2:** rzeczywisty `.blend`, GLB, 357 FBX i 357 OBJ; 357/357 kontrolnych importów FBX PASS. Fizyczny układ i modele w Blenderze oraz Unity korzystają z tych samych pozycji. `blender_v5.json`, `blender_models_v5.json`, `assembly_consistency.json`.
- **Wizualnie:** zapisano rzeczywiste rendery Unity, m.in. widok połączenia ścian, schodów, drabiny i wnętrza kanału, oraz rendery Blender. `C01ShipV5_QA/Screenshots`, `C01SourceV5/QA/Blender`.

Pierwszy pełny przebieg znalazł punkt kontrolny upraw pod nowym kanałem, a test gry wykrył nieukończone zejście z drabiny. Punkt przeniesiono w wolną przestrzeń, a wspinanie kończy się po kontakcie CharacterController z podłogą. Wcześniejsze wyniki FAIL pozostawiono w `C01SourceV5/QA/Unity_initial` i `Unity_second`.

Paczka Unity została rzeczywiście wyeksportowana i porównana z projektem: 2970 plików źródłowych w paczce ma zgodne bajty, wymagane scena i prefab są obecne. Kontrola 4851 wcześniejszych plików projektu potwierdziła ich zachowanie; ustawienie zmienione przez Test Runner przywrócono do dokładnej kopii sprzed testów. Zamierzona zmiana dotychczasowych plików dodaje wyłącznie scenę v5 do listy scen buildu. Szczegóły: `unitypackage_v5.json` i `host_preservation_v5.json`.

NOT RUN: ręczna sesja WASD/mysz, pomiar FPS, build Windows, import paczki do drugiego pustego projektu oraz osobny przejazd postaci po wszystkich 11 zestawach. Dwie trasy sprawdzono w rzeczywistym PlayMode, a wolne punkty wejścia w 11 sektorach sprawdzono na geometrii źródłowej. Cztery połączenia TRANSPORT w nawigacji są abstrakcją wind, które przetestowano oddzielnie z fizyczną postacią.
