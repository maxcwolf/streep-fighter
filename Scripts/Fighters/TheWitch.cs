using Godot;

namespace StreepFighter;

/// <summary>
/// "Curse of the Woods" - gathers a hex between her claws and hurls it.
/// </summary>
public partial class TheWitch : Fighter
{
    private const int ReleaseTick = 16;

    protected override Step[] SpecialSteps { get; } =
    {
        new(SpriteSheet.Sp0, 10), new(SpriteSheet.Sp1, 6), new(SpriteSheet.Sp2, 8), new(SpriteSheet.Sp3, 8)
    };

    protected override int SpecialActiveEnd => ReleaseTick + 2;

    protected override void SpecialTick(int t)
    {
        Velocity.X = 0;
        if (t == ReleaseTick)
            Projectile.Spawn(this, "curse", new Vector2(Dir * 30, -56), new Vector2(3.8f, 0), 0f, Stats.SpecialDmg);
    }
}
