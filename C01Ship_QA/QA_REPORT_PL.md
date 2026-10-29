# Raport QA — import C01 do Model Test

Wynik końcowy: **PASS**. Pełny przebieg 2026-10-29 09:12:08–09:13:00 UTC w działającym Unity 6000.3.14f1, DX12, z ustawieniami projektu docelowego.

## Dowody

| Kontrola | Wynik | Plik |
|---|---|---|
| Biblioteka i statek — EditMode | 12 PASS, 0 FAIL, 0 SKIP | model_test_editmode.xml |
| Biblioteka i statek — PlayMode | 4 PASS, 0 FAIL, 0 SKIP | model_test_playmode.xml |
| Statyczna geometria, powierzchnie, drzwi i FBX | PASS, 0 błędów | unity_ship_qa.json |
| Dostępność stref przy otwartych drzwiach | 35/35 | unity_ship_qa.json/routes |
| Weryfikacja wizualna | 12 rzeczywistych renderów, obejrzany przekrój i podgląd Game | Screenshots/ |
| Transfer plików biblioteki i statku | 1265 plików, 0 różnic SHA256 po imporcie i testach | transfer_verification.json |

Scena jest otwarta w edytorze. Dodano ją jako pierwszą do Build Scenes oraz dodano scenę ThreeRooms wymaganą przez bazowy test drzwi. Zachowano SampleScene, nazwę Model Test, URP 17.3.0 i Input System 1.19.0. Wcześniejsze lokalne zmiany użytkownika pozostają poza commitem integracji.

Pełny test PlayMode obejmuje 3 drzwi sceny bazowej, niezależne kąty sąsiadujących drzwi statku, cztery śluzy i fizyczne przejście CharacterController przez korytarz, kajutę oraz wyjście rufowe. Testy EditMode obejmują brakującą framugę, brakujący silnik, niezmienność zapisanego NavMesh przy negatywnym audycie oraz sockety wariantów ścian w czterech rotacjach.

W trakcie integracji poprawiono wywołanie SceneView API i synchronizację jednorazowego żądania testów. Rozszerzony test wykrył brak sceny bazowej na liście Build Scenes; po dodaniu sceny kompletny zestaw przeszedł. Historia prób pozostaje w integration_progress.txt. Raporty unity_negative_* mają celowo FAIL, jako dowód wykrywania braków konstrukcji.

## Ograniczenia

NOT RUN: samodzielny build aplikacji, ręczna sesja sterowania, ponowny eksport Blender w projekcie docelowym, opcjonalny import OBJ/GLB do Unity. Rzeczywiste źródło Blender i eksporty zostały przeniesione z wcześniejszej zweryfikowanej paczki v3.0.

Brak nowego wykrytego błędu blokującego scenę. Zapis NavMesh dotyczy stanu otwartych drzwi; runtime gracza używa colliderów. Symulacja lotu i ciśnienia nie należy do tej sceny testowej.
