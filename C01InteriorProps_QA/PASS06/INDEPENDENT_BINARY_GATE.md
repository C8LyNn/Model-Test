# C01-02 — PASS06 / niezależny odczyt rzeczywistych binarnych FBX (2026-10-30)

**Zakres:** 36 istniejących P15-01…P19-08. Tylko read-only QA, zero zmian producentów/architektury, zero merge. Artefakty były faktycznie pobrane z *wcześniejszych* udanych workflowów GitHub Actions i otwarte bajtowo przez niezależny parser FBX v7400; to **nie są nowe natywne eksporty PASS06**.

## Wykonane
- **7 archiwów** Actions, wszystkie ZIP CRC poprawne: P17 W01 [12992848775], P17 W02 [12991739268], P18 W01 [12993262623], P18 W02 [12994285353], P19 W01 pierwszy [12992184076], P19 W01 cleanup [12993127556], P19 W02 [12993051362].
- **22/22 prawdziwe binarne FBX** SHA256 policzone na aktualnie odczytanych bajtach. Wszystkie **22/22 FULL SHA równe** zamrożonym SHA niezależnego PASS05. Rzeczywiście odczytano Geometry/Vertices/PolygonVertexIndex, LayerElementUV, LayerElementNormal, LayerElementMaterial oraz węzły Model/Connections.
- 22/22 poprawnych indeksów wierzchołków, zero per-geometry unused vertices, zero boundary/non-manifold >2, zero indexed wrong-edge winding, zero exact coincident indexed vertices within Geometry; UV0 i normals zapisane i mają poprawne tablice. Wykonano test vertex-on-edge (T-junction *candidates*, nie automatyczne FAIL).
- **17/22** nie ma konserwatywnych fan-zero triangulation candidates. P17 7/7 bez n-gons; P18 7/7 indexed topology OK (P18-04…07 mają bezpieczne w statycznym fan-screen n-gons); P19-03/04/06 brak fan-zero.
- **5/22 P19 nadal FAIL_EXPORT_PREFLIGHT:** P19-01=12 fan-zero, P19-02=9, P19-05=1, P19-07=19, P19-08=7. To *ryzyko* niepoprawnej triangulacji zależnej od importera, nie rzeczywisty wynik Unity. P19-01 potwierdzony niepoprawny 6-wierzchołkowy polygon #59 w Geometry `Cube.001` na rzeczywistych współrzędnych. P19-07: 8 lokalnych T-junction candidates, nie weldować bez wizualnego potwierdzenia.
- P17-05 DisplayBezel/LowerDisplayRail; P18-01 crate shell/corners; P18-07 lid/lock: znane prawdziwe kontakty współpłaszczyznowe pozostają do oględzin w Blender/Unity; nie zakładamy, że każdy kontakt jest z-fightingiem.
- C01-16: odczytane bezpośrednio skrypty w obu bieżących gałęziach producenta `ci_pass04_native.py`, line 151, mają już **poprawione** `read_bytes().startswith(b"BLENDER-")`. 4/4 lokalne regresje QA PASS, w tym autentyczny nagłówek archiwalnego .blend i zgodność pełnych 22 hashy.

## Ograniczenia i blokady
- **P15-01…07:** GitHub Contents zwraca wyłącznie 7 pointerów Git LFS, brak w dostępnych Actions artefaktów z nawodnionymi końcowymi FBX. Nie dopisano fałszywych SHA z bajtów. QA binary NOT RUN / final BLOCKED. Zasada: 48 boundaries P15-07 Gauge_Face_0/1 to wyjątek, nie globalny weld.
- **P16-01…07:** nadal bez 7 rzeczywistych natywnych .blend i bez 7 binarnych FBX; istniejące ASCII FBX nie spełniają kontraktu. Binary QA NOT RUN / final BLOCKED.
- **GitHub Actions:** najnowsze repo workflowy (w tym bez Blender) mają job failure przed runnerem; przykładowo run [41099951538](https://github.com/C8LyNn/Model-Test/actions/runs/41099951538), runner_id=0/steps=[]; [41098559165](https://github.com/C8LyNn/Model-Test/actions/runs/41098559165) oba Ubuntu smoke bez kroków. Przyczyna administracyjna nieweryfikowalna dostępem tego połączenia, **nie potwierdzono billing/quota**.
- Tutejsze środowisko wykonawcze nie ma `blender`, `bpy`, `git-lfs` ani Unity. **Blender PASS06 NOT RUN**, **Unity 6 URP NOT RUN**. Historyczne sukcesy Blender PASS03 nie są nową naprawą.
- Brak rzeczywistych źródłowych napraw P19 PASS06; cztery offline FBX-kandydaty PASS05 nie stanowią zatwierdzonych par .blend+FBX.
- 22/22 static-byte re-audit ≠ 22 final approvals. **Final: 5 FAIL, 31 BLOCKED, 0 FULL PASS, 0 Unity PASS.**

## Odbiór / Next
**NEEDS_OWNER_ACTION** — właściciel musi (A) zobaczyć repo Settings → Actions → General/Runners oraz rzeczywistą adnotację błędnego job, sprawdzić osobno Settings → Billing / usage/budgets; nie zwiększać limitów bez zgody; **lub** (B) uruchomić na istniejącym Windows Blender 4.x + Git LFS producentów z PR #15/#29 (natywna korekta) i #12/#28 (eksport siedmiu P16) z `git lfs pull`. P15 po nawodnieniu siedmiu .fbx musi przekazać bajty i SHA do C01-02. C01-10 następnie wykonuje rzeczywiste Unity.

**Maszynowa macierz 36 modeli:** [PASS06/36_MODELS_PASS06.csv](./36_MODELS_PASS06.csv) (liczby V/E/F/T, fan-zero, lokalne T-junction candidates, dokładne pełne SHA, osobne bramki FBX/Blender/Unity). Niezależne wyniki oparte na realnym FBX; żadnego nowego źródłowego .blend/FBX ani prefab nie stworzono. Status #30/#33 OPEN; PR #13 Draft; no merge.
