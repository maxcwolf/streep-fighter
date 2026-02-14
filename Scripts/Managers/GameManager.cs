using Godot;

namespace StreepFighter;

public partial class GameManager : Node
{
    private Fighter _p1Fighter;
    private Fighter _p2Fighter;
    private AiController _aiController;

    private FightHUD _fightHud;
    private VictoryScreen _victoryScreen;

    private float _roundTimer = 90f;
    private bool _roundActive;
    private bool _matchOver;

    private Vector2 _p1Spawn = new(300, 500);
    private Vector2 _p2Spawn = new(980, 500);

    public override void _Ready()
    {
        var hudLayer = GetNode<CanvasLayer>("../HUDLayer");
        _fightHud = hudLayer.GetNode<FightHUD>("HUD");
        _victoryScreen = hudLayer.GetNode<VictoryScreen>("VictoryScreen");
        _victoryScreen.Visible = false;

        LoadStageBackground();

        // Defer spawning — parent node is still setting up children during _Ready
        CallDeferred(MethodName.SpawnAndStart);
    }

    private void LoadStageBackground()
    {
        var stage = GetParent();

        // Hide default background elements
        var bg = stage.GetNodeOrNull<CanvasItem>("Background");
        var fl = stage.GetNodeOrNull<CanvasItem>("FloorLine");
        var fa = stage.GetNodeOrNull<CanvasItem>("FloorAccent");
        if (bg != null) bg.Visible = false;
        if (fl != null) fl.Visible = false;
        if (fa != null) fa.Visible = false;

        // Show the selected pre-instanced background
        int idx = GameState.StageIndex;
        for (int i = 0; i < 6; i++)
        {
            var bgNode = stage.GetNodeOrNull<CanvasItem>($"BG{i}");
            if (bgNode != null)
            {
                bgNode.Visible = (i == idx);
                if (i == idx)
                    stage.MoveChild(bgNode, 0);
            }
        }
    }

    private void SpawnAndStart()
    {
        SpawnFighters();
        StartRound();
    }

    private void SpawnFighters()
    {
        var p1Stats = FighterData.GetByIndex(GameState.P1CharacterIndex);
        var p2Stats = FighterData.GetByIndex(GameState.P2CharacterIndex);

        var p1Scene = GD.Load<PackedScene>(p1Stats.ScenePath);
        var p2Scene = GD.Load<PackedScene>(p2Stats.ScenePath);

        if (p1Scene == null || p2Scene == null)
        {
            GD.PrintErr($"Failed to load fighter scenes: P1={p1Stats.ScenePath} P2={p2Stats.ScenePath}");
            return;
        }

        var p1Node = p1Scene.Instantiate();
        var p2Node = p2Scene.Instantiate();
        _p1Fighter = p1Node as Fighter;
        _p2Fighter = p2Node as Fighter;

        if (_p1Fighter == null || _p2Fighter == null)
        {
            GD.PrintErr($"Fighter instantiation failed - P1:{p1Node?.GetType()} P2:{p2Node?.GetType()}");
            p1Node?.QueueFree();
            p2Node?.QueueFree();
            return;
        }

        _p1Fighter.PlayerIndex = 0;
        _p1Fighter.Stats = p1Stats;
        _p1Fighter.Position = _p1Spawn;

        _p2Fighter.PlayerIndex = 1;
        _p2Fighter.Stats = p2Stats;
        _p2Fighter.Position = _p2Spawn;

        _p1Fighter.Opponent = _p2Fighter;
        _p2Fighter.Opponent = _p1Fighter;

        var gameLayer = GetParent();
        gameLayer.AddChild(_p1Fighter);
        gameLayer.AddChild(_p2Fighter);

        _p1Fighter.SetupCollisionLayers();
        _p2Fighter.SetupCollisionLayers();

        // Setup AI for P2 if vs CPU mode
        if (GameState.Mode == GameMode.VsCPU)
        {
            _aiController = new AiController();
            gameLayer.AddChild(_aiController);
            _aiController.Setup(_p2Fighter);
        }

        // Connect signals
        _p1Fighter.Died += () => OnFighterDied(1);
        _p2Fighter.Died += () => OnFighterDied(2);

        // Setup HUD connections
        _fightHud.SetupFighters(_p1Fighter, _p2Fighter);
    }

