# C01 — mostek v6.9

Otwórz `Assets/C01ShipV69/Scenes/C01_Ship_Multideck_v69.unity` w Unity 6000.3.14f1. Wersja jest osobną sceną i wariantem prefabu nadrzędnego `Assets/C01ShipV69/Prefabs/C01_SHIP_MASTER_V69.prefab`; wcześniejszy mostek v6.8 pozostaje w projekcie.

Na osi statku znajduje się fotel dowódcy. Przed nim rozmieszczono dwa stanowiska sterowania i bank sześciu ekranów, a po bokach symetryczne stanowiska naukowe, łączności, taktyki i inżynierii. Zachowano boczne półpiętra, windy i górną galerię prowadzącą na trasę pościgu. Wyposażenie pozostaje prostymi, osobnymi modułami z poprzedniej wersji; ich skala nie jest zmieniana.

Układ pozycji jest w `Assets/C01ShipV69/Data/bridge_layout.json`, generowany przez `C01SourceV69/bridge_layout.py`. Po zapisaniu otwartych scen można zbudować wariant ponownie przez **Tools / C01 Ship v6.9 / Build bridge variant**. W `C01SourceV69/Source` znajduje się edytowalny montaż bazowy Blender z tymi samymi pozycjami; użyte modele FBX/OBJ pozostają w `C01SourceV68/Models`. Bramy, windy, napisy i końcowa konfiguracja materiałów działają w Unity.
