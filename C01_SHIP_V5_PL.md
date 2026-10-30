# C01 — modułowy statek v5

Projekt Unity 6000.3.14f1 / URP. Nowa scena: `Assets/C01ShipV5/Scenes/C01_Ship_Multideck_v5.unity`. Prefab nadrzędny: `Assets/C01ShipV5/Prefabs/C01_SHIP_MULTIDECK_MASTER_V5.prefab`. Poprzednia scena v4 pozostaje w `Assets/C01ShipV4`.

Kratka to 3 m. Standardowe panele ścienne mają moduł 3 × 3 m, są osobnymi instancjami wspólnego prefabu, bez rozciągania. Nominalne 3 m szerokości obejmuje wspólne węzły na końcach; sama widoczna wkładka między nimi ma 2,7 m, aby sąsiednie ściany nie dublowały narożników. Krótkie elementy uzupełniają miejsca przy płytach, narożach i bramach. Podzielono również poszycie dziobu, framugi i ruchome segmenty bram.

Sektory pokładu 0 i 1 mają małe antresole 6 m nad podłogą, z czterech powtarzanych odcinków schodów i dwóch odcinków drabiny. Krótkie kanały wentylacyjne mają posadzkę, boczne ścianki, dach i kratkę na zamkniętym końcu; można wejść do nich z antresoli. Nie są to jeszcze kanały łączące sektory między sobą. Główne połączenia między pokładami zapewniają obie windy.

Po uruchomieniu Play startuje spacer: WASD ruch, przytrzymany prawy przycisk myszy obraca widok, Shift przyspiesza, Spacja skacze, E rozpoczyna/kończy wspinanie w pobliżu drabiny, W/S wspina w górę/w dół; lewy przycisk uruchamia panel bramy/windy pod celownikiem. `1` wybiera podgląd, `2` wraca do spaceru. `R` przełącza dachy, `L` etykiety.

Moduły są osobnymi prefabami w `Prefabs/Modules`; rzeczywiste pliki FBX/OBJ znajdują się w `Models`. W paczce źródłowej są generator, testy, plik `.blend` i GLB. Generator sceny w edytorze: `Tools > C01 Ship v5 > Rebuild and verify`. Rzeczywiste wyniki, zrzuty oraz testy niewykonane są w raporcie QA.
