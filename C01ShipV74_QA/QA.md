# QA — C01 Ship v7.4

## Zakres

Trasa poziomu 2 prowadzi przez pomosty w sektorze treningowym, sterowni maszynowni i sektorze medycznym. Sześć nowych bram zaczyna otwartych. Trzy przegrody uniemożliwiają ominięcie sektorów głównym korytarzem. Niższe funkcje sektorów pozostają w istniejącej scenie. Nowe modele, rozmieszczenie w Unity i montaż Blender korzystają z `Assets/C01ShipV74/Data/pursuit.json`.

## Dowody

- `route_initial.xml`: Unity 6000.3.14f1 Play Mode, przejście postacią od mostka do wyjścia przez wszystkie trzy sektory, blokady skrótów, przyciski po obu stronach sześciu bram i obecność modułów z colliderami.
- `regression.xml`: cztery testy Play Mode, obejmujące windy pasażerską i towarową, schody, drabinę, wejście do wentylacji, przejścia na poziomie 0 oraz dostęp do stanowisk mostka i rufy. Pierwsza próba w sandboxie nie uzyskała licencji Unity; ponowne uruchomienie poza sandboxem zakończyło się poprawnie.
- `source_audit.json`: pokrycie istniejących obszarów podłóg i sufitów oraz analiza brył dla trzech pozycji bram. Wynik geometrii nie zastępuje testu przejścia ani kontroli wizualnej.
- `catwalk_coverage.json`: pokrycie 24 kratek pomostów sprawdzone wraz z sąsiednimi elementami konstrukcji.
- `C01SourceV74/test_sector_route.py`: testy danych i dwa testy wykrywające celowo usuniętą kratkę oraz zdublowaną barierkę.
- `blender_reopened.json` i `blender_exports.json`: ponownie otwarty montaż Blender oraz rzeczywisty eksport i powtórny import nowych modeli bramy FBX. Pliki OBJ również wyeksportowano.
- `Screenshots/`: rzuty z Unity przed i po zmianie oraz osobno podpisany schemat trasy z danych montażowych.

## Ograniczenia

Nie wdrożono modelu potwora ani jego AI. Pełne ręczne przejście oraz samodzielny build Windows: NOT RUN. Automatyczne testy gracza sprawdzają ruch i kolizje, nie zachowanie potwora. Nowe przejścia mają wysokość 2,6 m z powodu istniejącej grubości stropu i rzędnej pomostu.
