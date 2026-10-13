using Godot;

namespace StreepFighter;

/// <summary>
/// A fighter, simulated SF2-style: everything is counted in 60Hz ticks, the
/// sprite is a baked sheet frame chosen from frame data (never tweened), and
/// hits are rectangle overlaps.  GameManager drives <see cref="PollInput"/> and
/// <see cref="Tick"/> in a fixed order so both players resolve deterministically.
/// Positions are native pixels (384x216 screen); the node origin is the feet.
/// </summary>
public partial class Fighter : Node2D
{
    [Signal] public delegate void HealthChangedEventHandler(int currentHealth, int maxHealth);
    [Signal] public delegate void DiedEventHandler();

    public int PlayerIndex { get; set; } = 0; // 0 = P1, 1 = P2
    public FighterStats Stats { get; set; }
    public Fighter Opponent { get; set; }

    public int CurrentHealth { get; protected set; }
    public FighterState CurrentState { get; private set; } = FighterState.Idle;
    public bool FacingRight { get; private set; } = true;
    public bool IsAiControlled { get; set; } = false;
    /// <summary>Wear the alternate colours (set before entering the tree; mirror matches).</summary>
    public bool UseAltPalette { get; set; }
    /// <summary>Ignore the pad (round intro / round over). Animation keeps running.</summary>
    public bool Locked { get; set; }
    /// <summary>Pixels per tick.</summary>
    public Vector2 Velocity;
    /// <summary>Projectiles this fighter currently has on screen.</summary>
    public int LiveProjectiles;

    public int Dir => FacingRight ? 1 : -1;
    public bool Grounded => Position.Y >= GroundY - 0.01f;
    public bool IsDown => CurrentState is FighterState.Knockdown or FighterState.Down
        or FighterState.GetUp or FighterState.KO;
    public bool IsAttacking => CurrentState is FighterState.Punch or FighterState.Kick
        or FighterState.CrouchPunch or FighterState.CrouchKick or FighterState.JumpPunch
        or FighterState.JumpKick or FighterState.Special;

    // ---- world (native pixels)
    public const float GroundY = 200f;
    public const float StageLeft = 14f;
    public const float StageRight = 498f;
    /// <summary>Horizontal limits of the visible screen; GameManager updates them as the camera pans.</summary>
    public static float ViewLeft = StageLeft, ViewRight = StageRight;

    // ---- physics, per tick
    private const float Gravity = 0.30f;
    private const float JumpVy = -6.5f;
    private const float JumpVxForward = 2.3f;
    private const float JumpVxBack = 2.0f;
    private const float PushFriction = 0.80f;
    public const float PushHalfWidth = 14f;

    // ---- timing, in ticks
    private const int PreJumpTicks = 3;
    private const int LandTicks = 3;
    private const int DownTicks = 26;
    private const int GetUpTicks = 14;
    private const int WakeInvuln = 8;
    private const int BufferTicks = 7;

    protected int StateTick;
    private int _stun;
    private int _invuln;
    private int _specialCooldown;
    private bool _hitDone;
    private bool _airAttackUsed;
    private bool _wasCrouching;
    private int _jumpDir;
    private float _push;
    private int _outcome; // +1 celebrate, -1 slump, 0 nothing pending
    private Move _currentMove;

    // ---- input
    private bool _hLeft, _hRight, _hUp, _hDown, _hBlock;
    private int _bufPunch, _bufKick, _bufSpecial;
    private bool _aiLeft, _aiRight, _aiJump, _aiCrouch, _aiPunch, _aiKick, _aiBlock, _aiSpecial;
    private bool _aiPunchPrev, _aiKickPrev, _aiSpecialPrev;

    // ---- presentation
    private Sprite2D _sprite;
    private Sprite2D _shadow;
    private int _frame = SpriteSheet.Idle0;
    private int _animClock;

