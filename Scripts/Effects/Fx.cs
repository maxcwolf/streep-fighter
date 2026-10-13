using Godot;

namespace StreepFighter;

/// <summary>
/// One-shot pixel effect: plays a horizontal strip from Assets/Sprites/FX
/// once, holding each frame for a fixed number of ticks, then frees itself.
/// </summary>
public partial class Fx : Sprite2D
{
    private int _ticksPerFrame = 3;
    private int _age;

    public static Fx Spawn(Node parent, string name, Vector2 position, int frames, int ticksPerFrame = 3,
                           bool flip = false)
    {
        if (parent == null) return null;
        var fx = new Fx
        {
            Texture = GD.Load<Texture2D>($"res://Assets/Sprites/FX/{name}.png"),
            Hframes = frames,
            Position = position.Round(),
            FlipH = flip,
            ZIndex = 20,
            _ticksPerFrame = ticksPerFrame,
        };
        parent.AddChild(fx);
        return fx;
    }

    public override void _PhysicsProcess(double delta)
    {
        // Sparks keep animating through hit-stop - that is when you look at them.
        _age++;
        int frame = _age / _ticksPerFrame;
        if (frame >= Hframes)
            QueueFree();
        else
            Frame = frame;
    }
}
