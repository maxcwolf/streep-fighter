using System;
using System.Collections.Generic;
using Godot;

namespace StreepFighter;

/// <summary>
/// Owns a fight: builds the stage, spawns the fighters and steps the whole
/// simulation once per 60Hz physics tick in a fixed order (input, fighters,
/// body push, camera) so nothing depends on scene-tree ordering.
/// </summary>
public partial class GameManager : Node2D
{
    private const float ScreenW = 384f;
    private const float ScreenH = 216f;
    private const float EdgeMargin = 20f;
    private const float RoundSeconds = 99f;

    private Fighter _p1, _p2;
    private AiController _ai;
    private AiController _demoAi;      // drives player 1 in the CPU-vs-CPU dev mode
    private double _baseTimeScale = 1.0;
    private FightHUD _hud;
    private VictoryScreen _victoryScreen;
    private Camera2D _camera;
    private Sprite2D _far;
    private float _camX = StageData.Width / 2f;

    private float _roundTimer = RoundSeconds;
    private bool _roundActive;
    private bool _matchOver;
    private int _tick;
    private int _slowTicks;
    private readonly List<(int At, Action Do)> _schedule = new();

    private readonly Vector2 _p1Spawn = new(StageData.Width / 2f - 62f, Fighter.GroundY);
    private readonly Vector2 _p2Spawn = new(StageData.Width / 2f + 62f, Fighter.GroundY);

    public override void _Ready()
    {
        BuildStage();
        BuildHud();
        SpawnFighters();
        StartRound();
    }

    public override void _ExitTree()
    {
        Engine.TimeScale = 1.0;
        Juice.Reset();
    }

    private void BuildStage()
    {
        var stage = StageData.GetByIndex(GameState.StageIndex);

        _far = new Sprite2D { Texture = GD.Load<Texture2D>(stage.FarPath), Centered = false, ZIndex = -20 };
        AddChild(_far);
        AddChild(new Sprite2D { Texture = GD.Load<Texture2D>(stage.MainPath), Centered = false, ZIndex = -10 });

        _camera = new CameraShake
        {
            Position = new Vector2(_camX, ScreenH / 2f),
            LimitLeft = 0, LimitTop = 0, LimitRight = (int)StageData.Width, LimitBottom = (int)ScreenH,
        };
        AddChild(_camera);
        _camera.MakeCurrent();
    }

    private void BuildHud()
    {
        var layer = new CanvasLayer { Layer = 10 };
        AddChild(layer);
        _hud = new FightHUD();
        layer.AddChild(_hud);
        _victoryScreen = new VictoryScreen();
        layer.AddChild(_victoryScreen);
        layer.AddChild(new PauseMenu());
    }

    private void SpawnFighters()
    {
        var p1Stats = FighterData.GetByIndex(GameState.P1CharacterIndex);
        var p2Stats = FighterData.GetByIndex(GameState.P2CharacterIndex);

        _p1 = GD.Load<PackedScene>(p1Stats.ScenePath)?.Instantiate() as Fighter;
        _p2 = GD.Load<PackedScene>(p2Stats.ScenePath)?.Instantiate() as Fighter;
        if (_p1 == null || _p2 == null)
        {
            GD.PrintErr($"Failed to load fighter scenes: P1={p1Stats.ScenePath} P2={p2Stats.ScenePath}");
            return;
        }

        _p1.PlayerIndex = 0;
        _p1.Stats = p1Stats;
        _p2.PlayerIndex = 1;
        _p2.Stats = p2Stats;
        _p2.UseAltPalette = p1Stats == p2Stats;
        _p1.Opponent = _p2;
        _p2.Opponent = _p1;

        AddChild(_p1);
        AddChild(_p2);

        // Dev aid for tuning the AI:  godot ... -- --cpu-vs-cpu <p1 level> <p2 level> [speed]
        // Both sides are CPU-driven, results are printed, and the game quits after the match.
        string[] args = OS.GetCmdlineUserArgs();
        int demo = System.Array.IndexOf(args, "--cpu-vs-cpu");
        if (demo >= 0 && args.Length > demo + 2)
        {
            _demoAi = new AiController(_p1, args[demo + 1].ToInt());
            _ai = new AiController(_p2, args[demo + 2].ToInt());
            if (args.Length > demo + 3) _baseTimeScale = Mathf.Max(1, args[demo + 3].ToInt());
        }
        else if (GameState.Mode == GameMode.VsCPU)
        {
            _ai = new AiController(_p2);
        }

        _p1.Died += () => OnFighterDied();
        _p2.Died += () => OnFighterDied();

        _hud.SetupFighters(_p1, _p2);
    }

