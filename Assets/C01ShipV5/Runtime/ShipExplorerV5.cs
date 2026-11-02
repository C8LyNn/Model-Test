using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace C01.Ship.V5
{
    public class ShipExplorerV5 : MonoBehaviour
    {
        public Camera view;
        public CharacterController player;
        public GameObject master;
        public ShipGateV5[] gates = new ShipGateV5[0];
        public ShipLiftV5[] lifts = new ShipLiftV5[0];
        public ShipButtonV5[] buttons = new ShipButtonV5[0];
        public bool walking;
        public int selectedDeck = 1;
        public float walkSpeed = 5, overviewSpeed = 20;
        bool roofs, labels = true, mouseCaptured;
        int lastDeck = 1;
        float pitch, verticalSpeed;
        [SerializeField, HideInInspector] bool overviewProjectionSaved, overviewOrthographic;
        [SerializeField, HideInInspector] float overviewSize, overviewFov;
        ShipZoneV5[] zones = new ShipZoneV5[0];
        Renderer[] renderers = new Renderer[0];
        ShipInstanceV5[] ladders = new ShipInstanceV5[0];
        struct VisibilityRecord
        {
            public Renderer renderer;
            public ShipInstanceV5 marker;
            public bool zoneLabel, ceiling, shell, floor;
        }
        VisibilityRecord[] visibility = new VisibilityRecord[0];
        GameObject cachedMaster;
        Vector3 climbFront;
        float climbBase;
        bool climbing, exitingClimb;
        public bool IsClimbing => climbing;

        void Start()
        {
            CacheScene();
            foreach (var lift in lifts) if (lift != null) lift.player = player;
            SetWalking(walking);
            if (!walking) ResetView();
        }

        void CacheScene()
        {
            if (view == null) view = Camera.main;
            if (master == cachedMaster && master != null && visibility.Length != 0) return;
            if (master == null) { InvalidateSceneCache(); return; }
            zones = master.GetComponentsInChildren<ShipZoneV5>(true);
            renderers = master.GetComponentsInChildren<Renderer>(true);
            ladders = master.GetComponentsInChildren<ShipInstanceV5>(true);
            visibility = new VisibilityRecord[renderers.Length];
            for (int i = 0; i < renderers.Length; i++)
            {
                var r = renderers[i];
                var marker = r.GetComponentInParent<ShipInstanceV5>();
                var category = marker != null ? marker.category ?? "" : "";
                visibility[i] = new VisibilityRecord { renderer = r, marker = marker,
                    zoneLabel = r.GetComponentInParent<ShipZoneV5>() != null,
                    ceiling = category.IndexOf("roof", StringComparison.OrdinalIgnoreCase) >= 0 || category.IndexOf("ceiling", StringComparison.OrdinalIgnoreCase) >= 0,
                    shell = category.IndexOf("hull", StringComparison.OrdinalIgnoreCase) >= 0 || category.IndexOf("shell", StringComparison.OrdinalIgnoreCase) >= 0,
                    floor = category.IndexOf("floor", StringComparison.OrdinalIgnoreCase) >= 0 };
            }
            cachedMaster = master;
        }

        // Call after changing the ship hierarchy or a module's category at runtime.
        public void InvalidateSceneCache()
        {
            cachedMaster = null;
            zones = Array.Empty<ShipZoneV5>();
            renderers = Array.Empty<Renderer>();
            ladders = Array.Empty<ShipInstanceV5>();
            visibility = Array.Empty<VisibilityRecord>();
        }

        public void SetWalking(bool value)
        {
            CacheScene();
            if (value && view != null && (!walking || !overviewProjectionSaved)) SaveOverviewProjection();
            walking = value;
            if (!walking) { climbing = false; exitingClimb = false; }
            verticalSpeed = 0;
            if (view != null)
            {
                if (walking)
                {
                    view.orthographic = false;
                    view.fieldOfView = 65;
                }
                if (walking && player != null)
                {
                    view.transform.SetParent(player.transform, false);
                    view.transform.localPosition = new Vector3(0, player.height - .15f, 0);
                    view.transform.localRotation = Quaternion.identity;
                    pitch = 0;
                }
                else view.transform.SetParent(null, true);
            }
            RefreshVisibility();
            if (!walking) ResetView();
            SetMouseCapture(walking && Application.isPlaying);
        }

        void SetMouseCapture(bool value)
        {
            mouseCaptured = value;
            Cursor.lockState = value ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !value;
        }

        void OnDisable()
        {
            if (Application.isPlaying && mouseCaptured) SetMouseCapture(false);
        }

        public void SetDeck(int deck)
        {
            selectedDeck = Mathf.Clamp(deck, -1, 2);
            if (selectedDeck >= 0) lastDeck = selectedDeck;
            RefreshVisibility();
            if (!walking) ResetView();
        }

        public void ShowAll(bool value) { SetDeck(value ? -1 : lastDeck); }

        float Floor(int deck)
        {
            foreach (var zone in zones) if (zone.deck == deck) return zone.floor;
            return deck == 0 ? -12.4f : deck == 2 ? 6.4f : 0;
        }

        void SaveOverviewProjection()
        {
            overviewOrthographic = view.orthographic;
            overviewSize = view.orthographicSize;
            overviewFov = view.fieldOfView;
            overviewProjectionSaved = true;
        }

        public void ResetView()
        {
            if (view == null) CacheScene();
            if (view == null || walking) return;
            if (!overviewProjectionSaved) SaveOverviewProjection();
            view.orthographic = overviewOrthographic;
            view.orthographicSize = overviewSize;
            view.fieldOfView = overviewFov;
            // Bounds include disabled renderers: changing the cutaway cannot change framing.
            var bounds = new Bounds(new Vector3(25.5f, 0, 22.5f), new Vector3(99, 25, 45));
            bool hasBounds = false;
            foreach (var renderer in renderers) if (renderer != null)
            {
                if (!hasBounds) { bounds = renderer.bounds; hasBounds = true; }
                else bounds.Encapsulate(renderer.bounds);
            }
            float floor = selectedDeck < 0 ? Floor(1) : Floor(selectedDeck);
            var target = new Vector3(bounds.center.x, floor + 1.5f, bounds.center.z);
            float span = Mathf.Max(bounds.size.x, bounds.size.z, 30);
            view.transform.position = target + new Vector3(span * .08f, span * .82f, -span * .64f);
            view.transform.rotation = Quaternion.LookRotation(target - view.transform.position, Vector3.up);
            if (view.orthographic)
            {
                // Camera distance does not change orthographic framing. Project
                // all corners so the enlarged ship fits at any viewport aspect.
                float required = 0;
                float aspect = Mathf.Max(.01f, view.aspect);
                for (int x=0; x<2; x++) for (int y=0; y<2; y++) for (int z=0; z<2; z++)
                {
                    var corner = new Vector3(x==0?bounds.min.x:bounds.max.x,
                        y==0?bounds.min.y:bounds.max.y, z==0?bounds.min.z:bounds.max.z);
                    var delta = corner-target;
                    required = Mathf.Max(required, Mathf.Abs(Vector3.Dot(delta,view.transform.up)),
                        Mathf.Abs(Vector3.Dot(delta,view.transform.right))/aspect);
                }
                view.orthographicSize = Mathf.Max(overviewSize,required*1.08f);
            }
            view.nearClipPlane = .05f;
            view.farClipPlane = Mathf.Max(500, span * 5);
        }

        void RefreshVisibility()
        {
            if (master == null) return;
            if (master != cachedMaster || visibility.Length == 0) CacheScene();
            float floor = Floor(selectedDeck);
            foreach (var record in visibility)
            {
                var renderer = record.renderer;
                if (renderer == null) continue;
                // Floor labels are enabled explicitly for editor plan captures only.
                // Runtime labels use OnGUI and follow the L toggle.
                if (record.zoneLabel)
                {
                    renderer.enabled = false;
                    continue;
                }
                bool visible = true;
                var marker = record.marker;
                if (!walking && marker != null)
                {
                    bool upperSlab = record.floor && selectedDeck >= 0 && renderer.bounds.min.y > floor + .25f;
                    visible = (selectedDeck < 0 || marker.deck < 0 || marker.deck <= selectedDeck) &&
                        (!record.ceiling || roofs) && !record.shell && !upperSlab;
                }
                renderer.enabled = visible;
            }
        }

        public bool TryPressRay(Ray ray, float maxDistance = 3.5f)
        {
            if (maxDistance <= 0 || !Physics.Raycast(ray, out var hit, maxDistance,
                Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)) return false;
            var button = hit.collider.GetComponentInParent<ShipButtonV5>();
            if (button == null || !button.isActiveAndEnabled) return false;
            button.Press();
            return true;
        }

        public bool TryPressScreen(Vector2 screen)
        {
            if (!walking && screen.x < 460 && screen.y > Screen.height - 120) return false;
            return TryPressRay(walking ? view.ViewportPointToRay(new Vector3(.5f, .5f)) : view.ScreenPointToRay(screen));
        }

        public bool TryBeginClimb()
        {
            if (!walking || player == null || !player.enabled) return false;
            if (ladders.Length == 0) CacheScene();
            foreach (var ladder in ladders)
            {
                if (ladder == null || ladder.modelId != "P_Ladder_3m" || !ladder.placementId.EndsWith("_LADDER_0")) continue;
                var p = ladder.transform.position;
                var front = p + new Vector3(.4f, 0, .55f);
                var delta = player.transform.position - front; delta.y = 0;
                if (delta.magnitude > 1.25f || player.transform.position.y < p.y-.1f || player.transform.position.y > p.y+6.3f) continue;
                climbBase = p.y; climbFront = front; climbing = true; exitingClimb = false; verticalSpeed = 0; return true;
            }
            return false;
        }

        public void MoveClimb(float input, float dt)
        {
            if (!climbing || player == null || !player.enabled) return;
            var pos = player.transform.position;
            if (exitingClimb)
            {
                var target = climbFront + new Vector3(0, 0, -.9f);
                var delta = Vector3.ProjectOnPlane(target - pos, Vector3.up);
                player.Move(Vector3.ClampMagnitude(delta, 2f * dt));
                if (delta.magnitude < .04f) { climbing = false; exitingClimb = false; verticalSpeed = 0; }
                return;
            }
            // At the upper landing lift the capsule over the last rung before moving out.
            var horizontal = Vector3.ProjectOnPlane(climbFront - pos, Vector3.up);
            if (pos.y > climbBase + 5.8f && pos.y < climbBase + 6.1f && (input >= 0 || horizontal.magnitude > .04f))
            { player.Move(Vector3.up * Mathf.Min(2f * dt, climbBase + 6.12f - pos.y)); return; }
            if (horizontal.magnitude > .04f) { player.Move(Vector3.ClampMagnitude(horizontal, 2f * dt)); return; }
            if (input > 0 && pos.y >= climbBase + 6.1f) { exitingClimb = true; return; }
            float next = Mathf.Clamp(pos.y + Mathf.Clamp(input,-1,1) * 2f * dt, climbBase + .02f, climbBase + 6.15f);
            var flags = player.Move(Vector3.up * (next - pos.y));
            if (input < 0 && ((flags & CollisionFlags.Below) != 0 || player.transform.position.y <= climbBase + .10f))
            { climbing = false; verticalSpeed = 0; }
        }

        void Update()
        {
            var keyboard = Keyboard.current;
            var mouse = Mouse.current;
            if (view == null) return;
            if (keyboard != null)
            {
                if (keyboard.digit1Key.wasPressedThisFrame) SetWalking(false);
                if (keyboard.digit2Key.wasPressedThisFrame) SetWalking(true);
                if (keyboard.rKey.wasPressedThisFrame) { roofs = !roofs; RefreshVisibility(); }
                if (keyboard.lKey.wasPressedThisFrame) labels = !labels;
                if (keyboard.escapeKey.wasPressedThisFrame && walking) SetMouseCapture(false);
                if (keyboard.eKey.wasPressedThisFrame && walking)
                {
                    if (climbing) climbing = false;
                    else if (!TryBeginClimb()) TryPressRay(view.ViewportPointToRay(new Vector3(.5f, .5f)));
                }
            }
            if (mouse != null && mouse.leftButton.wasPressedThisFrame)
            {
                var screen = mouse.position.ReadValue();
                if (walking && !mouseCaptured) SetMouseCapture(true);
                else TryPressScreen(screen);
            }
            // Device availability gates input only. Gravity must still run in batch mode
            // and when a keyboard is disconnected during a walking session.
            var axes = keyboard == null ? Vector2.zero : new Vector2(
                (keyboard.dKey.isPressed ? 1 : 0) - (keyboard.aKey.isPressed ? 1 : 0),
                (keyboard.wKey.isPressed ? 1 : 0) - (keyboard.sKey.isPressed ? 1 : 0));
            axes = Vector2.ClampMagnitude(axes, 1);
            if (mouse != null && ((walking && mouseCaptured) || (!walking && mouse.rightButton.isPressed)))
            {
                var delta = mouse.delta.ReadValue() * .12f;
                if (walking && player != null)
                {
                    player.transform.Rotate(0, delta.x, 0);
                    pitch = Mathf.Clamp(pitch - delta.y, -85, 85);
                    view.transform.localRotation = Quaternion.Euler(pitch, 0, 0);
                }
                else
                {
                    var euler = view.transform.eulerAngles;
                    view.transform.rotation = Quaternion.Euler(Mathf.Clamp(euler.x - delta.y, 5, 85), euler.y + delta.x, 0);
                }
            }
            if (walking && player != null && player.enabled)
            {
                if (climbing) { MoveClimb(axes.y, Time.deltaTime); return; }
                if (player.isGrounded && verticalSpeed < 0) verticalSpeed = -2;
                if (keyboard != null && keyboard.spaceKey.wasPressedThisFrame && player.isGrounded) verticalSpeed = Mathf.Sqrt(-2f * Physics.gravity.y * 1.1f);
                verticalSpeed = Mathf.Max(-30, verticalSpeed + Physics.gravity.y * Time.deltaTime);
                var direction = player.transform.right * axes.x + player.transform.forward * axes.y;
                float speed = keyboard != null && keyboard.leftShiftKey.isPressed ? walkSpeed * 1.4f : walkSpeed;
                player.Move((direction * speed + Vector3.up * verticalSpeed) * Time.deltaTime);
            }
            else
            {
                var forward = Vector3.ProjectOnPlane(view.transform.forward, Vector3.up).normalized;
                var right = Vector3.ProjectOnPlane(view.transform.right, Vector3.up).normalized;
                view.transform.position += (right * axes.x + forward * axes.y) * overviewSpeed * Time.deltaTime;
                if (mouse != null) view.transform.position += view.transform.forward * mouse.scroll.ReadValue().y * .04f;
            }
        }

        void OnGUI()
        {
            GUILayout.BeginArea(new Rect(12, 12, 440, 108), GUI.skin.box);
            GUILayout.Label("1: podgląd | 2: spacer | WASD: ruch | mysz: obrót");
            GUILayout.Label("Spacja: skok | Shift: bieg | E: drabina/przycisk | LPM: przycisk | Esc: kursor");
            GUILayout.BeginHorizontal();
            for (int deck = 0; deck < 3; deck++)
                if (GUILayout.Button((selectedDeck == deck ? "● " : "") + "Deck " + deck)) SetDeck(deck);
            if (GUILayout.Button("All")) ShowAll(true);
            if (GUILayout.Button("Reset view")) ResetView();
            GUILayout.EndHorizontal();
            GUILayout.EndArea();
            if (walking) GUI.Label(new Rect(Screen.width / 2f - 4, Screen.height / 2f - 10, 20, 20), "+");
            if (!labels || view == null) return;
            foreach (var zone in zones)
            {
                if (zone == null || (!walking && selectedDeck >= 0 && zone.deck != selectedDeck)) continue;
                if (walking && player != null && Mathf.Abs(player.transform.position.y - zone.floor) > 3) continue;
                var point = view.WorldToScreenPoint(new Vector3(zone.transform.position.x,
                    zone.floor + Mathf.Min(zone.height * .5f, 2), zone.transform.position.z));
                if (point.z <= 0) continue;
                GUI.Label(new Rect(point.x - 70, Screen.height - point.y, 160, 22), zone.label ?? zone.zoneId);
            }
        }
    }
}
