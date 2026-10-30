# C01-03 — DETAIL PASS14 / źródła rzeczywiście poprawione, natywny eksport oczekuje na runtime

**HQ:** https://github.com/C8LyNn/Model-Test/issues/36  
**Native export blockers:** https://github.com/C8LyNn/Model-Test/issues/33  
**Biblioteka:** Draft PR #27, bez merge. **Źródła** w producentach PR #18/#17/#16/#12/#28; C01-03 nie wprowadza zmian w modelach innych właścicieli.

## Rzeczywiste naprawy wykonane i odczytane w PASS14

| Owner / model | Poprawka rzeczywistych źródłowych wierzchołków | Pełny actual source SHA256 | SOURCE QA | NATIVE BLEND/FBX / Unity |
|---|---|---|---|---|
| C01-18 / P18-01 | Lower_Rim szczelina 10 mm → osadzenie 2 mm; 8 coplanar trim/backer → 0 | `6d1cbedba52d975594c4d1c4c1addcf14f752ee7118a521a3e63c880e8044b06` | PASS geometry/triangles | NOT RUN |
| C01-18 / P18-02 | 2 Back_Support szczeliny 30 mm → osadzenie w słupkach po 5 mm | `dc9434a32b7de2235d80a374cc04778b657e39c8f98d88b288bdad40fbf6af2c` | PASS geometry/triangles | NOT RUN |
| C01-18 / P18-03 | 4 listwy 5 mm nad półkami → osadzenie 2 mm; kolizje opona–słupek 11/11/13/13 → 0/0/0/0, 4/4 koła nadal Y=0, 2 mm luzu korony | `22513002afb38d2d3f4a13ef429a41c9a04928528b3cffef87613d51351c1901` | PASS geometry/triangles | NOT RUN |
| C01-17 / P17-02 | poprawiony już w PASS13 Keybed/Housing, 0.5 mm osadzenie; 4 oryginalne śruby 9×9×3 mm niezmienione | `a9995704a70776b49f2bd6916a50cf222a4ab40b370a0a9e258b63bdc4429786` | independent source PASS | NOT RUN |
| C01-15 / P15-03 | spec 0.1.3, nowy hinge sweep 361 próbek, luz do ucha min 0.729675 mm; płytki osadzone 0.5 mm | `f7001207c0a281b0a500a79a71264491151a32742091de71dfd64d4901a4de8b` | offline source candidate PASS, no native | NOT RUN |
| C01-16 / P16-01..07 | siedem zmienionych oryginalnych OBJ i siedem osobnych add-on OBJ, 57 celowych detali, statyczna topologia PASS 7/7; dodatkowo offline custom FBX candidates | full 7+7 SHA in manifests below | source-only PASS | seven native Blender .blend missing; NOT RUN |
| C01-19 / P19-01/02/05/07/08 | rzeczywiste offline-format binary BLEND/FBX candidates z raportów producentów (nie w Git LFS); P19-07 16 vertex-on-edge candidates: visual HOLD | producer-reported candidate hashes in per-model manifest (NOT independently hydrated) | producer parser QA only | Blender load/export/reimport NOT RUN |

**P18-01/02/03 source snapshot** at producer commit `996b8e8f8deb86e2a59f1468fb8b318a7815cfa7`, source blobs respectively `051ab09222a354f1c64f7c682442529b6f4d54ee`, `349fd2307eca8d2334cb8c8cbeb5f43ff9408d4b`, `e6440810d917df3c978505ce79f084ba1f98086c`. Producer PR #18 HEAD `681fc52d2159ac774abf1f48efd7b89965d1afe8` additionally contains QA+part_spec; no later model byte mutation detected at final source diff check.

## Co rzeczywiście sprawdził C01-03

