# C01 Ship v6.2

Scena: `Assets/C01ShipV62/Scenes/C01_Ship_Multideck_v62.unity`. Prefab nadrzędny: `Assets/C01ShipV62/Prefabs/C01_SHIP_MASTER_V62.prefab`; zachowuje zależność od modułów v6 i pozostawia elementy statku osobnymi obiektami.

Wyrównano linie paneli ścian do wspólnego poziomu co 3 m, niezależnie od tego, na jakiej wysokości zaczyna się moduł przy bramie. Wykończenie jest częścią powierzchni siatki i nie tworzy dodatkowej listwy ani collidera. Dodano ściany, dach i wejście do wszystkich czterech kabin wind, z luzem w szybach. Panele wywołania po zewnętrznej stronie oraz przyciski w kabinach pozostają; usunięto dwanaście duplikatów wystających do szybów. Mostek ma stanowiska i ekran inspirowane konwencją Star Treka.

Scenę i prefab generuje `Tools/C01 Ship v6.2/Build repaired ship` na podstawie `Data/polish_v62.json`. Dane tworzy `C01SourceV62/design_v62.py` z danych v6. Generator otwiera scenę v6.1; należy zapisać otwarte sceny. Zmiany w danych wymagają wygenerowania pliku JSON przed przebudową w Unity.

Sterowanie: `2` – spacer, `1` – podgląd, WASD i mysz – ruch i obrót, E/LPM – panel, Esc – kursor. Pozostałe informacje o sterowaniu i ograniczeniach znajdują się w dokumentacji v6.1 i raporcie QA.
