using Godot;

namespace StreepFighter;

/// <summary>One sheet frame held for a number of 60Hz ticks.</summary>
public readonly record struct Step(int Frame, int Ticks);

/// <summary>How an attack must be guarded.</summary>
public enum Guard
{
    Mid,   // standing or crouching guard
    Low,   // crouching guard only (sweeps)
    High   // standing guard only (jump-ins)
}

/// <summary>
/// Frame data for one attack, SF2 style: startup / active / recovery are
/// counted in ticks and the hitbox is a rectangle in front of the fighter
/// (x = pixels forward of the feet, y = pixels above the floor).
/// </summary>
public class Move
{
    public Step[] Steps = System.Array.Empty<Step>();
    public int Startup;
    public int Active;
    public Rect2 Box;
    public Guard Guard = Guard.Mid;
    public int Hitstun = 14;
    public int Blockstun = 9;
    public float Push = 1.8f;
    public bool Knockdown;
    public float LaunchX = 2.2f;
    public float LaunchY = -4.2f;
    public int Stop = Juice.StopLight;
    public float Trauma = Juice.TraumaLight;
    public string HitSfx = "punch_hit";

    public int Total
    {
        get
        {
            int t = 0;
            foreach (var s in Steps) t += s.Ticks;
            return t;
        }
    }

    public int FrameAt(int tick)
    {
        foreach (var s in Steps)
        {
            if (tick < s.Ticks) return s.Frame;
            tick -= s.Ticks;
        }
        return Steps.Length > 0 ? Steps[^1].Frame : 0;
    }
}
