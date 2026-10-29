# Odwzorowanie planu

Dziób jest po lewej (-X), rufa po prawej (+X), górna część rysunku odpowiada +Z. Wymiary ustalono na potrzeby sceny, ponieważ plan nie miał skali.

| Element z rysunku | Strefa sceny | Nominalny obszar x/z [m] |
|---|---|---|
| Mostek | BRIDGE | wielokąt x=-12..0, z=3..18 |
| Koszary | KOSZARY | x=0..15, z=15..21 |
| Laboratorium | LAB | x=15..30, z=15..21 |
| Sektor medyczny | MED | x=30..45, z=15..21 |
| Magazyn | CARGO | x=0..15, z=0..6 |
| Maszynownia | ENGINEERING | x=15..30, z=0..6 |
| Sektor techniczny | TECH | x=30..45, z=0..6 |
| Kajuty 01/02, 03/04, 05/06 | C01..C06 | z=12..15; szerokość kajuty 6 m |
| Kajuty 07/08, 09/10, 11/12 | C07..C12 | z=6..9; szerokość kajuty 6 m |
| Korytarze poprzeczne | XN1..XN3, XS1..XS3 | x=6..9, 21..24, 36..39 |
| Korytarz główny | MAIN_W / MAIN_M / MAIN_E | z=9..12 |
| D1 | D1 | x=12..18, z=9..12, środek x=15 |
| D2 | D2 | x=27..33, z=9..12, środek x=30 |
| Rufa / węzeł śluz | STERN | x=45..48, z=3..18 |
| D3 / wyjście 1 | D3 / EXIT_N | x=45..48; śluza z=18..21, podest z=21..24 |
| D4 / wyjście 2 | D4 / EXIT_S | x=45..48; śluza z=0..3, podest z=-3..0 |
| Napęd ×5 | ENGINE_01..05 | pięć prefabów P_Engine po prawej stronie rufy |

12 kajut ma dokładnie 12 wejść z korytarzy poprzecznych. Nie dodano drzwi z kajut do głównego korytarza ani do dużych sektorów. Trzy górne i trzy dolne sektory mają połączenia między sobą, tak jak na planie. Mostek i rufa mają po trzy połączenia z centralnym układem.

Łącznie są 36 osobne drzwi: 12 kajutowych, 6 wejść do sektorów z poprzecznych korytarzy, 4 połączenia między sektorami, 3 wejścia mostka, 3 rufy i 8 drzwi czterech śluz.

Kierunki skrzydeł dobrano po testach: kajutowe otwierają się do kajut, sektorowe do sektorów, boczne wejścia rufowe odchodzą od węzła śluz. Drzwi wyjściowych śluz otwierają się do ich komór z przeciwnych stron. Osiągnięto to zmianą orientacji standardowego modułu co 90° i zamianą końców osi, bez skalowania modeli lub ręcznych poprawek styku geometrii.

Pierwotny szkic jest referencją układu. Dodane wyposażenie, metryczne proporcje, grubość osłon i dwa podesty są decyzjami wykonawczymi. Wzmianka na obrazie o dziesięciu stylach nie była osobnym zamówieniem dziesięciu scen.
