# C01 v4.0 — raport QA, 29.10.2026

## Wynik

**PASS dostępnych testów.** Zbudowano rzeczywistą scenę i prefab w projekcie `Model Test`, Unity **6000.3.14f1 / URP 17.3.0**. Brak otwartych, potwierdzonych błędów geometrii lub sterowania w sprawdzonym zakresie. To wersja konstrukcyjna z prostymi, edytowalnymi modelami; nie zwiększano szczegółowości kosztem modularności.

Jednostki zgodnie z doprecyzowaniem użytkownika: kratka 3 m, kajuty 9×9 m, łazienki 3×6 m, wysokości kajut/korytarzy 6 m i sektorów 12 m, rufa 12 m. Trzy pokłady, 24 kajuty, 96 łóżek kajutowych, 192 szafki, 24 łazienki, 104 bramy i dwie windy. Trening bez łóżek; medyczny ma dwa łóżka badawcze. Dolny pokład zawiera wymagane zaplecze i edytowalny statek ewakuacyjny.

## Dowody

| Sprawdzenie | Rzeczywisty wynik | Pliki |
|---|---|---|
| Python: wymiary, zawartość, topologia, sockety, mutacje uszkadzające modele | 8/8 PASS, również z docelowego `C01SourceV4` | `QA/python_v4.log`, `QA/packaged_python_v4.log` |
| Niezależna kontrola powierzchni względem uzgodnionego planu | 2250 obszarów, 0 szczelin, brakujące pole 0 m² | `QA/layout_v4.json` |
| Pełna geometria źródłowa razem z detalami | 17 218 brył, 0 przenikań; bramy 0/25/50/75/100% | `QA/geometry_v4_0.json`, `geometry_v4_1.json`, `gate_intermediate_poses.json` |
| Natywne modele i zapisane instancje Unity | 4304 elementy, 17 218 części/colliderów, 0 przenikań | `C01ShipV4_QA/unity_v4_qa.json` |
| Powierzchnie i wysokości w rzeczywistej fizyce Unity | 13 507 promieni pokrycia, 98 kontroli prześwitu, PASS | ten sam raport |
| Nawigacja Unity | 98/98 stref; cztery jawne połączenia TRANSPORT wind | ten sam raport, trasy z punktami |
| Unity EditMode | 8 PASS, 0 FAIL, 0 SKIP | `C01ShipV4_QA/editmode.xml` |
| Unity PlayMode | 7 PASS, 0 FAIL, 0 SKIP | `C01ShipV4_QA/playmode.xml` |
| Blender 5.2.2 LTS | rzeczywiste .blend, GLB, 181 FBX i 181 OBJ; 181/181 ponownych importów FBX PASS | `QA/blender_v4.json`, `QA/blender_models_v4.json`, `Source` |
| Import FBX do Unity | 181/181, właściwe części, wymiary i orientacja | `C01ShipV4_QA/unity_v4_qa.json` |
| Kontrola wizualna | 17 rzeczywistych renderów Unity i 4 Blendera, obejrzane | `C01ShipV4_QA/Screenshots`, `QA/Blender` |

PlayMode testuje fizyczny CharacterController: zamknięta brama blokuje, kliknięty panel otwiera i umożliwia przejście; słupek i inne elementy nie poruszają się z panelami. Śluzy utrzymują wzajemną blokadę. Obie windy przewożą gracza ciągle pomiędzy wszystkimi pokładami, także z włączoną grawitacją spaceru. Odrębnie sprawdzono odwołanie wezwania, reset, obcego gracza obok szybu, blokady bram przystankowych i przełączanie podglądu/spaceru.

Negatywne testy wykrywają usuniętą podłogę, sufit, łóżko lub przycisk, niezgodny collider oraz pustą/skróconą geometrię mimo zachowania identyfikatora. Niezależny przegląd dodatkowo uszkodził powierzchnie dziobu, zewnętrznego pomostu i dachu pionu; każda mutacja została wykryta. Test błędnego audytu uruchamia również prawdziwą nawigację i potwierdza bajtową niezmienność zapisanego kontrolnego NavMesh.

## Przyczyny i naprawy

- Wysokie sektory przecinałyby posadzki górnego pokładu przy niezależnym składaniu każdego piętra. Wspólny generator scala przedziały ścian w 3D, wydziela pojedyncze węzły i wycina rzeczywiste powierzchnie płyt przy ścianach oraz szybach. Spód wspólnej płyty jest sufitem dolnego pomieszczenia.
- Obwiednia okładziny kończyła się 2 cm przed granicą przyjętą podczas wycinania posadzki. Rozszerzono rzeczywiste okładziny do ich formalnego obrysu. Domknięto również dwa małe naroża stopnia dachu mostka. Nie maskowano błędów przesunięciami.
- Pierwsze uruchomienie Unity ujawniło niezapisane nadpisanie odwołań wind do gracza. Generator zapisuje je jawnie jako nadpisania instancji prefabu.
- Audyt FBX kasował transformację osi nadaną przez importer. Weryfikacja zachowuje tę transformację i sprawdza wynik w przestrzeni Unity. Nie zmieniono prawidłowych modeli, aby dopasować je do błędnego testu.
- Test przejścia używał lewego socketa montażowego zamiast środka światła bramy. Przejście i ujęcie kamery wyznaczane są teraz z szerokości oraz obrotu modułu.
- Brak klawiatury zatrzymywał całą aktualizację spaceru, w tym grawitację. Teraz brak urządzenia zeruje wyłącznie wejście ruchu. Test przejazdu z aktywną grawitacją pozostaje rzeczywistym testem tej naprawy.

Pierwszy nieudany przebieg zachowano w `QA/Unity_initial`; końcowe wyniki to XML/JSON oraz ostatni wpis DONE PASS w `C01ShipV4_QA/progress.txt`. Uwagi niezależnych przeglądów i ich rozwiązania są w `docs/*review.md`.

## Granice weryfikacji

- **NOT RUN:** samodzielny build odtwarzacza Windows i import wyeksportowanego `.unitypackage` do drugiego, pustego projektu. Kompilacja, import modeli, fizyka i działanie sceny zostały uruchomione w wskazanym projekcie Unity.
- **NOT RUN:** ręczna sesja WASD/mysz. Sterowanie testowano automatycznie na rzeczywistych komponentach, przez promienie kliknięć i ruch fizycznej postaci.
- Statek ewakuacyjny jest modelem i ma wolną trasę przez szerokie bramy do zewnętrznego pomostu; pilotowanie nie jest częścią tej wersji.
- Cztery połączenia TRANSPORT są jawną abstrakcją nawigacji pomiędzy poziomami. Nie przedstawiamy ich jako ciągłej powierzchni do chodzenia ani dowodu działania wind; temu służą osobne testy przejazdów.
- Przekroje i wybór pokładu zmieniają widoczność rendererów. Collidery i geometria pozostają w scenie. W rzucie górnego pokładu przez otwartą przestrzeń widać niższe posadzki wysokich sektorów.

Poprzednie wersje zachowano. Z 1526 kontrolowanych wcześniejszych plików 1525 ma dokładnie pierwotne sumy SHA-256; jedyną zamierzoną różnicą jest dodanie sceny v4 do listy scen buildu. Cofnięto zmianę runInBackground Test Runnera oraz automatyczną migrację nieużywanego profilu Mobile URP, po sprawdzeniu zgodności z pierwotnymi bajtami. Integralność paczki ZIP potwierdza raport `.validation.json` i manifest SHA-256 każdego pliku w archiwum; integralność dawnej zawartości projektu dokumentuje `QA/host_preservation_v4.json`.
