#!/usr/bin/env bash
set -e

echo "==> Checking dependencies..."

if ! command -v wtype &>/dev/null; then
    echo ""
    echo "  [!] wtype not found — install it first:"
    echo "      sudo pacman -S wtype"
    echo ""
    exit 1
fi

if ! command -v wl-paste &>/dev/null; then
    echo ""
    echo "  [!] wl-clipboard not found — install it first:"
    echo "      sudo pacman -S wl-clipboard"
    echo ""
    exit 1
fi

echo "==> Installing hypr-typr..."
if command -v pipx &>/dev/null; then
    pipx install . --quiet --force
else
    pip install --user -e . --break-system-packages --quiet
fi

echo "==> Done!"
echo ""
echo "Add this line to ~/.config/hypr/hyprland.conf to bind a key:"
echo ""
echo "    bind = \$mainMod, T, exec, hypr-typr type"
echo ""
echo "Open settings with:  hypr-typr settings"
echo "Type clipboard with: hypr-typr type"
