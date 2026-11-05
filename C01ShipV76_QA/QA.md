# QA — układ eksploatacyjny statku v7.6

Zmiana porządkuje sześć pomieszczeń wsparcia, przenosi 14 elementów wyposażenia oraz ustawia prom przy nowym wylocie burtowym. Szersze wyjście składa się z modularnych elementów bramy i ośmiu kratek płyty zewnętrznej. Pozostałe śluzy, windy, wspólne sektory i trasa pościgu pozostają zachowane.

- `source_audit.json`: pokrycie istniejących podłóg i sufitów, dostępność stref oraz kolizje dla trzech położeń bram. Wynik braku penetracji nie zastępuje analizy prześwitu.
- `previous_shuttle_path.json`: poprzedni ruch w osi promu zatrzymywał się na elemencie `L0_EVAC_INNER_FRAME_6_0_0`.
- `C01SourceV76/test_operational.py`: kontrola sąsiedztwa, kratek płyty i przemieszczenia pełnej geometrii promu przez otwór. Test potwierdza blokadę przez zamkniętą bramę i wykrywa celowo dodaną przeszkodę.
- `blender_reopened.json` i `blender_exports.json`: ponownie otwarty plik źródłowy i eksport trzech nowych modeli bramy do FBX/OBJ, w tym ponowny import FBX.
- Unity 6000.3.14f1 Play Mode: `final.xml` — 16/16 testów przed końcową korektą styków bramy; `shuttle_full.xml` — test przesuwu całego promu o 18 m; `operations_final2.xml` — 4/4 ponowionych testów układu i bramy po korekcie. Zrzuty Unity: katalog `Screenshots`.

Brama wylotowa nie symuluje ciśnienia i nie jest automatycznie sprzężona z pozostałymi drzwiami hangaru; prom nie ma sterowania lotem. Pełna ręczna rozgrywka, samodzielny build Windows i AI potwora: NOT RUN.
