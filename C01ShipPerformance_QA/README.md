# C01 — poprawki wydajności sceny v6.8

Scena i prefab v6.8 nie zostały zastąpione. Zmiana dotyczy współdzielonych skryptów: nieruchome bramy nie wywołują już `Rigidbody.MovePosition` dla wszystkich skrzydeł na każdym kroku fizyki, a wyszukiwanie drabin przy klawiszu E korzysta z listy samych drabin. Blokada bram wind nadal jest sprawdzana co krok. Po zmianach hierarchii lub identyfikatorów drabin w trakcie gry należy wywołać `ShipExplorerV5.InvalidateSceneCache()`.

Pomiary wykonano w edytorze Unity 6000.3.14f1 na RTX 5080, w tej samej scenie i procedurze. Są to pomiary konkretnych operacji, nie pełnej liczby klatek w grze:

* 148 nieruchomych bram, 1184 skrzydła: mediana około 0,502 ms przed i 0,089 ms po na krok testowy. Pętla pomiarowa używa refleksji i zawiera jej stały koszt.
* Wyszukanie drabiny poza ich zasięgiem: mediana około 0,123 ms przed i 0,010 ms po; 12 051 markerów w scenie, z czego 6 to drabiny możliwe do użycia.
* Scena ma około 42 159 rendererów, 41 423 kolidery i 111 świateł. Nadal nie ma wypieczonego occlusion culling; pełne pomiary FPS, GPU i samodzielnego buildu Windows pozostają NOT RUN.

Test windy wykrył wcześniej zależność od kolejności: po innym teście pozostawała załadowana scena statku, której kolidery wpływały na pudełko testowe. Ten sam błąd odtworzono na poprzednim kodzie bram (`cargo_baseline_mixed.xml`); testy windy działają teraz na oddzielnej scenie.

Końcowy zestaw `final_tests.xml`: 10/10 PASS, w tym cztery próby windy towarowej uruchomione po scenie v5, brama po bezczynności i przesunięciu, 10 nowych przejść pokładu 0, windy w rzeczywistej scenie, drabina i wentylacja oraz widoczność oznaczeń. Wcześniejszy szerszy zestaw `integration_tests.xml` miał 29/30 PASS przed naprawą izolacji, w tym 10/10 prób sceny v6.8. Oryginalną nieudaną próbę zachowano jako dowód diagnostyczny.
