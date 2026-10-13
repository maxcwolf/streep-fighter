using Godot;

namespace StreepFighter;

/// <summary>
/// "Bon Appetit" - heaves a stockpot across the room.
/// </summary>
public partial class JuliaChild : Fighter
{
	private const int ReleaseTick = 14;

	protected override Step[] SpecialSteps { get; } =
	{
		new(SpriteSheet.Sp0, 8), new(SpriteSheet.Sp1, 6), new(SpriteSheet.Sp2, 8), new(SpriteSheet.Sp3, 10)
	};

	protected override int SpecialActiveEnd => ReleaseTick + 2;

	protected override void SpecialTick(int t)
	{
		Velocity.X = 0;
		if (t == ReleaseTick)
		{
			// Lobbed from overhead: a shallow arc that drops into the chest.
			Projectile.Spawn(this, "pot", new Vector2(Dir * 22, -84), new Vector2(3.3f, -0.9f), 0.055f,
				Stats.SpecialDmg, spin: true);
		}
	}
}
