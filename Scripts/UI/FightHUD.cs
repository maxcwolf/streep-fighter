using Godot;

namespace StreepFighter;

public partial class FightHUD : Control
{
    private ProgressBar _p1HealthBar;
    private ProgressBar _p2HealthBar;
    private Label _timerLabel;
    private Label _p1NameLabel;
    private Label _p2NameLabel;
    private Label _roundLabel;
    private Label _announcementLabel;
    private Label _stageNameLabel;

    private Panel _p1Round1;
    private Panel _p1Round2;
    private Panel _p2Round1;
    private Panel _p2Round2;

    private StyleBoxFlat _p1FillStyle;
    private StyleBoxFlat _p2FillStyle;
    private StyleBoxFlat _roundWonStyle;
    private StyleBoxFlat _roundEmptyStyle;

    public override void _Ready()
    {
        _p1HealthBar = GetNode<ProgressBar>("TopBar/P1Section/P1HealthBar");
        _p2HealthBar = GetNode<ProgressBar>("TopBar/P2Section/P2HealthBar");
        _timerLabel = GetNode<Label>("TopBar/TimerFrame/TimerLabel");
        _p1NameLabel = GetNode<Label>("TopBar/P1Section/P1Name");
        _p2NameLabel = GetNode<Label>("TopBar/P2Section/P2Name");
        _roundLabel = GetNode<Label>("RoundLabel");
        _announcementLabel = GetNode<Label>("AnnouncementLabel");
        _stageNameLabel = GetNode<Label>("StageNameLabel");

        var stageInfo = StageData.GetByIndex(GameState.StageIndex);
        _stageNameLabel.Text = stageInfo.DisplayLabel;

        _p1Round1 = GetNode<Panel>("TopBar/P1Section/P1RoundIndicators/P1Round1");
        _p1Round2 = GetNode<Panel>("TopBar/P1Section/P1RoundIndicators/P1Round2");
        _p2Round1 = GetNode<Panel>("TopBar/P2Section/P2RoundIndicators/P2Round1");
        _p2Round2 = GetNode<Panel>("TopBar/P2Section/P2RoundIndicators/P2Round2");

        // Clone fill styles so we can mutate color per-frame
        var origFill = _p1HealthBar.GetThemeStylebox("fill") as StyleBoxFlat;
        _p1FillStyle = origFill.Duplicate() as StyleBoxFlat;
        _p2FillStyle = origFill.Duplicate() as StyleBoxFlat;
        _p1HealthBar.AddThemeStyleboxOverride("fill", _p1FillStyle);
        _p2HealthBar.AddThemeStyleboxOverride("fill", _p2FillStyle);

        // Cache round indicator styles
        _roundEmptyStyle = _p1Round1.GetThemeStylebox("panel") as StyleBoxFlat;
        _roundWonStyle = new StyleBoxFlat();
        _roundWonStyle.BgColor = new Color(0.95f, 0.78f, 0.15f, 1);
        _roundWonStyle.CornerRadiusTopLeft = 6;
        _roundWonStyle.CornerRadiusTopRight = 6;
        _roundWonStyle.CornerRadiusBottomLeft = 6;
        _roundWonStyle.CornerRadiusBottomRight = 6;
    }

    public void SetupFighters(Fighter p1, Fighter p2)
    {
        _p1NameLabel.Text = p1.Stats.Name;
        _p2NameLabel.Text = p2.Stats.Name;

        _p1HealthBar.MaxValue = p1.Stats.MaxHealth;
        _p1HealthBar.Value = p1.Stats.MaxHealth;
        _p2HealthBar.MaxValue = p2.Stats.MaxHealth;
        _p2HealthBar.Value = p2.Stats.MaxHealth;

        p1.HealthChanged += (current, max) =>
        {
            _p1HealthBar.Value = current;
            UpdateHealthBarColor(_p1FillStyle, (float)current / max);
        };
        p2.HealthChanged += (current, max) =>
        {
            _p2HealthBar.Value = current;
            UpdateHealthBarColor(_p2FillStyle, (float)current / max);
        };

        UpdateRounds(GameState.P1RoundWins, GameState.P2RoundWins);
    }

    private void UpdateHealthBarColor(StyleBoxFlat fillStyle, float healthPct)
    {
        Color color;
        if (healthPct > 0.5f)
        {
            // Green to Yellow (1.0 → 0.5)
            float t = (healthPct - 0.5f) / 0.5f;
            color = new Color(0.9f, 0.9f, 0.15f, 1).Lerp(new Color(0.2f, 0.85f, 0.2f, 1), t);
        }
        else
        {
            // Yellow to Red (0.5 → 0.0)
            float t = healthPct / 0.5f;
            color = new Color(0.85f, 0.15f, 0.1f, 1).Lerp(new Color(0.9f, 0.9f, 0.15f, 1), t);
        }
        fillStyle.BgColor = color;
    }

    public void UpdateTimer(int seconds)
    {
        _timerLabel.Text = seconds.ToString();

        if (seconds <= 10)
            _timerLabel.AddThemeColorOverride("font_color", new Color(0.95f, 0.2f, 0.15f, 1));
        else
            _timerLabel.AddThemeColorOverride("font_color", new Color(1, 1, 1, 1));
    }

    public void UpdateRounds(int p1Wins, int p2Wins)
    {
        _roundLabel.Text = $"P1: {p1Wins}  |  P2: {p2Wins}";

        _p1Round1.AddThemeStyleboxOverride("panel", p1Wins >= 1 ? _roundWonStyle : _roundEmptyStyle);
        _p1Round2.AddThemeStyleboxOverride("panel", p1Wins >= 2 ? _roundWonStyle : _roundEmptyStyle);
        _p2Round1.AddThemeStyleboxOverride("panel", p2Wins >= 1 ? _roundWonStyle : _roundEmptyStyle);
        _p2Round2.AddThemeStyleboxOverride("panel", p2Wins >= 2 ? _roundWonStyle : _roundEmptyStyle);
    }

    public async void ShowAnnouncement(string text, float duration)
    {
        _announcementLabel.Text = text;
        _announcementLabel.Visible = true;
        _announcementLabel.Scale = new Vector2(2f, 2f);
        _announcementLabel.PivotOffset = _announcementLabel.Size / 2;

        var tween = CreateTween();
        tween.TweenProperty(_announcementLabel, "scale", new Vector2(1f, 1f), 0.2)
            .SetTrans(Tween.TransitionType.Back)
            .SetEase(Tween.EaseType.Out);

        await ToSignal(GetTree().CreateTimer(duration), SceneTreeTimer.SignalName.Timeout);
        _announcementLabel.Visible = false;
    }
}
