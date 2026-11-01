# Raport QA — C01 statek v6

- Nominalny obrys całości: 74 × 34 kratki po 3 m. Korpus: 42 × 30 kratek. Punkty pokładów: −12,4 m, 0 m i 6,4 m, bez zmiany względem v5.
- 24 kajuty na dwóch pokładach, każda 3 × 3 kratki, z 24 łazienkami 2 × 1 kratka, 96 łóżkami i 192 szafkami.
- W danych sceny: dwie windy osobowe i dwie towarowe, 133 bramy oraz dziewięć śluz. Winda towarowa składa się z czterech modułów platformy.
- Kontrola 68 010 pełnych brył źródłowych wykazała 0 przenikań dla pozycji bram 0%, 25%, 50%, 75% i 100%. Nie należy traktować tego wyniku jako dowodu braku szczelin.
- Niezależna kontrola powierzchni wykazała 0 braków w 4199 oczekiwanych obszarach podłóg i 4410 obszarach sufitów. Testy kontrolne wykryły celowe usunięcie pojedynczego modułu podłogi, sufitu i wybranej ściany.
- Przybliżona analiza przejść w siatce próbek co 0,5 m znalazła dostęp do wszystkich pomieszczeń, wyjść i podejść do wind przy otwartych bramach. Jest to analiza geometryczna, nie ręczne przejście wszystkich tras.
- Unity 6000.3.14f1 przeszło 6/6 testów sceny v6 po dodaniu poręczy i poprawce kadru: panele bram, obie windy osobowe, obie windy towarowe z postacią i skrzynią, otwarcie bramy, kadrowanie oraz schody, kanał i drabina w sektorze treningowym. Przeszły też 2 testy regresji podglądów wcześniejszych scen. Wynik: `C01SourceV6/QA/scene_v6_framing.xml`.
- Osobny test PlayMode sprawdził fizyczne wejście do każdej z czterech wind z każdego z trzech pokładów: 12/12 przystanków. Dwa testy EditMode potwierdziły zachowanie kolejności i stanu istniejących scen builda.
- Kontroler windy towarowej osobno: 4/4 testów PlayMode PASS, w tym ładunek na każdej z czterech powierzchni i blokada nieaktualnych przystanków.
- Blender 5.2.3 zapisał edytowalną scenę oraz 394 rzeczywiste modele FBX i 394 OBJ. Ponownie otwarty plik Blender zawiera 20 015 instancji, w tym 203 poręcze; porównano ich pozycje, obroty i przypisane modele z danymi Unity: 0 różnic. Kontrolny ponowny import wybranych 12 modeli FBX przeszedł 12/12; nie sprawdzano w ten sposób wszystkich 394 plików.
- Unity zaimportowało 394/394 pliki FBX z oczekiwaną liczbą części siatki. Wynik: `C01ShipV6_QA/fbx_import_v6.json`.
- Wyeksportowana paczka Unity zawiera scenę, prefab, kod oraz wszystkie 394 modele FBX. Porównanie 3363 plików v6 i 10 plików zależności v5 z projektem nie wykazało różnic: `C01ShipV6_QA/unitypackage_v6.json`.
- Paczkę zaimportowano do osobnego pustego projektu, a po ostatniej poprawce ponownie zaimportowano tam finalną wersję. Scena otworzyła się z czterema windami i bez brakujących skryptów; 3373 pliki po imporcie są identyczne z projektem testowym. Logi i wyniki znajdują się w `C01SourceV6/QA`.
- Testy Unity przeprowadzono w osobnej kopii projektu. Po skopiowaniu do Model Test porównano 6812 plików bajt po bajcie: 0 różnic. Scenę v6 dopisano na końcu listy, zachowując dotychczasową kolejność i scenę startową.
- Zrzuty pochodzą z renderowania rzeczywistej sceny Unity i znajdują się w `C01ShipV6_QA/Screenshots`. Kontrola wizualna nie obejmuje każdego połączenia.

Ograniczenia: kanały wentylacyjne kończą się kratkami i nie łączą sektorów. Poręcze nie otaczają w pełni każdego podestu i przejścia. Napisy na niektórych panelach mogą być widoczne od tyłu. Nie wykonano ręcznej sesji po wszystkich pomieszczeniach, pomiaru FPS ani buildu Windows. Analiza wszystkich ścian i narożników nie jest pełnym matematycznym dowodem szczelności.
