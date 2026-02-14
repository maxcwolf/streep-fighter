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

    // Node references
    private Color _originalColor;
    protected Polygon2D BodyPolygon;
    private Polygon2D _punchEffect;
    private Polygon2D _kickEffect;
    private Vector2 _bodyBasePosition;
    private Polygon2D _armR, _armL, _legR, _legL;
    private Vector2 _armRBase, _armLBase, _legRBase, _legLBase;
    private Polygon2D _head, _hair;
    private Vector2 _headBase, _hairBase;
    private Color _headOrigColor, _hairOrigColor;
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

        _head = GetNodeOrNull<Polygon2D>("Head");
        _hair = GetNodeOrNull<Polygon2D>("Hair");
        if (_head != null) { _headBase = _head.Position; _headOrigColor = _head.Color; }
        if (_hair != null) { _hairBase = _hair.Position; _hairOrigColor = _hair.Color; }

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
        float dt = (float)delta;
        _animTime += dt;

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

            // Land from jump
            if (CurrentState == FighterState.Jump)
            {
                AudioManager.Instance?.PlaySFX("land");
                ChangeState(FighterState.Idle);
            }
        }

        // Clamp X
        MoveAndSlide();
        var clampedPos = Position;
        clampedPos.X = Mathf.Clamp(clampedPos.X, LeftWall, RightWall);
        Position = clampedPos;

        // Blink timer
        _blinkTimer -= dt;
        if (_blinkTimer <= 0)
            _blinkTimer = BlinkInterval + (float)GD.RandRange(-0.5, 1.0);

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

        if (CurrentHealth <= 0)
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

    public void ResetForRound(Vector2 spawnPos)
    {
        CurrentHealth = Stats.MaxHealth;
        Position = spawnPos;
        Velocity = Vector2.Zero;
        _specialCooldownTimer = 0;
        _invincibilityTimer = 0;
        CurrentState = FighterState.Idle; // bypass KO guard in ChangeState
        ChangeState(FighterState.Idle);
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

    private void UpdateVisuals()
    {
        float alpha = 1f;
        if (_invincibilityTimer > 0)
            alpha = 0.5f + 0.5f * Mathf.Sin(_invincibilityTimer * 20f);

        float scaleX = FacingRight ? 1 : -1;
        float scaleY = 1f;
        float rotation = 0f;
        Vector2 bodyOffset = _bodyBasePosition;

        bool showPunch = false;
        bool showKick = false;

        float progress = _stateTimer / Mathf.Max(_stateTimer + 0.001f, 1f);

        switch (CurrentState)
        {
            case FighterState.Punch:
            {
                float dur = PunchDuration;
                progress = Mathf.Clamp(_stateTimer / dur, 0f, 1f);
                if (progress < 0.4f)
                {
                    float t = progress / 0.4f;
                    scaleX *= 1f + 0.15f * t;
                }
                else if (progress < 0.7f)
                {
                    scaleX *= 1.15f;
                    showPunch = true;
                }
                else
                {
                    float t = (progress - 0.7f) / 0.3f;
                    scaleX *= 1.15f - 0.15f * t;
                }
                break;
            }
            case FighterState.Kick:
            {
                float dur = KickDuration;
                progress = Mathf.Clamp(_stateTimer / dur, 0f, 1f);
                float dir = FacingRight ? 1f : -1f;
                if (progress < 0.4f)
                {
                    float t = progress / 0.4f;
                    rotation = -dir * 0.15f * t;
                    bodyOffset.Y = _bodyBasePosition.Y - 4f * t;
                }
                else if (progress < 0.7f)
                {
                    float t = (progress - 0.4f) / 0.3f;
                    rotation = dir * 0.2f * t;
                    showKick = true;
                }
                else
                {
                    float t = (progress - 0.7f) / 0.3f;
                    rotation = dir * 0.2f * (1f - t);
                }
                break;
            }
            case FighterState.Block:
            {
                scaleX *= 0.92f;
                scaleY = 0.95f;
                break;
            }
            case FighterState.Hurt:
            {
                progress = Mathf.Clamp(_stateTimer / HurtDuration, 0f, 1f);
                float decay = 1f - progress;
                float shake = Mathf.Sin(_stateTimer * 40f) * 4f * decay;
                bodyOffset.X = _bodyBasePosition.X + shake;
                float dir = FacingRight ? 1f : -1f;
                rotation = -dir * 0.12f * decay;
                break;
            }
            case FighterState.Special:
            {
                progress = Mathf.Clamp(_stateTimer / SpecialDuration, 0f, 1f);
                float scalePulse = 1f + 0.05f * Mathf.Sin(_stateTimer * 20f);
                scaleX *= scalePulse;
                scaleY = scalePulse;
                break;
            }
            case FighterState.Crouch:
            {
                scaleY = 0.8f;
                bodyOffset.Y = _bodyBasePosition.Y + 10f;
                break;
            }
            case FighterState.KO:
            {
                float dir = FacingRight ? 1f : -1f;
                rotation = dir * 0.4f;
                break;
            }
        }

        // Idle breathing bob
        if (CurrentState == FighterState.Idle)
            bodyOffset.Y += Mathf.Sin(_animTime * 2.5f) * 1.5f;

        BodyPolygon.Scale = new Vector2(scaleX, scaleY);
        BodyPolygon.Rotation = rotation;
        BodyPolygon.Position = bodyOffset;
        BodyPolygon.Color = TintColor(_originalColor, alpha);

        if (_punchEffect != null)
            _punchEffect.Visible = showPunch;
        if (_kickEffect != null)
            _kickEffect.Visible = showKick;

        // Head and hair follow body offset and rotation but not scale
        if (_head != null)
        {
            Vector2 bodyDelta = bodyOffset - _bodyBasePosition;
            _head.Position = _headBase + bodyDelta;
            _head.Rotation = rotation;
            _head.Scale = new Vector2(FacingRight ? 1 : -1, 1);
            _head.Color = TintColor(_headOrigColor, alpha);
        }
        if (_hair != null)
        {
            Vector2 bodyDelta = bodyOffset - _bodyBasePosition;
            _hair.Position = _hairBase + bodyDelta;
            _hair.Rotation = rotation;
            _hair.Scale = new Vector2(FacingRight ? 1 : -1, 1);
            _hair.Color = TintColor(_hairOrigColor, alpha);
        }

        UpdateFaceAnimations();

        Vector2 limbDelta = bodyOffset - _bodyBasePosition;
        UpdateLimbs(alpha, limbDelta);
    }

    private void UpdateLimbs(float alpha, Vector2 bodyDelta)
    {
        if (_armR == null) return;

        float dir = FacingRight ? 1f : -1f;

        // Compute mirrored base positions + body offset
        Vector2 armRPos = new(dir * Mathf.Abs(_armRBase.X), _armRBase.Y + bodyDelta.Y);
        Vector2 armLPos = new(-dir * Mathf.Abs(_armLBase.X), _armLBase.Y + bodyDelta.Y);
        Vector2 legRPos = new(dir * Mathf.Abs(_legRBase.X), _legRBase.Y + bodyDelta.Y);
        Vector2 legLPos = new(-dir * Mathf.Abs(_legLBase.X), _legLBase.Y + bodyDelta.Y);

        // Default rest pose
        float armRRot = -dir * 0.15f;
        float armLRot = dir * 0.15f;
        float legRRot = 0f;
        float legLRot = 0f;

        switch (CurrentState)
        {
            case FighterState.WalkForward:
            case FighterState.WalkBackward:
            {
                float swing = Mathf.Sin(_animTime * 8f);
                armRRot = -dir * (0.15f + swing * 0.3f);
                armLRot = dir * (0.15f - swing * 0.3f);
                legRRot = -dir * swing * 0.35f;
                legLRot = dir * swing * 0.35f;
                break;
            }
            case FighterState.Jump:
            {
                armRRot = -dir * 0.6f;
                armLRot = dir * 0.6f;
                legRRot = dir * 0.25f;
                legLRot = -dir * 0.15f;
                break;
            }
            case FighterState.Crouch:
            {
                armRRot = -dir * 0.3f;
                armLRot = dir * 0.3f;
                legRRot = -dir * 0.5f;
                legLRot = dir * 0.5f;
                break;
            }
            case FighterState.Punch:
            {
                float p = Mathf.Clamp(_stateTimer / PunchDuration, 0f, 1f);
                if (p < 0.4f)
                {
                    float t = p / 0.4f;
                    armRRot = Mathf.Lerp(-dir * 0.15f, dir * 0.5f, t);
                }
                else if (p < 0.7f)
                {
                    armRRot = -dir * 1.4f;
                    armLRot = dir * 0.3f;
                }
                else
                {
                    float t = (p - 0.7f) / 0.3f;
                    armRRot = Mathf.Lerp(-dir * 1.4f, -dir * 0.15f, t);
                }
                break;
            }
            case FighterState.Kick:
            {
                float p = Mathf.Clamp(_stateTimer / KickDuration, 0f, 1f);
                armRRot = -dir * 0.4f;
                armLRot = dir * 0.4f;
                if (p < 0.4f)
                {
                    float t = p / 0.4f;
                    legRRot = Mathf.Lerp(0f, dir * 0.4f, t);
                }
                else if (p < 0.7f)
                {
                    legRRot = -dir * 1.3f;
                }
                else
                {
                    float t = (p - 0.7f) / 0.3f;
                    legRRot = Mathf.Lerp(-dir * 1.3f, 0f, t);
                }
                break;
            }
            case FighterState.Block:
            {
                armRRot = -dir * 0.9f;
                armLRot = -dir * 0.7f;
                break;
            }
            case FighterState.Hurt:
            {
                float p = Mathf.Clamp(_stateTimer / HurtDuration, 0f, 1f);
                float decay = 1f - p;
                armRRot = dir * 0.6f * decay;
                armLRot = dir * 0.8f * decay;
                legRRot = -dir * 0.2f * decay;
                legLRot = dir * 0.3f * decay;
                break;
            }
            case FighterState.Special:
            {
                float pulse = Mathf.Sin(_stateTimer * 15f) * 0.15f;
                armRRot = -dir * (1.0f + pulse);
                armLRot = dir * (0.8f + pulse);
                break;
            }
            case FighterState.KO:
            {
                armRRot = dir * 0.5f;
                armLRot = dir * 0.7f;
                legRRot = -dir * 0.3f;
                legLRot = dir * 0.2f;
                break;
            }
        }

        _armR.Position = armRPos;
        _armL.Position = armLPos;
        _legR.Position = legRPos;
        _legL.Position = legLPos;

        _armR.Rotation = armRRot;
        _armL.Rotation = armLRot;
        _legR.Rotation = legRRot;
        _legL.Rotation = legLRot;

        // Front limbs use their own original color, back limbs 30% darker
        Color armRC = TintColor(_armROrigColor, alpha);
        Color armLC = TintColor(_armLOrigColor, alpha);
        Color legRC = TintColor(_legROrigColor, alpha);
        Color legLC = TintColor(_legLOrigColor, alpha);
        _armR.Color = armRC;
        _legR.Color = legRC;
        _armL.Color = new Color(armLC.R * 0.7f, armLC.G * 0.7f, armLC.B * 0.7f, armLC.A);
        _legL.Color = new Color(legLC.R * 0.7f, legLC.G * 0.7f, legLC.B * 0.7f, legLC.A);
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
