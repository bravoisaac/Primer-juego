using System.Collections.Generic;
using UnityEngine;

namespace TenFe
{
    // IMGUI resources belong to the HUD and are created once, never per repaint.
    internal sealed class HudTheme
    {
        internal static readonly Color Gold = new Color(.87f, .72f, .45f);
        internal static readonly Color Border = new Color(.36f, .32f, .25f, .85f);
        internal static readonly Color Health = new Color(.72f, .25f, .23f);
        internal static readonly Color Energy = new Color(.40f, .68f, .55f);
        static readonly Color Ink = new Color(.035f, .045f, .055f, .92f);
        static readonly Color Paper = new Color(.94f, .91f, .83f);
        readonly List<Texture2D> textures = new List<Texture2D>();
        readonly Texture2D eclipse, diamond;
        internal readonly GUIStyle Small, SmallGold, SmallRight, Body, Heading, Section, Center, CenterGold, Right, Title, Logo, Number;
        internal readonly GUIStyle Button, PrimaryButton, Slider, Thumb;
        readonly GUIStyle key;

        internal HudTheme()
        {
            Small = Label(13, new Color(.77f, .78f, .75f));
            SmallGold = Label(13, Gold); SmallRight = Label(13, Small.normal.textColor, TextAnchor.MiddleRight);
            Body = Label(16, Paper); Heading = Label(15, Paper); Section = Label(24, Paper);
            Center = Label(18, Paper, TextAnchor.MiddleCenter); CenterGold = Label(16, Gold, TextAnchor.MiddleCenter);
            Right = Label(15, Gold, TextAnchor.MiddleRight);
            Title = Label(44, Gold, TextAnchor.MiddleCenter); Logo = Label(45, Paper);
            Number = Label(30, Gold); key = Label(12, Paper, TextAnchor.MiddleCenter);
            Heading.fontStyle = FontStyle.Bold;
            Button = MakeButton(false); PrimaryButton = MakeButton(true);
            Slider = new GUIStyle(GUI.skin.horizontalSlider) { fixedHeight = 5, margin = new RectOffset(), padding = new RectOffset(), border = new RectOffset() };
            Slider.normal.background = Solid(Border);
            Thumb = new GUIStyle(GUI.skin.horizontalSliderThumb) { fixedWidth = 14, fixedHeight = 18 };
            Thumb.normal.background = Solid(Gold); Thumb.hover.background = Solid(Paper);
            Thumb.active.background = Thumb.hover.background; Thumb.focused.background = Thumb.hover.background;
            eclipse = new Texture2D(64, 64, TextureFormat.RGBA32, false) { name = "HUD eclipse", hideFlags = HideFlags.HideAndDontSave };
            var pixels = new Color[64 * 64];
            for (int y = 0; y < 64; y++)
                for (int x = 0; x < 64; x++)
                {
                    float distance = Vector2.Distance(new Vector2(x, y), new Vector2(31.5f, 31.5f));
                    float ring = Mathf.Clamp01(1.5f - Mathf.Abs(distance - 25));
                    float inner = Mathf.Clamp01(1 - Mathf.Abs(distance - 18)) * .25f;
                    pixels[y * 64 + x] = new Color(Gold.r, Gold.g, Gold.b, Mathf.Max(ring, inner));
                }
            eclipse.SetPixels(pixels); eclipse.Apply(); textures.Add(eclipse);
            diamond = new Texture2D(32, 32, TextureFormat.RGBA32, false) { name = "HUD diamond", hideFlags = HideFlags.HideAndDontSave };
            var diamondPixels = new Color[32 * 32];
            for (int y = 0; y < 32; y++)
                for (int x = 0; x < 32; x++)
                    diamondPixels[y * 32 + x] = new Color(1, 1, 1, Mathf.Clamp01(16 - Mathf.Abs(x - 15.5f) - Mathf.Abs(y - 15.5f)));
            diamond.SetPixels(diamondPixels); diamond.Apply(); textures.Add(diamond);
        }

        GUIStyle Label(int size, Color color, TextAnchor alignment = TextAnchor.MiddleLeft)
        {
            var style = new GUIStyle(GUI.skin.label)
            { fontSize = size, alignment = alignment, wordWrap = true, padding = new RectOffset(), richText = false };
            style.normal.textColor = color;
            return style;
        }

