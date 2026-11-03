# C01 v6.5 — symetryczny statek dla załogi

Otwórz `Scenes/C01_Ship_Multideck_v65.unity`. Główny prefab: `Prefabs/C01_SHIP_MASTER_V65.prefab`. Plany pokładów z tych samych danych montażowych znajdują się w `Documentation/Plan_Poklad_0_v65.png`, `Plan_Poklad_1_v65.png` i `Plan_Poklad_2_v65.png`.

Korytarz główny wyznacza oś symetrii. Kadłub, ściany, podłogi, 24 kajuty z łazienkami, bramy i sześć szybów wind mają odbite odpowiedniki. Funkcje pomieszczeń po przeciwnych stronach mogą się różnić. Są dwie windy towarowe na rufie i cztery osobowe: po dwie na mostku i rufie. Doki ewakuacyjny i zaopatrzeniowy są rozmieszczone symetrycznie.

- Poziom 0: maszynownia, oczyszczanie, hangar ewakuacyjny, magazyn, uprawy i zapasy żywności.
- Poziom 1: trening, laboratorium, medycyna, magazyn, sterowanie maszynownią i sektor techniczny, z pomieszczeniami pomocniczymi.
- Poziom 2: kajuty oraz kuchnia, jadalnia, salon, rekreacja, pralnia, pościel, środki higieny, naprawa odzieży, pokój wyciszenia, telemedycyna, łączność i nadzór wody oraz powietrza.

Każda kajuta ma cztery łóżka: łącznie 96 miejsc. Jadalnia i pralnia są wyposażone w powtarzalne osobne modele. To układ koncepcyjny: nie wykonano bilansu żywności, wody, tlenu ani zużycia części na wieloletnią misję; aparatura i zapasy nie są symulacją systemów podtrzymywania życia.

Jedna kratka to 3 m. Korytarze mają jedną kratkę szerokości; zwykłe pomieszczenia na poziomach 1 i 2 mają jedną kratkę wysokości, a sektory i poziom 0 — dwie. Sterowanie: `2` spacer, WASD ruch, mysz obrót, `E` interakcja/drabina, LPM panel, Esc kursor.

Generator: `C01SourceV65/Tools/scene_data_v6.py`, następnie `C01SourceV65/design_v65.py`; w Unity menu `Tools/C01 Ship v6.5/Rebuild base` i `Tools/C01 Ship v6.5/Build final`. Dane montażowe: `Data/ship_v65.json` oraz `Data/polish_v65.json`. Bazowy montaż Blender i osobne FBX/OBJ są w `C01SourceV65`; dodatkowa warstwa mostka i kabin wind jest tworzona w Unity. Poprzednie wersje pozostają w projekcie.
