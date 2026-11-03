# QA C01 v6.7

Jedna kratka = 3 m. Wersja oparta na osobnej scenie i prefabie v6.7. Kadłub zasadniczy ma 42 × 19 kratek (wcześniej 42 × 31); sektory mają szerokość 6 kratek. Standardowe pomieszczenia na wszystkich trzech poziomach mają wysokość 3 m. Atrium mostka i rufy ma 12 m od pokładu 0 do stropu; windy zatrzymują się na wysokościach -3,4 / 0 / 3,4 m. Na półpiętrach są podesty i schody. Na pokładzie 2 jest dziewięć przeszkód i otwarte wyjście rufowe. Chód/bieg 3,5/7 m/s.

Unity 6000.3.14f1 PlayMode (`playmode_final.xml`): **5/5 PASS**. Sprawdzono przejście postacią z głębi mostka przez przeszkody do wyjścia, wejście na półpiętro, przycisk i przejazd windą osobową i towarową wraz z kamerą, kolizje stanowisk mostka oraz wymiary i prędkości. Test wcześniejszy ujawnił kolizję ekranu z barierką; zwężono ekran i wykonano pełny test ponownie.

Kontrola danych generatora: 0 wykrytych przenikań elementów w pięciu położeniach bram (0, 25, 50, 75 i 100%); podłogi: 3060 obszarów, 0 braków; sufity: 2738 obszarów, 0 braków. Skan ścieżek 2D wskazuje dostępność wszystkich pomieszczeń i przystanków wind; to nie jest zastępstwo dla ręcznego przejścia całego statku. Wyniki i zrzuty w katalogu QA.

NOT RUN: pełna ręczna rozgrywka i build samodzielnej gry. Potwór i logika pościgu nie zostały dodane. Blender 5.2.3: wyeksportowano 412 modeli FBX i OBJ oraz edytowalny montaż bazowy `.blend`; 17 wybranych modeli przeszło próbę ponownego importu. Montaż bazowy odtwarza dane generatora; końcowe wykończenie i interakcje są składane w Unity. Prefab i .unitypackage pochodzą z rzeczywistego eksportu Unity (log `export_verified.log`).
