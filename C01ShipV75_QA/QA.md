# QA — wspólne sektory v7.5

Sześć sektorów poziomu 1 jest teraz pojedynczymi strefami o wysokości 6 m. Każda zawiera oddzielne moduły obu poziomów. Dodano pomosty z wejściami na poziomie 2 w laboratorium, sektorze technicznym i magazynie; pomosty pościgu w pozostałych sektorach zachowano. Historyczne identyfikatory dwóch górnych stref mapowano według położenia, a nie nazwy.

`source_audit.json` obejmuje istniejące podłogi i sufity oraz analizę brył po dodaniu pomostów; `catwalk_coverage.json` sprawdza pokrycie 24 nowych kratek. `blender_reopened.json` potwierdza ponowne otwarcie pliku i położenia nowych modułów. Wyniki testów Unity znajdują się w plikach XML. Wstępna próba łączenia prefabów wykryła zagnieżdżone instancje; finalny generator sprawdza wynik każdego przeniesienia i zachowuje instancje modułów.

W Unity 6000.3.14f1: `unified.xml` — 3/3 testy wejść z obu poziomów, nowych bram i widoczności; `transforms.xml` — zgodność pozycji i obrotów modułów; `regression.xml` — 8/8 testów trasy pościgu, wind, schodów, wentylacji i przejść. Cztery testy danych sprawdzają właścicieli, połączenia i niezmienione transformacje.

Kontrola w edytorze potwierdziła 1655/1655 modułów sektorów połączonych z osobnymi prefabami. Nowa geometria korzysta z istniejących modułów; w tej wersji nie eksportowano nowych FBX.

Pełna ręczna rozgrywka, samodzielny build Windows i AI potwora: NOT RUN. Testy dostępności gracza nie dowodzą działania AI.
