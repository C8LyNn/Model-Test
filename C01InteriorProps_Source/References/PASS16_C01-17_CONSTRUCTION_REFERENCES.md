# C01-17 / DETAIL PASS16 — construction reference register

Reviewed 2026-10-30, official manufacturers. Sources are used to reason about hardware, not to reproduce commercial products or redistribute images/CAD.

1. Schneider Electric HMI GXO — https://product-help.schneider-electric.com/Machine%20Expert/V1.1/en/hmigxo/hmigxo/HMI_GXO_Installation_and_Wiring/HMI_GXO_Installation_and_Wiring-3.htm — installation gasket, rigid panel mounting, retaining fasteners and slots; P17-02 wall backing, P17-01 service panel rationale.
2. ROLEC conTROL enclosures — https://rolec.com/en/products/product-ranges/control — diecast aluminium, powdercoat, separate screw channels, captive screws, and molded gasket; rationale for STEEL fixture/ DARK housing separation.
3. Rockwell Automation PanelView clip 2711P-RTMC — https://www.rockwellautomation.com/en-us/products/details.2711P-RTMC.html — removable metal panel mounting clips; concept for functional P17-01/P17-02 fastening, not copied geometry.
4. APEM Series 3000 joystick official PDF, page 3 — https://www.apem.com/storage/datasheets/files/joystick_serie_3000/media/joystick-serie-3000.pdf — drop-in vs under-panel mounting bezel, screw holes, mechanical shaft boot and clearance; concept for fixed P17-03 mount vs separate animated LeverPivot.

PASS16 decision: clean P17-01 coplanar faults rather than scatter more decorative parts. Two KeyboardGuide fronts moved +1mm Z, Backbone rear moved -1mm Z. No extra geometry or changes to P17-02/P17-03. All 16 PASS15 functional mounts retained.

IP/rights: links + factual observations only; do not bundle vendor photos, PDF page images, design dimensions, CAD or textures. All 3D C01 shapes are original fictional industrial sci-fi.
