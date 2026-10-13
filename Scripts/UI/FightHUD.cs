using Godot;

namespace StreepFighter;

/// <summary>
/// SF2-style fight HUD: two life gauges draining toward the K.O. badge, names,
/// round markers, the big timer and the centre-screen announcer art.
/// </summary>
public partial class FightHUD : Control
{
    private const int BarW = 154, BarH = 8, BarY = 16;
    private const int P1BarX = 16, P2BarX = 214;
    private const int MeterW = 40;

    private static readonly Color BarEmpty = new("d82800");
    private static readonly Color BarFull = new("f8d800");
    private static readonly Color BarShine = new("fcf8a0");
    private static readonly Color BarChunk = new("fcfcfc");

    private Fighter _p1, _p2;
    private readonly ColorRect[] _fill = new ColorRect[2];
    private readonly ColorRect[] _shine = new ColorRect[2];
    private readonly ColorRect[] _chunk = new ColorRect[2];
    private readonly ColorRect[] _meter = new ColorRect[2];
    private readonly float[] _shown = { 1f, 1f };   // gauge as drawn (lags the truth)
    private readonly float[] _actual = { 1f, 1f };
    private readonly TextureRect[,] _rounds = new TextureRect[2, 2];
    private Texture2D _roundWon, _roundEmpty;

    private Label _timerLabel, _p1Name, _p2Name, _stageName;
    private TextureRect _koBadge, _announce;
    private int _announceTicks, _announceAge, _stageNameTicks, _clock;

    public override void _Ready()
    {
        PixelUI.Fill(this);
        _roundWon = PixelUI.Tex("res://Assets/UI/round_won.png");
        _roundEmpty = PixelUI.Tex("res://Assets/UI/round_empty.png");

        BuildGauge(0, P1BarX);
        BuildGauge(1, P2BarX);
        _koBadge = PixelUI.Image(this, "res://Assets/UI/ko_badge.png", 172, 13);

        PixelUI.Text(this, "1P", 16, 4);
        PixelUI.Text(this, GameState.Mode == GameMode.VsCPU ? "CPU" : "2P", 248, 4, "bold", null,
            HorizontalAlignment.Right, 120);
        _p1Name = PixelUI.Text(this, "", 16, 27, "bold", PixelUI.Yellow);
        _p2Name = PixelUI.Text(this, "", 248, 27, "bold", PixelUI.Yellow, HorizontalAlignment.Right, 120);

        for (int i = 0; i < 2; i++)
        {
            _rounds[0, i] = PixelUI.Image(this, "res://Assets/UI/round_empty.png", 152 - i * 11, 28);
            _rounds[1, i] = PixelUI.Image(this, "res://Assets/UI/round_empty.png", 223 + i * 11, 28);
        }

        // Special-move charge, under each name.
        for (int p = 0; p < 2; p++)
        {
            int x = p == 0 ? 16 : PixelUI.W - 16 - MeterW;
            PixelUI.Box(this, x - 1, 38, MeterW + 2, 4, PixelUI.Ink);
            _meter[p] = PixelUI.Box(this, x, 39, MeterW, 2, PixelUI.Cyan);
        }

        _timerLabel = PixelUI.Centered(this, "99", 192, 29, "big", null, 60);
        _stageName = PixelUI.Centered(this, "", 192, 203, "pixel", null, 380);
        _stageName.Visible = false;

        _announce = new TextureRect { MouseFilter = MouseFilterEnum.Ignore, Visible = false };
        AddChild(_announce);
    }

    private void BuildGauge(int p, int x)
    {
        PixelUI.Box(this, x - 2, BarY - 2, BarW + 4, BarH + 4, PixelUI.Ink);
        PixelUI.Box(this, x - 1, BarY - 1, BarW + 2, BarH + 2, PixelUI.White);
        PixelUI.Box(this, x, BarY, BarW, BarH, BarEmpty);
        _chunk[p] = PixelUI.Box(this, x, BarY, 0, BarH, BarChunk);
        _fill[p] = PixelUI.Box(this, x, BarY, BarW, BarH, BarFull);
        _shine[p] = PixelUI.Box(this, x, BarY, BarW, 2, BarShine);
    }

