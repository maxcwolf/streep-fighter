using Godot;

namespace StreepFighter;

/// <summary>
/// "That's All" — dash-slap combo. Miranda dashes forward and hits.
/// </summary>
public partial class MirandaPriestly : Fighter
{
    private const float DashSpeed = 600f;
    private bool _dashHit;

    public override void _Ready()
    {
        base._Ready();
        SpecialDuration = 0.45f;
    }

    protected override void HandleSpecialState(float dt)
    {
        _stateTimer += dt;
        float progress = _stateTimer / SpecialDuration;

        // Dash forward for first 60%
        if (progress < 0.6f)
        {
            float dir = FacingRight ? 1 : -1;
            var vel = Velocity;
            vel.X = dir * DashSpeed;
            Velocity = vel;
        }
        else
        {
            var vel = Velocity;
            vel.X = 0;
            Velocity = vel;
        }

        // Hit at 50-70%
        if (progress >= 0.5f && progress < 0.7f && !_dashHit)
        {
            _dashHit = true;
            if (Opponent != null)
            {
                float dist = Mathf.Abs(Position.X - Opponent.Position.X);
                if (dist < 80)
                    Opponent.TakeDamage(Stats.SpecialDmg, this);
            }
        }

        if (_stateTimer >= SpecialDuration)
        {
            _dashHit = false;
            ChangeState(FighterState.Idle);
        }
    }
}
