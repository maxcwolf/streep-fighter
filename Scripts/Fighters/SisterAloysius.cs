using Godot;

namespace StreepFighter;

/// <summary>
/// "Divine Discipline" — forward lunge with heavy knockback.
/// </summary>
public partial class SisterAloysius : Fighter
{
    private const float LungeSpeed = 400f;
    private const float LungeKnockback = 500f;
    private bool _lungeHit;

    public override void _Ready()
    {
        base._Ready();
        SpecialDuration = 0.5f;
    }

    protected override void HandleSpecialState(float dt)
    {
        _stateTimer += dt;
        float progress = _stateTimer / SpecialDuration;

        // Lunge forward for first 50%
        if (progress < 0.5f)
        {
            float dir = FacingRight ? 1 : -1;
            var vel = Velocity;
            vel.X = dir * LungeSpeed;
            Velocity = vel;
        }
        else
        {
            var vel = Velocity;
            vel.X = 0;
            Velocity = vel;
        }

        // Hit at 50-70%
        if (progress >= 0.5f && progress < 0.7f && !_lungeHit)
        {
            _lungeHit = true;
            if (Opponent != null)
            {
                float dist = Mathf.Abs(Position.X - Opponent.Position.X);
                if (dist < 80)
                {
                    Opponent.TakeDamage(Stats.SpecialDmg, this);
                    // Apply extra knockback
                    float knockDir = Position.X < Opponent.Position.X ? 1 : -1;
                    var oppVel = Opponent.Velocity;
                    oppVel.X = knockDir * LungeKnockback;
                    Opponent.Velocity = oppVel;
                }
            }
        }

        if (_stateTimer >= SpecialDuration)
        {
            _lungeHit = false;
            ChangeState(FighterState.Idle);
        }
    }
}