    // =====================================================================
    //  Frame data shared by the whole cast
    // =====================================================================
    private static readonly Step[] IdleLoop =
    {
        new(SpriteSheet.Idle0, 9), new(SpriteSheet.Idle1, 7), new(SpriteSheet.Idle2, 9), new(SpriteSheet.Idle3, 7)
    };
    private static readonly int[] WalkFrames =
    {
        SpriteSheet.Walk0, SpriteSheet.Walk1, SpriteSheet.Walk2,
        SpriteSheet.Walk3, SpriteSheet.Walk4, SpriteSheet.Walk5
    };
    // One walk cycle covers 52px of floor in the art; holding each frame for
    // this many ticks keeps the feet from skating at the fighter's walk speed.
    private int WalkFrameTicks => Mathf.Clamp(Mathf.RoundToInt(52f / 6f / (Stats.WalkSpeed / 60f)), 3, 8);

    private static readonly Move StandPunch = new()
    {
        Steps = new Step[] { new(SpriteSheet.Punch0, 4), new(SpriteSheet.Punch1, 6), new(SpriteSheet.Punch2, 4), new(SpriteSheet.Idle0, 3) },
        Startup = 4, Active = 4, Box = new Rect2(12, 58, 38, 18),
        Hitstun = 15, Blockstun = 10, Push = 1.9f,
    };
    private static readonly Move StandKick = new()
    {
        Steps = new Step[] { new(SpriteSheet.Kick0, 6), new(SpriteSheet.Kick1, 7), new(SpriteSheet.Kick2, 6), new(SpriteSheet.Kick0, 4) },
        Startup = 6, Active = 5, Box = new Rect2(12, 42, 42, 26),
        Hitstun = 19, Blockstun = 13, Push = 2.5f,
        Stop = Juice.StopHeavy, Trauma = Juice.TraumaMedium, HitSfx = "kick_hit",
    };
    private static readonly Move LowPunch = new()
    {
        Steps = new Step[] { new(SpriteSheet.Cpunch0, 3), new(SpriteSheet.Cpunch1, 6), new(SpriteSheet.Cpunch0, 4) },
        Startup = 3, Active = 4, Box = new Rect2(12, 28, 38, 18),
        Hitstun = 13, Blockstun = 9, Push = 1.6f,
    };
    private static readonly Move Sweep = new()
    {
        Steps = new Step[] { new(SpriteSheet.Ckick0, 5), new(SpriteSheet.Ckick1, 7), new(SpriteSheet.Ckick0, 10) },
        Startup = 5, Active = 5, Box = new Rect2(10, 0, 42, 14), Guard = Guard.Low,
        Hitstun = 18, Blockstun = 12, Push = 2.2f, Knockdown = true, LaunchX = 1.2f, LaunchY = -3.2f,
        Stop = Juice.StopHeavy, Trauma = Juice.TraumaMedium, HitSfx = "kick_hit",
    };
    private static readonly Move AirPunch = new()
    {
        Steps = new Step[] { new(SpriteSheet.Jpunch0, 60) },
        Startup = 3, Active = 40, Box = new Rect2(6, 22, 32, 30), Guard = Guard.High,
        Hitstun = 17, Blockstun = 11, Push = 1.8f,
    };
    private static readonly Move AirKick = new()
    {
        Steps = new Step[] { new(SpriteSheet.Jkick0, 60) },
        Startup = 4, Active = 40, Box = new Rect2(6, 14, 40, 26), Guard = Guard.High,
        Hitstun = 19, Blockstun = 12, Push = 2.2f,
        Stop = Juice.StopHeavy, Trauma = Juice.TraumaMedium, HitSfx = "kick_hit",
    };
    /// <summary>What a thrown projectile does when it lands.</summary>
    public static readonly Move ProjectileHit = new()
    {
        Hitstun = 20, Blockstun = 12, Push = 2.4f, Knockdown = true, LaunchX = 2.0f, LaunchY = -3.8f,
        Stop = Juice.StopHeavy, Trauma = Juice.TraumaHeavy, HitSfx = "kick_hit",
    };

