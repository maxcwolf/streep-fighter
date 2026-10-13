using Godot;

namespace StreepFighter;

public partial class CharacterSelect : Control
{
    private const int Columns = 3;
    private const int GridX = 126, GridY = 104, CellW = 44, CellH = 54;
    private const int PortraitW = 40, PortraitH = 50;
    private const int BigW = 80, BigH = 100, BigY = 38;

    private int _p1Selection = 0;
    private int _p2Selection = 1;
    private bool _p1Confirmed;
    private bool _p2Confirmed;
    private int _leaveTicks = -1;

    // Character select voice clip keys (matches Assets/Audio/SFX/select_*.mp3)
    private static readonly string[] SelectClipKeys = {
        "select_miranda", "select_julia", "select_thatcher",
        "select_witch", "select_donna", "select_aloysius"
    };

    private readonly Control[] _cursor = new Control[2];
    private Control _p2Outer; // player 2's frame, drawn outside player 1's when they share a portrait
    private Control _p2Tag;
    private int _p2TagRightX;
    private readonly TextureRect[] _big = new TextureRect[2];
    private readonly Label[] _name = new Label[2];
    private readonly Label[] _film = new Label[2];
    private readonly Label[] _special = new Label[2];
    private readonly Label[] _ready = new Label[2];
    private Label _cpuLabel;
    private Label _hint;

    private static bool VsCpu => GameState.Mode == GameMode.VsCPU;

    public override void _Ready()
    {
        // Come back to the picks you had (after Esc from stage select, or a rematch).
        _p1Selection = Mathf.Clamp(GameState.P1CharacterIndex, 0, FighterData.Count - 1);
        _p2Selection = Mathf.Clamp(GameState.P2CharacterIndex, 0, FighterData.Count - 1);

        PixelUI.Fill(this);
        PixelUI.Image(this, "res://Assets/UI/select_bg.png", 0, 0);
        PixelUI.Centered(this, "PLAYER SELECT", 192, 6, "big");

        _hint = PixelUI.Centered(this, "", 192, 28, "tiny", PixelUI.Grey, 380);

        for (int i = 0; i < FighterData.Count; i++)
        {
            var (x, y) = Cell(i);
            PixelUI.Box(this, x - 2, y - 2, PortraitW + 4, PortraitH + 4, PixelUI.Ink);
            PixelUI.Image(this, FighterData.GetByIndex(i).PortraitPath, x, y);
        }

        _p2Outer = MakeCursor(1, PixelUI.P2Red, 3); // created first so player 1's tag draws over it
        for (int p = 0; p < 2; p++)
        {
            Color col = p == 0 ? PixelUI.P1Blue : PixelUI.P2Red;
            int bx = p == 0 ? 10 : PixelUI.W - 10 - BigW;
            PixelUI.Box(this, bx - 2, BigY - 2, BigW + 4, BigH + 4, PixelUI.White);
            PixelUI.Box(this, bx - 1, BigY - 1, BigW + 2, BigH + 2, PixelUI.Ink);
            _big[p] = PixelUI.Image(this, FighterData.GetByIndex(p).BigPortraitPath, bx, BigY);
            _big[p].FlipH = p == 1;
            int cx = bx + BigW / 2;
            _name[p] = PixelUI.Centered(this, "", cx, BigY + BigH + 6, "bold", PixelUI.Yellow, 110);
            _film[p] = PixelUI.Centered(this, "", cx, BigY + BigH + 18, "tiny", PixelUI.White, 110);
            _special[p] = PixelUI.Centered(this, "", cx, BigY + BigH + 26, "tiny", PixelUI.Cyan, 110);
            _ready[p] = PixelUI.Centered(this, "READY!", cx, BigY + BigH + 38, "bold", PixelUI.Red, 110);

            _cursor[p] = MakeCursor(p, col, 0);
        }

        _cpuLabel = PixelUI.Centered(this, "CPU", PixelUI.W - 10 - BigW / 2, BigY + BigH / 2 - 8, "big");

        UpdateDisplay();

        AudioManager.Instance?.PlaySFX("select_welcome");
    }

    /// <summary>A steady 2px frame in the player's colour with a "1P" / "2P" / "CPU" tag riding on top.</summary>
    private Control MakeCursor(int player, Color colour, int grow)
    {
        var cursor = new Control { MouseFilter = MouseFilterEnum.Ignore };
        AddChild(cursor);
        int w = PortraitW + grow * 2, h = PortraitH + grow * 2;
        PixelUI.Frame(cursor, -4 - grow, -4 - grow, w + 8, h + 8, PixelUI.White, 1);
        PixelUI.Frame(cursor, -3 - grow, -3 - grow, w + 6, h + 6, colour, 2);
        // 1P's tag hangs off the top-left corner, the 2P / CPU tag off the top-right.
        string text = player == 0 ? "1P" : VsCpu ? "CPU" : "2P";
        int tagW = text.Length * 8 + 1;
        int tagX = player == 0 ? -4 : PortraitW + 4 + grow - tagW;
        var tag = new Control { Position = new Vector2(tagX, -13 - grow), MouseFilter = MouseFilterEnum.Ignore };
        cursor.AddChild(tag);
        PixelUI.Box(tag, 0, 0, tagW, 10, colour);
        PixelUI.Text(tag, text, 1, 1);
        if (player == 1 && grow == 0)
        {
            _p2Tag = tag;
            _p2TagRightX = tagX;
        }
        return cursor;
    }

    private static (int X, int Y) Cell(int index) =>
        (GridX + index % Columns * CellW, GridY + index / Columns * CellH);

