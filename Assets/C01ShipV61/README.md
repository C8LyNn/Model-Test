# C01 Ship v6.1 – poprawki ogólne

Scena: `Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity`. Zachowuje połączenie z edytowalnym prefabem nadrzędnym v6. Poprzednia scena v6 pozostaje dostępna.

W widoku gry: `2` – spacer, `1` – podgląd, WASD – ruch, mysz – obrót, E lub lewy przycisk myszy – użycie panelu, Esc – zwolnienie kursora. Przyciski poziomów i Reset view znajdują się w lewym górnym rogu.

Zmiany: podpisy paneli są dopasowane do ekranów, jednostronne i zasłaniane przez geometrię; oświetlenie otoczenia delikatnie rozjaśniono bez dodawania świateł. Przełączanie widoków korzysta z bufora przynależności obiektów. Po dodaniu, usunięciu lub zmianie kategorii modułu w czasie działania gry kod wywołujący powinien użyć `ShipExplorerV5.InvalidateSceneCache()` przed następną zmianą widoku. Zmiana `master` jest wykrywana automatycznie.

Scenę można odtworzyć z v6 przez `Tools/C01 Ship v6.1/Build polished scene`. Wykonuj to na zapisanym projekcie: polecenie otwiera scenę v6. Zmiany w hierarchii i modelach pozostają edytowalne.

Znane ograniczenia: kanały wentylacyjne kończą się kratkami; nie wszystkie podesty mają komplet barierek. Nie wykonano pełnego ręcznego przejścia statku ani pomiaru FPS w samodzielnym buildzie. Sama poprawa czasu przełączania widoków nie jest pomiarem FPS.
