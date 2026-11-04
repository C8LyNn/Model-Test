# QA — magazyn i zaplecze techniczne v7.3

Zamieniono funkcje dwóch sektorów poziomu 1 i przeniesiono osiem istniejących modułów wyposażenia. Magazyn i ładownia pokrywają się w obu osiach, a cztery pomieszczenia zaplecza mają funkcje zgodne z sąsiednimi sektorami. Dotychczasowe bramy i ściany nie zmieniły położenia.

- Testy źródłowe sprawdzają zgodność obu osi magazynów i maszynowni, role zaplecza, wyposażenie oraz niezmienioną geometrię bram i konstrukcji. `collision_positive_control.json` to oczekiwany FAIL dla celowo zdublowanej skrzyni.
- `source_audit.json` sprawdza podłogi, sufity, dojścia i trzy położenia bram.
- `regression.xml` dokumentuje testy PlayMode Unity, w tym przejścia do pomieszczeń, windy i trasę pościgu.
- `blender_reopened.json` potwierdza ponowne otwarcie pliku Blender i sprawdzenie położeń.
- `Screenshots` zawiera zrzuty Unity i schemat oparty na danych montażowych.

Modele wykorzystano ponownie bez nowego eksportu FBX. Pełna ręczna rozgrywka i osobny build Windows: NOT RUN.
