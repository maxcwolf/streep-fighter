using Godot;

namespace StreepFighter;

/// <summary>
/// "Iron Fist" — armored power punch. Cannot be interrupted during windup.
/// </summary>
public partial class MargaretThatcher : Fighter
{
    private bool _armorActive;
    private bool _specialHit;

    public override void _Ready()
    {
        base._Ready();
        SpecialDuration = 0.7f;
    }

    protected override void HandleSpecialState(float dt)
    {
        _stateTimer += dt;
        float progress = _stateTimer / SpecialDuration;

        _armorActive = progress < 0.8f;

        // Step forward slowly
        if (progress < 0.6f)
        {
            float dir = FacingRight ? 1 : -1;
            var vel = Velocity;
            vel.X = dir * 120;
            Velocity = vel;
        }
        else
        {
            var vel = Velocity;
            vel.X = 0;
            Velocity = vel;
        }

        // Hit at 60-80%
        if (progress >= 0.6f && progress < 0.8f && !_specialHit)
        {
            _specialHit = true;
            if (Opponent != null)
            {
                float dist = Mathf.Abs(Position.X - Opponent.Position.X);
                if (dist < 90)
                    Opponent.TakeDamage(Stats.SpecialDmg, this);
            }
        }

        if (_stateTimer >= SpecialDuration)
        {
            _armorActive = false;
            _specialHit = false;
            ChangeState(FighterState.Idle);
        }
    }

    public override void TakeDamage(int amount, Fighter attacker)
    {
        if (_armorActive)
        {
            // Take half damage, no stun/knockback
            int reduced = amount / 2;
            CurrentHealth = Mathf.Max(0, CurrentHealth - reduced);
            EmitSignal(SignalName.HealthChanged, CurrentHealth, Stats.MaxHealth);
            if (CurrentHealth <= 0)
            {
                ChangeState(FighterState.KO);
                EmitSignal(SignalName.Died);
            }
            return;
        }
        base.TakeDamage(amount, attacker);
    }
}
