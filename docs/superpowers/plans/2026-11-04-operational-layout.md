# Ship operational layout implementation plan

**Goal:** Improve ship-wide living and service logic while making the evacuation shuttle's physical exit plausible.

**Architecture:** Keep the existing ship and modular sectors. Exchange furnished support rooms between identically sized areas, so communications is near the bridge, life-support control is above purification, and laundry is alongside clothing repair. Provide the hangar with a six-metre modular side launch aperture and orient the existing shuttle toward it; retain the existing personnel and cargo routes. The aperture is a closable segmented gate, not an automated depressurisation simulation.

**Verification:** Compare previous and new room content and placement; inspect actual shuttle swept geometry against closed and opened gates and other solids, including a deliberate obstruction control. In Unity test gate buttons, physical clearances, route access and regression of existing pursuit, lifts and deck visibility. Keep earlier scenes intact.
