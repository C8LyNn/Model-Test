# Unified two-level sectors implementation plan

**Goal:** Make the six sectors single editable spaces shared by decks 1 and 2, while preserving the playable chase galleries.

**Architecture:** Match each upper metadata zone to the lower sector by identical horizontal bounds, not its historical name. Keep the lower six-metre zone as the sole owner; migrate zone references and nest its individually editable prefab instances under that zone. Keep per-module deck metadata so cutaways still work. Update zone-label visibility to distinguish labels from modular renderers and show a spanning zone on both levels.

**Verification:** Check one owner per sector and both-deck child hierarchy, unchanged transforms and gate references; exercise overview visibility, gate interactions and the complete pursuit path in Unity 6000.3.14f1. Retain v7.4.