    public override void _Input(InputEvent @event)
    {
        if (@event is not InputEventKey and not InputEventJoypadButton and not InputEventJoypadMotion) return;
        if (!@event.IsPressed() || @event.IsEcho()) return;

        if (@event.IsActionPressed("ui_cancel"))
        {
            GetViewport().SetInputAsHandled();
            GoBack();
            return;
        }
        if (_leaveTicks >= 0) return;

        if (VsCpu)
        {
            // One player makes both picks: their own fighter, then the CPU's.
            // (else-if, so the press that locks in 1P can't also lock in the CPU.)
            if (!_p1Confirmed)
            {
                HandlePlayer("p1", ref _p1Selection, ref _p1Confirmed);
                // Start the CPU box on a different portrait so it is clearly a second pick
                // (a mirror match is still one step away).
                if (_p1Confirmed && _p2Selection == _p1Selection)
                {
                    _p2Selection = (_p1Selection + 1) % FighterData.Count;
                    UpdateDisplay();
                }
            }
            else if (!_p2Confirmed)
            {
                HandlePlayer("p1", ref _p2Selection, ref _p2Confirmed);
            }
            return;
        }

        if (!_p1Confirmed)
            HandlePlayer("p1", ref _p1Selection, ref _p1Confirmed);

        if (!_p2Confirmed)
            HandlePlayer("p2", ref _p2Selection, ref _p2Confirmed);
    }

    private void HandlePlayer(string prefix, ref int selection, ref bool confirmed)
    {
        int count = FighterData.Count;
        int row = selection / Columns, col = selection % Columns;
        int next = selection;

        if (Input.IsActionJustPressed(prefix + "_left"))
            next = row * Columns + (col + Columns - 1) % Columns;
        else if (Input.IsActionJustPressed(prefix + "_right"))
            next = row * Columns + (col + 1) % Columns;
        else if (Input.IsActionJustPressed(prefix + "_jump") || Input.IsActionJustPressed(prefix + "_crouch"))
            next = (selection + Columns) % count;
        else if (Input.IsActionJustPressed(prefix + "_punch"))
        {
            AudioManager.Instance?.PlaySFX("menu_confirm");
            PlaySelectClip(selection);
            confirmed = true;
            UpdateDisplay();
            CheckBothConfirmed();
            return;
        }

        if (next != selection)
        {
            selection = next;
            AudioManager.Instance?.PlaySFX("menu_select");
            UpdateDisplay();
        }
    }

    /// <summary>
    /// Esc: take back a locked-in pick first (even if the countdown to the next
    /// screen has started); with nothing locked in, return to the title screen.
    /// Against the CPU the picks come back one at a time: CPU's, then yours.
    /// </summary>
    private void GoBack()
    {
        AudioManager.Instance?.PlaySFX("menu_select");
        if (_p1Confirmed || _p2Confirmed)
        {
            if (VsCpu && _p2Confirmed)
                _p2Confirmed = false;
            else
                _p1Confirmed = _p2Confirmed = false;
            _leaveTicks = -1;
            UpdateDisplay();
            return;
        }
        GetTree().ChangeSceneToFile("res://Scenes/UI/TitleScreen.tscn");
    }

    private void CheckBothConfirmed()
    {
        if (_p1Confirmed && _p2Confirmed)
        {
            GameState.P1CharacterIndex = _p1Selection;
            GameState.P2CharacterIndex = _p2Selection;
            _leaveTicks = 50; // let "READY!" land before moving on
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        // Cursors and "READY!" hold steady - no blinking.
        _ready[0].Visible = _p1Confirmed;
        _ready[1].Visible = _p2Confirmed;

        if (_leaveTicks > 0 && --_leaveTicks == 0)
            GetTree().ChangeSceneToFile("res://Scenes/UI/StageSelect.tscn");
    }

    private void PlaySelectClip(int characterIndex)
    {
        if (characterIndex >= 0 && characterIndex < SelectClipKeys.Length)
            AudioManager.Instance?.PlaySFX(SelectClipKeys[characterIndex]);
    }

    private void UpdateDisplay()
    {
        ShowPick(0, _p1Selection, true);
        // Against the CPU the second cursor only appears once 1P is locked in.
        bool showP2 = !VsCpu || _p1Confirmed;
        ShowPick(1, _p2Selection, showP2);
        _cpuLabel.Visible = !showP2;

        if (!VsCpu)
            _hint.Text = "1P: A/D/W/S + F      2P: ARROWS + K      ESC: BACK";
        else if (!_p1Confirmed)
            _hint.Text = "PICK YOUR FIGHTER: A/D/W/S + F      ESC: BACK";
        else
            _hint.Text = "PICK THE CPU'S FIGHTER: A/D/W/S + F      ESC: BACK";

        // Both players on one portrait: player 2's frame steps outside player 1's.
        bool shared = showP2 && _p2Selection == _p1Selection;
        _cursor[1].Visible = showP2 && !shared;
        _p2Outer.Visible = shared;
        _p2Outer.Position = _cursor[1].Position;

        // Directly left of 1P's box the two tags would run together ("CPU1P"):
        // hang this one off the left corner instead.
        bool leftOfP1 = _p2Selection / Columns == _p1Selection / Columns
                        && _p2Selection % Columns == _p1Selection % Columns - 1;
        _p2Tag.Position = new Vector2(leftOfP1 ? -4 : _p2TagRightX, _p2Tag.Position.Y);
    }

    private void ShowPick(int p, int selection, bool visible)
    {
        var stats = FighterData.GetByIndex(selection);
        var (x, y) = Cell(selection);
        _cursor[p].Position = new Vector2(x, y);
        _big[p].Visible = visible;
        _big[p].Texture = PixelUI.Tex(stats.BigPortraitPath);
        _name[p].Text = visible ? stats.ShortName : "";
        _film[p].Text = visible ? stats.Film : "";
        _special[p].Text = visible ? stats.SpecialName : "";
    }
}
