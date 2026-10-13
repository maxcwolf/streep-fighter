using Godot;

namespace StreepFighter;

/// <summary>
/// CPU opponent. It presses the same buttons a player would and can only act
/// on what a player could see: where the opponent is, what state they are in,
/// and whether their attack has already whiffed.
///
/// Two layers:
///   - Reactions. When the opponent does something (attacks, jumps, throws a
///     projectile, gets up) the CPU decides once, there and then, whether it
///     will answer - guard, anti-air, punish the recovery, time a wake-up
///     attack - and then does so after its reaction delay.
///   - Neutral. Every "think" interval it picks a plan: walk into its own
///     striking range, poke, sweep, jump in, zone with a projectile, back off.
///
/// The CPU level (1-8, <see cref="Settings.CpuLevel"/>) sets how fast it
/// reacts, how often each reaction succeeds, how aggressive it is and how
/// often it simply does nothing. GameManager calls <see cref="Tick"/> once
/// per simulation tick, just before the fighters read their input.
/// </summary>
public class AiController
{
    private enum Plan { Hold, Approach, Retreat }

    // Own reach, in native pixels (see the frame data in Fighter.cs).
    private const float PunchReach = 47f;
    private const float KickReach = 53f;
    private const float SweepReach = 50f;
    private const float StrikeRange = 62f;   // close enough to step in and hit
    private const float JumpInMin = 76f, JumpInMax = 116f;
    private const float ZoneRange = 90f;     // projectiles are thrown from beyond this

    private readonly Fighter _me;
    private readonly bool _hasProjectile;
    private readonly float _specialReach;
    private readonly int _specialStartup;

    // ---- skill, from the CPU level
    private readonly int _reactTicks;        // delay between seeing and doing
    private readonly int _thinkMin, _thinkMax;
    private readonly float _guard;           // chance to block an attack it sees coming
    private readonly float _antiAir;         // chance to swat a jump-in
    private readonly float _punish;          // chance to hit back after a whiff / time a wake-up attack
    private readonly float _combo;           // chance to follow a landed jump-in with a ground hit
    private readonly float _aggression;      // how readily it attacks when in range
    private readonly float _specialUse;
    private readonly float _hesitate;        // chance a decision is "stand there"

    // ---- what it last saw
    private FighterState _oppState = FighterState.Idle;
    private int _oppProjectiles;

    // ---- pending reactions
    private int _guardIn = -1;               // ticks until the guard comes up (-1 = none planned)
    private bool _guarding, _guardLow;
    private int _guardTicks;
    private bool _antiAirArmed, _punishArmed, _airAttackArmed, _comboArmed;
    private int _meatyIn = -1;               // ticks until the wake-up attack is pressed

    // ---- neutral
    private Plan _plan = Plan.Hold;
    private int _think;
    private int _crouchTicks;

    private bool _left, _right, _jump, _crouch, _punch, _kick, _block, _special;

    /// <param name="level">1-8; defaults to the player's CPU LEVEL setting.</param>
    public AiController(Fighter fighter, int level = 0)
    {
        if (level <= 0) level = Settings.CpuLevel;
        level = Mathf.Clamp(level, Settings.MinCpuLevel, Settings.MaxCpuLevel);
        _me = fighter;
        _me.IsAiControlled = true;
        _hasProjectile = fighter is JuliaChild or TheWitch;
        // How far each signature move reaches (travel + hitbox) and how long before it hits.
        (_specialReach, _specialStartup) = fighter switch
        {
            MirandaPriestly => (104f, 18),
            SisterAloysius => (96f, 18),
            MargaretThatcher => (66f, 22),
            DonnaSheridan => (46f, 3),
            _ => (0f, 16),
        };

        float t = (level - Settings.MinCpuLevel) / (float)(Settings.MaxCpuLevel - Settings.MinCpuLevel);
        _reactTicks = Mathf.RoundToInt(Mathf.Lerp(20f, 4f, t));
        _thinkMin = Mathf.RoundToInt(Mathf.Lerp(44f, 9f, t));
        _thinkMax = Mathf.RoundToInt(Mathf.Lerp(70f, 16f, t));
        _guard = Mathf.Lerp(0.08f, 0.85f, t);
        _antiAir = Mathf.Lerp(0.00f, 0.80f, t);
        _punish = Mathf.Lerp(0.00f, 0.85f, t);
        _combo = Mathf.Lerp(0.00f, 0.80f, t);
        _aggression = Mathf.Lerp(0.28f, 0.90f, t);
        _specialUse = Mathf.Lerp(0.10f, 0.70f, t);
        _hesitate = Mathf.Lerp(0.50f, 0.03f, t);
    }