    /// <summary>Signature move animation. Subclasses override this and <see cref="SpecialTick"/>.</summary>
    protected virtual Step[] SpecialSteps { get; } =
    {
        new(SpriteSheet.Sp0, 8), new(SpriteSheet.Sp1, 6), new(SpriteSheet.Sp2, 8), new(SpriteSheet.Sp3, 8)
    };

    private int SpecialTotal
    {
        get
        {
            int t = 0;
            foreach (var s in SpecialSteps) t += s.Ticks;
            return t;
        }
    }

    // =====================================================================
    //  Setup
    // =====================================================================
    public override void _Ready()
    {
        Stats ??= FighterData.MirandaPriestly;
        CurrentHealth = Stats.MaxHealth;

        _shadow = new Sprite2D
        {
            Texture = GD.Load<Texture2D>("res://Assets/Sprites/FX/shadow.png"),
            TopLevel = true,
            ZIndex = -1,
        };
        AddChild(_shadow);

        _sprite = new Sprite2D
        {
            Texture = GD.Load<Texture2D>(UseAltPalette ? Stats.AltSheetPath : Stats.SheetPath),
            Hframes = SpriteSheet.Columns,
            Vframes = SpriteSheet.Rows,
            Centered = false,
            Offset = new Vector2(-SpriteSheet.OriginX, -SpriteSheet.OriginY),
        };
        AddChild(_sprite);
        ZIndex = PlayerIndex; // P2 draws over P1 when they overlap
    }

    public void ResetForRound(Vector2 spawnPos, bool faceRight)
    {
        CurrentHealth = Stats.MaxHealth;
        Position = spawnPos;
        Velocity = Vector2.Zero;
        FacingRight = faceRight;
        _specialCooldown = 0;
        _invuln = 0;
        _stun = 0;
        _push = 0;
        _outcome = 0;
        _bufPunch = _bufKick = _bufSpecial = 0;
        _currentMove = null;
        CurrentState = FighterState.Idle;
        StateTick = 0;
        Visible = true;
        EmitSignal(SignalName.HealthChanged, CurrentHealth, Stats.MaxHealth);
    }

    /// <summary>Round is decided: celebrate (true), slump (false) once back on the feet.</summary>
    public void RoundOver(bool won)
    {
        Locked = true;
        _outcome = won ? 1 : -1;
    }

    public float GetSpecialCooldownPercent()
    {
        if (Stats == null || Stats.SpecialCooldown <= 0) return 1f;
        return 1f - Mathf.Clamp(_specialCooldown / (Stats.SpecialCooldown * 60f), 0, 1);
    }

    // =====================================================================
    //  Input
    // =====================================================================
    public void AiInput(bool left, bool right, bool jump, bool crouch,
                        bool punch, bool kick, bool block, bool special)
    {
        _aiLeft = left; _aiRight = right; _aiJump = jump; _aiCrouch = crouch;
        _aiPunch = punch; _aiKick = kick; _aiBlock = block; _aiSpecial = special;
    }

    public void ClearAiInput() => AiInput(false, false, false, false, false, false, false, false);

    /// <summary>
    /// Sample the pad. Called every physics tick - including hit-stop ticks -
    /// so a button pressed during a freeze or the tail of a recovery is
    /// buffered and comes out on the first possible frame.
    /// </summary>
    public void PollInput()
    {
        bool punch, kick, special;
        if (IsAiControlled)
        {
            _hLeft = _aiLeft; _hRight = _aiRight; _hUp = _aiJump; _hDown = _aiCrouch; _hBlock = _aiBlock;
            punch = _aiPunch && !_aiPunchPrev;
            kick = _aiKick && !_aiKickPrev;
            special = _aiSpecial && !_aiSpecialPrev;
            _aiPunchPrev = _aiPunch; _aiKickPrev = _aiKick; _aiSpecialPrev = _aiSpecial;
        }
        else
        {
            _hLeft = Pressed("left"); _hRight = Pressed("right");
            _hUp = Pressed("jump"); _hDown = Pressed("crouch"); _hBlock = Pressed("block");
            punch = JustPressed("punch"); kick = JustPressed("kick"); special = JustPressed("special");
        }

        _bufPunch = punch ? BufferTicks : Mathf.Max(0, _bufPunch - 1);
        _bufKick = kick ? BufferTicks : Mathf.Max(0, _bufKick - 1);
        _bufSpecial = special ? BufferTicks : Mathf.Max(0, _bufSpecial - 1);
    }

