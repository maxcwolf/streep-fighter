using Godot;

namespace StreepFighter;

/// <summary>
/// "Dancing Queen" — spin attack hitting twice at 30% and 60% of 0.6s.
/// </summary>
public partial class DonnaSheridan : Fighter
{
    private bool _hit1;
    private bool _hit2;

    public override void _Ready()
    {
        base._Ready();
        SpecialDuration = 0.6f;
    }

    protected override void HandleSpecialState(float dt)
    {
        _stateTimer += dt;
        float progress = _stateTimer / SpecialDuration;

        // Hit 1 at 30%
        if (progress >= 0.3f && !_hit1)
        {
            _hit1 = true;
            TrySpinHit();
        }

        // Hit 2 at 60%
        if (progress >= 0.6f && !_hit2)
        {
            _hit2 = true;
            TrySpinHit();
        }

        var vel = Velocity;
        vel.X = 0;
        Velocity = vel;

        if (_stateTimer >= SpecialDuration)
        {
            _hit1 = false;
            _hit2 = false;
            ChangeState(FighterState.Idle);
        }
    }

    private void TrySpinHit()
    {
        if (Opponent != null)
        {
            float dist = Mathf.Abs(Position.X - Opponent.Position.X);
            if (dist < 85)
                Opponent.TakeDamage(Stats.SpecialDmg / 2, this);
        }
    }
}
