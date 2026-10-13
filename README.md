<div align="center">

# 👊 STREEP FIGHTER 👊

### _Meryl Kombat_

A 16-bit-style arcade fighting game starring six iconic Meryl Streep characters.
Built with Godot 4.6 and C#.

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Meryl_Streep_by_Lincoln_Townley.JPG/400px-Meryl_Streep_by_Lincoln_Townley.JPG" width="280" alt="Meryl Streep portrait by Lincoln Townley" />

---

![Godot](https://img.shields.io/badge/Godot-4.6-%23478CBF?logo=godotengine&logoColor=white)
![C#](https://img.shields.io/badge/C%23-.NET%208.0-%23512BD4?logo=dotnet)
![License](https://img.shields.io/badge/license-MIT-green)
![Fighters](https://img.shields.io/badge/fighters-6-red)
![Stages](https://img.shields.io/badge/stages-6-gold)
![Meryl](https://img.shields.io/badge/Meryl%20Streeps-100%25-ff69b4)

</div>

---

## 🎬 About

**Streep Fighter** is a love letter to both classic 90s arcade fighters and the greatest actress of all time. Pick your favorite Meryl, choose a stage inspired by her filmography, and duke it out in best-of-3 rounds.

Features PvP local multiplayer and a VS CPU mode with AI opponent.

It looks and plays like the SNES-era Street Fighter II it parodies: chunky 384×216 pixel art, frame-by-frame
sprite animation, scrolling parallax stages, and frame-data combat with crouching and jumping attacks,
high/low blocking, knockdowns and hit-stop.

<div align="center">

<img src="docs/screenshots/title.png" width="384" alt="Title screen" /> <img src="docs/screenshots/select.png" width="384" alt="Player select" />

<img src="docs/screenshots/fight_kitchen.png" width="384" alt="Julia Child vs Margaret Thatcher in Julia's Kitchen" /> <img src="docs/screenshots/fight_forest.png" width="384" alt="The Witch vs Donna Sheridan in the Enchanted Woods" />

<img src="docs/screenshots/fight_villa.png" width="384" alt="A Thatcher mirror match on Kalokairi Island" /> <img src="docs/screenshots/fight_church.png" width="384" alt="Sister Aloysius vs The Witch in St. Nicholas Church" />

</div>

---

## 🎭 The Roster

Six playable fighters, each with unique stats and a signature special move.

<table>
<tr>
<td align="center" width="33%">
<img src="docs/roster/miranda.png" width="250" alt="Miranda Priestly: in-game portrait and sprite" /><br/>
<b>Miranda Priestly</b><br/>
<i>The Devil Wears Prada (2006)</i><br/><br/>
<b>Special:</b> "That's All" — Lightning dash-slap<br/>
<b>Type:</b> ⚡ Speedster<br/>
<code>HP 1000 · SPD 105 · DMG 150</code>
</td>
<td align="center" width="33%">
<img src="docs/roster/julia.png" width="250" alt="Julia Child: in-game portrait and sprite" /><br/>
<b>Julia Child</b><br/>
<i>Julie & Julia (2009)</i><br/><br/>
<b>Special:</b> "Bon Appétit" — Throws a pot projectile<br/>
<b>Type:</b> 🍳 Zoner<br/>
<code>HP 1000 · SPD 84 · DMG 180</code>
</td>
<td align="center" width="33%">
<img src="docs/roster/thatcher.png" width="250" alt="Margaret Thatcher: in-game portrait and sprite" /><br/>
<b>Margaret Thatcher</b><br/>
<i>The Iron Lady (2011)</i><br/><br/>
<b>Special:</b> "Iron Fist" — Armored power punch<br/>
<b>Type:</b> 🛡️ Tank<br/>
<code>HP 1200 · SPD 76 · DMG 250</code>
</td>
</tr>
<tr>
<td align="center">
<img src="docs/roster/witch.png" width="250" alt="The Witch: in-game portrait and sprite" /><br/>
<b>The Witch</b><br/>
<i>Into the Woods (2014)</i><br/><br/>
<b>Special:</b> "Curse of the Woods" — Curse projectile<br/>
<b>Type:</b> 🔮 Glass Cannon<br/>
<code>HP 900 · SPD 92 · DMG 200</code>
</td>
<td align="center">
<img src="docs/roster/donna.png" width="250" alt="Donna Sheridan: in-game portrait and sprite" /><br/>
<b>Donna Sheridan</b><br/>
<i>Mamma Mia! (2008)</i><br/><br/>
<b>Special:</b> "Dancing Queen" — Double spin attack<br/>
<b>Type:</b> 💃 Combo Fighter<br/>
<code>HP 950 · SPD 118 · DMG 130</code>
</td>
<td align="center">
<img src="docs/roster/aloysius.png" width="250" alt="Sister Aloysius: in-game portrait and sprite" /><br/>
<b>Sister Aloysius</b><br/>
<i>Doubt (2008)</i><br/><br/>
<b>Special:</b> "Divine Discipline" — Lunging knockback strike<br/>
<b>Type:</b> ✝️ Bruiser<br/>
<code>HP 1100 · SPD 84 · DMG 180</code>
</td>
</tr>
</table>

---

## 🗺️ Stages

Six arenas inspired by Meryl's filmography, drawn as SNES-era pixel art: each is wider than the screen, with a half-speed parallax layer behind it.

| Stage                   | Film                    | Location              |
| ----------------------- | ----------------------- | --------------------- |
| **Runway Magazine**     | _The Devil Wears Prada_ | New York City         |
| **Julia's Kitchen**     | _Julie & Julia_         | Paris, France         |
| **House of Commons**    | _The Iron Lady_         | London, England       |
| **Enchanted Woods**     | _Into the Woods_        | A dark magical forest |
| **Kalokairi Island**    | _Mamma Mia!_            | Greece                |
| **St. Nicholas Church** | _Doubt_                 | The Bronx, New York   |

---

## 🕹️ Controls

### Player 1 (Keyboard Left)

| Key       | Action            |
| --------- | ----------------- |
| `A` / `D` | Move Left / Right |
| `W`       | Jump              |
| `S`       | Crouch            |
| `F`       | Punch             |
| `G`       | Kick              |
| `H`       | Block             |
| `T`       | Special Move      |

### Player 2 (Keyboard Right)

| Key       | Action            |
| --------- | ----------------- |
| `←` / `→` | Move Left / Right |
| `↑`       | Jump              |
| `↓`       | Crouch            |
| `Num1`    | Punch             |
| `Num2`    | Kick              |
| `Num3`    | Block             |
| `Num0`    | Special Move      |

### Moves

| Input                         | Move                                             |
| ----------------------------- | ------------------------------------------------ |
| Punch / Kick                  | Standing straight / high kick                    |
| Crouch + Punch / Kick         | Low jab / sweep (knocks down, must be blocked low) |
| Jump, then Punch / Kick       | Jump-in attack (must be blocked standing)        |
| Jump + Left / Right           | Committed forward or backward jump               |
| Hold **away** from an attack  | Block (crouch to block low). The Block key works too |
| Special                       | Signature move, on a cooldown shown under your name |

Menus: `W`/`S` or the arrow keys to move, `F` / `Enter` to confirm, `Esc` to pause.

---

## 🏗️ Project Structure

```
streep-fighter/
├── Assets/
│   ├── Portraits/             # Source film stills (digitised into UI portraits)
│   ├── Sprites/Fighters/      # Generated sprite sheets (44 frames each, + P2 colours)
│   ├── Sprites/FX/            # Generated hit sparks, dust, projectiles, shadow
│   ├── Stages/                # Generated stage layers + thumbnails
│   ├── UI/                    # Generated logo, portraits, announcer art
│   └── Fonts/                 # Generated bitmap fonts
├── Scenes/                    # Thin scenes; the scripts build their own nodes
├── Scripts/
│   ├── AI/                    # CPU opponent controller
│   ├── Fighters/              # Fighter simulation, frame data, special moves, stats
│   ├── Managers/              # GameManager, GameState, StageData
│   └── UI/                    # HUD, menus and screens (built in code at 384x216)
├── Tools/art/                 # The pixel-art generator (Python + Pillow)
├── docs/                      # README images: screenshots + roster cards (`build.py docs`)
├── screenshot_tool.tscn       # Dev tool: scripted playthrough that saves screenshots
├── project.godot
└── StreepFighter.csproj
```

---

## ⚔️ Game Mechanics

- **Best of 3 rounds** — First to 2 round wins takes the match
- **99-second timer** — If time runs out, the fighter with more HP% wins the round
- **Blocking** — Hold away from an attack; reduces damage (varies per fighter, 70%–92%)
- **High / low** — Sweeps must be blocked crouching, jump-ins standing
- **Special moves** — Unique per fighter, with cooldowns ranging from 3–5 seconds
- **Knockdowns** — Sweeps, specials and anything that hits you out of the air put you on the floor
- **Frame data** — Everything runs on a fixed 60Hz tick with startup / active / recovery frames, hit-stop and an input buffer, like the 16-bit originals

---

## 🎨 Art Pipeline

The game renders at **384×216** (the original Street Fighter II arcade width) and is scaled up with
nearest-neighbour filtering. All of the art is generated by the scripts in `Tools/art/`:

- `rig.py` / `anims.py` — a 2D skeleton and the pose library (every animation frame as IK targets)
- `fighters.py` — each fighter's costume and hand-pixelled head
- `stage_*.py` — one script per stage backdrop
- `ui.py`, `fx.py`, `font.py` — logo, portraits, effects and bitmap fonts

To regenerate everything after changing a pose, a costume or a stage (needs Python 3 + Pillow):

```bash
python3 Tools/art/build.py
```

Pass `fighters`, `stages`, `ui`, `fx` or `fonts` to rebuild just one group. Open the project in the Godot
editor afterwards (or run `godot --headless --import`) so it re-imports the changed images.

To check the result without playing through by hand, `screenshot_tool.tscn` drives the real menus and a
fight with synthetic key presses and saves native-resolution screenshots:

```bash
godot --path . res://screenshot_tool.tscn -- <out_dir> [fighter 0-5] [stage 0-5] [cpu|pvp]
```

---

## 🚀 Getting Started

### Requirements

- [Godot 4.6](https://godotengine.org/) with .NET support
- [.NET 8.0 SDK](https://dotnet.microsoft.com/download)

### Running

1. Clone the repo
2. Open `project.godot` in Godot 4.6 (.NET edition)
3. Build the C# solution (`dotnet build` or via Godot editor)
4. Hit Play (F5)

---

## 🎥 Game Flow

```
🎬 Title Screen
   ├── VS Player (PvP)
   └── VS CPU
         ↓
🎭 Character Select
   P1 picks fighter → P2 picks (or CPU auto-picks)
         ↓
🗺️ Stage Select
   Pick your arena from 6 movie-themed stages
         ↓
🆚 VS Card
         ↓
👊 FIGHT!
   Best of 3 rounds · 99 seconds each
         ↓
🏆 Victory Screen
   Winner and win quote → Play again or main menu
```

---

<div align="center">

_"I don't know why I'm so scary. I don't want to be."_

— Meryl Streep, before selecting Margaret Thatcher and landing a 250-damage Iron Fist

---

Made with 🎬 and 👊 in Godot 4.6

_Photo: [Meryl Streep by Lincoln Townley](https://commons.wikimedia.org/wiki/File:Meryl_Streep_by_Lincoln_Townley.JPG), CC BY-SA 4.0_

</div>