    private bool Pressed(string action) => Input.IsActionPressed(InputManager.Action(PlayerIndex, action));
    private bool JustPressed(string action) => Input.IsActionJustPressed(InputManager.Action(PlayerIndex, action));

    private static bool Take(ref int buffer)
    {
        if (buffer <= 0) return false;
        buffer = 0;
        return true;
    }

    private bool HoldingBack => FacingRight ? _hLeft && !_hRight : _hRight && !_hLeft;
    private bool HoldingForward => FacingRight ? _hRight && !_hLeft : _hLeft && !_hRight;

    /// <summary>Is this fighter doing something the other should guard against right now?</summary>
    public bool Threatens(Fighter other)
    {
        if (LiveProjectiles > 0) return true;
        return IsAttacking && Mathf.Abs(other.Position.X - Position.X) < 96f;
    }

    // =====================================================================
    //  Simulation
    // =====================================================================
    public void Tick()
    {
        if (_invuln > 0) _invuln--;
        if (_specialCooldown > 0) _specialCooldown--;
        _animClock++;

        switch (CurrentState)
        {
            case FighterState.Idle:
            case FighterState.WalkForward:
            case FighterState.WalkBackward:
            case FighterState.Crouch:
            case FighterState.Block:
            case FighterState.CrouchBlock:
                TickFree();
                break;
            case FighterState.PreJump:
                Velocity.X = 0;
                if (StateTick >= PreJumpTicks)
                {
                    Enter(FighterState.Jump);
                    Velocity = new Vector2(_jumpDir * (_jumpDir == Dir ? JumpVxForward : JumpVxBack), JumpVy);
                    _airAttackUsed = false;
                    AudioManager.Instance?.PlaySFX("jump");
                }
                break;
            case FighterState.Jump:
                if (!_airAttackUsed && !Locked)
                {
                    if (Take(ref _bufPunch)) StartAirAttack(FighterState.JumpPunch, AirPunch, "punch_swing");
                    else if (Take(ref _bufKick)) StartAirAttack(FighterState.JumpKick, AirKick, "kick_swing");
                }
                break;
            case FighterState.JumpPunch:
            case FighterState.JumpKick:
                TickStrike(_currentMove, CurrentState == FighterState.JumpPunch ? Stats.PunchDmg : Stats.KickDmg);
                break;
            case FighterState.Land:
                Velocity.X = 0;
                if (StateTick >= LandTicks) Enter(FighterState.Idle);
                break;
            case FighterState.Punch:
            case FighterState.CrouchPunch:
                TickGroundAttack(Stats.PunchDmg);
                break;
            case FighterState.Kick:
            case FighterState.CrouchKick:
                TickGroundAttack(Stats.KickDmg);
                break;
            case FighterState.Special:
                SpecialTick(StateTick);
                if (CurrentState == FighterState.Special && StateTick >= SpecialTotal)
                {
                    Velocity.X = 0;
                    Enter(FighterState.Idle);
                }
                break;
            case FighterState.Hurt:
            case FighterState.CrouchHurt:
                Velocity.X = 0;
                if (--_stun <= 0)
                    Enter(CurrentState == FighterState.CrouchHurt && _hDown ? FighterState.Crouch : FighterState.Idle);
                break;
            case FighterState.Down:
                Velocity.X = 0;
                if (StateTick >= DownTicks) Enter(FighterState.GetUp);
                break;
            case FighterState.GetUp:
                if (StateTick >= GetUpTicks)
                {
                    _invuln = WakeInvuln;
                    Enter(FighterState.Idle);
                }
                break;
            case FighterState.Knockdown:
            case FighterState.KO:
            case FighterState.Win:
            case FighterState.Lose:
                if (Grounded) Velocity.X = 0;
                break;
        }

        Integrate();
        StateTick++;
    }

