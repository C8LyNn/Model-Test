# Raport C01 v6.1

Środowisko: Unity 6000.3.14f1, URP, Windows, GeForce RTX 5080. Przed zmianami zapisano `baseline.json` i zdjęcia `baseline/`; po zmianach `after.json` i `after/`. Ujęcia `after/button_front.png` i `after/button_back.png` pokazują odpowiednio czytelny podpis z przodu i zasłonięcie od tyłu.

## Pomiar przełączania widoków

Mediany czterech wywołań w edytorze w trybie batch, na tym samym komputerze, w milisekundach:

| Operacja | v6 przed | v6.1 po |
| --- | ---: | ---: |
| Spacer → podgląd | 162,6 | 38,9 |
| Podgląd → spacer | 117,5 | 13,1 |
| Zmiana pokładu | 108,2 | 43,3 |

To pomiar metod przełączających w edytorze, nie pomiar FPS w grze. Wartości renderingu w JSON obejmują odczyt obrazu z GPU. Liczba draw calls nie została zmierzona (`-1`). Pomiary przydziałów pamięci zwróciły zera i nie są podstawą wniosków o GC. Liczba świateł: 102 przed i po; liczba rendererów wzrosła o 278 tymczasowych napisów (68 422 → 68 700).

## Testy

- Wyniki Unity EditMode: `editmode_final.xml`.
- Pierwsza seria PlayMode: `playmode.xml`: 8/9; test windy z obiektem poza platformą zgłosił przesunięcie o 0,03225 m przy tolerancji 0,03 m.
- Powtórzenie: `playmode_retry.xml`: 2/2, w tym ten sam test windy i otwarcie bramy w scenie v6.1. Przyczyna pierwszego wyniku nie została jednoznacznie ustalona; test traktować jako niestabilny.
- Render przycisku sprawdzono w Unity z przodu i z tyłu. Automatyczny test sceny sprawdza dopasowanie napisów do ekranów i przełączanie ich widoczności.

Nie wykonano pełnego ręcznego spaceru po statku, testu wydajności w samodzielnej kompilacji Windows ani pomiaru FPS. Kanały wentylacyjne nadal kończą się kratkami, a nie wszystkie podesty mają komplet barierek. Geometria całego statku nie była ponownie poddana pełnemu audytowi szczelin podczas tych poprawek.
