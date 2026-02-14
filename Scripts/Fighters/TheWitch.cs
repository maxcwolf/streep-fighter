using Godot;

namespace StreepFighter;

/// <summary>
/// "Curse of the Woods" — throws a curse projectile.
/// </summary>
public partial class TheWitch : Fighter
{
    private readonly PackedScene _curseScene = GD.Load<PackedScene>("res://Scenes/Fighters/CurseProjectile.tscn");

    public override void _Ready()
    {
        base._Ready();
        SpecialDuration = 0.5f;
    }

    protected override void HandleSpecialState(float dt)
    {
        _stateTimer += dt;
        float progress = _stateTimer / SpecialDuration;

        // Spawn curse at 50%
        if (progress >= 0.5f && !SpecialActive)
        {
            SpecialActive = true;
            SpawnCurse();
        }

        var vel = Velocity;
        vel.X = 0;
        Velocity = vel;

        if (_stateTimer >= SpecialDuration)
            ChangeState(FighterState.Idle);
    }

    private void SpawnCurse()
    {
        var curse = _curseScene.Instantiate<Projectile>();
        curse.Damage = Stats.SpecialDmg;
        curse.Direction = FacingRight ? 1 : -1;
        curse.OwnerFighter = this;

        curse.SetPlayerIndex(PlayerIndex);

        float xOffset = FacingRight ? 50 : -50;
        curse.Position = new Vector2(Position.X + xOffset, Position.Y - 30);
        GetParent().AddChild(curse);
    }
}
