# C01-03 DETAIL PASS13 — OSTATNI STAN PO NOWYCH COMMITACH PRODUCENTÓW

**Source revisions:** C01-18 PR #18 HEAD `9dc58f654d1799208dda3334b9b9ecf9eae33a76`; C01-17 PR #17 HEAD `cdcc18428d2fb52c2c60826fc8af9a70f51c82f9`; C01-02 niezależne QA PR #13 HEAD `877f1db668047d41fe5c6b5273d04eb81c24666c`. Wszystkie Draft; bez merge.

## Rzeczywiście wykonana korekta źródła i niezależne wyniki

- **P17-02**: poprawiono rzeczywisty `Housing` w glTF, translacja Z `0.04→0.0405 m`, skala Z `1→1.0285714285714285`; jego zewnętrzna granica Z obecnie **0.0585m**, `Keybed` tylna granica 0.0580m. Wcześniejszy dystans **+0.5mm** zamieniony na **-0.5mm** kontrolowanego osadzenia. Niezależny C01-02 potwierdził trójkątowy kontakt. Śruby 9×9×3mm, kontakt 4/4, bez ich ruszania. Aktualny glTF blob `d80a67af140e434b983104aaec0078f9cf5bd66f`, producer-reported SHA256 `a9995704a70776b49f2bd6916a50cf222a4ab40b370a0a9e258b63bdc4429786`. **SOURCE_CONTACT_PASS**, ale natywny Blender/FBX i Unity nadal NOT RUN.
- **P18-01**: rzeczywiście edytowano osiem istniejących blach TrimBacker o 2mm, source OBJ blob `c0f9d6b5131c987e1c484ce4eb83ac2115e1d7f7`, source SHA256 `5749f13e30f8e1d853c4488dde2e030fb7b55a59b14b71bedeef61297c8c3adf`. Nowy niezależny C01-02 nadal znajduje **osiem współpłaszczyznowych par** Trim↔TrimBacker, łączny obszar 0.002496 m² (spadek z 0.003328, ale **FAIL_SOURCE_ZFIGHT_COPLANAR**). Niezależny C01-03 ponownie znajduje wolny **Lower_Rim 10mm** od Crate_Shell. Wymagana kolejna precyzyjna korekta.
- **P18-02**: poprawiono tylko dwie blachy Top_Label_MountingBackplate, source OBJ blob `9a81151c93006cd2a52d0e5541fe1d3c2cbc2011`, SHA256 `55d652a42ab7c22709814938535445a0814d9c9ff81237b59925a9115521ee98`; próbki niezależnego C01-02 mają kontakt PASS dla etykiet i półki, ale **oba** `Back_Support_0.6/1.48` nadal pozostają **30mm od najbliższego słupka** w grafie kontaktów rzeczywistego OBJ. Nie oznaczać całego modelu final PASS.
- **P18-03**: źródło OBJ blob `df5a68c87fd49597c79bbb6f70735f32543489bf`, SHA256 `3996be33105a17163d4c8a753012aca891c1b19b156abf32ddab02d8fbca50e0` bez nowego przemieszczenia części. 4/4 koła i układy mocowań pozytywne w próbkowanym source QA, ale cztery `Cart_Shelf_Lip` nadal **5mm nad półkami**; producent poprawił walidator pionowej osi po imporcie do Blendera (Z zamiast Y), co nie jest wykonaną korektą tych czterech części.

**Suma ostatnia:** źródłowy kontakt P17-02 naprawiony. Nadal **7 rozłączonych części OBJ w trzech P18** oraz **8 par niepożądanego same-facing coplanar overlap P18-01**. C01-02 source topology/pass sampled ≠ ostateczny kontakt wszystkich części. Wersje i dokładne source blob+SHA: [AFTER_NEW_PRODUCER_COMMITS_CONTACT_QA.json](./AFTER_NEW_PRODUCER_COMMITS_CONTACT_QA.json) i [36-model registry](./asset_registry_36.json).

## Gate końcowy

- Zmodyfikowane rzeczywiste źródła P17-02 i P18-01/02: **3 modele** (późne korekty PASS13), **0 nowych ID**.
- Statyczne source-contact: P17-02 PASS na podstawie niezależnego C01-02; P18-01/02/03 FAIL kontakt/koplanary (7 luk i 8 par nakładania).
- C01-19 P19-02/05: offline native-format BLEND/FBX candidates w ZIP producenta, nie w Git LFS i nie wykonany Blender application roundtrip. Nie promować.
- **Nowe natywne .blend zapisane przez aplikację Blender 4.x: 0; nowe FBX wyeksportowane/reimportowane w Blenderze: 0; C01-02 final exact-binary QA: 0/36; Unity 6 URP: NOT RUN; release 36/36 BLOCKED.**
- C01 Actions [run #41119479370](https://github.com/C8LyNn/Model-Test/actions/runs/41119479370) z 0 przydzielonymi krokami. C01-18 zgłasza również późniejszy #41123519054 jako bez runnera. Lokalny executor C01-03 bez Blender/bpy, git-lfs i Unity. Nie zakładać przyczyny.

**NEEDS_OWNER_ACTION:** przywrócić GitHub Actions runnera albo rzeczywiście uruchomić Windows Blender4+Git LFS. Najpierw C01-18 musi poprawić ostatnie 7 wolnych źródłowych części i 8 coplanar overlaps; następnie każdy producent zapisuje aktualne `.blend` przez Blendera, eksportuje nowe binarne `.fbx`, ponownie importuje i dostarcza rzeczywiste wireframe/shaded BEFORE/AFTER i dokładne full binary SHA. C01-02 podpisuje realne FBX, C01-10 testuje prawdziwy import Unity 6. Bez merge i bez przypadkowego welding.
