# C01 Ship v7.2 — logistyka poziomu 0

Otwórz scenę `Assets/C01ShipV72/Scenes/C01_Ship_Multideck_v72.unity`. Główny prefab znajduje się w `Assets/C01ShipV72/Prefabs/C01_SHIP_MASTER_V72.prefab`. Wersja v7.1 pozostaje oddzielna.

Maszynownia znajduje się bezpośrednio pod sterownią maszynowni na poziomie 1. Ładownia graniczy ze śluzą towarową; zapasy żywności znajdują się bliżej kuchni i w tej samej części statku co hydroponika, po drugiej stronie korytarza. Oczyszczalnia pozostaje w swoim sektorze. Ściany, bramy i wymiary sektorów pozostały na siatce, a wyposażenie jest nadal edytowalne jako osobne moduły.

`Data/logistics.json` opisuje przeniesienia i zmianę funkcji stref. Ze względu na istniejące odwołania identyfikatory bram zachowują dawne nazwy techniczne; identyfikatory stref i ich etykiety odpowiadają nowemu układowi. Scenę można przebudować z v7.1 przez `Tools/C01 Ship v7.2/Improve deck zero logistics`.

Raport i zrzuty znajdują się w `C01ShipV72_QA`. Plik `C01SourceV72/Source/C01_Ship_Multideck_v72_base.blend` to edytowalny montaż geometryczny; interakcje są skonfigurowane w Unity. Skrypty generujące wymagają danych z pełnego projektu i wcześniejszych wersji.