    // ------------------------------------------------------------- rounds
    private void StartRound()
    {
        if (_p1 == null || _p2 == null) return;

        _schedule.Clear();
        _roundTimer = RoundSeconds;
        _roundActive = false;
        _matchOver = false;
        Engine.TimeScale = _baseTimeScale;
        _slowTicks = 0;
        Juice.Reset();

        _p1.ResetForRound(_p1Spawn, true);
        _p2.ResetForRound(_p2Spawn, false);
        _p1.Locked = _p2.Locked = true;
        _camX = StageData.Width / 2f;
        _hud.UpdateTimer((int)RoundSeconds);
        _hud.UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);

        int roundNum = GameState.P1RoundWins + GameState.P2RoundWins + 1;
        bool final = GameState.P1RoundWins == GameState.RoundsToWin - 1
                     && GameState.P2RoundWins == GameState.RoundsToWin - 1;
        _hud.ShowStageName(StageData.GetByIndex(GameState.StageIndex).DisplayLabel, 150);

        After(20, () =>
        {
            _hud.Announce(final ? "final" : $"round{Mathf.Clamp(roundNum, 1, 3)}", 80);
            AudioManager.Instance?.PlaySFX("round");
        });
        After(110, () =>
        {
            _hud.Announce("fight", 46);
            AudioManager.Instance?.PlaySFX("fight");
        });
        After(150, () =>
        {
            _p1.Locked = _p2.Locked = false;
            _roundActive = true;
        });
    }

    private void After(int ticks, Action action) => _schedule.Add((_tick + ticks, action));

    public override void _PhysicsProcess(double delta)
    {
        if (_p1 == null || _p2 == null) return;

        _tick++;
        for (int i = _schedule.Count - 1; i >= 0; i--)
        {
            if (_schedule[i].At > _tick) continue;
            var act = _schedule[i].Do;
            _schedule.RemoveAt(i);
            act();
        }

        if (_slowTicks > 0 && --_slowTicks == 0)
            Engine.TimeScale = _baseTimeScale;

        // Hit-stop: the world holds still, but buttons pressed now are buffered.
        if (Juice.HitStopFrames > 0)
        {
            Juice.HitStopFrames--;
            _p1.PollInput();
            _p2.PollInput();
            return;
        }

        _demoAi?.Tick();
        _ai?.Tick();
        _p1.PollInput();
        _p2.PollInput();

        // Alternate who resolves first so neither side wins every trade.
        if ((_tick & 1) == 0) { _p1.Tick(); _p2.Tick(); }
        else { _p2.Tick(); _p1.Tick(); }

        ResolveBodies();
        UpdateCamera();

        if (!_roundActive || _matchOver) return;

        _roundTimer -= 1f / 60f;
        _hud.UpdateTimer((int)Mathf.Ceil(Mathf.Max(_roundTimer, 0f)));
        if (_roundTimer <= 0)
            OnTimeout();
    }

    /// <summary>Fighters cannot stand inside each other or leave the screen.</summary>
    private void ResolveBodies()
    {
        float camLeft = _camX - ScreenW / 2f;
        float left = Mathf.Max(Fighter.StageLeft, camLeft + EdgeMargin);
        float right = Mathf.Min(Fighter.StageRight, camLeft + ScreenW - EdgeMargin);
        Fighter.ViewLeft = left;
        Fighter.ViewRight = right;

        bool bodies = Mathf.Abs(_p1.Position.Y - _p2.Position.Y) < 50f
                      && !IsLying(_p1) && !IsLying(_p2);
        float min = Fighter.PushHalfWidth * 2f;
        float dx = _p2.Position.X - _p1.Position.X;
        if (bodies && Mathf.Abs(dx) < min)
        {
            float sign = dx > 0 ? 1f : dx < 0 ? -1f : (_p1.FacingRight ? 1f : -1f);
            float half = (min - Mathf.Abs(dx)) / 2f;
            _p1.Position -= new Vector2(sign * half, 0);
            _p2.Position += new Vector2(sign * half, 0);
        }

        float x1 = Mathf.Clamp(_p1.Position.X, left, right);
        float x2 = Mathf.Clamp(_p2.Position.X, left, right);
        if (bodies && Mathf.Abs(x2 - x1) < min)
        {
            // One of them is against the edge: the other gives all the ground.
            float sign = x2 >= x1 ? 1f : -1f;
            if (x1 <= left + 0.01f || x1 >= right - 0.01f) x2 = Mathf.Clamp(x1 + sign * min, left, right);
            else x1 = Mathf.Clamp(x2 - sign * min, left, right);
        }
        _p1.Position = new Vector2(x1, _p1.Position.Y);
        _p2.Position = new Vector2(x2, _p2.Position.Y);
    }

    private static bool IsLying(Fighter f) =>
        f.CurrentState is FighterState.Down or FighterState.KO && f.Grounded;

    private void UpdateCamera()
    {
        float mid = (_p1.Position.X + _p2.Position.X) / 2f;
        float target = Mathf.Clamp(mid, ScreenW / 2f, StageData.Width - ScreenW / 2f);
        _camX = Mathf.MoveToward(_camX, target, 3f);
        float x = Mathf.Round(_camX);
        _camera.Position = new Vector2(x, ScreenH / 2f);
        // The far layer scrolls at half speed.
        _far.Position = new Vector2(Mathf.Round((x - ScreenW / 2f) * 0.5f), 0);
    }

    // ---------------------------------------------------------- round end
    private void OnFighterDied()
    {
        if (!_roundActive) return;
        _roundActive = false;

        // Dramatic slow-motion on the finishing blow.
        Engine.TimeScale = 0.4 * _baseTimeScale;
        _slowTicks = 34;

        _hud.Announce("ko", 110);
        AudioManager.Instance?.PlaySFX("ko_announce");

        // Resolve a tick later so a same-frame double KO is seen as one.
        After(1, () =>
        {
            bool p1Dead = _p1.CurrentHealth <= 0, p2Dead = _p2.CurrentHealth <= 0;
            _p1.Locked = _p2.Locked = true;
            if (p1Dead && p2Dead)
            {
                After(120, () => _hud.Announce("draw", 90));
                After(230, CheckMatchEnd);
                return;
            }

            Fighter winner = p1Dead ? _p2 : _p1;
            if (p1Dead) GameState.P2RoundWins++;
            else GameState.P1RoundWins++;
            winner.RoundOver(true);
            _hud.UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);

            if (winner.CurrentHealth >= winner.Stats.MaxHealth)
                After(120, () => _hud.Announce("perfect", 90));
            After(230, CheckMatchEnd);
        });
    }

    private void OnTimeout()
    {
        if (!_roundActive) return;
        _roundActive = false;
        _roundTimer = 0;

        _hud.Announce("timeover", 110);
        AudioManager.Instance?.PlaySFX("time");

        float p1Pct = (float)_p1.CurrentHealth / _p1.Stats.MaxHealth;
        float p2Pct = (float)_p2.CurrentHealth / _p2.Stats.MaxHealth;

        if (Mathf.IsEqualApprox(p1Pct, p2Pct))
        {
            _p1.RoundOver(false);
            _p2.RoundOver(false);
            After(120, () => _hud.Announce("draw", 90));
        }
        else
        {
            bool p1Wins = p1Pct > p2Pct;
            if (p1Wins) GameState.P1RoundWins++;
            else GameState.P2RoundWins++;
            _p1.RoundOver(p1Wins);
            _p2.RoundOver(!p1Wins);
            _hud.UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);
        }
        After(230, CheckMatchEnd);
    }

    private void CheckMatchEnd()
    {
        if (GameState.P1RoundWins >= GameState.RoundsToWin ||
            GameState.P2RoundWins >= GameState.RoundsToWin)
        {
            _matchOver = true;
            AudioManager.Instance?.PlaySFX("victory");
            int winner = GameState.P1RoundWins >= GameState.RoundsToWin ? 0 : 1;
            if (_demoAi != null)
            {
                GD.Print($"MATCH winner=P{winner + 1} rounds={GameState.P1RoundWins}-{GameState.P2RoundWins}");
                GameState.Reset();
                GetTree().Quit();
                return;
            }
            var stats = FighterData.GetByIndex(winner == 0 ? GameState.P1CharacterIndex : GameState.P2CharacterIndex);
            _victoryScreen.ShowWinner(winner, stats);
        }
        else
        {
            StartRound();
        }
    }
}