    private void TickFree()
    {
        // Block-stun: locked into the guard pose, sliding back.
        if (_stun > 0)
        {
            _stun--;
            Velocity.X = 0;
            return;
        }

        UpdateFacing();
        Velocity.X = 0;

        if (Locked)
        {
            if (_outcome > 0) Enter(FighterState.Win);
            else if (_outcome < 0) Enter(FighterState.Lose);
            else Set(FighterState.Idle);
            return;
        }

        if (_specialCooldown <= 0 && Take(ref _bufSpecial))
        {
            _specialCooldown = Mathf.RoundToInt(Stats.SpecialCooldown * 60f);
            Enter(FighterState.Special);
            AudioManager.Instance?.PlaySFX("special");
            return;
        }
        if (Take(ref _bufPunch))
        {
            StartGroundAttack(_hDown ? FighterState.CrouchPunch : FighterState.Punch, _hDown ? LowPunch : StandPunch);
            return;
        }
        if (Take(ref _bufKick))
        {
            StartGroundAttack(_hDown ? FighterState.CrouchKick : FighterState.Kick, _hDown ? Sweep : StandKick);
            return;
        }

        // Guard: the block button, or SF2-style - hold away while they attack.
        if (_hBlock || (HoldingBack && Opponent != null && Opponent.Threatens(this)))
        {
            Set(_hDown ? FighterState.CrouchBlock : FighterState.Block);
            return;
        }

        if (_hUp)
        {
            _jumpDir = _hRight == _hLeft ? 0 : (_hRight ? 1 : -1);
            Enter(FighterState.PreJump);
            return;
        }

        if (_hDown)
        {
            Set(FighterState.Crouch);
            return;
        }

        float perTick = Stats.WalkSpeed / 60f;
        if (HoldingForward)
        {
            Set(FighterState.WalkForward);
            Velocity.X = Dir * perTick;
        }
        else if (HoldingBack)
        {
            Set(FighterState.WalkBackward);
            Velocity.X = -Dir * perTick * 0.8f;
        }
        else
        {
            Set(FighterState.Idle);
        }
    }

    private void StartGroundAttack(FighterState state, Move move)
    {
        _currentMove = move;
        Enter(state);
    }

    private void StartAirAttack(FighterState state, Move move, string sfx)
    {
        _airAttackUsed = true;
        _currentMove = move;
        Enter(state);
        AudioManager.Instance?.PlaySFX(sfx);
    }

    private void TickGroundAttack(int damage)
    {
        Velocity.X = 0;
        var move = _currentMove;
        if (StateTick == move.Startup)
            AudioManager.Instance?.PlaySFX(CurrentState is FighterState.Kick or FighterState.CrouchKick ? "kick_swing" : "punch_swing");
        TickStrike(move, damage);
        if (StateTick >= move.Total)
        {
            bool low = CurrentState is FighterState.CrouchPunch or FighterState.CrouchKick;
            Enter(low && _hDown ? FighterState.Crouch : FighterState.Idle);
        }
    }

    /// <summary>Check the current move's hitbox during its active window.</summary>
    private void TickStrike(Move move, int damage)
    {
        if (StateTick >= move.Startup && StateTick < move.Startup + move.Active)
            Strike(move, damage);
    }

    /// <summary>
    /// Try to land <paramref name="move"/> right now. Each attack connects at
    /// most once; call <see cref="RearmStrike"/> for multi-hit moves.
    /// </summary>
    protected bool Strike(Move move, int damage)
    {
        if (_hitDone || Locked || Opponent == null) return false;
        Rect2 box = WorldBox(move.Box);
        Rect2 hurt = Opponent.Hurtbox;
        if (hurt.Size.X <= 0 || !box.Intersects(hurt)) return false;

        Rect2 overlap = box.Intersection(hurt);
        Vector2 contact = overlap.GetCenter();
        if (Opponent.ReceiveHit(this, damage, move, contact))
            _hitDone = true;
        return _hitDone;
    }

