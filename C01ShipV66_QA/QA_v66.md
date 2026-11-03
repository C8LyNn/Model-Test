# QA — C01 Ship v6.6, 2026-11-03

Unity 6000.3.14f1, PlayMode: **4/4 PASS** (`playmode.xml`). Testy sprawdziły kapsułę 1,8 m / promień 0,28 m, wysokość kamery 1,65 m, chód 2,5 m/s, bieg 5 m/s, FOV 75°, brak kolizji w punkcie startowym, zoom ortograficzny i powrót do spaceru, wejście po schodach oraz przycisk i przejazd po jednej windzie osobowej i towarowej wraz z kamerą.

Test wyjściowy v6.5: 0/2 PASS — oczekiwane niezgodności prędkości i pola widzenia (przed zmianą: 5 m/s i 65°), patrz `before_playmode.xml`. Zbudowano scenę z prefabrykatu v6.5; nie modyfikowano geometrii statku. Zmiany wspólnego kontrolera są konfigurowane przez nową scenę, wartości domyślne zachowują poprzednie zachowanie.

Nie wykonano kompletnego ręcznego przejścia wszystkich pomieszczeń ani kompilacji samodzielnej gry Windows. Zrzuty w `Screenshots` pochodzą z kamery sceny wyrenderowanej w Unity; nie są dowodem ręcznej rozgrywki.
