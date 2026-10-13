using Godot;

namespace StreepFighter;

/// <summary>
/// CPU opponent. Presses the same buttons a player would, re-deciding every
/// few ticks (its "reaction time"). GameManager calls <see cref="Tick"/> once
/// per simulation tick, just before the fighters read their input.
/// </summary>
public class AiController
{
    private readonly Fighter _fighter;
    private readonly bool _hasProjectile;
    private int _wait;
    private bool _airAttackDecided;

    private bool _left, _right, _jump, _crouch, _punch, _kick, _block, _special;

    // Ranges in native pixels (fighters are ~22px wide, a kick reaches ~54).
    private const float FarRange = 104f;
    private const float PokeRange = 56f;

    public AiController(Fighter fighter)
    {
        _fighter = fighter;
        _fighter.IsAiControlled = true;
        _hasProjectile = fighter is JuliaChild or TheWitch;
    }

    public void Tick()
    {
        Fighter opp = _fighter.Opponent;
        if (opp == null || _fighter.Locked || _fighter.IsDown)
        {
            _fighter.ClearAiInput();
            _wait = 0;
            return;
        }

        // Buttons are taps: release them the tick after pressing.
        _punch = _kick = _special = false;

        float dist = Mathf.Abs(_fighter.Position.X - opp.Position.X);

        // Jump-ins: kick on the way down, decided once per jump.
        if (_fighter.CurrentState == FighterState.Jump)
        {
            if (!_airAttackDecided && _fighter.Velocity.Y > -1f && dist < 70f)
            {
                _airAttackDecided = true;
                if (GD.Randf() < 0.75f) _kick = true;
            }
        }
        else
        {
            _airAttackDecided = false;
        }

        if (--_wait <= 0)
        {
            _wait = (int)GD.RandRange(9, 17);
            Decide(opp, dist);
        }

        _fighter.AiInput(_left, _right, _jump, _crouch, _punch, _kick, _block, _special);
        _jump = false;
    }

    private void Decide(Fighter opp, float dist)
    {
        _left = _right = _jump = _crouch = _block = false;
        bool oppRight = opp.Position.X > _fighter.Position.X;
        float roll = GD.Randf();

        // Guard against whatever is coming (low for sweeps).
        if (opp.Threatens(_fighter) && roll < 0.55f)
        {
            _block = true;
            _crouch = opp.CurrentState == FighterState.CrouchKick;
            return;
        }

        // Swat jump-ins out of the air.
        if (!opp.Grounded && dist < 64f && roll < 0.5f)
        {
            _kick = true;
            return;
        }

        // Punish a floored opponent's wake-up by spacing, not by swinging at air.
        if (opp.IsDown)
        {
            if (dist < PokeRange) Walk(!oppRight);
            else if (dist > FarRange) Walk(oppRight);
            return;
        }

        if (_fighter.GetSpecialCooldownPercent() >= 1f)
        {
            if (_hasProjectile ? dist > 84f && roll < 0.6f : dist < 76f && roll < 0.45f)
            {
                _special = true;
                return;
            }
        }

        if (dist > FarRange)
        {
            Walk(oppRight);
            if (roll < 0.10f) _jump = true;
            return;
        }

        if (dist > PokeRange)
        {
            if (roll < 0.45f) Walk(oppRight);
            else if (roll < 0.60f) { Walk(oppRight); _jump = true; }
            else if (roll < 0.75f) _kick = true;
            else if (roll < 0.88f) Walk(!oppRight);
            return;
        }

        // In range: mix highs, lows and a little footsies.
        if (roll < 0.28f) _punch = true;
        else if (roll < 0.50f) _kick = true;
        else if (roll < 0.66f) { _crouch = true; _kick = true; }
        else if (roll < 0.76f) { _crouch = true; _punch = true; }
        else if (roll < 0.86f) _block = true;
        else Walk(!oppRight);
    }

    private void Walk(bool right)
    {
        _right = right;
        _left = !right;
    }
}
