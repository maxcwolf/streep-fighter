using Godot;

namespace StreepFighter;

/// <summary>
/// "That's All" - glides across the floor and delivers a backhand slap.
/// </summary>
public partial class MirandaPriestly : Fighter
{
    private const int DashStart = 6, DashEnd = 18;
    private const float DashSpeed = 6.0f;

    private static readonly Move Slap = new()
    {
        Startup = DashEnd, Active = 5, Box = new Rect2(8, 54, 40, 24),
        Hitstun = 22, Blockstun = 14, Push = 2.6f, Knockdown = true, LaunchX = 2.4f, LaunchY = -4.4f,
        Stop = Juice.StopSpecial, Trauma = Juice.TraumaHeavy, HitSfx = "punch_hit",
    };

    protected override Step[] SpecialSteps { get; } =
    {
        new(SpriteSheet.Sp0, DashStart), new(SpriteSheet.Sp1, DashEnd - DashStart),
        new(SpriteSheet.Sp2, 8), new(SpriteSheet.Sp3, 12)
    };

    protected override int SpecialActiveEnd => Slap.Startup + Slap.Active;

    protected override void SpecialTick(int t)
    {
        Velocity.X = t >= DashStart && t < DashEnd ? Dir * DashSpeed : 0;
        if (t >= Slap.Startup && t < Slap.Startup + Slap.Active)
            Strike(Slap, Stats.SpecialDmg);
    }
}
