# C01 Ship v7.0 — połączenia stropów i ścian

Otwórz scenę `Assets/C01ShipV70/Scenes/C01_Ship_Multideck_v70.unity`. Prefab nadrzędny znajduje się w `Assets/C01ShipV70/Prefabs/C01_SHIP_MASTER_V70.prefab`. Poprzednie wersje pozostają oddzielne. Budowę można powtórzyć poleceniem `Tools/C01 Ship v7.0/Unify walls and roof` w Unity, korzystając z v6.9 i danych w katalogu `Data`.

Siatka konstrukcyjna ma moduł 3 m. Stropy mają grubość 0,4 m, a ich boczne wypełnienia i kolidery pozostają częścią konstrukcji. W miejscach wskazanych na zrzutach usunięto powtórzony poziomy podział wizualny: ściana i krawędź stropu tworzą ciągłą powierzchnię z jednym podziałem na poziomie podłogi. Położenie segmentów zmieniono bez zmiany zajmowanej bryły.

Sufity sektorów na poziomie 1 zachowują spód na wysokości 6,0 m; ich górna powierzchnia jest wyrównana do 6,6 m przez zwiększenie grubości ku górze i wypełnienie wycięć. Dwa warianty ścian i dziewięć wariantów sufitów są współdzielonymi prefabami w `Prefabs/Modules`, bez rozciągania całych modułów.

W `C01SourceV70` znajdują się skrypty i dane montażowe, edytowalny montaż Blender oraz osobne modele ścian i sufitów wyeksportowane do FBX i OBJ. Raport i dowody testów są w `C01ShipV70_QA`. Montaż Blender jest źródłem geometrii; interakcje i skrypty działają w scenie Unity.
