# Standard montażu C01 PASS 02

Wartości poniżej są wymaganiami nowego systemu. Komentarze i instrukcje w starej paczce v1.3 są materiałem audytowym.

## Osie, pivot i skala

Unity: +Y w górę, +Z do przodu. Ściana biegnie lokalnie po +X. Root każdego modułu ma skalę (1,1,1). Transform części geometrii jest tożsamościowy; jej rzeczywiste wierzchołki mają wymiary w metrach.

| Moduł | Pivot | Obrys lokalny | Montaż |
|---|---|---|---|
| F01/F02 | narożnik płytki na poziomie chodu | x,z=0..3; y=-0,18..0 | y=0 |
| C01 | narożnik spodu płytki | x,z=0..3; y=0..0,18 | y=3 |
| W01/W02/W05 | początek osi ściany | x=0,15..2,85; y=0..3; z=±0,15 | jeden węzeł na każdy koniec |
| W04 | identycznie jak pozostałe ściany | ten sam obrys z otworem | framuga/skrz. jako dzieci socketów |
| N_* | środek wspólnego węzła | x,z=±0,15; y=0..3 | dokładnie jeden właściciel |
| W00 STANDALONE | początek pełnego panelu | x=0..3; y=0..3; z=±0,15 | niezależny panel, własne półwęzły |

Dodatni obrót Unity Y: lokalne +X przechodzi w -Z. Zatem yaw=0 biegnie po +X, yaw=90 po -Z, yaw=180 po -X, yaw=270 / -90 po +Z. Master używa kanonicznie yaw=0 i -90; biblioteka i scena połączeń obsługują wszystkie cztery orientacje.

## Sockety ścian i węzłów

Start=(0,0,0), normalna=(-1,0,0); End=(3,0,0), normalna=(1,0,0). To punkty osiowe na siatce. Płaszczyzny fizycznego styku są odpowiednio na x=0,15 i x=2,85. JSON rozróżnia `position` i `contact`, aby rozstaw siatki nie był mylony z długością samego wypełnienia.

Sockety węzła E/N/W/S mają wspólną pozycję osiową i kierunki ±X/±Z; ich contact leży 0,15 m w danym kierunku. Port ściany i port węzła mają przeciwne normalne, tę samą pozycję osiową oraz tę samą płaszczyznę kontaktu. Niewykorzystane strony węzła są zamknięte pełną powierzchnią.

Klasyfikacja wynika wyłącznie z liczby i kierunku krawędzi: END=1, STRAIGHT=2 przeciwległe, CORNER=2 prostopadłe, T=3, CROSS=4. Węzeł jest deduplikowany po współrzędnych na siatce; nie należy scalać kilku słupków w jednym miejscu. Wszystkie typy mają identyczny przekrój, więc obrócenie lub podmiana wariantu nie zmienia płaszczyzny styku.

Na krawędzi podłogi/sufitu dwie płytki dotykają się dokładnie na tej samej płaszczyźnie. Dekoracje są rozłącznymi objętościowo fragmentami jednej płaskiej warstwy. Nie stosuje się przesunięć 1 mm, nakładania paneli ani listew ukrywających niedopasowanie.

## Drzwi

Surowy otwór: x=0,50..2,50; y=0..2,50. Światło framugi: x=0,60..2,40; y=0..2,40. Cała framuga leży w przekroju ściany z=±0,15 i w jej module 3 m.

Socket Frame=(0,0,0); Hinge=(0,66;0,02;0). Skrzydło ma lokalnie x=0..1,68, y=0..2,34, z=±0,03; dwa prostokątne segmenty zawiasów rozciągają się do x=-0,035. Luzy są jawne i zamierzone: 20 mm od podłogi, 40 mm od nadproża, 60 mm od głównego korpusu skrzydła do bocznej framugi, 25 mm przy segmentach zawiasów. To luźne drzwi demonstratora geometrycznego, bez uszczelek; nie są deklarowane jako hermetyczne.

Drzwi obracają się lokalnie o 0..90° wokół +Y. Controller jest na W04, hinge to dziecko z kinematycznym Rigidbody; każda część ma BoxCollider. Nie ma niezależnych pozycji skrzydła w świecie. Każde drzwi mają własny stan i API `SetOpen`, `Toggle`, `SetAngleImmediate`.

Przejścia między pokojami korzystają ze stykających się podłóg po obu stronach. Zewnętrzne wejście ma dodatkowy podest 3×3 m. Przy 90° testowana jest kapsuła o średnicy 0,60 m i wysokości 1,80 m, prowadzona przez przejście w 21 pozycjach.

## Blender i formaty wymiany

Źródło Blender mapuje współrzędne Unity (x,y,z) na (x,-z,y). Skala jednostki Blender=1 m; wszystkie części są osobnymi meshami. FBX używa -Z forward / Y up i kopii siatek z odbiciem X, które kompensuje rzeczywistą konwersję prawoskrętną → lewoskrętną importera Unity. Odbicie jest zapisane w wierzchołkach eksportu; źródła i transformacje montażu nie otrzymują ręcznych poprawek ani ujemnych skal.

Konwersję sprawdzono na rzeczywistych importach: w Blenderze po udokumentowanej konwersji i w Unity już we współrzędnych docelowych. Kontrola obejmuje każdy obiekt części, obrys i liczbę ścian, nie tylko zbiorczy bounding box.