    public void Tick()
    {
        Fighter opp = _me.Opponent;
        if (opp == null || _me.Locked)
        {
            Reset();
            _me.ClearAiInput();
            return;
        }

        // Attack buttons and jump are taps: let go the tick after pressing.
        _punch = _kick = _special = _jump = false;

        float dx = opp.Position.X - _me.Position.X;
        float dist = Mathf.Abs(dx);
        bool oppRight = dx > 0;

        Perceive(opp, dist, oppRight);
        Act(opp, dist, oppRight);

        _me.AiInput(_left, _right, _jump, _crouch, _punch, _kick, _block, _special);
    }

    private void Reset()
    {
        _guardIn = _meatyIn = -1;
        _guarding = _antiAirArmed = _punishArmed = _airAttackArmed = _comboArmed = false;
        _plan = Plan.Hold;
        _think = 0;
        _crouchTicks = 0;
        _left = _right = _jump = _crouch = _punch = _kick = _block = _special = false;
    }

    // =====================================================================
    //  Seeing: one decision per thing the opponent does
    // =====================================================================
    private void Perceive(Fighter opp, float dist, bool oppRight)
    {
        if (opp.CurrentState != _oppState)
        {
            _oppState = opp.CurrentState;
            switch (_oppState)
            {
                case FighterState.Punch:
                case FighterState.Kick:
                case FighterState.CrouchPunch:
                case FighterState.CrouchKick:
                case FighterState.Special:
                    if (dist < (_oppState == FighterState.Special ? 124f : 74f) && GD.Randf() < _guard)
                        PlanGuard(_oppState == FighterState.CrouchKick);
                    _punishArmed = GD.Randf() < _punish;
                    break;

                case FighterState.Jump:
                    bool towardMe = opp.Velocity.X != 0 && opp.Velocity.X > 0 != oppRight;
                    if (towardMe && dist < 134f)
                    {
                        _antiAirArmed = GD.Randf() < _antiAir;
                        if (!_antiAirArmed && GD.Randf() < _guard)
                            PlanGuard(false, Mathf.Max(_reactTicks, 16)); // jump-ins are blocked standing
                    }
                    break;

                case FighterState.GetUp:
                    // Wake-up attack: GetUp is 14 ticks + 8 of invulnerability, a sweep needs 5 to start.
                    if (dist < 64f && GD.Randf() < _punish)
                        _meatyIn = 17;
                    break;

                case FighterState.Hurt:
                case FighterState.CrouchHurt:
                    if (_me.CurrentState is FighterState.JumpKick or FighterState.JumpPunch)
                        _comboArmed = GD.Randf() < _combo;
                    break;
            }
        }

        // A projectile just left their hands.
        if (opp.LiveProjectiles > _oppProjectiles && GD.Randf() < _guard)
            PlanGuard(false);
        _oppProjectiles = opp.LiveProjectiles;
    }

    private void PlanGuard(bool low, int delay = -1)
    {
        if (_guarding) return;
        _guardIn = delay >= 0 ? delay : _reactTicks;
        _guardLow = low;
    }

