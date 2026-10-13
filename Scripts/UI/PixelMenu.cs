using System;
using System.Collections.Generic;
using Godot;

namespace StreepFighter;

/// <summary>
/// A vertical arcade menu: centred bitmap-font entries with a ">" cursor.
/// Up/down with W/S or the arrows, confirm with F / K / Enter, or click.
/// A row can also be a star setting, changed with left/right.
/// </summary>
public partial class PixelMenu : Control
{
    private const int RowHeight = 14;

    private const int StarStep = 10;

    private sealed class Item
    {
        public Label Label;
        public float Width;            // of the whole row, for placing the cursor
        public Action Do;              // confirm
        public Action<int> Adjust;     // left / right (null for plain entries)
    }

    private readonly List<Item> _items = new();
    private Label _cursor;
    private int _index;
    private int _blink;
    private int _delay;
    private bool _waitForRelease;

    /// <summary>Ignore input while false (e.g. during a screen transition).</summary>
    public bool Active { get; set; } = true;

    public PixelMenu()
    {
        MouseFilter = MouseFilterEnum.Ignore;
    }

    /// <summary>
    /// Start taking input. A confirm button that is already held (or still being
    /// mashed from the fight) is ignored until it has been released, and nothing
    /// is accepted for the first <paramref name="delayFrames"/> frames.
    /// </summary>
    public void Arm(int delayFrames = 0)
    {
        Active = true;
        _delay = delayFrames;
        _waitForRelease = true;
    }

    public PixelMenu Add(string text, Action action)
    {
        int row = _items.Count;
        var label = PixelUI.Centered(this, text, 0, row * RowHeight);
        label.MouseFilter = MouseFilterEnum.Stop;
        label.MouseEntered += () => Select(row, false);
        label.GuiInput += e =>
        {
            if (Active && e is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
            {
                Select(row, false); // act on the row that was clicked, hover or not
                Activate();
            }
        };
        _items.Add(new Item { Label = label, Width = TextWidth(label), Do = action });
        _cursor ??= PixelUI.Text(this, ">", 0, 0, "bold", PixelUI.Red);
        Select(_index, false);
        return this;
    }

    /// <summary>
    /// A setting shown as a row of stars (SF2's difficulty levels). Left/right
    /// change it, confirm steps it up and wraps round, clicking a star sets it.
    /// </summary>
    public PixelMenu AddStars(string text, int max, Func<int> get, Action<int> set)
    {
        int row = _items.Count;
        var label = PixelUI.Text(this, text, 0, row * RowHeight);
        float textWidth = TextWidth(label);
        float width = textWidth + 6 + max * StarStep;
        int left = Mathf.RoundToInt(-width / 2f);
        label.Position = new Vector2(left, row * RowHeight);

        var on = PixelUI.Tex("res://Assets/UI/star_on.png");
        var off = PixelUI.Tex("res://Assets/UI/star_off.png");
        var stars = new TextureRect[max];
        void Refresh()
        {
            for (int i = 0; i < max; i++)
                stars[i].Texture = i < get() ? on : off;
        }
        void Change(int value)
        {
            if (value == get()) return;
            set(value);
            AudioManager.Instance?.PlaySFX("menu_select");
            Refresh();
        }

        for (int i = 0; i < max; i++)
        {
            int level = i + 1;
            stars[i] = PixelUI.Image(this, "res://Assets/UI/star_off.png",
                left + (int)textWidth + 6 + i * StarStep, row * RowHeight - 1);
            stars[i].MouseFilter = MouseFilterEnum.Stop;
            stars[i].MouseEntered += () => Select(row, false);
            stars[i].GuiInput += e =>
            {
                if (Active && e is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
                    Change(level);
            };
        }
        Refresh();

        label.MouseFilter = MouseFilterEnum.Stop;
        label.MouseEntered += () => Select(row, false);
        _items.Add(new Item
        {
            Label = label,
            Width = width,
            Do = () => Change(get() >= max ? 1 : get() + 1),
            Adjust = delta => Change(Mathf.Clamp(get() + delta, 1, max)),
        });
        _cursor ??= PixelUI.Text(this, ">", 0, 0, "bold", PixelUI.Red);
        Select(_index, false);
        return this;
    }

    private static float TextWidth(Label label) =>
        label.LabelSettings.Font.GetStringSize(label.Text, HorizontalAlignment.Left, -1,
            label.LabelSettings.FontSize).X;

    private void Select(int index, bool sound = true)
    {
        if (_items.Count == 0) return;
        if (sound && index != _index) AudioManager.Instance?.PlaySFX("menu_select");
        _index = (index + _items.Count) % _items.Count;
        for (int i = 0; i < _items.Count; i++)
            PixelUI.Tint(_items[i].Label, i == _index ? PixelUI.Yellow : PixelUI.White);

        _cursor.Position = new Vector2(Mathf.Round(-_items[_index].Width / 2f) - 12, _index * RowHeight);
    }

    private void Activate()
    {
        if (_items.Count == 0) return;
        if (_items[_index].Adjust == null) // star rows make their own sound when the value changes
            AudioManager.Instance?.PlaySFX("menu_confirm");
        _items[_index].Do();
    }

    public override void _Process(double delta)
    {
        if (_cursor != null)
            _cursor.Visible = ++_blink / 16 % 2 == 0;

        if (!Active || !IsVisibleInTree()) return;
        if (_delay > 0)
        {
            _delay--;
            return;
        }

        // Polled rather than event-driven: "just pressed" fires once per press for keys,
        // buttons and analogue sticks alike (stick events arrive many times per flick).
        if (Input.IsActionJustPressed("ui_up") || Input.IsActionJustPressed("p1_jump"))
            Select(_index - 1);
        else if (Input.IsActionJustPressed("ui_down") || Input.IsActionJustPressed("p1_crouch"))
            Select(_index + 1);

        var adjust = _items.Count > 0 ? _items[_index].Adjust : null;
        if (adjust != null)
        {
            if (Input.IsActionJustPressed("ui_left") || Input.IsActionJustPressed("p1_left")) adjust(-1);
            else if (Input.IsActionJustPressed("ui_right") || Input.IsActionJustPressed("p1_right")) adjust(1);
        }

        bool held = Input.IsActionPressed("ui_accept") || Input.IsActionPressed("p1_punch")
                    || Input.IsActionPressed("p2_punch");
        if (_waitForRelease)
        {
            _waitForRelease = held;
            return;
        }
        if (Input.IsActionJustPressed("ui_accept") || Input.IsActionJustPressed("p1_punch")
            || Input.IsActionJustPressed("p2_punch"))
            Activate();
    }
}
