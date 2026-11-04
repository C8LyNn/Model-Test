# C01 Ship v7.1 — mostek i windy

Scena: `Assets/C01ShipV71/Scenes/C01_Ship_Multideck_v71.unity`. Prefab nadrzędny: `Assets/C01ShipV71/Prefabs/C01_SHIP_MASTER_V71.prefab`. Poprzednia scena v7.0 pozostaje dostępna.

Dwie windy pasażerskie mostka przeniesiono symetrycznie do bocznych części pomieszczenia; ich kabiny, szyby, bramy i przyciski są zsynchronizowane na trzech poziomach. Zmieniono otwory podłóg oraz przedłużono galerię na górnym pokładzie, aby zachować dojście. Moduły powtarzają się na siatce 3 m. Na mostku dodano pulpit dowodzenia i parę bocznych stanowisk z fotelami, wykorzystując dostępne moduły.

Układ zapisano w `Data/bridge_delta.json`; polecenie edytora `Tools/C01 Ship v7.1/Build bridge and edge lifts` buduje wariant z v7.0. Modele pozostają osobnymi obiektami. Plik `C01SourceV71/Source/C01_Ship_Multideck_v71_base.blend` zawiera edytowalny montaż geometryczny; skrypty, bramy i logika wind działają w scenie Unity.

Raport, testy i zrzuty znajdują się w `C01ShipV71_QA`.