    public void SetupFighters(Fighter p1, Fighter p2)
    {
        _p1 = p1;
        _p2 = p2;
        _p1Name.Text = p1.Stats.ShortName;
        _p2Name.Text = p2.Stats.ShortName;

        p1.HealthChanged += (current, max) => SetHealth(0, (float)current / max);
        p2.HealthChanged += (current, max) => SetHealth(1, (float)current / max);

        UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);
    }

    private void SetHealth(int p, float pct)
    {
        if (pct > _actual[p]) _shown[p] = pct; // refilled for a new round: no trailing chunk
        _actual[p] = pct;
    }

    public void UpdateTimer(int seconds)
    {
        _timerLabel.Text = seconds.ToString("00");
        _timerLabel.Modulate = seconds <= 10 ? new Color(1f, 0.45f, 0.4f) : Colors.White;
    }

    public void UpdateRounds(int p1Wins, int p2Wins)
    {
        for (int i = 0; i < 2; i++)
        {
            _rounds[0, i].Texture = p1Wins > i ? _roundWon : _roundEmpty;
            _rounds[1, i].Texture = p2Wins > i ? _roundWon : _roundEmpty;
        }
    }

    /// <summary>Slam an announcer graphic (Assets/UI/announce_{key}.png) onto the screen.</summary>
    public void Announce(string key, int ticks)
    {
        var tex = PixelUI.Tex($"res://Assets/UI/announce_{key}.png");
        _announce.Texture = tex;
        _announce.Size = tex.GetSize();
        _announce.PivotOffset = tex.GetSize() / 2f;
        _announce.Position = new Vector2(Mathf.Round((PixelUI.W - tex.GetWidth()) / 2f), 96 - tex.GetHeight() / 2);
        _announce.Visible = true;
        _announceTicks = ticks;
        _announceAge = 0;
    }

    public void ShowStageName(string text, int ticks)
    {
        _stageName.Text = text;
        _stageName.Visible = true;
        _stageNameTicks = ticks;
    }

    public override void _PhysicsProcess(double delta)
    {
        _clock++;

        // Announcer: three-frame zoom-in pop, hold, blink out.
        if (_announceTicks > 0)
        {
            _announceAge++;
            int scale = _announceAge < 3 ? 3 : _announceAge < 6 ? 2 : 1;
            _announce.Scale = new Vector2(scale, scale);
            if (--_announceTicks < 12)
                _announce.Visible = _announceTicks > 0 && (_announceTicks & 2) == 0;
        }

        if (_stageNameTicks > 0 && --_stageNameTicks == 0)
            _stageName.Visible = false;

        for (int p = 0; p < 2; p++)
        {
            _shown[p] = Mathf.MoveToward(_shown[p], _actual[p], 0.012f);
            int w = Mathf.RoundToInt(BarW * _actual[p]);
            int lag = Mathf.RoundToInt(BarW * _shown[p]);
            // Both gauges empty from the outside in, toward the K.O. badge.
            int x0 = p == 0 ? P1BarX + BarW - w : P2BarX;
            int lagX = p == 0 ? P1BarX + BarW - lag : P2BarX;
            _fill[p].Position = new Vector2(x0, BarY);
            _fill[p].Size = new Vector2(w, BarH);
            _shine[p].Position = new Vector2(x0, BarY);
            _shine[p].Size = new Vector2(w, 2);
            _chunk[p].Position = new Vector2(lagX, BarY);
            _chunk[p].Size = new Vector2(lag, BarH);
        }

        // K.O. badge flashes while anyone is in danger.
        bool danger = (_actual[0] > 0 && _actual[0] < 0.25f) || (_actual[1] > 0 && _actual[1] < 0.25f);
        _koBadge.Modulate = danger && _clock / 6 % 2 == 0 ? new Color(1f, 0.5f, 0.5f) : Colors.White;

        UpdateMeter(0, _p1);
        UpdateMeter(1, _p2);
    }

    private void UpdateMeter(int p, Fighter fighter)
    {
        if (fighter == null) return;
        float pct = fighter.GetSpecialCooldownPercent();
        int w = Mathf.RoundToInt(MeterW * pct);
        int x = p == 0 ? 16 : PixelUI.W - 16 - w;
        _meter[p].Position = new Vector2(x, 39);
        _meter[p].Size = new Vector2(w, 2);
        _meter[p].Color = pct >= 1f ? (_clock / 8 % 2 == 0 ? PixelUI.Yellow : PixelUI.White) : PixelUI.Cyan;
    }
}
