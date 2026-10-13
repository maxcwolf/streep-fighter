using Godot;

namespace StreepFighter;

/// <summary>
/// "Dancing Queen" - a whirling double spin that hits on both sides, twice,
/// and ends on the disco point.
/// </summary>
public partial class DonnaSheridan : Fighter
{
    private const int FirstHit = 3, SecondHit = 15, HitWindow = 6;

    private static readonly Move SpinA = new()
    {
        Box = new Rect2(-30, 40, 64, 40),
        Hitstun = 14, Blockstun = 10, Push = 0.8f,
        Stop = Juice.StopLight, Trauma = Juice.TraumaLight, HitSfx = "punch_hit",
    };
    private static readonly Move SpinB = new()
    {
        Box = new Rect2(-30, 40, 64, 40),
        Hitstun = 20, Blockstun = 12, Push = 2.4f, Knockdown = true, LaunchX = 2.2f, LaunchY = -4.6f,
        Stop = Juice.StopHeavy, Trauma = Juice.TraumaHeavy, HitSfx = "kick_hit",
    };

    protected override Step[] SpecialSteps { get; } =
    {
        new(SpriteSheet.Sp0, 5), new(SpriteSheet.Sp1, 5), new(SpriteSheet.Sp2, 5),
        new(SpriteSheet.Sp1, 5), new(SpriteSheet.Sp0, 5), new(SpriteSheet.Sp3, 12)
    };

    protected override int SpecialActiveEnd => SecondHit + HitWindow;

    protected override void SpecialTick(int t)
    {
        Velocity.X = t < 25 ? Dir * 1.3f : 0;
        if (t == SecondHit) RearmStrike();
        if (t >= FirstHit && t < FirstHit + HitWindow)
            Strike(SpinA, Stats.SpecialDmg / 2);
        else if (t >= SecondHit && t < SecondHit + HitWindow)
            Strike(SpinB, Stats.SpecialDmg / 2);
    }
}
