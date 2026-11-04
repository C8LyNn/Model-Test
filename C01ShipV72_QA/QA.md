# QA — logistyka poziomu 0, v7.2

Zamieniono funkcje czterech równych sektorów: maszynownię ustawiono bezpośrednio pod sterownią w obu osiach, a ładownię przy śluzie towarowej; zapasy znajdują się w tej samej części statku co hydroponika i bliżej kuchni. Przeniesiono 50 istniejących elementów wyposażenia, zachowując ich skalę i możliwość edycji.

- `logistics_aligned.xml` sprawdza położenia, etykiety, dostęp do maszynowni i przejście przez bramę śluzy towarowej.
- `regression_aligned.xml` zawiera wyniki szerszych testów PlayMode, obejmujących także mostek, windy i trasę pościgu.
- `hydroponics.xml` potwierdza przejście z korytarza do hydroponiki oraz z hydroponiki do oczyszczalni.
- `source_audit.json` sprawdza 2723 obszary podłóg, 2234 obszary sufitów, dostępność stref oraz trzy położenia bram. `collision_positive_control.json` zawiera oczekiwany wynik FAIL dla celowo zdublowanego modelu.
- `blender_reopened.json` potwierdza odczyt i położenia obiektów w ponownie otwartym pliku Blender.
- `Screenshots` zawiera zrzuty Unity i schemat poziomu 0 z danych montażowych.

Nie eksportowano nowych modeli FBX, ponieważ wykorzystano istniejące. Pełna ręczna rozgrywka i osobny build Windows: NOT RUN.
