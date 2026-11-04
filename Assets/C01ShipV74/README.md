# C01 Ship v7.4 — trasa pościgu przez sektory

Otwórz `Scenes/C01_Ship_Multideck_v74.unity` w Unity 6000.3.14f1. Nadrzędny prefab znajduje się w `Prefabs/C01_SHIP_MASTER_V74.prefab`. Sceny wcześniejszych wersji pozostają oddzielne.

Na poziomie 2 droga od mostka do wyjścia prowadzi teraz kolejno przez sektor treningowy, sterownię maszynowni i sektor medyczny. Trzy przegrody odcinają skrót głównym korytarzem. Każdy sektor otrzymał pomost z powtarzalnych kafli 3 × 3 m, barierki, przeszkody oraz dwie bramy z przyciskami po obu stronach. Bramy zaczynają otwarte, ale można je zamykać i otwierać. Pomosty pozostawiają funkcje dolnych części sektorów.

Poziom 2 wykorzystuje istniejące korytarze boczne. Nowe przejścia mają 2,6 m wysokości ze względu na istniejący strop i poziom podłogi. Plik `Data/pursuit.json` jest wspólnym źródłem dla generatora Unity, testów i dodatkowego montażu Blender. Otwórz tryb chodzenia zgodnie z istniejącymi kontrolkami projektu.

To trasa dla gracza i przygotowane miejsce na pościg: nie dodaje ona sztucznej inteligencji ani modelu potwora. Raport testów i zrzuty znajdują się w `C01ShipV74_QA` w pełnej paczce.