    protected void RearmStrike() => _hitDone = false;

    /// <summary>Called every tick of the Special state (t = ticks since it began).</summary>
    protected virtual void SpecialTick(int t)
    {
        Velocity.X = 0;
    }

    private void Integrate()
    {
        bool wasAir = !Grounded;
        if (wasAir || Velocity.Y < 0)
            Velocity.Y += Gravity;

        var pos = Position + Velocity;
        pos.X += _push;
        _push *= PushFriction;
        if (Mathf.Abs(_push) < 0.05f) _push = 0;

        if (pos.Y >= GroundY && Velocity.Y >= 0)
        {
            pos.Y = GroundY;
            Velocity.Y = 0;
            if (wasAir) OnLand();
        }
        Position = pos;
    }

    private void OnLand()
    {
        switch (CurrentState)
        {
            case FighterState.Jump:
            case FighterState.JumpPunch:
            case FighterState.JumpKick:
                AudioManager.Instance?.PlaySFX("land");
                Fx.Spawn(GetParent(), "dust", new Vector2(Position.X, GroundY - 7), 4, 3);
                Enter(FighterState.Land);
                break;
            case FighterState.Knockdown:
                AudioManager.Instance?.PlaySFX("land");
                Fx.Spawn(GetParent(), "dust", new Vector2(Position.X, GroundY - 7), 4, 4);
                Juice.AddTrauma(Juice.TraumaLight);
                Enter(FighterState.Down);
                break;
            case FighterState.KO:
                AudioManager.Instance?.PlaySFX("land");
                Fx.Spawn(GetParent(), "dust", new Vector2(Position.X, GroundY - 7), 4, 4);
                Juice.AddTrauma(Juice.TraumaMedium);
                break;
        }
    }

    private void UpdateFacing()
    {
        if (Opponent == null) return;
        float dx = Opponent.Position.X - Position.X;
        if (Mathf.Abs(dx) > 1f)
            FacingRight = dx > 0;
    }

    /// <summary>Switch state and restart its clock.</summary>
    protected void Enter(FighterState state)
    {
        _wasCrouching = CurrentState is FighterState.Crouch or FighterState.CrouchBlock
            or FighterState.CrouchPunch or FighterState.CrouchKick or FighterState.CrouchHurt;
        CurrentState = state;
        StateTick = -1; // Tick() increments after the state logic, so the first full tick reads 0
        _hitDone = false;
    }

    /// <summary>Switch state only if it actually changes (keeps loops running).</summary>
    private void Set(FighterState state)
    {
        if (CurrentState != state) Enter(state);
    }

    // =====================================================================
    //  Boxes
    // =====================================================================
    /// <summary>Convert a facing-relative box (x forward, y up from the feet) to world space.</summary>
    protected Rect2 WorldBox(Rect2 local)
    {
        float x = FacingRight ? Position.X + local.Position.X : Position.X - local.Position.X - local.Size.X;
        return new Rect2(x, Position.Y - local.Position.Y - local.Size.Y, local.Size.X, local.Size.Y);
    }

    /// <summary>Where this fighter can be hit; empty while knocked down.</summary>
    public Rect2 Hurtbox
    {
        get
        {
            switch (CurrentState)
            {
                case FighterState.Knockdown:
                case FighterState.Down:
                case FighterState.GetUp:
                case FighterState.KO:
                    return new Rect2();
                case FighterState.Crouch:
                case FighterState.CrouchBlock:
                case FighterState.CrouchPunch:
                case FighterState.CrouchKick:
                case FighterState.CrouchHurt:
                    return new Rect2(Position.X - 11, Position.Y - 60, 22, 60);
                case FighterState.Jump:
                case FighterState.JumpPunch:
                case FighterState.JumpKick:
                    return new Rect2(Position.X - 10, Position.Y - 84, 20, 62);
                default:
                    return new Rect2(Position.X - 10, Position.Y - 90, 20, 90);
            }
        }
    }