    // =====================================================================
    //  Doing
    // =====================================================================
    private void Act(Fighter opp, float dist, bool oppRight)
    {
        _block = false;
        if (_crouchTicks > 0 && --_crouchTicks == 0) _crouch = false;

        // Nothing to press while knocked about.
        if (_me.IsDown || _me.CurrentState is FighterState.Hurt or FighterState.CrouchHurt)
        {
            StopMoving();
            _guarding = false;
            _guardIn = -1;
            return;
        }

        // In the air: the jump-in kick, on the way down.
        if (_me.CurrentState is FighterState.Jump or FighterState.PreJump)
        {
            if (_airAttackArmed && _me.Velocity.Y > 0.4f && dist < 60f)
            {
                _kick = true;
                _airAttackArmed = false;
            }
            return;
        }
        if (_me.IsAttacking || _me.CurrentState == FighterState.Land)
            return;

        // ---- reactions, most urgent first ----
        if (_guardIn >= 0 && --_guardIn < 0)
        {
            _guarding = true;
            _guardTicks = 0;
        }
        if (_guarding)
        {
            _guardTicks++;
            // Still dangerous: a projectile in flight, a swing that has not finished hitting,
            // or someone dropping in from above. A spent attack is an opening, not a threat.
            bool threat = opp.LiveProjectiles > 0
                          || (opp.IsAttacking && dist < 96f && !opp.AttackSpent)
                          || (!opp.Grounded && dist < 80f);
            if (threat || _guardTicks < 8)
            {
                StopMoving();
                _block = true;
                // Read the attack: low for sweeps, standing for anything from the air.
                if (opp.CurrentState == FighterState.CrouchKick) _guardLow = true;
                else if (!opp.Grounded) _guardLow = false;
                _crouch = _guardLow;
                _crouchTicks = _guardLow ? 2 : 0;
                return;
            }
            _guarding = false;
            _think = Mathf.Min(_think, 4); // the block is over: decide what to do with the opening
        }

        // Still in block-stun: nothing will come out yet, so wait rather than waste the press.
        if (!_me.IsFree)
            return;

        // Anti-air: they are coming down on top of us.
        if (_antiAirArmed)
        {
            if (opp.Grounded)
            {
                _antiAirArmed = false;
            }
            else if (opp.Velocity.Y > 0f && dist < 56f && Fighter.GroundY - opp.Position.Y is > 18f and < 76f)
            {
                StopMoving();
                _kick = true;
                _antiAirArmed = false;
                return;
            }
        }

        // Punish: their attack is spent and they are stuck in its recovery.
        if (_punishArmed)
        {
            if (!opp.IsAttacking)
            {
                _punishArmed = false;
            }
            else if (opp.Grounded && opp.AttackSpent)
            {
                int left = opp.AttackTicksLeft;
                bool specialReady = _me.GetSpecialCooldownPercent() >= 1f;
                if (dist <= PunchReach && left >= 5) { Press(ref _punch); return; }
                if (dist <= KickReach && left >= 7) { Press(ref _kick); return; }
                if (!_hasProjectile && specialReady && dist <= _specialReach && left >= _specialStartup + 2)
                {
                    Press(ref _special);
                    return;
                }
            }
        }

        // Combo: the jump-in connected, they are still reeling as we land.
        if (_comboArmed)
        {
            if (opp.CurrentState is FighterState.Hurt or FighterState.CrouchHurt && dist <= SweepReach)
            {
                StopMoving();
                _crouch = true;
                _crouchTicks = 3;
                _kick = true;
                _comboArmed = false;
                _think = 20;
                return;
            }
            _comboArmed = false;
        }

        // Wake-up attack, timed to land as they finish getting up.
        if (_meatyIn >= 0 && --_meatyIn < 0 && dist <= SweepReach
            && opp.CurrentState is FighterState.GetUp or FighterState.Idle)
        {
            StopMoving();
            _crouch = true;
            _crouchTicks = 3;
            _kick = true;
            _think = 22;
            return;
        }

        // ---- neutral ----
        if (--_think <= 0)
        {
            _think = (int)GD.RandRange(_thinkMin, _thinkMax);
            Decide(opp, dist, oppRight);
        }
        Move(dist, oppRight);
    }

