using Godot;

namespace StreepFighter;

public partial class Projectile : Area2D
{
    public int Damage { get; set; } = 100;
    public int Direction { get; set; } = 1; // 1=right, -1=left
    public Fighter OwnerFighter { get; set; }

    private const float Speed = 450f;
    private const float Lifetime = 2f;
    private float _timer;

    public void SetPlayerIndex(int playerIndex)
    {
        // Projectile layer: 16 (Projectiles)
        // Mask: opponent hurtbox layer (P1=1, P2=2)
        CollisionLayer = 16;
        CollisionMask = playerIndex == 0 ? 2u : 1u;
    }

    public override void _Ready()
    {
        AreaEntered += OnAreaEntered;
    }

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        _timer += dt;

        Position += new Vector2(Direction * Speed * dt, 0);

        if (_timer >= Lifetime || Position.X < 0 || Position.X > 1280)
            QueueFree();
    }

    private void OnAreaEntered(Area2D area)
    {
        if (area.GetParent() is Fighter target && target != OwnerFighter)
        {
            target.TakeDamage(Damage, OwnerFighter);
            QueueFree();
        }
    }
}
