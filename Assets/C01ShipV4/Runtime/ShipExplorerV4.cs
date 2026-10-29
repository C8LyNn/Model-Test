using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace C01.Ship.V4
{
    public class ShipExplorerV4 : MonoBehaviour
    {
        public Camera view;
        public CharacterController player;
        public GameObject master;
        public ShipGateV4[] gates = new ShipGateV4[0];
        public ShipLiftV4[] lifts = new ShipLiftV4[0];
        public ShipButtonV4[] buttons = new ShipButtonV4[0];
        public bool walking;
        public int selectedDeck = 1;
        public float walkSpeed = 5, overviewSpeed = 20;
        bool roofs, labels = true;
        int lastDeck = 1;
        float pitch, verticalSpeed;
        [SerializeField, HideInInspector] bool overviewProjectionSaved, overviewOrthographic;
        [SerializeField, HideInInspector] float overviewSize, overviewFov;
        ShipZoneV4[] zones = new ShipZoneV4[0];
        Renderer[] renderers = new Renderer[0];

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
            if (master == null) return;
            zones = master.GetComponentsInChildren<ShipZoneV4>(true);
            renderers = master.GetComponentsInChildren<Renderer>(true);
        }

        public void SetWalking(bool value)
        {
            CacheScene();
            if (value && view != null && (!walking || !overviewProjectionSaved)) SaveOverviewProjection();
            walking = value;
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
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
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
            if (renderers.Length > 0)
            {
                bounds = renderers[0].bounds;
                foreach (var renderer in renderers) bounds.Encapsulate(renderer.bounds);
            }
            float floor = selectedDeck < 0 ? Floor(1) : Floor(selectedDeck);
            var target = new Vector3(bounds.center.x, floor + 1.5f, bounds.center.z);
            float span = Mathf.Max(bounds.size.x, bounds.size.z, 30);
            view.transform.position = target + new Vector3(span * .08f, span * .82f, -span * .64f);
            view.transform.rotation = Quaternion.LookRotation(target - view.transform.position, Vector3.up);
            view.nearClipPlane = .05f;
            view.farClipPlane = Mathf.Max(500, span * 5);
        }

        void RefreshVisibility()
        {
            if (master == null) return;
            if (renderers.Length == 0) CacheScene();
            float floor = Floor(selectedDeck);
            foreach (var renderer in renderers)
            {
                if (renderer == null) continue;
                // Floor labels are enabled explicitly for editor plan captures only.
                // Runtime labels use OnGUI and follow the L toggle.
                if (renderer.GetComponentInParent<ShipZoneV4>() != null)
                {
                    renderer.enabled = false;
                    continue;
                }
                bool visible = true;
                var marker = renderer.GetComponentInParent<ShipInstanceV4>();
                if (!walking && marker != null)
                {
                    string category = (marker.category ?? "").ToLowerInvariant();
                    bool ceiling = category.Contains("roof") || category.Contains("ceiling");
                    bool shell = category.Contains("hull") || category.Contains("shell");
                    bool upperSlab = category.Contains("floor") && selectedDeck >= 0 && renderer.bounds.min.y > floor + .25f;
                    visible = (selectedDeck < 0 || marker.deck < 0 || marker.deck <= selectedDeck) &&
                        (!ceiling || roofs) && !shell && !upperSlab;
                }
                renderer.enabled = visible;
            }
        }

        public bool TryPressRay(Ray ray, float maxDistance = 3.5f)
        {
            if (maxDistance <= 0 || !Physics.Raycast(ray, out var hit, maxDistance,
                Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)) return false;
            var button = hit.collider.GetComponentInParent<ShipButtonV4>();
            if (button == null || !button.isActiveAndEnabled) return false;
            button.Press();
            return true;
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
            }
            if (mouse != null && mouse.leftButton.wasPressedThisFrame)
            {
                // GUI controls occupy this area; they are not world button clicks.
                var screen = mouse.position.ReadValue();
                if (!(screen.x < 460 && screen.y > Screen.height - 94))
                    TryPressRay(walking ? view.ViewportPointToRay(new Vector3(.5f, .5f)) : view.ScreenPointToRay(screen));
            }
            // Device availability gates input only. Gravity must still run in batch mode
            // and when a keyboard is disconnected during a walking session.
            var axes = keyboard == null ? Vector2.zero : new Vector2(
                (keyboard.dKey.isPressed ? 1 : 0) - (keyboard.aKey.isPressed ? 1 : 0),
                (keyboard.wKey.isPressed ? 1 : 0) - (keyboard.sKey.isPressed ? 1 : 0));
            axes = Vector2.ClampMagnitude(axes, 1);
            if (mouse != null && mouse.rightButton.isPressed)
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
                if (player.isGrounded && verticalSpeed < 0) verticalSpeed = -2;
                verticalSpeed = Mathf.Max(-30, verticalSpeed + Physics.gravity.y * Time.deltaTime);
                var direction = player.transform.right * axes.x + player.transform.forward * axes.y;
                player.Move((direction * walkSpeed + Vector3.up * verticalSpeed) * Time.deltaTime);
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
            GUILayout.BeginArea(new Rect(12, 12, 440, 82), GUI.skin.box);
            GUILayout.Label("C01 · 1 Overview  2 Walk  WASD / RMB  LMB Button  R Roofs  L Labels");
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