    private void Decide(Fighter opp, float dist, bool oppRight)
    {
        _plan = Plan.Hold;
        bool specialReady = _me.GetSpecialCooldownPercent() >= 1f;

        // They are on the floor: take up position just inside sweep range and wait.
        if (opp.IsDown)
        {
            _plan = dist > SweepReach - 4f ? Plan.Approach : dist < 34f ? Plan.Retreat : Plan.Hold;
            _think = Mathf.Min(_think, 10);
            return;
        }

        if (GD.Randf() < _hesitate)
            return;

        // Zoners keep you out.
        if (_hasProjectile && specialReady && dist > ZoneRange && _me.LiveProjectiles == 0
            && GD.Randf() < _specialUse)
        {
            _special = true;
            return;
        }

        if (dist > JumpInMax)
        {
            _plan = Plan.Approach;
            return;
        }

        if (dist > StrikeRange)
        {
            float r = GD.Randf();
            if (!_hasProjectile && specialReady && dist <= _specialReach && r < _specialUse * 0.45f)
            {
                _special = true;
            }
            else if (dist >= JumpInMin && r < 0.08f + _aggression * 0.20f)
            {
                // Jump in: the direction is read on the tick the jump starts.
                Walk(oppRight);
                _jump = true;
                _airAttackArmed = GD.Randf() < 0.45f + _aggression * 0.5f;
                _plan = Plan.Hold;
                _think = 50;
            }
            else
            {
                _plan = r < 0.30f + _aggression * 0.55f ? Plan.Approach : r < 0.92f ? Plan.Hold : Plan.Retreat;
            }
            return;
        }

        // In striking range.
        if (GD.Randf() >= _aggression)
        {
            float r = GD.Randf();
            _plan = r < 0.45f ? Plan.Retreat : Plan.Hold;
            return;
        }

        if (dist > KickReach)
        {
            // A step short: close the last few pixels, then decide again.
            _plan = Plan.Approach;
            _think = Mathf.Min(_think, 6);
            return;
        }

        float pick = GD.Randf();
        if (!_hasProjectile && specialReady && pick < _specialUse * 0.3f)
        {
            _special = true;
        }
        else if (pick < 0.40f || dist > SweepReach)
        {
            _kick = true;                                // the long poke
        }
        else if (pick < 0.62f)
        {
            _crouch = true;                              // sweep: low, knocks down
            _crouchTicks = 3;
            _kick = true;
        }
        else if (pick < 0.86f && dist <= PunchReach)
        {
            _punch = true;                               // the quick one
        }
        else if (dist <= PunchReach)
        {
            _crouch = true;
            _crouchTicks = 3;
            _punch = true;
        }
        else
        {
            _kick = true;
        }
        _think = Mathf.Max(_think, 16);
    }

    /// <summary>Carry out the current plan with the stick.</summary>
    private void Move(float dist, bool oppRight)
    {
        if (_jump) return; // the stick is already set for the jump direction
        switch (_plan)
        {
            case Plan.Approach:
                if (dist <= KickReach - 4f)
                {
                    StopMoving();
                    _plan = Plan.Hold;
                    _think = Mathf.Min(_think, 3);
                }
                else
                {
                    Walk(oppRight);
                }
                break;
            case Plan.Retreat:
                bool cornered = oppRight ? _me.Position.X <= Fighter.ViewLeft + 16f
                                         : _me.Position.X >= Fighter.ViewRight - 16f;
                if (cornered || dist > JumpInMax) StopMoving();
                else Walk(!oppRight);
                break;
            default:
                StopMoving();
                break;
        }
    }

    private void Press(ref bool button)
    {
        StopMoving();
        button = true;
        _punishArmed = false;
        _think = 18;
    }

    private void Walk(bool right)
    {
        _right = right;
        _left = !right;
    }

    private void StopMoving()
    {
        _left = _right = false;
    }
}
