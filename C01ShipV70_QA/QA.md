# QA — C01 Ship v7.0

Ujednolicono krawędzie stropów i podziały paneli bez usuwania konstrukcyjnego wypełnienia. Przesunięto 628 segmentów ścian, zachowując ich łączną bryłę; zmieniono podział wizualny w 784 modułach ścian i 14 zakończeniach. Wyrównano powierzchnie 504 modułów dachu, zachowując dotychczasowe wysokości sufitów od wewnątrz. Dziewięć powtarzalnych wariantów dachów i dwa warianty ścian zapisano jako osobne prefaby.

- Testy danych źródłowych: 6 przypadków obejmujących bryły ścian, podziały i pokrycie dachu.
- Kontrola geometryczna danych: 2669 obszarów podłogi i 2234 obszary sufitu bez braków; test penetracji w trzech położeniach bram w plikach `geometry_*.json`.
- Kontrola dodatnia: `collision_positive_control.json` dokumentuje celowo nałożoną kopię ściany. Audyt wykrył ten problem; wynik `FAIL` w tym pliku jest oczekiwany dla uszkodzonej próbki, nie dla sceny.
- Unity EditMode: `prefabs_editmode.xml` sprawdza powiązania wszystkich 1302 zmienionych modułów z 11 współdzielonymi prefabami.
- Unity PlayMode: wyniki końcowej sceny zapisano w `regression_final.xml`. Testy obejmują geometrię, przejścia, bramy, windy oraz trasę pościgu.
- Blender 5.2.3 LTS: `blender_reopened.json` opisuje ponownie otwarty plik źródłowy, a `blender_exports.json` potwierdza eksport i ponowny import 11 modeli FBX. Modele OBJ również zapisano.
- Zrzuty porównawcze Unity znajdują się w `Screenshots`.

Pełna ręczna rozgrywka i oddzielny build Windows: NOT RUN. Testy geometrii nie zastępują wizualnej kontroli każdego miejsca statku.
