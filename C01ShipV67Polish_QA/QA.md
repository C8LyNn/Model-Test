# QA: drobne poprawki C01 v6.7.1

- W spacerze etykiety pomieszczeń są ograniczone do 18 m, pola widzenia kamery i niezasłoniętej linii widzenia. L nadal włącza/wyłącza etykiety, a podgląd zachowuje oznaczenia poziomów.
- Przy widocznym przycisku w zasięgu pojawia się wskazówka E / LPM dla bramy lub windy. Wskazówka korzysta z tego samego pierwszego trafienia fizyki co interakcja; samo spojrzenie nie naciska przycisku.
- Unity 6000.3.14f1, PlayMode: `final.xml` 2/2, `ship_regression.xml` 5/5, `older_scene.xml` 4/4. Obejmują ścianę zasłaniającą etykietę i przycisk, zasięg, celowanie i aktywację, trasę, półpiętro oraz windy i starszą scenę.
- NOT RUN: pełna ręczna rozgrywka oraz build standalone; nie weryfikowano wizualnie wszystkich pomieszczeń.
