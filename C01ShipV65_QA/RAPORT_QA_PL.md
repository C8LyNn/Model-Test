# C01 v6.5 — raport QA

Konstrukcja wykorzystuje siatkę 3 m i oś symetrii Z = 43,5 m. Symetria obejmuje obrys, rozmieszczenie pomieszczeń, łazienek, modułów ścian i podłóg, bram, wind oraz napędów; funkcje i wyposażenie przeciwległych pomieszczeń różnią się celowo.

## Kontrole danych

- 29 testów źródłowych, w tym testy symetrii pomieszczeń, łazienek, 144 bram, ścian, podłóg, wind i napędów oraz testy wykrywające brakujące elementy: PASS (`source_tests.txt`).
- Pełna geometria źródłowa wraz z wyposażeniem, pięć położeń bram: 0 wykrytych przenikań (`geometry_*.json`).
- Podłogi: 4654 regiony, sufity: 4566 regionów — bez wykrytych braków (`floor_coverage.json`, `ceiling_coverage.json`).
- 27 korytarzy, 198 pól: brak wykrytych braków podłogi (`corridor_floor_coverage.json`).
- Próbkowanie tras z otwartymi bramami znalazło dojście do wszystkich stref i przystanków (`routes.json`); nie zastępuje ręcznego przejścia.
- Sprawdzenie obudów sześciu wind w pełnym zakresie podróży i pięciu pozycjach bram: 0 wykrytych przenikań (`cabin_swept_clearance.json`).

## Ograniczenia

Plan uwzględnia 24 kajuty po cztery łóżka, funkcje żywienia, higieny, odpoczynku, medycyny, zaopatrzenia, upraw oraz utrzymania systemów. Nie przeprowadzono inżynieryjnego bilansu zapasów i zasobów na wieloletni lot, nie symuluje się systemów podtrzymywania życia ani nie potwierdzono pojemności ewakuacji dla 96 osób. To wiarygodniejszy program funkcjonalny, a nie dowód samowystarczalności rzeczywistego statku.

Eksport Blender 5.2.3 LTS: 406 modeli FBX/OBJ; 17 wybranych modeli ponownie zaimportowano i porównano z geometrią źródłową — PASS (`../C01SourceV65/QA/blender_models_v65.json`). Bazowy plik .blend został ponownie otwarty; zweryfikowano położenie napędu. Warstwa mostka i obudowy wind składana jest w Unity. Unity 6000.3.14f1 URP: 14/14 testów PlayMode PASS (`living_playmode.xml`, `regression_playmode.xml`, `freight_playmode.xml`), obejmujących wejścia do kuchni, jadalni, salonu, pralni, kontroli wody i czterech lustrzanych łazienek, schody i wentylację, wszystkie sześć wind z trzech poziomów, przyciski i blokadę śluzy towarowej. Pełne ręczne przejście statku, samodzielny build Windows i import FBX do czystego projektu Unity: NOT RUN.



Zrzuty Unity w `Screenshots/` pokazują korytarze, mostek, windę, sektor, kuchnię, jadalnię i pralnię. Nowe wyposażenie to uproszczone modele przestrzenne; gotowanie, pranie i magazynowanie nie są symulowane.
