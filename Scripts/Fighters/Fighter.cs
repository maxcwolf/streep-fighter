using Godot;

namespace StreepFighter;

public partial class Fighter : CharacterBody2D
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

    // Physics
    private const float Gravity = 1200f;
    private const float JumpVelocity = -550f;
    private const float GroundY = 500f;
    private const float LeftWall = 80f;
    private const float RightWall = 1200f;

    // State timing
    protected float _stateTimer;
    private const float PunchDuration = 0.35f;
    private const float KickDuration = 0.4f;
    private const float HurtDuration = 0.4f;
    private const float InvincibilityDuration = 0.3f;

    // Special
    private float _specialCooldownTimer;
    protected float SpecialDuration = 0.5f;
    protected bool SpecialActive;

    // Hitbox management
    private bool _hitboxActivatedThisAttack;
    private bool _hitConnectedThisAttack;
    private float _invincibilityTimer;

    // AI input state
    private bool _aiLeft, _aiRight, _aiJump, _aiCrouch;
    private bool _aiPunch, _aiKick, _aiBlock, _aiSpecial;

    // Animation
    private float _animTime;
    // Body squash/stretch follow-through spring (settles overshoot after states)
    private Vector2 _bodyScaleVel = Vector2.Zero;
    private Vector2 _bodyScaleSmoothed = Vector2.One;
    // Limb lag — arms trail the torso by a couple frames for follow-through.
    private float _armRRotLag, _armLRotLag, _legRRotLag, _legLRotLag;
    private float _foreRRotLag, _foreLRotLag, _shinRRotLag, _shinLRotLag;
    // Landing squash impulse (decays); set when we touch the ground from a jump.
    private float _landSquash;
    private float _prevFallSpeed;
    // Idle micro-flourish timing.
    private float _flourishTimer;
    private float _flourish; // 0..1 active flourish amount

    // Node references
    private Color _originalColor;
    protected Polygon2D BodyPolygon;
    private Polygon2D _punchEffect;
    private Polygon2D _kickEffect;
    private Vector2 _bodyBasePosition;
    private Polygon2D _armR, _armL, _legR, _legL;
    private Vector2 _armRBase, _armLBase, _legRBase, _legLBase;
    // Articulated second segments (optional — graceful single-segment fallback).
    private Node2D _forearmR, _forearmL, _shinR, _shinL;
    private float _forearmRBaseRot, _forearmLBaseRot, _shinRBaseRot, _shinLBaseRot;
    private Polygon2D _head, _hair;
    private Vector2 _headBase, _hairBase;
    private float _headBaseRot, _hairBaseRot;
    private Color _headOrigColor, _hairOrigColor;
    // Secondary-motion cloth nodes (swayed by velocity lag + spring overshoot).
    private static readonly string[] ClothNames =
        { "Hair", "Cape", "Veil", "Coat", "Skirt", "Scarf", "Apron" };
    private Node2D[] _clothNodes;
    private float[] _clothBaseRot;
    private float[] _clothSway;     // current sway angle
    private float[] _clothSwayVel;  // angular velocity for spring
    // South Park face nodes
    private Polygon2D _eyeWhiteL, _eyeWhiteR;
    private Polygon2D _pupilL, _pupilR;
    private Vector2 _pupilLBase, _pupilRBase;
    // Blink animation
    private float _blinkTimer;
    private const float BlinkInterval = 4f;
    private const float BlinkDuration = 0.12f;
    private Color _armROrigColor, _armLOrigColor, _legROrigColor, _legLOrigColor;
    private Area2D _punchHitbox;
    private Area2D _kickHitbox;
    private Area2D _hurtbox;
    private CollisionShape2D _punchShape;
    private CollisionShape2D _kickShape;

    public override void _Ready()
    {
        if (Stats == null)
            Stats = FighterData.MirandaPriestly;

        CurrentHealth = Stats.MaxHealth;

        BodyPolygon = GetNode<Polygon2D>("BodyPolygon");
        _punchHitbox = GetNode<Area2D>("PunchHitbox");
        _kickHitbox = GetNode<Area2D>("KickHitbox");
        _hurtbox = GetNode<Area2D>("Hurtbox");
        _punchShape = _punchHitbox.GetNode<CollisionShape2D>("PunchShape");
        _kickShape = _kickHitbox.GetNode<CollisionShape2D>("KickShape");

        _punchShape.Disabled = true;
        _kickShape.Disabled = true;

        _punchEffect = GetNodeOrNull<Polygon2D>("PunchEffect");
        _kickEffect = GetNodeOrNull<Polygon2D>("KickEffect");
        _bodyBasePosition = BodyPolygon.Position;

        _armR = GetNodeOrNull<Polygon2D>("ArmR");
        _armL = GetNodeOrNull<Polygon2D>("ArmL");
        _legR = GetNodeOrNull<Polygon2D>("LegR");
        _legL = GetNodeOrNull<Polygon2D>("LegL");
        if (_armR != null) { _armRBase = _armR.Position; _armROrigColor = _armR.Color; }
        if (_armL != null) { _armLBase = _armL.Position; _armLOrigColor = _armL.Color; }
        if (_legR != null) { _legRBase = _legR.Position; _legROrigColor = _legR.Color; }
        if (_legL != null) { _legLBase = _legL.Position; _legLOrigColor = _legL.Color; }

        // Articulated second segments (forearms / shins). Optional — the rig
        // animates fine single-segment if these are absent.
        _forearmR = _armR?.GetNodeOrNull<Node2D>("ForearmR");
        _forearmL = _armL?.GetNodeOrNull<Node2D>("ForearmL");
        _shinR = _legR?.GetNodeOrNull<Node2D>("ShinR");
        _shinL = _legL?.GetNodeOrNull<Node2D>("ShinL");
        if (_forearmR != null) _forearmRBaseRot = _forearmR.Rotation;
        if (_forearmL != null) _forearmLBaseRot = _forearmL.Rotation;
        if (_shinR != null) _shinRBaseRot = _shinR.Rotation;
        if (_shinL != null) _shinLBaseRot = _shinL.Rotation;

        _head = GetNodeOrNull<Polygon2D>("Head");
        _hair = GetNodeOrNull<Polygon2D>("Hair");
        if (_head != null) { _headBase = _head.Position; _headOrigColor = _head.Color; _headBaseRot = _head.Rotation; }
        if (_hair != null) { _hairBase = _hair.Position; _hairOrigColor = _hair.Color; _hairBaseRot = _hair.Rotation; }

        // Gather secondary-motion cloth nodes (direct children matching exact names).
        var cloth = new System.Collections.Generic.List<Node2D>();
        var clothRot = new System.Collections.Generic.List<float>();
        foreach (string n in ClothNames)
        {
            var node = GetNodeOrNull<Node2D>(n);
            if (node != null) { cloth.Add(node); clothRot.Add(node.Rotation); }
        }
        _clothNodes = cloth.ToArray();
        _clothBaseRot = clothRot.ToArray();
        _clothSway = new float[_clothNodes.Length];
        _clothSwayVel = new float[_clothNodes.Length];

        // South Park face nodes (backward compatible)
        if (_head != null)
        {
            _eyeWhiteL = _head.GetNodeOrNull<Polygon2D>("EyeWhiteL");
            _eyeWhiteR = _head.GetNodeOrNull<Polygon2D>("EyeWhiteR");
            if (_eyeWhiteL != null)
                _pupilL = _eyeWhiteL.GetNodeOrNull<Polygon2D>("PupilL");
            if (_eyeWhiteR != null)
                _pupilR = _eyeWhiteR.GetNodeOrNull<Polygon2D>("PupilR");
            if (_pupilL != null) _pupilLBase = _pupilL.Position;
            if (_pupilR != null) _pupilRBase = _pupilR.Position;
        }
        _blinkTimer = BlinkInterval;

        _originalColor = BodyPolygon.Color;

        _punchHitbox.AreaEntered += OnPunchHit;
        _kickHitbox.AreaEntered += OnKickHit;
        _hurtbox.AreaEntered += OnHurtboxEntered;
    }

    public void SetupCollisionLayers()
    {
        // Body: own layer
        uint bodyLayer = PlayerIndex == 0 ? 1u : 2u;
        CollisionLayer = bodyLayer;
        CollisionMask = PlayerIndex == 0 ? 2u : 1u;

        // Hurtbox: on own layer, masks opponent's attack layer
        uint hurtLayer = PlayerIndex == 0 ? 1u : 2u;
        uint attackMask = PlayerIndex == 0 ? 8u : 4u; // P1 hurtbox masks P2Attacks(8), P2 masks P1Attacks(4)
        _hurtbox.CollisionLayer = hurtLayer;
        _hurtbox.CollisionMask = attackMask | 16u; // also mask projectiles

        // Punch/Kick hitboxes: on own attack layer
        uint atkLayer = PlayerIndex == 0 ? 4u : 8u;
        uint opponentHurtMask = PlayerIndex == 0 ? 2u : 1u;
        _punchHitbox.CollisionLayer = atkLayer;
        _punchHitbox.CollisionMask = opponentHurtMask;
        _kickHitbox.CollisionLayer = atkLayer;
        _kickHitbox.CollisionMask = opponentHurtMask;
    }

    public override void _PhysicsProcess(double delta)
    {
        // HIT-STOP: while frozen, do not advance movement, state timers, the
        // anim clock or transitions. Rendering keeps running in _Process so the
        // impact freeze-frame stays fully drawn.
        if (Juice.HitStopFrames > 0)
            return;

        float dt = (float)delta;

        if (_invincibilityTimer > 0)
            _invincibilityTimer -= dt;

        if (_specialCooldownTimer > 0)
            _specialCooldownTimer -= dt;

        UpdateFacing();

        switch (CurrentState)
        {
            case FighterState.Idle:
            case FighterState.WalkForward:
            case FighterState.WalkBackward:
            case FighterState.Crouch:
                HandleFreeState(dt);
                break;
            case FighterState.Jump:
                HandleJumpState(dt);
                break;
            case FighterState.Punch:
                HandleAttackState(dt, PunchDuration, FighterState.Punch);
                break;
            case FighterState.Kick:
                HandleAttackState(dt, KickDuration, FighterState.Kick);
                break;
            case FighterState.Block:
                HandleBlockState(dt);
                break;
            case FighterState.Special:
                HandleSpecialState(dt);
                break;
            case FighterState.Hurt:
                HandleHurtState(dt);
                break;
            case FighterState.KO:
                break;
        }

        // Track fall speed so landing can squash proportionally to impact.
        _prevFallSpeed = Velocity.Y;

        // Apply gravity if airborne
        if (Position.Y < GroundY)
        {
            var vel = Velocity;
            vel.Y += Gravity * dt;
            Velocity = vel;
        }
        else if (Velocity.Y > 0)
        {
            var pos = Position;
            pos.Y = GroundY;
            Position = pos;
            var vel = Velocity;
            vel.Y = 0;
            Velocity = vel;

            // Land from jump — kick off a wide landing squash (recovers via spring).
            if (CurrentState == FighterState.Jump)
            {
                AudioManager.Instance?.PlaySFX("land");
                _landSquash = Mathf.Clamp(_prevFallSpeed / 600f, 0.4f, 1f);
                SpawnLandingDust();
                ChangeState(FighterState.Idle);
            }
        }

        // Clamp X
        MoveAndSlide();
        var clampedPos = Position;
        clampedPos.X = Mathf.Clamp(clampedPos.X, LeftWall, RightWall);
        Position = clampedPos;
    }

    public override void _Process(double delta)
    {
        float dt = (float)delta;

        // Freeze the anim clock during hit-stop (rendering still runs so the
        // current freeze-frame pose holds), but always re-render.
        if (Juice.HitStopFrames <= 0)
        {
            _animTime += dt;

            // Blink scheduler (visual only — safe in _Process).
            _blinkTimer -= dt;
            if (_blinkTimer <= 0)
                _blinkTimer = BlinkInterval + (float)GD.RandRange(-0.5, 1.0);

            // Landing-squash impulse decay.
            if (_landSquash > 0f)
                _landSquash = Mathf.MoveToward(_landSquash, 0f, dt * 3.2f);

            // Idle micro-flourish scheduler (occasional little weight shift).
            _flourishTimer -= dt;
            if (_flourishTimer <= 0f && CurrentState == FighterState.Idle)
            {
                _flourishTimer = (float)GD.RandRange(3.5, 7.0);
                _flourish = 1f;
            }
            if (_flourish > 0f)
                _flourish = Mathf.MoveToward(_flourish, 0f, dt * 0.7f);

            UpdateSecondaryMotion(dt);
        }

        UpdateVisuals();
    }

    private void UpdateFacing()
    {
        if (Opponent == null) return;
        bool shouldFaceRight = Opponent.Position.X > Position.X;
        if (shouldFaceRight != FacingRight)
        {
            FacingRight = shouldFaceRight;
            float dir = FacingRight ? 1 : -1;
            // Flip hitbox positions using actual scene values
            float punchX = Mathf.Abs(_punchHitbox.Position.X);
            float kickX = Mathf.Abs(_kickHitbox.Position.X);
            _punchHitbox.Position = new Vector2(dir * punchX, _punchHitbox.Position.Y);
            _kickHitbox.Position = new Vector2(dir * kickX, _kickHitbox.Position.Y);
            // Flip effect positions
            if (_punchEffect != null)
            {
                float peX = Mathf.Abs(_punchEffect.Position.X);
                _punchEffect.Position = new Vector2(dir * peX, _punchEffect.Position.Y);
            }
            if (_kickEffect != null)
            {
                float keX = Mathf.Abs(_kickEffect.Position.X);
                _kickEffect.Position = new Vector2(dir * keX, _kickEffect.Position.Y);
            }
        }
    }

    private bool GetInput(string action)
    {
        if (IsAiControlled)
        {
            return action switch
            {
                "left" => _aiLeft,
                "right" => _aiRight,
                "jump" => _aiJump,
                "crouch" => _aiCrouch,
                "punch" => _aiPunch,
                "kick" => _aiKick,
                "block" => _aiBlock,
                "special" => _aiSpecial,
                _ => false
            };
        }
        return Input.IsActionPressed(InputManager.Action(PlayerIndex, action));
    }

    private bool GetInputJustPressed(string action)
    {
        if (IsAiControlled)
        {
            // AI uses held inputs; treat as just pressed for action triggers
            return action switch
            {
                "punch" => _aiPunch,
                "kick" => _aiKick,
                "special" => _aiSpecial,
                "jump" => _aiJump,
                _ => false
            };
        }
        return Input.IsActionJustPressed(InputManager.Action(PlayerIndex, action));
    }

    public void AiInput(bool left, bool right, bool jump, bool crouch,
                         bool punch, bool kick, bool block, bool special)
    {
        _aiLeft = left;
        _aiRight = right;
        _aiJump = jump;
        _aiCrouch = crouch;
        _aiPunch = punch;
        _aiKick = kick;
        _aiBlock = block;
        _aiSpecial = special;
    }

    public void ClearAiInput()
    {
        _aiLeft = _aiRight = _aiJump = _aiCrouch = false;
        _aiPunch = _aiKick = _aiBlock = _aiSpecial = false;
    }

    private void HandleFreeState(float dt)
    {
        // Priority: special > attacks > block > movement
        if (GetInputJustPressed("special") && _specialCooldownTimer <= 0)
        {
            ChangeState(FighterState.Special);
            return;
        }
        if (GetInputJustPressed("punch"))
        {
            ChangeState(FighterState.Punch);
            return;
        }
        if (GetInputJustPressed("kick"))
        {
            ChangeState(FighterState.Kick);
            return;
        }
        if (GetInput("block"))
        {
            ChangeState(FighterState.Block);
            return;
        }
        if (GetInputJustPressed("jump") && Position.Y >= GroundY - 1)
        {
            ChangeState(FighterState.Jump);
            var vel = Velocity;
            vel.Y = JumpVelocity;
            Velocity = vel;
            return;
        }

        // Movement
        float moveDir = 0;
        if (GetInput("left")) moveDir -= 1;
        if (GetInput("right")) moveDir += 1;

        if (GetInput("crouch"))
        {
            CurrentState = FighterState.Crouch;
            var vel = Velocity;
            vel.X = 0;
            Velocity = vel;
            return;
        }

        if (moveDir != 0)
        {
            bool movingTowardOpponent = (moveDir > 0 && FacingRight) || (moveDir < 0 && !FacingRight);
            CurrentState = movingTowardOpponent ? FighterState.WalkForward : FighterState.WalkBackward;
            var vel = Velocity;
            vel.X = moveDir * Stats.WalkSpeed;
            Velocity = vel;
        }
        else
        {
            CurrentState = FighterState.Idle;
            var vel = Velocity;
            vel.X = 0;
            Velocity = vel;
        }
    }

    private void HandleJumpState(float dt)
    {
        // Allow air control
        float moveDir = 0;
        if (GetInput("left")) moveDir -= 1;
        if (GetInput("right")) moveDir += 1;
        var vel = Velocity;
        vel.X = moveDir * Stats.WalkSpeed * 0.7f;
        Velocity = vel;
    }

    private void HandleAttackState(float dt, float duration, FighterState attackType)
    {
        _stateTimer += dt;
        float progress = _stateTimer / duration;

        // Activate hitbox at 40%, deactivate at 70%
        if (progress >= 0.4f && progress < 0.7f && !_hitboxActivatedThisAttack)
        {
            _hitboxActivatedThisAttack = true;
            if (attackType == FighterState.Punch)
                _punchShape.Disabled = false;
            else
                _kickShape.Disabled = false;
        }
        else if (progress >= 0.7f)
        {
            _punchShape.Disabled = true;
            _kickShape.Disabled = true;
        }

        if (progress >= 1.0f)
        {
            if (attackType == FighterState.Punch && !_hitConnectedThisAttack)
                AudioManager.Instance?.PlaySFX("punch_swing");
            _punchShape.Disabled = true;
            _kickShape.Disabled = true;
            ChangeState(FighterState.Idle);
        }

        // Stop movement during attack
        var vel = Velocity;
        vel.X = 0;
        Velocity = vel;
    }

    private void HandleBlockState(float dt)
    {
        var vel = Velocity;
        vel.X = 0;
        Velocity = vel;

        if (!GetInput("block"))
            ChangeState(FighterState.Idle);
    }

    protected virtual void HandleSpecialState(float dt)
    {
        _stateTimer += dt;
        if (_stateTimer >= SpecialDuration)
            ChangeState(FighterState.Idle);

        var vel = Velocity;
        vel.X = 0;
        Velocity = vel;
    }

    private void HandleHurtState(float dt)
    {
        _stateTimer += dt;

        // Decelerate knockback
        var vel = Velocity;
        vel.X = Mathf.MoveToward(vel.X, 0, 600 * dt);
        Velocity = vel;

        if (_stateTimer >= HurtDuration)
        {
            _invincibilityTimer = InvincibilityDuration;
            ChangeState(FighterState.Idle);
        }
    }

    protected void ChangeState(FighterState newState)
    {
        if (CurrentState == FighterState.KO) return;

        CurrentState = newState;
        _stateTimer = 0;
        _hitboxActivatedThisAttack = false;
        _hitConnectedThisAttack = false;
        _punchShape.Disabled = true;
        _kickShape.Disabled = true;
        SpecialActive = false;

        if (newState == FighterState.Special)
            _specialCooldownTimer = Stats.SpecialCooldown;

        // SFX on state entry
        switch (newState)
        {
            case FighterState.Kick:
                AudioManager.Instance?.PlaySFX("kick_swing");
                break;
            case FighterState.Block:
                AudioManager.Instance?.PlaySFX("block");
                break;
            case FighterState.Special:
                AudioManager.Instance?.PlaySFX("special");
                break;
            case FighterState.Jump:
                AudioManager.Instance?.PlaySFX("jump");
                break;
        }
    }

    private void OnPunchHit(Area2D area)
    {
        if (area.GetParent() is Fighter target && target != this)
        {
            _hitConnectedThisAttack = true;
            AudioManager.Instance?.PlaySFX("punch_hit");
            target.TakeDamage(Stats.PunchDmg, this);
        }
    }

    private void OnKickHit(Area2D area)
    {
        if (area.GetParent() is Fighter target && target != this)
        {
            AudioManager.Instance?.PlaySFX("kick_hit");
            target.TakeDamage(Stats.KickDmg, this);
        }
    }

    private void OnHurtboxEntered(Area2D area)
    {
        // Handled by hitbox side (OnPunchHit/OnKickHit)
    }

    public virtual void TakeDamage(int amount, Fighter attacker)
    {
        if (CurrentState == FighterState.KO) return;
        if (_invincibilityTimer > 0) return;

        bool blocked = CurrentState == FighterState.Block;
        if (blocked)
            amount = (int)(amount * (1f - Stats.BlockReduction));

        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        EmitSignal(SignalName.HealthChanged, CurrentHealth, Stats.MaxHealth);

        bool isKo = CurrentHealth <= 0;
        // JUICE: hit-stop + screen shake + comic burst for every connect.
        ApplyHitJuice(attacker, isKo, blocked);

        if (isKo)
        {
            AudioManager.Instance?.PlaySFX("ko");
            ChangeState(FighterState.KO);
            var vel = Velocity;
            vel.X = 0;
            Velocity = vel;
            EmitSignal(SignalName.Died);
            return;
        }

        if (blocked)
        {
            AudioManager.Instance?.PlaySFX("block_hit");
        }
        else
        {
            AudioManager.Instance?.PlaySFX("hurt");
            ChangeState(FighterState.Hurt);
            // Knockback away from attacker
            float knockDir = attacker.Position.X < Position.X ? 1 : -1;
            var v = Velocity;
            v.X = knockDir * 300;
            Velocity = v;
        }
    }

    /// <summary>
    /// Pure presentation: freeze frame, camera trauma, and the pop-art burst.
    /// Touches NO gameplay numbers / state / velocity. Weight is inferred from
    /// the attacker's current action so kicks/specials hit harder than jabs.
    /// </summary>
    private void ApplyHitJuice(Fighter attacker, bool isKo, bool blocked)
    {
        int stopFrames;
        float trauma;

        if (isKo)
        {
            stopFrames = Juice.StopSpecial;
            trauma = Juice.TraumaKO;
        }
        else if (attacker != null && attacker.CurrentState == FighterState.Special)
        {
            stopFrames = Juice.StopSpecial;
            trauma = Juice.TraumaHeavy;
        }
        else if (attacker != null && attacker.CurrentState == FighterState.Kick)
        {
            stopFrames = Juice.StopHeavy;
            trauma = Juice.TraumaMedium;
        }
        else
        {
            stopFrames = Juice.StopLight;
            trauma = Juice.TraumaLight;
        }

        // Blocked hits land softer — still a punchy little freeze, less shake.
        if (blocked && !isKo)
        {
            stopFrames = Mathf.Max(2, stopFrames - 2);
            trauma *= 0.5f;
        }

        Juice.HitStop(stopFrames);
        Juice.AddTrauma(trauma);

        // Comic burst at the impact point (chest-height, between the fighters).
        if (!blocked || isKo)
        {
            Vector2 impact = GlobalPosition + new Vector2(0f, -50f);
            if (attacker != null)
                impact = attacker.GlobalPosition.Lerp(GlobalPosition, 0.62f) + new Vector2(0f, -50f);
            bool heavy = isKo || stopFrames >= Juice.StopHeavy;
            HitSpark.Spawn(GetParent(), impact, heavy);
        }
    }

    private void SpawnLandingDust()
    {
        // Optional polish: a quick cel-shaded dust puff at the feet that grows
        // wide and fades, then frees itself. Self-contained (no extra script).
        var layer = GetParent();
        if (layer == null) return;

        var puff = new Polygon2D
        {
            Position = GlobalPosition + new Vector2(0f, 44f),
            ZIndex = 5,
            Color = new Color(0.86f, 0.82f, 0.7f, 0.85f),
            // Low, wide comic dust cloud (a flattened lumpy shape).
            Polygon = new Vector2[]
            {
                new(-18, 0), new(-12, -7), new(-4, -4), new(2, -9),
                new(10, -5), new(18, -8), new(20, 0), new(12, 4),
                new(0, 5), new(-10, 4)
            }
        };
        layer.AddChild(puff);
        puff.Scale = new Vector2(0.6f, 0.5f);

        var tw = puff.CreateTween();
        tw.SetParallel(true);
        tw.TweenProperty(puff, "scale", new Vector2(1.5f, 0.9f), 0.28).SetEase(Tween.EaseType.Out);
        tw.TweenProperty(puff, "modulate:a", 0f, 0.28).SetEase(Tween.EaseType.In);
        tw.Chain().TweenCallback(Callable.From(puff.QueueFree));
    }

    public void ResetForRound(Vector2 spawnPos)
    {
        CurrentHealth = Stats.MaxHealth;
        Position = spawnPos;
        Velocity = Vector2.Zero;
        _specialCooldownTimer = 0;
        _invincibilityTimer = 0;
        CurrentState = FighterState.Idle; // bypass KO guard in ChangeState
        ChangeState(FighterState.Idle);

        // Reset animation/secondary-motion state to a clean rest pose.
        _bodyScaleSmoothed = Vector2.One;
        _bodyScaleVel = Vector2.Zero;
        _landSquash = 0f;
        _flourish = 0f;
        _armRRotLag = _armLRotLag = _legRRotLag = _legLRotLag = 0f;
        _foreRRotLag = _foreLRotLag = _shinRRotLag = _shinLRotLag = 0f;
        if (_clothSway != null)
            for (int i = 0; i < _clothSway.Length; i++) { _clothSway[i] = 0f; _clothSwayVel[i] = 0f; }

        EmitSignal(SignalName.HealthChanged, CurrentHealth, Stats.MaxHealth);
    }

    private Color TintColor(Color original, float alpha)
    {
        switch (CurrentState)
        {
            case FighterState.Hurt:
            {
                float p = Mathf.Clamp(_stateTimer / HurtDuration, 0f, 1f);
                float t = 1f - p;
                return new Color(
                    Mathf.Lerp(original.R, 1f, 0.6f * t),
                    Mathf.Lerp(original.G, 0.2f, 0.6f * t),
                    Mathf.Lerp(original.B, 0.2f, 0.6f * t),
                    alpha);
            }
            case FighterState.Block:
                return new Color(
                    original.R * 0.85f,
                    original.G * 0.85f,
                    Mathf.Min(original.B + 0.15f, 1f),
                    alpha);
            case FighterState.KO:
            {
                float gray = original.R * 0.3f + original.G * 0.59f + original.B * 0.11f;
                return new Color(gray, gray, gray, 0.6f);
            }
            case FighterState.Special:
            {
                float pulse = 0.5f + 0.5f * Mathf.Sin(_stateTimer * 25f);
                float brighten = 0.2f * pulse;
                return new Color(
                    Mathf.Min(original.R + brighten, 1f),
                    Mathf.Min(original.G + brighten, 1f),
                    Mathf.Min(original.B + brighten, 1f),
                    alpha);
            }
            default:
                return new Color(original.R, original.G, original.B, alpha);
        }
    }

    // Smoothstep helper (3t^2 - 2t^3) for non-linear anticipation/follow-through.
    private static float SmoothStep(float t)
    {
        t = Mathf.Clamp(t, 0f, 1f);
        return t * t * (3f - 2f * t);
    }

    private void UpdateVisuals()
    {
        if (BodyPolygon == null) return;

        float alpha = 1f;
        if (_invincibilityTimer > 0)
            alpha = 0.5f + 0.5f * Mathf.Sin(_invincibilityTimer * 20f);

        float facing = FacingRight ? 1f : -1f;
        float dir = facing;

        // Target body squash/stretch (1,1 = neutral), rotation, and offset.
        float tgtSx = 1f;
        float tgtSy = 1f;
        float rotation = 0f;
        Vector2 bodyOffset = _bodyBasePosition;

        bool showPunch = false;
        bool showKick = false;
        bool springScale = true; // most states ease the scale via the spring

        switch (CurrentState)
        {
            case FighterState.Idle:
            {
                // Breathing: gentle vertical bob + a soft anti-phase squash so
                // the torso "settles" with the breath. Subtle weight shift via
                // a slow lean, plus an occasional micro-flourish.
                float breath = Mathf.Sin(_animTime * 2.5f);
                bodyOffset.Y += breath * 1.6f;
                tgtSy = 1f - breath * 0.025f;
                tgtSx = 1f + breath * 0.02f;
                float shift = Mathf.Sin(_animTime * 1.1f) * 0.6f;
                bodyOffset.X += shift;
                rotation = Mathf.Sin(_animTime * 1.1f) * 0.012f;
                if (_flourish > 0f)
                {
                    float f = SmoothStep(_flourish);
                    bodyOffset.Y -= f * 2.5f;
                    rotation += dir * f * 0.04f;
                }
                break;
            }
            case FighterState.WalkForward:
            case FighterState.WalkBackward:
            {
                // Contact/passing bob: torso bobs twice per stride and leans
                // slightly into the travel direction.
                float bob = Mathf.Abs(Mathf.Sin(_animTime * 8f));
                bodyOffset.Y += -bob * 2.2f;
                bool forward = CurrentState == FighterState.WalkForward;
                float lean = forward ? 1f : -1f;
                rotation = dir * lean * 0.05f;
                tgtSy = 1f - bob * 0.03f;
                tgtSx = 1f + bob * 0.02f;
                break;
            }
            case FighterState.Punch:
            {
                float p = Mathf.Clamp(_stateTimer / PunchDuration, 0f, 1f);
                springScale = false;
                if (p < 0.4f)
                {
                    // Anticipation: coil back slightly (thin + lean away).
                    float t = SmoothStep(p / 0.4f);
                    tgtSx = 1f - 0.05f * t;
                    tgtSy = 1f + 0.04f * t;
                    rotation = -dir * 0.06f * t;
                }
                else if (p < 0.7f)
                {
                    // Strike: stretch toward the hit.
                    tgtSx = 1.16f;
                    tgtSy = 0.92f;
                    rotation = dir * 0.05f;
                    showPunch = true;
                }
                else
                {
                    // Follow-through overshoot then settle.
                    float t = SmoothStep((p - 0.7f) / 0.3f);
                    tgtSx = Mathf.Lerp(1.16f, 1f, t);
                    tgtSy = Mathf.Lerp(0.92f, 1f, t);
                    rotation = dir * 0.05f * (1f - t);
                }
                break;
            }
            case FighterState.Kick:
            {
                float p = Mathf.Clamp(_stateTimer / KickDuration, 0f, 1f);
                springScale = false;
                if (p < 0.4f)
                {
                    float t = SmoothStep(p / 0.4f);
                    rotation = -dir * 0.16f * t;
                    bodyOffset.Y = _bodyBasePosition.Y - 5f * t;
                    tgtSy = 1f + 0.05f * t;
                    tgtSx = 1f - 0.04f * t;
                }
                else if (p < 0.7f)
                {
                    float t = SmoothStep((p - 0.4f) / 0.3f);
                    rotation = dir * 0.22f * t;
                    bodyOffset.Y = _bodyBasePosition.Y - 5f * (1f - t);
                    tgtSx = 1.12f;
                    tgtSy = 0.94f;
                    showKick = true;
                }
                else
                {
                    float t = SmoothStep((p - 0.7f) / 0.3f);
                    rotation = dir * 0.22f * (1f - t);
                    tgtSx = Mathf.Lerp(1.12f, 1f, t);
                    tgtSy = Mathf.Lerp(0.94f, 1f, t);
                }
                break;
            }
            case FighterState.Block:
            {
                tgtSx = 0.9f;
                tgtSy = 0.95f;
                rotation = -dir * 0.04f;
                break;
            }
            case FighterState.Hurt:
            {
                float p = Mathf.Clamp(_stateTimer / HurtDuration, 0f, 1f);
                float decay = 1f - p;
                float shake = Mathf.Sin(_stateTimer * 40f) * 4f * decay;
                bodyOffset.X = _bodyBasePosition.X + shake;
                rotation = -dir * 0.14f * decay;
                // Impact squash that recovers via spring.
                tgtSx = 1f + 0.12f * decay;
                tgtSy = 1f - 0.1f * decay;
                springScale = false;
                break;
            }
            case FighterState.Special:
            {
                float scalePulse = 0.06f * Mathf.Sin(_stateTimer * 20f);
                tgtSx = 1.05f + scalePulse;
                tgtSy = 1.05f + scalePulse;
                springScale = false;
                break;
            }
            case FighterState.Crouch:
            {
                tgtSy = 0.82f;
                tgtSx = 1.1f;
                bodyOffset.Y = _bodyBasePosition.Y + 10f;
                break;
            }
            case FighterState.Jump:
            {
                // Takeoff stretches tall + thin; airborne keeps a light stretch.
                bool rising = Velocity.Y < 0;
                tgtSx = rising ? 0.86f : 0.94f;
                tgtSy = rising ? 1.16f : 1.06f;
                springScale = false;
                break;
            }
            case FighterState.KO:
            {
                // Campy topple: fall over with a rotation and a wide ground squash.
                float t = SmoothStep(Mathf.Clamp(_stateTimer / 0.55f, 0f, 1f));
                rotation = dir * (0.05f + t * (Mathf.Pi * 0.5f - 0.05f));
                bodyOffset.Y = _bodyBasePosition.Y + t * 18f;
                tgtSx = 1f + 0.18f * t;
                tgtSy = 1f - 0.16f * t;
                springScale = false;
                break;
            }
        }

        // Landing squash impulse (wide + low), recovers via the spring.
        if (_landSquash > 0f && CurrentState != FighterState.KO)
        {
            tgtSx += 0.16f * _landSquash;
            tgtSy -= 0.14f * _landSquash;
            bodyOffset.Y += 4f * _landSquash;
            springScale = false;
        }

        // Clamp campy-but-tasteful (±18%).
        tgtSx = Mathf.Clamp(tgtSx, 0.82f, 1.18f);
        tgtSy = Mathf.Clamp(tgtSy, 0.82f, 1.18f);

        // Critically-damped spring on the body scale so transitions never snap
        // and impacts overshoot before settling (squash & stretch follow-through).
        Vector2 target = new(tgtSx, tgtSy);
        if (springScale)
            SpringScale(target);
        else
        {
            // Drive directly but keep velocity continuous for the next release.
            _bodyScaleVel = (target - _bodyScaleSmoothed) / Mathf.Max(0.016f, 1f / 60f);
            _bodyScaleSmoothed = target;
        }

        float sx = _bodyScaleSmoothed.X * facing;
        float sy = _bodyScaleSmoothed.Y;

        BodyPolygon.Scale = new Vector2(sx, sy);
        BodyPolygon.Rotation = rotation;
        BodyPolygon.Position = bodyOffset;
        BodyPolygon.Color = TintColor(_originalColor, alpha);

        if (_punchEffect != null) _punchEffect.Visible = showPunch;
        if (_kickEffect != null) _kickEffect.Visible = showKick;

        Vector2 bodyDelta = bodyOffset - _bodyBasePosition;

        // Head follows the torso offset + rotation (but not its squash scale).
        if (_head != null)
        {
            _head.Position = _headBase + bodyDelta;
            _head.Rotation = _headBaseRot + rotation;
            _head.Scale = new Vector2(facing, 1f);
            _head.Color = TintColor(_headOrigColor, alpha);
        }
        // Hair position + color here; its rotation (base + body + sway) is set
        // in the cloth pass so the two systems don't fight over Rotation.
        if (_hair != null)
        {
            _hair.Position = _hairBase + bodyDelta;
            _hair.Scale = new Vector2(facing, 1f);
            _hair.Color = TintColor(_hairOrigColor, alpha);
        }

        ApplyClothSway(rotation);
        UpdateFaceAnimations();
        UpdateLimbs(alpha, bodyDelta);
    }

    // Spring the smoothed body scale toward a target (semi-implicit, stable).
    private void SpringScale(Vector2 target)
    {
        const float stiffness = 220f;
        const float damping = 22f;
        float dt = 1f / 60f;
        Vector2 force = (target - _bodyScaleSmoothed) * stiffness - _bodyScaleVel * damping;
        _bodyScaleVel += force * dt;
        _bodyScaleSmoothed += _bodyScaleVel * dt;
    }

    private void UpdateLimbs(float alpha, Vector2 bodyDelta)
    {
        if (_armR == null) return;

        float dir = FacingRight ? 1f : -1f;

        // Mirrored joint positions + body vertical offset (pivots = node origin).
        _armR.Position = new Vector2(dir * Mathf.Abs(_armRBase.X), _armRBase.Y + bodyDelta.Y);
        _armL.Position = new Vector2(-dir * Mathf.Abs(_armLBase.X), _armLBase.Y + bodyDelta.Y);
        _legR.Position = new Vector2(dir * Mathf.Abs(_legRBase.X), _legRBase.Y + bodyDelta.Y);
        _legL.Position = new Vector2(-dir * Mathf.Abs(_legLBase.X), _legLBase.Y + bodyDelta.Y);

        // Target rotations (rest pose) + per-segment forearm/shin bend targets.
        float armRRot = -dir * 0.15f, armLRot = dir * 0.15f;
        float legRRot = 0f, legLRot = 0f;
        float foreRRot = -dir * 0.25f, foreLRot = dir * 0.25f; // soft resting elbow bend
        float shinRRot = 0.15f, shinLRot = 0.15f;               // soft resting knee bend
        float limbLag = 0.5f; // default lerp toward target (≈1-2 frame trail)

        switch (CurrentState)
        {
            case FighterState.WalkForward:
            case FighterState.WalkBackward:
            {
                float swing = Mathf.Sin(_animTime * 8f);
                armRRot = -dir * (0.15f + swing * 0.35f);
                armLRot = dir * (0.15f - swing * 0.35f);
                legRRot = -dir * swing * 0.38f;
                legLRot = dir * swing * 0.38f;
                // Counter-swing the forearms/shins so the stride reads as a real
                // contact/passing gait (elbows/knees bend on the back-swing).
                foreRRot = -dir * (0.3f + Mathf.Max(0f, swing) * 0.5f);
                foreLRot = dir * (0.3f + Mathf.Max(0f, -swing) * 0.5f);
                shinRRot = 0.2f + Mathf.Max(0f, -swing) * 0.7f;
                shinLRot = 0.2f + Mathf.Max(0f, swing) * 0.7f;
                limbLag = 0.55f;
                break;
            }
            case FighterState.Jump:
            {
                armRRot = -dir * 0.6f; armLRot = dir * 0.6f;
                legRRot = dir * 0.25f; legLRot = -dir * 0.15f;
                foreRRot = -dir * 0.7f; foreLRot = dir * 0.7f;
                shinRRot = 0.9f; shinLRot = 0.5f; // tuck knees
                limbLag = 0.6f;
                break;
            }
            case FighterState.Crouch:
            {
                armRRot = -dir * 0.3f; armLRot = dir * 0.3f;
                legRRot = -dir * 0.5f; legLRot = dir * 0.5f;
                foreRRot = -dir * 0.6f; foreLRot = dir * 0.6f;
                shinRRot = 1.1f; shinLRot = 1.1f; // deep knee bend
                limbLag = 0.6f;
                break;
            }
            case FighterState.Punch:
            {
                float p = Mathf.Clamp(_stateTimer / PunchDuration, 0f, 1f);
                if (p < 0.4f)
                {
                    float t = SmoothStep(p / 0.4f);
                    armRRot = Mathf.Lerp(-dir * 0.15f, dir * 0.5f, t); // wind back
                    foreRRot = Mathf.Lerp(-dir * 0.25f, -dir * 0.9f, t); // cock the elbow
                    limbLag = 0.45f;
                }
                else if (p < 0.7f)
                {
                    armRRot = -dir * 1.4f;
                    armLRot = dir * 0.3f;
                    foreRRot = -dir * 0.05f; // snap the forearm straight at impact
                    limbLag = 0.8f;           // fast on the strike
                }
                else
                {
                    float t = SmoothStep((p - 0.7f) / 0.3f);
                    armRRot = Mathf.Lerp(-dir * 1.4f, -dir * 0.15f, t);
                    foreRRot = Mathf.Lerp(-dir * 0.05f, -dir * 0.25f, t);
                    limbLag = 0.4f; // overshoot/settle reads via the trail
                }
                break;
            }
            case FighterState.Kick:
            {
                float p = Mathf.Clamp(_stateTimer / KickDuration, 0f, 1f);
                armRRot = -dir * 0.4f; armLRot = dir * 0.4f;
                if (p < 0.4f)
                {
                    float t = SmoothStep(p / 0.4f);
                    legRRot = Mathf.Lerp(0f, dir * 0.4f, t); // chamber
                    shinRRot = Mathf.Lerp(0.15f, 1.3f, t);    // bend knee back
                    limbLag = 0.45f;
                }
                else if (p < 0.7f)
                {
                    legRRot = -dir * 1.3f;
                    shinRRot = 0.05f; // snap leg straight
                    limbLag = 0.8f;
                }
                else
                {
                    float t = SmoothStep((p - 0.7f) / 0.3f);
                    legRRot = Mathf.Lerp(-dir * 1.3f, 0f, t);
                    shinRRot = Mathf.Lerp(0.05f, 0.15f, t);
                    limbLag = 0.4f;
                }
                break;
            }
            case FighterState.Block:
            {
                armRRot = -dir * 0.9f; armLRot = -dir * 0.7f;
                foreRRot = -dir * 1.1f; foreLRot = -dir * 1.0f; // guard up
                shinRRot = 0.35f; shinLRot = 0.35f;
                limbLag = 0.6f;
                break;
            }
            case FighterState.Hurt:
            {
                float p = Mathf.Clamp(_stateTimer / HurtDuration, 0f, 1f);
                float decay = 1f - p;
                armRRot = dir * 0.6f * decay; armLRot = dir * 0.8f * decay;
                legRRot = -dir * 0.2f * decay; legLRot = dir * 0.3f * decay;
                foreRRot = dir * 0.5f * decay; foreLRot = dir * 0.6f * decay;
                limbLag = 0.65f;
                break;
            }
            case FighterState.Special:
            {
                float pulse = Mathf.Sin(_stateTimer * 15f) * 0.15f;
                armRRot = -dir * (1.0f + pulse); armLRot = dir * (0.8f + pulse);
                foreRRot = -dir * (0.6f + pulse); foreLRot = dir * (0.5f + pulse);
                limbLag = 0.55f;
                break;
            }
            case FighterState.KO:
            {
                // Limbs splay out as she topples.
                armRRot = dir * 0.9f; armLRot = dir * 1.1f;
                legRRot = -dir * 0.5f; legLRot = dir * 0.4f;
                foreRRot = dir * 0.4f; foreLRot = dir * 0.5f;
                shinRRot = 0.4f; shinLRot = 0.3f;
                limbLag = 0.4f;
                break;
            }
        }

        // Apply the upper-limb rotations with a little lag (follow-through trail).
        _armRRotLag = Mathf.LerpAngle(_armRRotLag, armRRot, limbLag);
        _armLRotLag = Mathf.LerpAngle(_armLRotLag, armLRot, limbLag);
        _legRRotLag = Mathf.LerpAngle(_legRRotLag, legRRot, limbLag);
        _legLRotLag = Mathf.LerpAngle(_legLRotLag, legLRot, limbLag);
        _armR.Rotation = _armRRotLag;
        _armL.Rotation = _armLRotLag;
        _legR.Rotation = _legRRotLag;
        _legL.Rotation = _legLRotLag;

        // Articulated second segments — drive elbow/knee bend if present, with
        // a slightly tighter lag so they crack like a whip on the strike.
        float segLag = Mathf.Min(1f, limbLag + 0.15f);
        if (_forearmR != null)
        {
            _foreRRotLag = Mathf.LerpAngle(_foreRRotLag, foreRRot, segLag);
            _forearmR.Rotation = _forearmRBaseRot + _foreRRotLag;
        }
        if (_forearmL != null)
        {
            _foreLRotLag = Mathf.LerpAngle(_foreLRotLag, foreLRot, segLag);
            _forearmL.Rotation = _forearmLBaseRot + _foreLRotLag;
        }
        if (_shinR != null)
        {
            _shinRRotLag = Mathf.LerpAngle(_shinRRotLag, shinRRot, segLag);
            _shinR.Rotation = _shinRBaseRot + _shinRRotLag;
        }
        if (_shinL != null)
        {
            _shinLRotLag = Mathf.LerpAngle(_shinLRotLag, shinLRot, segLag);
            _shinL.Rotation = _shinLBaseRot + _shinLRotLag;
        }

        // Front limbs use their own original color, back limbs 30% darker.
        Color armRC = TintColor(_armROrigColor, alpha);
        Color armLC = TintColor(_armLOrigColor, alpha);
        Color legRC = TintColor(_legROrigColor, alpha);
        Color legLC = TintColor(_legLOrigColor, alpha);
        _armR.Color = armRC;
        _legR.Color = legRC;
        _armL.Color = new Color(armLC.R * 0.7f, armLC.G * 0.7f, armLC.B * 0.7f, armLC.A);
        _legL.Color = new Color(legLC.R * 0.7f, legLC.G * 0.7f, legLC.B * 0.7f, legLC.A);
    }

    // Velocity-lagged cloth/hair sway with spring overshoot. Called from the
    // anim clock (_Process) so cloth keeps drifting while physics is frozen.
    private void UpdateSecondaryMotion(float dt)
    {
        if (_clothNodes == null || _clothNodes.Length == 0) return;

        // Drive the sway target from horizontal velocity (drag) + a tiny idle
        // float. Cloth lags BEHIND motion, so it leans opposite to travel.
        float vx = Velocity.X;
        float idleFloat = Mathf.Sin(_animTime * 1.8f) * 0.025f;
        float dragTarget = Mathf.Clamp(-vx / 600f, -0.45f, 0.45f) + idleFloat;
        // Extra flutter when airborne / hurt for camp.
        if (CurrentState == FighterState.Jump)
            dragTarget += -Mathf.Sign(Velocity.Y) * 0.12f;

        const float stiffness = 90f;
        const float damping = 9f;

        for (int i = 0; i < _clothNodes.Length; i++)
        {
            // Stagger so multiple cloth pieces don't move in lockstep.
            float target = dragTarget + Mathf.Sin(_animTime * 2.3f + i) * 0.02f;
            float force = (target - _clothSway[i]) * stiffness - _clothSwayVel[i] * damping;
            _clothSwayVel[i] += force * dt;
            _clothSway[i] += _clothSwayVel[i] * dt;
        }
    }

    private void ApplyClothSway(float bodyRotation)
    {
        if (_clothNodes == null) return;
        for (int i = 0; i < _clothNodes.Length; i++)
        {
            var node = _clothNodes[i];
            if (node == null) continue;
            // Sway swings with facing so it always trails behind travel.
            float sway = _clothSway[i] * (FacingRight ? 1f : -1f);
            node.Rotation = _clothBaseRot[i] + bodyRotation + sway;
        }
    }

    private void UpdateFaceAnimations()
    {
        // Eye blinking — squash eye whites (iris/pupil children scale with them)
        if (_eyeWhiteL != null)
        {
            bool blinking = _blinkTimer < BlinkDuration && CurrentState != FighterState.KO;
            float eyeScaleY = blinking ? 0.15f : 1f;
            _eyeWhiteL.Scale = new Vector2(1, eyeScaleY);
            _eyeWhiteR.Scale = new Vector2(1, eyeScaleY);
        }

        // Pupil tracking — shift toward opponent
        if (_pupilL != null && Opponent != null)
        {
            float dirToOpponent = Mathf.Sign(Opponent.Position.X - Position.X);
            float flip = FacingRight ? 1f : -1f;
            float trackX = dirToOpponent * flip * 1.5f;
            _pupilL.Position = _pupilLBase + new Vector2(trackX, 0);
            _pupilR.Position = _pupilRBase + new Vector2(trackX, 0);
        }
    }

    public float GetSpecialCooldownPercent()
    {
        if (Stats == null || Stats.SpecialCooldown <= 0) return 1f;
        return 1f - Mathf.Clamp(_specialCooldownTimer / Stats.SpecialCooldown, 0, 1);
    }
}
