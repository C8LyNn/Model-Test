# C01-18 — DETAIL PASS 16 / konstrukcyjne referencje i decyzje

Zebrano **5 rzeczywistych, publicznie dostępnych referencji**. Stosujemy mechanikę konstrukcji (principles, not a clone). Żadnych cudzych obrazów ani modeli nie kopiujemy do repo. Użytkowanie: tylko odnośniki i parafrazy faktów; bez twierdzenia o licencji na zdjęcia, rysunki ani CAD.

| Nr | Producent / źródło (link) | Dane konstrukcyjne | Adaptacja do istniejącego modelu |
|----|---------------------------|-------------------|----------------------------------|
| R16-01 | Blickle — *Basic information / definitions*, https://www.blickle.com/guide/basic-information-definitions | Koło: opona, piasta, łożysko; wózek: widełki, oś, mocowanie/płyta. Mechanika osi i łożysk musi pozostawać czytelna. | P18-03: zachowano oddzielne koła, oryginalne piasty i osie; nowe drobne elementy zakotwiczono przy istniejących węzłach ramy, nie przy oponie. |
| R16-02 | Blickle — *Fitting types*, https://www.blickle.com/guide/fitting-types | Montaż płytowy koła wykonywany śrubami/nakrętkami na płaskiej powierzchni. | P18-03: stalowe śruby mocujące istniejące kotwy kołowe; celowo na zewnętrznej stronie nieruchomych płyt, z prześwitem od gumy. |
| R16-03 | ULINE — *Industrial Steel Shelving*, https://www.uline.com/BL_3944/Industrial-Steel-Shelving | Ramy stalowe, tylne/boczne stężenia, mocowania półek i zatrzaski/klipsy. | P18-02: utrzymanie tylnych poprzeczek i usztywnień PASS15; ich połączenia z oryginalnymi słupkami otrzymają małe mocowania w obszarze gusset–post, bez kolejnej podpory udającej obciążenie. |
| R16-04 | Southco — *F6-904 removable hinge*, https://southco.com/en_in_int/f6-904 | Stalowe, ukryte zawiasy z demontowalnymi/zabezpieczanymi sworzniami; wymagają zachowania rozdziału elementów ruchomych. | P18-01: utrzymano dwa odrębne sworznie i cztery kołnierze PASS15; nie łączymy ich z korpusem skrzyni. |
| R16-05 | Southco — *A1 adjustable over-center draw latch*, https://southco.com/en_us_int/a1-99-711 | Zamek dźwigniowy wymaga osobnego punktu zaczepu/keepera mocowanego do drugiej części; metalowe zamknięcie reguluje docisk. | P18-01: dwa proste stalowe zaczepy na ruchomej pokrywie, osobne od frontowych dźwigni; bez kopiowania wymiarów i kształtu konkretnych produktów. |

## Ograniczenia i weryfikacja

- Źródła: strony producentów, pobrane w dniu 2026-10-30. Prawa do treści, zdjęć, rysunków/CAD: **zastrzeżone / brak prawa do redystrybucji** — repo przechowuje wyłącznie adresy URL, własne podsumowania i niezależnie zaprojektowane bryły.
- Industrial sci-fi to **kierunek stylistyczny**; szczegóły muszą mieć rolę retencyjną, podpierającą lub łączącą.
- Rzeczywiste wymiary modeli pozostają **autorskie i dopasowane do siatki C01**, nie przepisane z katalogów.
- Nie utożsamiaj dodatniego AABB z precyzyjnym połączeniem. Przy odbiorze C01-02 wymagany rzeczywisty test trójkątów, normalnych, UV0, łączeń i prześwitów ruchomych części.
- Historyczne natywne .blend i FBX w Git LFS są starsze niż bieżące OBJ. W tej fali **Blender/FBX/Unity status NOT RUN**, dopóki uruchomiony Blender 4.x faktycznie nie zapisze nowych binarnych plików i nie przejdą one reimportu/QA.
