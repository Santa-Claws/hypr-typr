# hypr-typr

Types your clipboard as individual keystrokes in any Hyprland app. Works anywhere
paste is blocked — remote desktops, VMs, web forms, terminals, etc.

Optional humanizer adds subtle random variation to make it look less robotic.

---

## Requirements

- Hyprland (Wayland compositor)
- `wtype` — Wayland key injection tool
- `wl-clipboard` — Wayland clipboard reader

## Install

```bash
sudo pacman -S wtype wl-clipboard
bash install.sh
```

The install script uses `pipx` to create an isolated environment. After install,
`hypr-typr` will be available as a command.

## Hyprland keybinds

Add these to `~/.config/hypr/bindings.conf` (or wherever you keep bindings):

```
bind = SUPER, Y, exec, bash -c 'hypr-typr type &>/dev/null'
bind = SUPER ALT, Y, exec, bash -c 'hypr-typr stop &>/dev/null'
```

- `Super+Y` — start typing the clipboard
- `Super+Alt+Y` — stop typing immediately

## Usage

```
hypr-typr type      # type clipboard now (use via keybind)
hypr-typr stop      # kill an in-progress typing session
hypr-typr settings  # open TUI to configure speed and humanizer
```

## Settings

Open `hypr-typr settings` to configure:

| Setting | Default | Description |
|---|---|---|
| WPM | 120 | Base typing speed |
| Humanizer | Off | Enable random variation |
| Variation ±% | 12% | How much each keystroke varies |
| Word pause chance | 8% | Chance of a brief pause at spaces |
| Word pause range | 20–60ms | Duration of word pauses |
| Burst typing | Off | Occasionally type a few chars faster |

Config is saved to `~/.config/hypr-typr/config.json` and can be edited directly.

## How it works

1. Reads clipboard via `wl-paste`
2. Iterates characters one at a time
3. Injects each character via `wtype` with a computed delay
4. Special characters (`\n`, `\t`) are sent as keysyms via `wtype -k`

The humanizer applies gaussian-distributed delay variation per keystroke,
with optional extra pauses at word boundaries and occasional burst runs.
