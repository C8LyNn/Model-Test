# C01 — statek wielopokładowy v4.0

Jedna kratka konstrukcyjna ma **3 m**. Kajuty mają 3×3 kratki (9×9 m), łazienki 1×2 kratki (3×6 m), wysokość kajut i korytarzy to 2 kratki (6 m), a sektorów 4 kratki (12 m). Korytarze zachowują szerokość 3 m, boczne ramiona długość 9 m. Rufa ma szerokość 4 kratek (12 m).

Otwórz kompletny projekt **Model Test** w Unity **6000.3.14f1**, z zachowanym URP 17.3.0. Scena: `Assets/C01ShipV4/Scenes/C01_Ship_Multideck.unity`. Prefab nadrzędny: `Assets/C01ShipV4/Prefabs/C01_SHIP_MULTIDECK_MASTER.prefab`. Osobne moduły edytowalne i wymienne: `Prefabs/Modules`; rzeczywiste eksporty FBX/OBJ: `Models`.

## Układ i sterowanie

- Poziom 0, posadzka −12,4 m: maszynownia, dodatkowy magazyn, oczyszczalnia, uprawy i hangar ze statkiem ewakuacyjnym. Statek ewakuacyjny jest edytowalnym modelem; pilotowanie nie jest zaimplementowane.
- Poziom 1, posadzka 0 m: 12 kajut, trening, laboratorium, badania medyczne z dwoma łóżkami, magazyn, sterowanie maszynownią i sektor techniczny.
- Poziom 2, posadzka 6,4 m: kolejne 12 kajut i powtórzony układ korytarzy. Większe sektory zachowują pełną wysokość 12 m; piętro mieszkalne zajmuje pas nad kajutami.
- Każda kajuta: cztery łóżka, osiem szafek i osobna łazienka. Dwie fizyczne windy łączą wszystkie poziomy w pionowym mostku i rufie.

Uruchom **Play**. `1` wybiera podgląd, `2` spacer, `WASD` ruch, przytrzymany prawy przycisk myszy obrót widoku. Lewy przycisk klika fizyczny panel bramy lub windy. `R` przełącza dachy, `L` etykiety. W spacerze klikaj panel pod celownikiem z odległości do 3,5 m. Przy windzie naciśnij WEZWIJ, wejdź do kabiny i wybierz 0/1/2. Bramy przystankowe otwierają się dopiero po przyjeździe kabiny. Śluzy blokują jednoczesne otwarcie obu bram.

## Regeneracja

W Unity: `Tools > C01 Ship v4 > Rebuild and verify`. Zapisz własne edytowane sceny przed ręcznym przebudowaniem. Generator odtwarza wyłącznie przestrzeń `C01ShipV4`, korzystając ze wspólnego `Data/ship_v4.json`. Poprzednie wersje pozostają osobno.

Źródła pipeline znajdują się w `C01SourceV4` kompletnej paczki. Python 3: `python C01SourceV4/Tools/build_ship_v4.py`, następnie `python C01SourceV4/Tools/validate_ship_v4.py --geometry`. Z katalogu `C01SourceV4`: `python -m unittest discover -s Tests -v`. Eksport: `blender --background --python C01SourceV4/Tools/blender_ship_v4.py`. W katalogu źródłowym samodzielnej wersji skrypty używają `UnityProject`; w kompletnym projekcie wykrywają nadrzędny folder `Assets`.

Plik `.blend` zawiera osobne źródłowe modele, ich sockety oraz instancje całej konstrukcji. GLB zawiera kompletną geometrię; działanie bram, przycisków i wind zapewniają skrypty Unity, a nie sam format wymiany.

## Weryfikacja

Wyniki rzeczywistych uruchomień, ograniczenia i dowody są w `QA_REPORT_PL.md` oraz raportach JSON/XML i screenshotach. Obrazy są renderami rzeczywistych scen Unity/Blendera. Kontrola przenikań obejmuje detale modeli; niezależna kontrola pokrycia sprawdza brakujące powierzchnie. Cztery połączenia TRANSPORT w teście nawigacji oznaczają przejazdy windami, które są dodatkowo testowane z fizycznym graczem.
