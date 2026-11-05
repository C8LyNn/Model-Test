# C01 statek v7.8 — podwyższone sektory

Sześć sektorów wspólnych dla poziomów 1 i 2 ma wysokość 9 m (3 kratki po 3 m); ich podesty, przejścia oraz trasa pościgu pozostają na dotychczasowych wysokościach. Wygenerowano dodatkowy pas z osobnych ścian i słupków, podniesiono 504 moduły sufitowe oraz przycięto krawędzie 112 sąsiednich płyt dla uniknięcia przenikania na styku. Grubość konstrukcyjna istniejącego stropu powoduje, że część nowych ścian ma wysokość 2,6 m; moduły nie są rozciągane.

Scena: `Assets/C01ShipV78/Scenes/C01_Ship_Multideck_v78.unity`. Prefab nadrzędny: `Assets/C01ShipV78/Prefabs/C01_SHIP_MASTER_V78.prefab`. Starsze sceny pozostają dostępne.

Źródłowy generator danych: `build_tall_sectors.py`; budowa w Unity: `Tools/C01 Ship v7.8/Raise sector roofs`. Testy danych: `test_tall_sectors.py`; audyt pokrycia i kolizji: `audit_tall_sectors.py`; testy Play Mode: `Assets/C01ShipV78/Tests/PlayMode`.

Uwaga: zmiana geometrii v7.8 została wykonana w generatorze Unity. Osobny nowy plik `.blend` i eksport FBX dla nowych modeli v7.8 nie są zawarte w tej wersji.
