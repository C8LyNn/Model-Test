using System.Collections.Generic;
using C01.Ship.V5;
using UnityEngine;

namespace C01.Ship.V61.Signage
{
    // Add to the v6.1 ship root and serialize the included shader through Configure.
    // Existing controls remain intact; generated labels are transient and reversible.
    [ExecuteAlways]
    [DisallowMultipleComponent]
    public sealed class ButtonSignage : MonoBehaviour
    {
        [SerializeField] private Shader textShader;
        private readonly List<Label> labels = new List<Label>();
        private Material material;
        private Font font;

        private sealed class Label
        {
            public Renderer original;
            public bool originalEnabled;
            public GameObject generated;
            public Renderer renderer;
            public Renderer screen;
            public Vector2 screenSize;
            public bool fitted;
        }

        public static float FitScale(Vector2 textSize, Vector2 screenSize, float fill)
        {
            if (textSize.x <= 0f || textSize.y <= 0f || screenSize.x <= 0f || screenSize.y <= 0f || fill <= 0f)
                return 0f;
            return Mathf.Min(screenSize.x / textSize.x, screenSize.y / textSize.y) * Mathf.Clamp01(fill);
        }

        public void Configure(Shader shader)
        {
            textShader = shader;
            if (isActiveAndEnabled) Rebuild();
        }

        private void OnEnable() { Rebuild(); }
        private void OnDisable() { Clear(); }
        private void OnDestroy() { Clear(); }

        public void Rebuild()
        {
            Clear();
            if (textShader == null || !textShader.isSupported) return;
            font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (font == null || font.material == null) return;
            material = new Material(textShader) { name = "C01 button text (temporary)", hideFlags = HideFlags.HideAndDontSave };
            material.mainTexture = font.material.mainTexture;
            Font.textureRebuilt += OnTextureRebuilt;
            foreach (var button in GetComponentsInChildren<ShipButtonV5>(true))
            {
                var old = button.transform.Find("Button_Label");
                var oldText = old != null ? old.GetComponent<TextMesh>() : null;
                var oldRenderer = old != null ? old.GetComponent<Renderer>() : null;
                if (oldText == null || oldRenderer == null || string.IsNullOrEmpty(oldText.text)) continue;
                ShipSolidV5 screen = null;
                foreach (var part in button.GetComponentsInChildren<ShipSolidV5>(true))
                    if (part.role == "SCREEN") { screen = part; break; }
                var filter = screen != null ? screen.GetComponent<MeshFilter>() : null;
                if (filter == null || filter.sharedMesh == null) continue;
                var bounds = filter.sharedMesh.bounds;
                if (bounds.size.x <= 0f || bounds.size.y <= 0f) continue;
                var go = new GameObject("Button_Label_V61") { hideFlags = HideFlags.HideAndDontSave };
                go.transform.SetParent(screen.transform, false);
                go.transform.localPosition = new Vector3(bounds.center.x, bounds.center.y, bounds.max.z + 0.002f);
                go.transform.localRotation = Quaternion.Euler(0, 180, 0);
                var text = go.AddComponent<TextMesh>();
                text.font = font;
                text.fontSize = 40;
                text.characterSize = 1f;
                text.anchor = TextAnchor.MiddleCenter;
                text.alignment = TextAlignment.Center;
                text.text = oldText.text;
                text.color = oldText.color;
                var renderer = go.GetComponent<Renderer>();
                renderer.sharedMaterial = material;
                renderer.enabled = false;
                labels.Add(new Label { original = oldRenderer, originalEnabled = oldRenderer.enabled, generated = go,
                    renderer = renderer, screen = screen.GetComponent<Renderer>(), screenSize = new Vector2(bounds.size.x, bounds.size.y) });
            }
            FitPendingLabels();
        }

        private void LateUpdate() { Synchronize(); }

        public void Synchronize()
        {
            FitPendingLabels();
            foreach (var label in labels) if (label.fitted && label.renderer != null)
            {
                if (label.original != null && label.original.enabled) label.original.enabled = false;
                bool visible = label.screen != null && label.screen.enabled;
                if (label.renderer.enabled != visible) label.renderer.enabled = visible;
            }
        }

        private void FitPendingLabels()
        {
            foreach (var label in labels)
            {
                if (label.fitted || label.renderer == null) continue;
                var size = label.renderer.localBounds.size;
                float scale = FitScale(new Vector2(size.x, size.y), label.screenSize, 0.85f);
                if (scale <= 0f) continue; // Keep the original until Unity supplies text bounds.
                label.generated.transform.localScale = Vector3.one * scale;
                label.renderer.enabled = label.screen != null && label.screen.enabled;
                if (label.original != null) label.original.enabled = false;
                label.fitted = true;
            }
        }

        private void OnTextureRebuilt(Font changed)
        {
            if (changed == font && material != null && font.material != null)
                material.mainTexture = font.material.mainTexture;
        }

        private void Clear()
        {
            Font.textureRebuilt -= OnTextureRebuilt;
            foreach (var label in labels)
            {
                if (label.original != null) label.original.enabled = label.screen != null ? label.screen.enabled : label.originalEnabled;
                if (label.generated != null) DestroyTemporary(label.generated);
            }
            labels.Clear();
            if (material != null) DestroyTemporary(material);
            material = null;
            font = null;
        }

        private static void DestroyTemporary(Object value)
        {
            if (Application.isPlaying) Destroy(value); else DestroyImmediate(value);
        }
    }
}