    // =====================================================================
    //  Getting hit
    // =====================================================================
    /// <returns>false if the attack passed straight through (invulnerable / down).</returns>
    public virtual bool ReceiveHit(Fighter attacker, int damage, Move move, Vector2 contact)
    {
        if (IsDown || _invuln > 0) return false;

        bool crouched = CurrentState is FighterState.Crouch or FighterState.CrouchBlock;
        bool low = crouched || CurrentState is FighterState.CrouchPunch or FighterState.CrouchKick
            or FighterState.CrouchHurt;
        bool guarding = Grounded && (
            CurrentState is FighterState.Block or FighterState.CrouchBlock
            || (CurrentState is FighterState.Idle or FighterState.WalkBackward or FighterState.Crouch
                && (_hBlock || HoldingBack)));
        bool blocked = guarding
            && !(move.Guard == Guard.Low && !crouched)
            && !(move.Guard == Guard.High && crouched);

        if (blocked)
            damage = (int)(damage * (1f - Stats.BlockReduction));
        ApplyDamage(damage);

        float away = attacker != null && attacker.Position.X > Position.X ? -1f : 1f;
        bool ko = CurrentHealth <= 0;

        Juice.HitStop(ko ? Juice.StopSpecial : blocked ? Mathf.Max(2, move.Stop - 2) : move.Stop);
        Juice.AddTrauma(ko ? Juice.TraumaKO : blocked ? move.Trauma * 0.5f : move.Trauma);

        if (ko)
        {
            Fx.Spawn(GetParent(), "hitspark", contact, 4, 3);
            AudioManager.Instance?.PlaySFX(move.HitSfx);
            AudioManager.Instance?.PlaySFX("ko");
            Enter(FighterState.KO);
            Velocity = new Vector2(away * 2.6f, -5.2f);
            Position = new Vector2(Position.X, Mathf.Min(Position.Y, GroundY - 1f));
            _stun = 0;
            EmitSignal(SignalName.Died);
            return true;
        }

        if (blocked)
        {
            Fx.Spawn(GetParent(), "blockspark", contact, 3, 3);
            AudioManager.Instance?.PlaySFX("block_hit");
            Enter(crouched ? FighterState.CrouchBlock : FighterState.Block);
            _stun = move.Blockstun;
            ShoveFrom(attacker, away, move.Push);
            return true;
        }

        Fx.Spawn(GetParent(), "hitspark", contact, 4, 3);
        AudioManager.Instance?.PlaySFX(move.HitSfx);
        AudioManager.Instance?.PlaySFX("hurt");

        if (!Grounded || move.Knockdown)
        {
            Enter(FighterState.Knockdown);
            Velocity = new Vector2(away * move.LaunchX, move.LaunchY);
            Position = new Vector2(Position.X, Mathf.Min(Position.Y, GroundY - 1f));
        }
        else
        {
            Enter(low ? FighterState.CrouchHurt : FighterState.Hurt);
            _stun = move.Hitstun;
            Velocity = Vector2.Zero;
            ShoveFrom(attacker, away, move.Push);
        }
        return true;
    }

    /// <summary>Slide back from a hit; if the corner stops us, the attacker slides instead.</summary>
    private void ShoveFrom(Fighter attacker, float away, float amount)
    {
        bool cornered = away > 0 ? Position.X >= ViewRight - 2f : Position.X <= ViewLeft + 2f;
        if (cornered && attacker != null && attacker.Grounded)
            attacker._push = -away * amount;
        else
            _push = away * amount;
    }

    protected void ApplyDamage(int amount)
    {
        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        EmitSignal(SignalName.HealthChanged, CurrentHealth, Stats.MaxHealth);
    }

    /// <summary>Tiny shove used by armoured moves that eat a hit without flinching.</summary>
    protected void Nudge(float amount) => _push += amount;

