using Godot;

namespace StreepFighter;

/// <summary>
/// Helpers for building the 384x216 pixel UI in code: bitmap-font labels,
/// textures and flat rectangles placed on whole pixels.
/// </summary>
public static class PixelUI
{
    public const int W = 384;
    public const int H = 216;

    public static readonly Color White = new("fcfcfc");
    public static readonly Color Yellow = new("fcd800");
    public static readonly Color Orange = new("f87800");
    public static readonly Color Red = new("f83800");
    public static readonly Color P1Blue = new("3880f8");
    public static readonly Color P2Red = new("f83828");
    public static readonly Color Ink = new("181028");
    public static readonly Color Grey = new("a8a4c8");
    public static readonly Color Cyan = new("58d8f8");

    /// <summary>Bitmap fonts baked by Tools/art/build.py: "tiny", "pixel", "bold", "big".</summary>
    public static FontFile Font(string name) => GD.Load<FontFile>($"res://Assets/Fonts/{name}.fnt");

    public static Texture2D Tex(string path) => GD.Load<Texture2D>(path);

    public static void Fill(Control c)
    {
        c.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        c.MouseFilter = Control.MouseFilterEnum.Ignore;
    }

    /// <param name="width">
    /// 0 = left-aligned at x. Otherwise the label is a box of that width starting at x,
    /// and the text is aligned inside it.
    /// </param>
    public static Label Text(Node parent, string text, int x, int y, string font = "bold", Color? color = null,
                             HorizontalAlignment align = HorizontalAlignment.Left, int width = 0)
    {
        var f = Font(font);
        var label = new Label
        {
            Text = text,
            LabelSettings = new LabelSettings
            {
                Font = f,
                FontSize = f.FixedSize > 0 ? f.FixedSize : 8,
                FontColor = color ?? White,
            },
            HorizontalAlignment = align,
            Position = new Vector2(x, y),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        parent.AddChild(label);
        if (width > 0)
            label.Size = new Vector2(width, label.Size.Y);
        return label;
    }

    /// <summary>Text centred on x.</summary>
    public static Label Centered(Node parent, string text, int centerX, int y, string font = "bold",
                                 Color? color = null, int width = 240)
        => Text(parent, text, centerX - width / 2, y, font, color, HorizontalAlignment.Center, width);

    public static void Tint(Label label, Color color) => label.LabelSettings.FontColor = color;

    public static TextureRect Image(Node parent, string path, int x, int y)
    {
        var tex = Tex(path);
        var rect = new TextureRect
        {
            Texture = tex,
            Position = new Vector2(x, y),
            Size = tex.GetSize(),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        parent.AddChild(rect);
        return rect;
    }

    public static ColorRect Box(Node parent, int x, int y, int w, int h, Color color)
    {
        var rect = new ColorRect
        {
            Color = color,
            Position = new Vector2(x, y),
            Size = new Vector2(w, h),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        parent.AddChild(rect);
        return rect;
    }

    /// <summary>A hollow rectangle (4 strips) - cursors and picture frames.</summary>
    public static Control Frame(Node parent, int x, int y, int w, int h, Color color, int thickness = 1)
    {
        var frame = new Control { Position = new Vector2(x, y), Size = new Vector2(w, h), MouseFilter = Control.MouseFilterEnum.Ignore };
        parent.AddChild(frame);
        Box(frame, 0, 0, w, thickness, color);
        Box(frame, 0, h - thickness, w, thickness, color);
        Box(frame, 0, 0, thickness, h, color);
        Box(frame, w - thickness, 0, thickness, h, color);
        return frame;
    }
}
