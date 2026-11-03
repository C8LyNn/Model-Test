# C01 Statek v6.4 — siatka i niższe pokłady

Otwórz `Scenes/C01_Ship_Multideck_v64.unity`. Główny prefab to `Prefabs/C01_SHIP_MASTER_V64.prefab`. Poprzednie sceny pozostają dostępne. Model składa się z osobnych instancji modułów.

- Jedna kratka = 3 m. Wszystkie główne i boczne korytarze mają szerokość jednej kratki (3 m nominalnie; ok. 2,7 m między powierzchniami ścian).
- Kajuty mają 3 × 3 kratki. Na pokładach 1 i 2 zwykłe pomieszczenia i korytarze mają 1 kratkę (3 m) wysokości. Sektory oraz pomieszczenia na pokładzie 0 mają 2 kratki (6 m) wysokości.
- Podłogi pokładów są na wysokościach -6,4, 0 i 3,4 m. Różnicę między wysokością w świetle a wysokością następnej podłogi stanowi 0,4 m konstrukcji stropu.
- Mostek i rufa są podzielone na pokłady; cztery zabudowane windy zapewniają przejście między poziomami. W sektorach schody i drabiny prowadzą na antresolę i do kanałów wentylacji.

Sterowanie: `2` spacer, `1` podgląd, WASD ruch, mysz obrót, `E` interakcja/drabina, lewy przycisk myszy panel, Esc uwalnia kursor, ponowne kliknięcie go przechwytuje.

Źródło montażu: `Assets/C01ShipV64/Data/ship_v64.json` i `polish_v64.json`. W katalogu `C01SourceV64/Tools` program `scene_data_v6.py` generuje bazę z siatki, następnie `C01SourceV64/design_v64.py` tworzy dane wykończenia. W Unity użyj kolejno menu `Tools/C01 Ship v6.4/Rebuild base` i `Tools/C01 Ship v6.4/Build final`; zapisz inne otwarte sceny przed przebudową.

`C01SourceV64/Source/C01_Ship_Multideck_v64_base.blend` to edytowalny montaż bazowy z tych samych danych, z osobnymi modelami FBX/OBJ w `C01SourceV64/Models`. Warstwa końcowa Unity z wyrównaniem ścian, zamkniętymi kabinami wind i mostkiem jest składana dodatkowo z `polish_v64.json` i nie jest wmontowana do bazowego pliku Blender. Modele źródłowe wykończenia z v6.2 pozostają w projekcie.
`C01SourceV64/PolishSource` zawiera osobny plik Blender i FBX nowego, obniżonego ekranu mostka. Jego FBX został ponownie wczytany z pięcioma częściami.