- 3/3 P18: pełny odczyt oryginalnych 137 grup OBJ, 3228 trójkątów; własny graf AABB kontaktów: brak dawnych siedmiu rozłącznych elementów. Dla P18-01 sprawdzono 8 wskazanych par same-facing coplanar przez rzutowanie i przycinanie rzeczywistych trójkątów: obszar 0. Dla P18-03 policzono rzeczywiste ścisłe przecinanie trójkątów koło–słupek: 4×0; każda opona minimalne Y=0. Dokładne świadectwo: [MECHANICAL_REPAIR_SOURCE_QA.json](./MECHANICAL_REPAIR_SOURCE_QA.json).
- 10/10 aktualnych autorskich OBJ (P18 trzy i P16 siedem): własny kontroler indeksów v/vt/vn, fan triangulation, niezerowe pola, per-object watertight/manifold edges i spójna orientacja: **10 PASS, 0 FAIL**. [ACTUAL_10_OBJ_TOPOLOGY_STATIC_QA.json](./ACTUAL_10_OBJ_TOPOLOGY_STATIC_QA.json).
- 11 aktualnych dokładnie odczytanych OBJ/glTF source SHA256: [ACTUAL_SOURCE_SHA256_11.json](./ACTUAL_SOURCE_SHA256_11.json). Osobno wszystkie 7 P16 add-on OBJ: [P16_DETAIL_7_P15_SPEC_SHA256.json](./P16_DETAIL_7_P15_SPEC_SHA256.json). Źródło P15-03 spec 0.1.3: [P15_03_LATEST_SOURCE_SPEC_0_1_3_SHA256.json](./P15_03_LATEST_SOURCE_SPEC_0_1_3_SHA256.json).
- Niezależny C01-02 przeprowadził źródłowy test tri-mesh [INDEPENDENT_MECHANICAL_REPAIR_QA.json](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS14/INDEPENDENT_MECHANICAL_REPAIR_QA.json). Trzy analityczne źródłowe BEFORE/AFTER SVG są pod `C01InteriorProps_QA/DETAIL_PASS14/Previews/P18-0x_SOURCE_BEFORE_AFTER.svg`; **nie są renderami wykonanymi przez Blendera**.

## Jednoznaczne bramki wydania

**36/36 release BLOCKED**, mimo że źródłowy P18 contact PASS dla trzech modeli jest potwierdzony. **Najnowszy fizyczny zapis przez Blender 4.x .blend: 0, eksport FBX wykonany przez aplikację Blender po naprawach: 0, Blender FBX reimport: NOT RUN, pełny niezależny C01-02 na zatwierdzonych nowych binarnych FBX: 0/36, prawdziwe Unity 6 URP: NOT RUN.**

- Dla P16 i P17 istnieją rzeczywiste binarne FBX kandydaci z własnych generatorów producentów. **Nie są** to eksporty z aplikacji Blender, nie są zatwierdzone. Dla P19 istnieją raportowane binarne `.blend`/FBX kandidaten zapisane offline, poza Git LFS; C01-03 nie potwierdził fizycznych bajtów tych ZIP.
- Repo C01 GitHub Actions: sprawdzony run `41127873426` — zadania zakończyły się z **0 kroków i bez runnera**; kolejne workflow też fail. Nie znamy dokładnej przyczyny. Lokalny dostęp do Windows Blendera/Unity przez dostępne narzędzia nie istnieje; w tym środowisku brak Blender, bpy, git-lfs i Unity.
- **NEEDS_OWNER_ACTION:** uprawniony właściciel sprawdza read-only repo Settings → Actions → General/Runners, komentarze/annotacje, account usage i budżety; odblokowuje faktyczne wykonanie albo używa już istniejącego komputera Windows z Blenderem 4.x i Git LFS. Bez zwiększania płatności/zmian uprawnień przez C01-03. Następnie producenci zapisują wszystkie aktualne źródła przez Blendera, generują nowe binarne FBX, reimport, PNG render BEFORE/AFTER, pełny SHA; C01-02 wykonuje niezależne QA na **dokładnych nowych bajtach** 36 FBX, C01-10 realny Unity prefab/URP; C01-00 decyduje release. **Nie wykonywać merge bez podpisu.**

**Rejestr 36 modeli:** [asset_registry_36.json](./asset_registry_36.json). **Kontrola integralności:** [VALIDATION_RESULT.json](./VALIDATION_RESULT.json). 