    private async void StartRound()
    {
        if (_p1Fighter == null || _p2Fighter == null) return;
        _roundTimer = 90f;
        _roundActive = false;
        _matchOver = false;
        _p1Fighter.ResetForRound(_p1Spawn);
        _p2Fighter.ResetForRound(_p2Spawn);

        // Freeze fighters during announcements
        _p1Fighter.SetPhysicsProcess(false);
        _p2Fighter.SetPhysicsProcess(false);

        int roundNum = GameState.P1RoundWins + GameState.P2RoundWins + 1;
        _fightHud.ShowAnnouncement($"ROUND {roundNum}", 1.5f);
        AudioManager.Instance?.PlaySFX("round");
        await ToSignal(GetTree().CreateTimer(1.8), SceneTreeTimer.SignalName.Timeout);

        _fightHud.ShowAnnouncement("FIGHT!", 0.8f);
        AudioManager.Instance?.PlaySFX("fight");
        await ToSignal(GetTree().CreateTimer(1.0), SceneTreeTimer.SignalName.Timeout);

        // Unfreeze and start
        _p1Fighter.SetPhysicsProcess(true);
        _p2Fighter.SetPhysicsProcess(true);
        _roundActive = true;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!_roundActive || _matchOver) return;

        _roundTimer -= (float)delta;

        _fightHud.UpdateTimer((int)Mathf.Ceil(_roundTimer));

        if (_roundTimer <= 0)
        {
            _roundTimer = 0;
            OnTimeout();
        }
    }

    private async void OnFighterDied(int loserPlayer)
    {
        if (!_roundActive) return;
        _roundActive = false;

        _fightHud.ShowAnnouncement("K.O.", 1.5f);
        AudioManager.Instance?.PlaySFX("ko_announce");

        if (loserPlayer == 1)
            GameState.P2RoundWins++;
        else
            GameState.P1RoundWins++;

        _fightHud.UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);

        await ToSignal(GetTree().CreateTimer(1.5), SceneTreeTimer.SignalName.Timeout);
        CheckMatchEnd();
    }

    private async void OnTimeout()
    {
        if (!_roundActive) return;
        _roundActive = false;

        _fightHud.ShowAnnouncement("TIME", 1.5f);
        AudioManager.Instance?.PlaySFX("time");

        // Player with more health wins the round
        float p1Pct = (float)_p1Fighter.CurrentHealth / _p1Fighter.Stats.MaxHealth;
        float p2Pct = (float)_p2Fighter.CurrentHealth / _p2Fighter.Stats.MaxHealth;

        if (p1Pct >= p2Pct)
            GameState.P1RoundWins++;
        else
            GameState.P2RoundWins++;

        _fightHud.UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);

        await ToSignal(GetTree().CreateTimer(1.5), SceneTreeTimer.SignalName.Timeout);
        CheckMatchEnd();
    }

    private async void CheckMatchEnd()
    {
        if (GameState.P1RoundWins >= GameState.RoundsToWin ||
            GameState.P2RoundWins >= GameState.RoundsToWin)
        {
            _matchOver = true;
            await ToSignal(GetTree().CreateTimer(0.5), SceneTreeTimer.SignalName.Timeout);
            ShowVictoryScreen();
        }
        else
        {
            await ToSignal(GetTree().CreateTimer(1.0), SceneTreeTimer.SignalName.Timeout);
            StartRound();
        }
    }

    private void ShowVictoryScreen()
    {
        AudioManager.Instance?.PlaySFX("victory");
        int winner = GameState.P1RoundWins >= GameState.RoundsToWin ? 0 : 1;
        var stats = FighterData.GetByIndex(winner == 0 ? GameState.P1CharacterIndex : GameState.P2CharacterIndex);
        _victoryScreen.ShowWinner(winner, stats.Name);
    }
}
