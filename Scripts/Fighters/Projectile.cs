using Godot;

namespace StreepFighter;

/// <summary>
/// A thrown special (stockpot, curse). Moves in pixels per tick, optionally
/// under gravity, and hits by rectangle overlap with the opponent's hurtbox.
/// </summary>
public partial class Projectile : Node2D
{
    public int Damage { get; set; } = 100;
    public Fighter OwnerFighter { get; set; }

    private const int Frames = 4;
    private const int LifetimeTicks = 150;
    private static readonly Vector2 HalfSize = new(7, 7);

    private Vector2 _velocity;
    private float _gravity;
    private int _age;
    private Sprite2D _sprite;

    /// <param name="offset">Start point relative to the thrower's feet (already facing-adjusted in X).</param>
    /// <param name="velocity">Pixels per tick; X is "forward" and gets flipped for a left-facing thrower.</param>
    public static Projectile Spawn(Fighter owner, string sprite, Vector2 offset, Vector2 velocity, float gravity,
                                   int damage, bool spin = false)
    {
        var p = new Projectile
        {
            OwnerFighter = owner,
            Damage = damage,
            Position = owner.Position + offset,
            _velocity = new Vector2(velocity.X * owner.Dir, velocity.Y),
            _gravity = gravity,
            ZIndex = 5,
        };
        var tex = GD.Load<Texture2D>($"res://Assets/Sprites/FX/{sprite}.png");
        p._sprite = new Sprite2D { Texture = tex, Hframes = Frames, FlipH = owner.Dir < 0 };
        p.AddChild(p._sprite);
        owner.LiveProjectiles++;
        owner.GetParent().AddChild(p);
        return p;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (Juice.HitStopFrames > 0) return;

        _age++;
        _velocity.Y += _gravity;
        Position += _velocity;
        _sprite.Frame = _age / 4 % Frames;

        var target = OwnerFighter?.Opponent;
        if (target != null)
        {
            var box = new Rect2(Position - HalfSize, HalfSize * 2);
            var hurt = target.Hurtbox;
            if (hurt.Size.X > 0 && box.Intersects(hurt)
                && target.ReceiveHit(OwnerFighter, Damage, Fighter.ProjectileHit, Position))
            {
                Remove();
                return;
            }
        }

        if (Position.Y >= Fighter.GroundY)
        {
            Fx.Spawn(GetParent(), "dust", new Vector2(Position.X, Fighter.GroundY - 7), 4, 3);
            Remove();
        }
        else if (_age >= LifetimeTicks || Position.X < -20 || Position.X > Fighter.StageRight + 34)
        {
            Remove();
        }
    }

    private void Remove()
    {
        if (OwnerFighter != null && OwnerFighter.LiveProjectiles > 0)
            OwnerFighter.LiveProjectiles--;
        OwnerFighter = null;
        QueueFree();
    }
}
