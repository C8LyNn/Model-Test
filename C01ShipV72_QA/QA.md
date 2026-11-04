# QA — logistyka poziomu 0, v7.2

Zamieniono funkcje czterech równych sektorów: maszynownię ustawiono pod sterownią, a ładownię przy śluzie towarowej; zapasy znalazły się przy hydroponice i bliżej kuchni. Przeniesiono 14 istniejących elementów wyposażenia, zachowując ich skalę i możliwość edycji.

- `logistics_tests.xml` sprawdza położenia, etykiety, dostęp do maszynowni i przejście przez bramę śluzy towarowej.
- `regression.xml` zawiera wyniki szerszych testów PlayMode, obejmujących także mostek, windy i trasę pościgu.
- `source_audit.json` sprawdza 2723 obszary podłóg, 2234 obszary sufitów, dostępność stref oraz trzy położenia bram. `collision_positive_control.json` zawiera oczekiwany wynik FAIL dla celowo zdublowanego modelu.
- `blender_reopened.json` potwierdza odczyt i położenia obiektów w ponownie otwartym pliku Blender.
- `Screenshots` zawiera zrzuty Unity i schemat poziomu 0 z danych montażowych.

Nie eksportowano nowych modeli FBX, ponieważ wykorzystano istniejące. Pełna ręczna rozgrywka i osobny build Windows: NOT RUN.
