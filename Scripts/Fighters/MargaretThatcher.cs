using Godot;

namespace StreepFighter;

/// <summary>
/// "Iron Fist" - winds the handbag right round and brings it down. She walks
/// through anything thrown at her on the way: hits during the wind-up do half
/// damage and do not make her flinch.
/// </summary>
public partial class MargaretThatcher : Fighter
{
    private const int ArmorEnd = 34;

    private static readonly Move Handbag = new()
    {
        Startup = 22, Active = 6, Box = new Rect2(8, 36, 44, 46),
        Hitstun = 24, Blockstun = 16, Push = 3.0f, Knockdown = true, LaunchX = 2.8f, LaunchY = -4.8f,
        Stop = Juice.StopSpecial, Trauma = Juice.TraumaHeavy, HitSfx = "kick_hit",
    };

    protected override Step[] SpecialSteps { get; } =
    {
        new(SpriteSheet.Sp0, 12), new(SpriteSheet.Sp1, 10), new(SpriteSheet.Sp2, 8), new(SpriteSheet.Sp3, 12)
    };

    protected override int SpecialActiveEnd => Handbag.Startup + Handbag.Active;

    private bool ArmorActive => CurrentState == FighterState.Special && StateTick < ArmorEnd;

    protected override void SpecialTick(int t)
    {
        Velocity.X = t < Handbag.Startup ? Dir * 1.0f : 0;
        if (t >= Handbag.Startup && t < Handbag.Startup + Handbag.Active)
            Strike(Handbag, Stats.SpecialDmg);
    }

    public override bool ReceiveHit(Fighter attacker, int damage, Move move, Vector2 contact)
    {
        if (ArmorActive && CurrentHealth > damage / 2)
        {
            ApplyDamage(damage / 2);
            Fx.Spawn(GetParent(), "blockspark", contact, 3, 3);
            AudioManager.Instance?.PlaySFX("block_hit");
            Juice.HitStop(Juice.StopLight);
            Nudge(attacker != null && attacker.Position.X > Position.X ? -0.8f : 0.8f);
            return true;
        }
        return base.ReceiveHit(attacker, damage, move, contact);
    }
}
