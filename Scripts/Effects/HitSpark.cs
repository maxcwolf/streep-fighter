using Godot;

namespace StreepFighter;

/// <summary>
/// A comic-book "POW!" impact burst. A pop-art starburst Polygon2D + ink
/// outline + a big onomatopoeia Label. Pops in with a Back ease, jitters,
/// fades out and frees itself in ~0.35s.
///
/// Spawn via <see cref="Spawn"/>: it adds itself to the stage layer and runs.
/// </summary>
public partial class HitSpark : Node2D
{
    private static readonly string[] Words =
        { "POW!", "BAM!", "SLAP!", "BIFF!", "WHACK!", "ZONK!", "KAPOW!" };

    // Palette (from the art bible).
    private static readonly Color Gold = new(0.96f, 0.79f, 0.18f, 1f);
    private static readonly Color GoldBright = new(1.0f, 0.92f, 0.45f, 1f);
    private static readonly Color Crimson = new(0.80f, 0.10f, 0.13f, 1f);
    private static readonly Color Ink = new(0.09f, 0.07f, 0.12f, 1f);

    private const float Lifetime = 0.35f;

    private Polygon2D _burst;
    private Line2D _burstInk;
    private Label _word;
    private float _time;
    private Vector2 _baseScale = Vector2.One;
    private bool _useCrimson;

    /// <summary>
    /// Convenience spawner. Loads the scene, places it at <paramref name="worldPos"/>
    /// in <paramref name="layer"/> with a high z so it sits above everything.
    /// </summary>
    public static void Spawn(Node layer, Vector2 worldPos, bool heavy = false)
    {
        if (layer == null) return;
        var scene = GD.Load<PackedScene>("res://Scenes/Effects/HitSpark.tscn");
        if (scene == null) return;
        if (scene.Instantiate() is not HitSpark spark) return;
        spark.GlobalPosition = worldPos;
        spark._useCrimson = GD.Randf() < 0.5f;
        spark.Configure(heavy);
        layer.AddChild(spark);
    }

    private void Configure(bool heavy)
    {
        // Bigger pop for heavy hits.
        _baseScale = heavy ? new Vector2(1.35f, 1.35f) : Vector2.One;
    }

    public override void _Ready()
    {
        ZIndex = 200;
        ZAsRelative = false;

        _burst = GetNodeOrNull<Polygon2D>("Burst");
        _burstInk = GetNodeOrNull<Line2D>("Burst/BurstInk");
        _word = GetNodeOrNull<Label>("Word");

        // Random spin so each spark feels hand-drawn.
        Rotation = (float)GD.RandRange(-0.35, 0.35);

        Color fill = _useCrimson ? Crimson : Gold;
        Color textFill = _useCrimson ? GoldBright : Crimson;

        if (_burst != null) _burst.Color = fill;
        if (_word != null)
        {
            _word.Text = Words[GD.RandRange(0, Words.Length - 1)];
            _word.AddThemeColorOverride("font_color", textFill);
            _word.AddThemeColorOverride("font_outline_color", Ink);
        }

        // Start tiny so the Back ease can overshoot outward.
        Scale = _baseScale * 0.05f;
    }

    public override void _Process(double delta)
    {
        _time += (float)delta;
        float t = _time / Lifetime;
        if (t >= 1f)
        {
            QueueFree();
            return;
        }

        // Scale-in with a Back ease for the first ~45%, then settle.
        float scaleProg = Mathf.Min(t / 0.45f, 1f);
        float eased = EaseOutBack(scaleProg);
        Scale = _baseScale * (0.05f + eased * 0.95f);

        // Jitter — a tiny shimmy that reads as energetic comic ink.
        float jitterAmt = (1f - t) * 3.5f;
        Position += new Vector2(
            (float)GD.RandRange(-jitterAmt, jitterAmt),
            (float)GD.RandRange(-jitterAmt, jitterAmt));

        // Fade out over the back half.
        float alpha = t < 0.6f ? 1f : 1f - (t - 0.6f) / 0.4f;
        Modulate = new Color(1f, 1f, 1f, Mathf.Clamp(alpha, 0f, 1f));
    }

    // Standard "ease out back" (slight overshoot past 1 then settle).
    private static float EaseOutBack(float x)
    {
        const float c1 = 1.70158f;
        const float c3 = c1 + 1f;
        float xm = x - 1f;
        return 1f + c3 * xm * xm * xm + c1 * xm * xm;
    }
}
