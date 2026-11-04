# QA — mostek v6.9

Nowa scena `Assets/C01ShipV69/Scenes/C01_Ship_Multideck_v69.unity` i wariant prefabu `C01_SHIP_MASTER_V69.prefab` bazują na v6.8. Wspólne dane `bridge_layout.json` obejmują 19 osobnych elementów: 6 konsol, 7 foteli i 6 ekranów. Jest to zmiana układu istniejących modeli, a nie kompletna przebudowa wnętrza lub finalne modele graficzne.

Testy źródłowe `C01SourceV69/test_bridge_layout.py` sprawdzają liczby stanowisk, brak duplikatów i lustrzane pozycje par. Rzeczywiste testy PlayMode w `bridge_verified.xml` sprawdzają zgodność 19 pozycji sceny z danymi, brak penetracji koliderów, dojście postaci do stanowisk i obu wind oraz trasę pościgu od mostka do wyjścia. Osobna próba `bridge_interaction.xml` sprawdza przycisk bramy i przejazd windą z graczem. Zrzuty sceny Unity znajdują się w `Screenshots`.

Blender 5.2.3 LTS zapisał osobny edytowalny montaż bazowy i ponownie go otworzył w osobnym procesie: `blender_reopened.json` potwierdza wszystkie 19 pozycji i współdzielenie siatek modeli. Ponownie wykorzystano rzeczywiste FBX/OBJ z `C01SourceV68/Models`; nie wykonywano nowego eksportu FBX, ponieważ geometria tych modeli nie uległa zmianie.

Ograniczenia: materiały i modele są uproszczone; pełna ręczna rozgrywka i osobny build Windows NOT RUN. Zmiany nie stanowią przebudowy pozostałych stref statku.
