# hypr-typr

Paste your clipboard as simulated keystrokes — character by character — in any Hyprland app. Includes a humanizer with random speed variation, word pauses, and burst typing.

## Install

```bash
# Requires wtype for Wayland key injection
sudo pacman -S wtype wl-clipboard

bash install.sh
```

## Usage

```bash
hypr-typr type      # type clipboard contents now
hypr-typr settings  # open TUI to configure
```

## Hyprland keybind

Add to `~/.config/hypr/hyprland.conf`:

```
bind = $mainMod, T, exec, hypr-typr type
```

## Settings

| Setting | Description |
|---|---|
| WPM | Base typing speed (words per minute) |
| Humanizer | Enable random variation |
| Variation ±% | How much each keystroke varies from base speed |
| Word pause chance | Probability of a pause at spaces/newlines |
| Word pause range | Min/max duration of word pauses in ms |
| Burst typing | Occasionally type a few chars at high speed |

Config is saved to `~/.config/hypr-typr/config.json`.
