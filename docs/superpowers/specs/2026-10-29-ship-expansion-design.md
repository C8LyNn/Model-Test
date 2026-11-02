# Rozszerzenie statku C01 — v3.1

Żądanie: jednakowa szerokość korytarzy, większy statek i dłuższe boczne odnogi. Zachowane są topologia planu, 12 kajut, 6 sektorów, 36 drzwi i 5 silników.

Wybór wykonawczy: sześć bocznych odnóg rośnie z 3 do 9 m, przy szerokości nominalnej 3 m. Korytarz główny, rufowy i śluzy zachowują tę szerokość. Korpus 45 × 21 m zmienia się w 45 × 33 m. Kajuty rosną z 6 × 3 m do 6 × 9 m; sektory pozostają 15 × 6 m. Otwory kajut znajdą się w środkowych modułach dłuższych odnóg. Nominalna siatka pozostaje 3 m; wszystkie skale instancji wynoszą 1.

Dodawanie modułów zachowuje zgodność istniejących modeli. Rozciąganie gotowego prefabu zmieniłoby grubości i drzwi, więc odpada. Samo przesunięcie sektorów pozostawiłoby brakujące fragmenty podłóg i kabin; dlatego granice, kadłub, sufit i podłogi powstają ponownie z tych samych danych montażowych.

Poprzednia paczka Desktop v3.0 i istniejący commit PR pozostają dostępne. Aktualizacja trafia do otwartego projektu Model Test i tego samego PR. Generowanie zachowuje ustawienia projektu użytkownika.

Dowód: niezależne testy długości/szerokości i pola podłogi, audyty braków geometrii, penetracji i drzwi, rzeczywisty eksport Blender/FBX, import Unity i przejście postaci przez pełne boczne odnogi. Render z góry i przekrój muszą pokazać wydłużenie, a kamera obejmować cały statek.
