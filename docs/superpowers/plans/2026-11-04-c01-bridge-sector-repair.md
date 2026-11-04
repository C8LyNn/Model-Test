# C01 v6.8: mostek, rufa, siatka i łączność

Cel: sektory poziomu 1 mają dwa moduły (6 m) wysokości; główny kadłub pozostaje szeroki na 19 kratek. Układ mostka i rufy ma czytelne funkcje i ścieżki: stanowiska dowodzenia, nawigacji, obsługi napędu i windy dostępne z galerii, bez losowych podestów w przejściu. Poziom 0 otrzymuje dodatkowe przejścia od korytarza i pomiędzy strefami. Zachować możliwość pościgu na poziomie 2 oraz wcześniejsze sceny.

Podejście: oddzielny generator i prefab v6.8, podłoga z siatki 3 m i prześwit 3 m, pokłady -3,4 / 0 / 3,4 m wraz z grubością stropu 0,4 m. Ściany dzielić na zgodne z pokładami pełne moduły i osobne strefy stropowe; brama wraz z ościeżnicą pozostaje w jednej kratce. Linie wizualne liczyć z rzeczywistych wysokości, a nie z globalnej wielokrotności 3 m. Znaleźć i poprawić źródło napisów widocznych przez ściany.

1. Odtworzyć problem etykiet, wymiarów sektorów i braku połączeń testami danych oraz Unity.
2. Wygenerować sześć sektorów dwukondygnacyjnych i więcej przejść poziomu 0; zachować ciągłą trasę poziomu 2, zabezpieczyć krawędzie galerii, sprawdzić dojścia do każdego sektora.
3. Zaprojektować i wymodelować czytelne wnętrza mostka i rufy z osobnych prefabów; sprawdzić sprzęt, kolizje i dostępność.
4. Sprawdzić pełną geometrię bram w różnych stanach, pokrycie, moduły ścian, napisy z obu stron w rzeczywistym Unity; zapisać zrzuty oraz ograniczenia.
5. Zachować stare wersje, dostarczyć scenę, prefab, modele i źródła, wdrożyć w zamkniętym projekcie oraz zaktualizować GitHub i Dysk Google.
