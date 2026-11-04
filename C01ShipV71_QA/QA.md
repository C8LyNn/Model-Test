# QA — mostek v7.1

Windy pasażerskie znajdują się symetrycznie po bokach mostka. Szyby, bramy, przyciski, kabiny i trzy podesty przesunięto razem; podłogi oraz galeria zostały dostosowane do nowego układu. Dodano trzy istniejące modele pulpitów i dwa modele foteli, zachowując pozostałe stanowiska.

- `source_audit.json`: kontrola 2723 obszarów podłóg i 2234 obszarów sufitów, trzy pozycje bram oraz dostępność stref i podestów na trzech poziomach.
- `collision_positive_control.json`: celowo zdublowana ściana została wykryta przez audyt. Wynik `FAIL` w tym pliku dotyczy umyślnie uszkodzonej próbki.
- `regression.xml`: wyniki testów PlayMode Unity dla nowej sceny, w tym dojścia do obu wind, działania przycisków i przewozu postaci oraz innych urządzeń i trasy pościgu.
- `blender_reopened.json`: kontrola ponownie otwartego edytowalnego montażu Blender 5.2.3 LTS.
- `Screenshots`: rzeczywiste zrzuty Unity przed i po zmianie.

Modele nowych stanowisk wykorzystują już istniejące prefaby. Nowego eksportu FBX nie wykonywano, ponieważ same modele nie zostały zmienione. Pełna ręczna rozgrywka i osobny build Windows: NOT RUN.
