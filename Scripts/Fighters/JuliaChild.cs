using Godot;

namespace StreepFighter;

/// <summary>
/// "Bon Appétit" — throws a pot projectile.
/// </summary>
public partial class JuliaChild : Fighter
{
	private readonly PackedScene _potScene = GD.Load<PackedScene>("res://Scenes/Fighters/PotProjectile.tscn");

	public override void _Ready()
	{
		base._Ready();
		SpecialDuration = 0.5f;
	}

	protected override void HandleSpecialState(float dt)
	{
		_stateTimer += dt;
		float progress = _stateTimer / SpecialDuration;

		// Spawn pot at 50%
		if (progress >= 0.5f && !SpecialActive)
		{
			SpecialActive = true;
			SpawnPot();
		}

		var vel = Velocity;
		vel.X = 0;
		Velocity = vel;

		if (_stateTimer >= SpecialDuration)
			ChangeState(FighterState.Idle);
	}

	private void SpawnPot()
	{
		var pot = _potScene.Instantiate<Projectile>();
		pot.Damage = Stats.SpecialDmg;
		pot.Direction = FacingRight ? 1 : -1;
		pot.OwnerFighter = this;

		// Set projectile collision: layer 16 (Projectiles), mask opponent hurtbox
		pot.SetPlayerIndex(PlayerIndex);

		float xOffset = FacingRight ? 50 : -50;
		pot.Position = new Vector2(Position.X + xOffset, Position.Y - 30);
		GetParent().AddChild(pot);
	}
}
