# C01 v6.7 — przebudowa wymiarów i trasy pościgu

Cel: jeden moduł = 3 m; zwykłe pomieszczenia wszystkich pokładów mają 3 m wysokości, sześć kratek szerokości sektorów na stronę; mostek i rufa to czteromodułowe atria z częściowymi podestami i windami; pokład 2 prowadzi od mostka do wyjścia przez tor przeszkód. Chód i bieg są szybsze od 2,5/5 m/s.

Architektura: osobny generator v6.7 i prefab/scena Unity, wywiedzione ze wspólnych modułów v6.5. Geometria, gniazda, pokłady, windy i przejścia muszą wynikać z tych samych danych; stare warianty pozostają dostępne. Testy sprawdzają nie tylko wymiary, ale też fizyczną przechodność w Unity i geometrię pełnych assetów.

1. Odtworzyć testem niezgodności wysokości, szerokości i ciągłości; zachować wynik bazowy.
2. Przebudować plan i generator, wymodelować atria/podesty oraz trasę pościgu z przejściami.
3. Zbudować prefab i scenę, dobrać tempo gracza, przetestować wejścia, przejazdy wind i przejście trasy w Unity.
4. Sprawdzić rzut i widoki połączeń, dokumentować ograniczenia; bezpiecznie wgrać nową scenę i przygotować dostawę.
