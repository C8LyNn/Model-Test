# C01 statek v6.8

Otwórz `Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity` w Unity 6000.3.14f1. Poprzednie sceny pozostają w projekcie.

Jedna kratka ma 3 m. Sektory na poziomie 1 mają wysokość dwóch kratek (6 m) i są otwarte do góry; schody, drabiny i wentylacja prowadzą na podesty. Pokład 2 zachowuje trasę pościgu, która przechodzi boczną galerią mostka. Na poziomie 0 jest sześć dodatkowych bram od korytarza do stref bocznych i cztery między sąsiednimi strefami. Mostek ma obszar dowodzenia, stanowiska nawigacji, ekrany i galerie; rufa ma stanowiska napędu i ładunku oraz dojścia do wind.

Pokłady mają wysokości -3,4 / 0 / 3,4 m: każdy zwykły przedział ma 3 m prześwitu, a 0,4 m przypada na strop. Bramy wraz z ramami mieszczą się w module 3 × 3 m. Panele dzielą się na pełne moduły i osobne pasy stropowe; pasy dekoracyjne pełnej ściany są dopasowane do jej brzegów.

Sterowanie: WASD, mysz, Shift — bieg, spacja — skok, E lub LPM — przycisk, E — drabina, Esc — kursor, 1/2 — podgląd/spacer, L — nazwy pomieszczeń. Wycelowanie w dostępny przycisk pokazuje podpowiedź.

Źródło montażu: `C01SourceV68/Tools/scene_data_v6.py`, potem `C01SourceV68/design_v68.py`. W Unity użyj **Tools / C01 Ship v6.8 / Build complete** po zapisaniu otwartych scen. `C01SourceV68/Source/C01_Ship_Multideck_v68_base.blend` zawiera edytowalny montaż bazowy, a `C01SourceV68/Models` osobne FBX/OBJ; docelowe animacje i konfiguracja bram/wind są w Unity.