    // =====================================================================
    //  Presentation
    // =====================================================================
    public override void _Process(double delta)
    {
        if (_sprite == null) return;

        _frame = PickFrame();
        _sprite.Frame = _frame;
        _sprite.Scale = new Vector2(Dir, 1);

        // The victim rattles for the length of the hit-stop.
        bool rattle = Juice.HitStopFrames > 0
            && CurrentState is FighterState.Hurt or FighterState.CrouchHurt or FighterState.Knockdown or FighterState.KO;
        _sprite.Position = rattle ? new Vector2((Juice.HitStopFrames & 1) == 0 ? 1 : -1, 0) : Vector2.Zero;

        // Wake-up invulnerability flickers.
        _sprite.Visible = _invuln <= 0 || (_invuln & 2) == 0;

        float height = Mathf.Max(0f, GroundY - Position.Y);
        float s = Mathf.Clamp(1f - height / 110f, 0.55f, 1f);
        bool lying = CurrentState is FighterState.Down or FighterState.KO && Grounded;
        _shadow.GlobalPosition = new Vector2(Mathf.Round(Position.X) + (lying ? Dir * -4 : 0), GroundY + 1);
        _shadow.Scale = new Vector2(lying ? 1.7f : s, 1f);
    }

    private int PickFrame()
    {
        int t = Mathf.Max(StateTick, 0);
        switch (CurrentState)
        {
            case FighterState.Idle:
                return LoopFrame(IdleLoop, _animClock);
            case FighterState.WalkForward:
                return WalkFrames[t / WalkFrameTicks % WalkFrames.Length];
            case FighterState.WalkBackward:
                return WalkFrames[WalkFrames.Length - 1 - t / WalkFrameTicks % WalkFrames.Length];
            case FighterState.Crouch:
                return t < 2 && !_wasCrouching ? SpriteSheet.Crouch0 : SpriteSheet.Crouch1;
            case FighterState.PreJump:
            case FighterState.Land:
                return SpriteSheet.Crouch0;
            case FighterState.Jump:
                return Velocity.Y < -2.2f ? SpriteSheet.Jump0 : Velocity.Y < 2.2f ? SpriteSheet.Jump1 : SpriteSheet.Jump2;
            case FighterState.Punch:
            case FighterState.Kick:
            case FighterState.CrouchPunch:
            case FighterState.CrouchKick:
            case FighterState.JumpPunch:
            case FighterState.JumpKick:
                return _currentMove.FrameAt(t);
            case FighterState.Special:
                return FrameAt(SpecialSteps, t);
            case FighterState.Block:
                return SpriteSheet.Block0;
            case FighterState.CrouchBlock:
                return SpriteSheet.Cblock0;
            case FighterState.Hurt:
                return t < 8 ? SpriteSheet.Hurt0 : SpriteSheet.Hurt1;
            case FighterState.CrouchHurt:
                return SpriteSheet.Churt0;
            case FighterState.Knockdown:
            case FighterState.KO:
                if (Grounded) return SpriteSheet.Kd2;
                return Velocity.Y < 0.5f ? SpriteSheet.Kd0 : SpriteSheet.Kd1;
            case FighterState.Down:
                return SpriteSheet.Kd2;
            case FighterState.GetUp:
                return t < GetUpTicks / 2 ? SpriteSheet.Getup0 : SpriteSheet.Getup1;
            case FighterState.Win:
                return t / 14 % 2 == 0 ? SpriteSheet.Win0 : SpriteSheet.Win1;
            case FighterState.Lose:
                return SpriteSheet.Lose0;
        }
        return SpriteSheet.Idle0;
    }

    private static int LoopFrame(Step[] steps, int clock)
    {
        int total = 0;
        foreach (var s in steps) total += s.Ticks;
        return FrameAt(steps, clock % total);
    }

    private static int FrameAt(Step[] steps, int tick)
    {
        foreach (var s in steps)
        {
            if (tick < s.Ticks) return s.Frame;
            tick -= s.Ticks;
        }
        return steps[^1].Frame;
    }
}
