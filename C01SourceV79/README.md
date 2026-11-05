# Prototyp v7.9 — wentylacja (NIEUKOŃCZONY)

Prototyp usuwa 12 kajut i ich łazienki z poziomu 2, zastępując je pomieszczeniami technicznymi. Kajuty i łazienki poziomu 1 pozostają w dotychczasowym stanie. W każdej z 12 nowych przestrzeni znajdują się dwa połączone ze sobą istniejące moduły kanału, razem 24 moduły.

**To nie jest sieć wentylacyjna całego statku.** Audyt wykrywa 12 oddzielnych odcinków, a wyloty do 102 stref wewnętrznych nie zostały wykonane ani sprawdzone. Kontrola `test_shipwide_network_is_physically_connected` celowo nie przechodzi. Same drzwi, przynależność do pokoju lub narysowany graf nie stanowią dowodu fizycznego połączenia kanałów. Nie zaimplementowano symulacji przepływu ani dostępu z każdego pomieszczenia.

Prototyp może zawierać nierozpoznane problemy i nie zastępuje sceny v7.8. Dalsza praca wymaga wytyczenia kanałów oraz szybów pomiędzy piętrami, wykonania otworów i włazów w istniejących modułach, zbadania kolizji i ciągłości oraz rzeczywistego testu dostępu z każdego pomieszczenia i korytarza.

Scena: `Assets/C01ShipV79/Scenes/C01_Ship_Ventilation_PROTOTYPE_v79.unity`. Dane i generator: `build_service_rooms.py`; niezależna kontrola fizycznej łączności: `network_audit.py`; test wymagań: `test_ventilation.py`.
