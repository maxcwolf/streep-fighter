using Godot;

namespace StreepFighter;

public partial class AiController : Node
{
    [Export] public NodePath FighterPath;

    private Fighter _fighter;
    private float _decisionTimer;
    private const float DecisionInterval = 0.3f;

    // Current AI intent
    private bool _wantLeft, _wantRight, _wantJump, _wantCrouch;
    private bool _wantPunch, _wantKick, _wantBlock, _wantSpecial;

    public override void _Ready()
    {
        SetPhysicsProcess(false);
    }

    public void Setup(Fighter fighter)
    {
        _fighter = fighter;
        _fighter.IsAiControlled = true;
        SetPhysicsProcess(true);
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_fighter == null || _fighter.Opponent == null) return;
        if (_fighter.CurrentState == FighterState.KO) return;

        _decisionTimer -= (float)delta;
        if (_decisionTimer <= 0)
        {
            _decisionTimer = DecisionInterval;
            MakeDecision();
        }

        _fighter.AiInput(_wantLeft, _wantRight, _wantJump, _wantCrouch,
                          _wantPunch, _wantKick, _wantBlock, _wantSpecial);

        // Clear one-shot actions after sending
        _wantPunch = false;
        _wantKick = false;
        _wantSpecial = false;
        _wantJump = false;
    }

    private void MakeDecision()
    {
        ClearIntent();

        Fighter opp = _fighter.Opponent;
        float dist = Mathf.Abs(_fighter.Position.X - opp.Position.X);
        bool oppAttacking = opp.CurrentState is FighterState.Punch or FighterState.Kick or FighterState.Special;

        // Use special if off cooldown and in range
        if (_fighter.GetSpecialCooldownPercent() >= 1.0f && dist < 150)
        {
            _wantSpecial = true;
            return;
        }

        // Far: approach
        if (dist > 200)
        {
            bool oppRight = opp.Position.X > _fighter.Position.X;
            _wantRight = oppRight;
            _wantLeft = !oppRight;

            // Occasionally jump approach
            if (GD.Randf() < 0.15f)
                _wantJump = true;
            return;
        }

        // Medium range: mix attack and approach
        if (dist > 100)
        {
            float roll = GD.Randf();
            if (roll < 0.3f)
            {
                // Approach
                bool oppRight = opp.Position.X > _fighter.Position.X;
                _wantRight = oppRight;
                _wantLeft = !oppRight;
            }
            else if (roll < 0.55f)
                _wantKick = true;
            else if (roll < 0.8f)
                _wantPunch = true;
            else if (oppAttacking)
                _wantBlock = true;
            return;
        }

        // Close range: fight
        float closeRoll = GD.Randf();
        if (oppAttacking && closeRoll < 0.4f)
        {
            _wantBlock = true;
        }
        else if (closeRoll < 0.5f)
            _wantPunch = true;
        else if (closeRoll < 0.75f)
            _wantKick = true;
        else
        {
            // Back off slightly
            bool oppRight = opp.Position.X > _fighter.Position.X;
            _wantLeft = oppRight;
            _wantRight = !oppRight;
        }
    }

    private void ClearIntent()
    {
        _wantLeft = _wantRight = _wantJump = _wantCrouch = false;
        _wantPunch = _wantKick = _wantBlock = _wantSpecial = false;
    }
}
