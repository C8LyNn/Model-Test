# QA C01 v6.8

Jedna kratka to 3 m. Sześć sektorów poziomu 1 ma wysokość 6 m i otwartą przestrzeń nad nimi; w każdym są schody, podest, drabina i wentylacja. Mostek ma uporządkowane stanowiska dowodzenia i nawigacji; rufa stanowiska napędu i ładunku. Górna trasa biegnie boczną galerią mostka. Poziom 0 ma sześć nowych wejść od głównego korytarza i cztery przejścia między sąsiednimi strefami.

Przyczyny: linie ścian liczono według wielokrotności 3 m od zera, mimo pokładów -3,4 / 0 / 3,4 m i stropów 0,4 m. Ściany dzielono od początku złączonego zakresu, przez co powstawały odcinki 0,8 m i linie nie pokrywały się z górą bramy. v6.8 dzieli ściany według rzeczywistych granic pokładów i stropów oraz rysuje pasy na brzegach pełnych modułów 3 m; krótsze przejścia stropowe nie udają kolejnej kratki.

Napisów prześwitujących nie powodowały nazwy pomieszczeń: po przełączeniu widoku kontroler ponownie włączał stare TextMesh z materiałem nieweryfikującym głębi. Test bazowy wykrył 308 aktywnych starych napisów. Kontroler nie włącza ich, kiedy aktywny jest system nowych, dopasowanych i testujących głębię napisów; nowy test przechodzi w starszej scenie i v6.8.

Unity 6000.3.14f1: `scene_verified.xml` 10/10 PASS. Test sprawdził otwarcie z widoku gracza i fizyczne przekroczenie wszystkich 10 nowych bram, dojście do stanowisk mostka i rufy, trasę pościgu, windy, schody, drabinę i wejście do wentylacji, wysokość sektorów, dopasowanie ramek do ścian oraz pasy wszystkich ponad 2000 ścian. `older_scene.xml` zawiera regresję wcześniejszej sceny. Zrzuty w `Screenshots` są renderami z kamer Unity; nie zastępują pełnego ręcznego przejścia.

Generator: 0 wykrytych przenikań w pięciu pozycjach bram; podłogi 2669 obszarów, sufity 2234 obszary, bez braków w sprawdzanych powierzchniach. Kontrola tras 2D wykazuje dostępność stref przy otwartych bramach; dodatkowy test grafu sprawdza obejście awarii jednego z sześciu bezpośrednich wejść. Są to osobne kontrole i nie dowodzą braku wszystkich możliwych problemów w rozgrywce.

Blender 5.2.3: 418 wyeksportowanych modeli FBX/OBJ oraz edytowalny montaż bazowy; 17 modeli sprawdzonych ponownym importem. Końcowa konfiguracja bram, wind i napisy powstają w Unity. NOT RUN: pełna ręczna rozgrywka, samodzielny build Windows; potwór i logika pościgu pozostają poza sceną.
