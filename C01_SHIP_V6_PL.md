# Statek C01 — scena modularna v6

Otwórz scenę `Assets/C01ShipV6/Scenes/C01_Ship_Multideck_v6.unity`. Prefab całego statku znajduje się w `Assets/C01ShipV6/Prefabs/C01_SHIP_MULTIDECK_MASTER_V6.prefab`, a osobne wymienne prefabrykaty w `Assets/C01ShipV6/Prefabs/Modules`. Wersje v3–v5 pozostają w projekcie.

Jedna kratka to 3 m. Całkowity nominalny obrys wraz z pomostami to **74 × 34 kratki**; w v5 było to **37 × 17 kratek**. Obrys jest liczony do zewnętrznych pomostów, a drobne grubości ścian wystają poza nominalną siatkę. Wysokości pokładów pozostają takie same jak w v5. Kajuty mają 3 × 3 kratki i po cztery łóżka; łazienki mają 2 × 1 kratkę. Korytarze zachowują szerokość jednej kratki. W górnej części ścian zastosowano gładkie wypełnienie technicznej różnicy grubości stropu, bez dodatkowej małej kratki.

Mostek ma modułowy, schodkowy obrys. Windy osobowe przeniesiono od głównej osi do części bocznych mostka i rufy. Na rufie są dwie windy towarowe, każda z platformą z czterech osobnych modułów, łączące trzy poziomy. Ładunek musi być obiektem z Rigidbody i colliderem bezpośrednio stojącym na platformie; przewóz stosu ładunków nie jest gwarantowany. Sektory mają galerie, schody, drabiny i krótkie dostępne kanały wentylacyjne.

W trybie Play: **WASD** — ruch, **mysz** — obrót widoku, **LPM** lub **E** — panel pod celownikiem, **E** przy drabinie — wspinanie, **W/S** — góra/dół na drabinie, **Shift** — bieg, **Spacja** — skok. **Esc** zwalnia kursor; kliknięcie przywraca sterowanie. **1** — podgląd, **2** — spacer, **R** — dachy, **L** — etykiety.

Generator danych jest w `C01SourceV6/Tools/scene_data_v6.py`; w folderze projektu uruchom `python C01SourceV6/Tools/scene_data_v6.py`, a następnie w Unity wybierz **Tools → C01 Ship v6 → Rebuild**. Generator sceny korzysta z `Assets/C01ShipV6/Data/ship_v6.json`. Repozytorium v5 jest wymagane jako katalog pierwotnych modeli i materiałów. Przed przebudową zapisz otwarte sceny.

Ograniczenia i dowody testów są w `C01_SHIP_V6_QA_PL.md`.
