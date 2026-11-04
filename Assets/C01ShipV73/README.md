# C01 Ship v7.3 — magazyn i zaplecze techniczne

Scena: `Assets/C01ShipV73/Scenes/C01_Ship_Multideck_v73.unity`. Główny prefab: `Assets/C01ShipV73/Prefabs/C01_SHIP_MASTER_V73.prefab`. Poprzednia wersja v7.2 pozostaje dostępna.

Magazyn ładunkowy na poziomie 1 znajduje się dokładnie nad ładownią poziomu 0, obok rufowych wind i śluzy towarowej. Ewidencja i narzędzia ładunkowe znajdują się w pobliskich pomieszczeniach pomocniczych. Sektor techniczny i sąsiadujące z nim warsztat oraz części zamienne przeniesiono do zwolnionej części. Ustawienie maszynowni bezpośrednio pod sterownią jest zachowane.

Konstrukcja oraz bramy zachowują geometrię i pierwotne identyfikatory techniczne; etykiety i identyfikatory sektorów odpowiadają nowym funkcjom. Wyposażenie pozostaje osobnymi modułami. Dane zmian znajdują się w `Data/zoning.json`, a polecenie `Tools/C01 Ship v7.3/Align cargo and workshop` odtwarza scenę z v7.2.

Plik `C01SourceV73/Source/C01_Ship_Multideck_v73_base.blend` zawiera edytowalny montaż geometryczny. Interakcje są skonfigurowane w Unity; skrypty generujące wymagają danych pełnego projektu i wcześniejszych wersji. Raport oraz zrzuty są w `C01ShipV73_QA`.