        Texture2D Solid(Color color)
        {
            var texture = new Texture2D(1, 1) { name = "HUD surface", hideFlags = HideFlags.HideAndDontSave };
            texture.SetPixel(0, 0, color); texture.Apply(); textures.Add(texture);
            return texture;
        }

        GUIStyle MakeButton(bool primary)
        {
            var style = new GUIStyle(GUI.skin.button)
            { fontSize = 17, alignment = TextAnchor.MiddleCenter, border = new RectOffset(), padding = new RectOffset(12, 12, 8, 8) };
            style.normal.background = Solid(primary ? new Color(.72f, .58f, .34f) : new Color(.12f, .14f, .15f));
            style.normal.textColor = primary ? new Color(.055f, .065f, .07f) : Paper;
            style.hover.background = Solid(primary ? Gold : new Color(.22f, .24f, .25f));
            style.hover.textColor = style.normal.textColor;
            style.active.background = Solid(new Color(.48f, .39f, .24f)); style.active.textColor = Paper;
            style.focused.background = style.hover.background; style.focused.textColor = style.normal.textColor;
            return style;
        }

        internal void Text(Rect rect, string text, GUIStyle style) => GUI.Label(rect, text, style);
        internal void Box(Rect rect, Color color)
        {
            Color old = GUI.color; GUI.color = color;
            GUI.DrawTexture(rect, Texture2D.whiteTexture); GUI.color = old;
        }
        internal void Outline(Rect r, Color color)
        {
            Box(new Rect(r.x, r.y, r.width, 1), color); Box(new Rect(r.x, r.yMax - 1, r.width, 1), color);
            Box(new Rect(r.x, r.y, 1, r.height), color); Box(new Rect(r.xMax - 1, r.y, 1, r.height), color);
        }
        internal void Panel(Rect rect, bool opaque = false)
        { Box(rect, opaque ? new Color(Ink.r, Ink.g, Ink.b, 1) : Ink); Outline(rect, Border); }
        internal void Key(Rect rect, string value)
        { Box(rect, new Color(.10f, .12f, .14f)); Outline(rect, Border); Text(rect, value, key); }
        internal void Bar(Rect rect, float fraction, Color color, float trail = 0)
        {
            Box(new Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4), Border);
            Box(rect, new Color(.045f, .05f, .055f));
            Box(new Rect(rect.x, rect.y, rect.width * Mathf.Clamp01(trail), rect.height), new Color(.74f, .57f, .37f));
            float filled = rect.width * Mathf.Clamp01(fraction);
            Box(new Rect(rect.x, rect.y, filled, rect.height), color);
            Box(new Rect(rect.x, rect.y, filled, 1), new Color(1, 1, 1, .25f));
        }
        internal void Diamond(float x, float y, float radius, Color color)
        {
            Color old = GUI.color; GUI.color = color;
            GUI.DrawTexture(new Rect(x - radius, y - radius, radius * 2, radius * 2), diamond);
            GUI.color = old;
        }
        internal void Eclipse(Rect rect)
        {
            GUI.DrawTexture(rect, eclipse);
            Diamond(rect.center.x, rect.center.y, rect.width * .07f, Gold);
        }
        internal void Rule(float x, float y, float w)
        {
            Box(new Rect(x, y, w / 2 - 12, 1), Border);
            Diamond(x + w / 2, y, 3, Gold);
            Box(new Rect(x + w / 2 + 12, y, w / 2 - 12, 1), Border);
        }
        internal void Target(float x, float y)
        {
            Box(new Rect(x - 12, y - 12, 7, 2), Paper); Box(new Rect(x - 12, y - 12, 2, 7), Paper);
            Box(new Rect(x + 5, y - 12, 7, 2), Paper); Box(new Rect(x + 10, y - 12, 2, 7), Paper);
            Box(new Rect(x - 12, y + 10, 7, 2), Paper); Box(new Rect(x - 12, y + 5, 2, 7), Paper);
            Box(new Rect(x + 5, y + 10, 7, 2), Paper); Box(new Rect(x + 10, y + 5, 2, 7), Paper);
            Diamond(x, y, 2, Gold);
        }
        internal void Dispose()
        { foreach (var texture in textures) Object.Destroy(texture); textures.Clear(); }
    }
}
