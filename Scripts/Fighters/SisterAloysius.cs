using Godot;

namespace StreepFighter;

/// <summary>
/// "Divine Discipline" - raises the ruler to heaven, lunges, and cracks it
/// down hard enough to send the sinner across the nave.
/// </summary>
public partial class SisterAloysius : Fighter
{
    private const int LungeStart = 8, LungeEnd = 18;
    private const float LungeSpeed = 5.0f;

    private static readonly Move Ruler = new()
    {
        Startup = LungeEnd, Active = 5, Box = new Rect2(10, 34, 50, 40),
        Hitstun = 24, Blockstun = 15, Push = 3.4f, Knockdown = true, LaunchX = 3.6f, LaunchY = -4.2f,
        Stop = Juice.StopSpecial, Trauma = Juice.TraumaHeavy, HitSfx = "kick_hit",
    };

    protected override Step[] SpecialSteps { get; } =
    {
        new(SpriteSheet.Sp0, LungeStart), new(SpriteSheet.Sp1, LungeEnd - LungeStart),
        new(SpriteSheet.Sp2, 8), new(SpriteSheet.Sp3, 12)
    };

    protected override int SpecialActiveEnd => Ruler.Startup + Ruler.Active;

    protected override void SpecialTick(int t)
    {
        Velocity.X = t >= LungeStart && t < LungeEnd ? Dir * LungeSpeed : 0;
        if (t >= Ruler.Startup && t < Ruler.Startup + Ruler.Active)
            Strike(Ruler, Stats.SpecialDmg);
    }
}
