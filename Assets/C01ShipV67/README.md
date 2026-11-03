# C01 statek v6.7

Otwórz `Assets/C01ShipV67/Scenes/C01_Ship_Multideck_v67.unity` w Unity 6000.3.14f1. Warianty v6.5 i v6.6 pozostają w projekcie.

Jedna kratka to 3 m. Zwykłe pomieszczenia i sektory mają wysokość jednej kratki; sektory boczne zajmują po sześć kratek szerokości. Mostek i rufa są atriami o wysokości czterech kratek z częściowymi galeriami, półpiętrami i windami. Pokład 2 ma otwartą trasę pościgu od mostka do wyjścia ewakuacyjnego przy rufie, z naprzemiennymi przeszkodami. To układ do rozgrywki; nie dodano potwora ani logiki pościgu.

WASD — ruch, mysz — rozglądanie, Shift — bieg, spacja — skok, E/lewy przycisk myszy — interakcja, Esc — zwolnienie kursora, 1/2 — podgląd/spacer. Prędkość chodu wynosi 3,5 m/s, biegu 7 m/s.

Generator danych: `C01SourceV67/Tools/scene_data_v6.py`; następnie `C01SourceV67/design_v67.py`. Sceny/prefaby generują kolejno menu **Tools/C01 Ship v6.7/Rebuild base** i **Build final**. Wymaga to zapisania otwartych scen.
