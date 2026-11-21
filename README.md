# Lookiyam themes for Omarchy

Six dark, minimal [Omarchy](https://omarchy.org/) themes. Each one is built
around an invented mark and a single point of light: near-black backgrounds,
thin grey line art, and one glowing accent.

| Theme | Accent | Background | Motif |
|---|---|---|---|
| [Graphite](themes/graphite) | `#8fbfff` blue | `#191919` | Open "G" ring, honeycomb, night landscapes |
| [Umbra](themes/umbra) | `#a8c8ff` ice blue | `#0d0f14` | Eclipses: crescents, corona, diamond ring |
| [Meridian](themes/meridian) | `#7cc8ff` sky blue | `#101216` | Triangles with a light at the apex |
| [Strata](themes/strata) | `#e6b072` amber | `#14120f` | Stacked horizontal layers |
| [Northline](themes/northline) | `#6ee7b7` mint | `#0c1013` | Vertical lines of light, aurora |
| [Carbon](themes/carbon) | `#ff7b54` ember | `#121212` | Hexagons with one glowing atom |

The logos and names (Umbra, Meridian, Strata, Northline, Carbon, Graphite) are
made up for these wallpapers and do not belong to any real brand.

## Install

`omarchy theme install` expects one theme per repository, so copy the folders
in by hand:

```bash
git clone https://github.com/lookiyam-94/omarchy-lookiyam-themes
cp -r omarchy-lookiyam-themes/themes/* ~/.config/omarchy/themes/
omarchy theme set umbra        # or graphite, meridian, strata, northline, carbon
```

Cycle backgrounds with `omarchy theme bg next` or the background switcher.

## What each theme contains

- `colors.toml` — the palette. Omarchy generates the terminal, Hyprland, btop,
  Neovim, VS Code and the rest from it.
- `backgrounds/` — 3840×2400 wallpapers (Graphite's photographic ones are
  upscaled to 7680×4800).
- `preview.png` — the theme switcher preview.
- `shell.lock.toml` — the lock screen: a near-black password card over the
  blurred wallpaper, with a thin border in the accent that turns soft red
  after a wrong password. Omarchy merges it into the `[lock]` section of the
  generated `shell.toml`.
- `unlock.png` — mark and name on a transparent background, for the boot
  disk-unlock screen.
- `icons.theme` — the Yaru icon colour that matches the accent.

## Backgrounds

Everything except Graphite's photographic landscapes is drawn procedurally with
NumPy and Pillow. The scripts are in [`tools/`](tools/):

| Script | Draws |
|---|---|
| `gen_bg.py` | Graphite landscapes (ridges, still lake, halo, night sky) |
| `gen_logo.py` | Graphite mark |
| `gen_pair.py` | Graphite extras, Strata, Northline and Carbon |
| `gen_umbra.py` | Umbra |
| `gen_meridian.py` | Meridian |
| `gen_marks.py` | The first logo studies (Strata, Umbra, Meridian, Northline) |
| `gen_unlock_*.py` | `unlock.png` for each theme |

Run them with [uv](https://docs.astral.sh/uv/) so nothing is installed globally,
for example:

```bash
uv run --with numpy --with pillow python tools/gen_pair.py carbon /tmp/carbon-bgs
uv run --with numpy --with pillow python tools/gen_umbra.py /tmp/umbra-bgs 0.25   # quarter-size preview
```

The wordmarks use DejaVu Sans ExtraLight from `/usr/share/fonts/TTF/`.

## Vivaldi

The same themes for the Vivaldi browser live in
[vivaldi-lookiyam-themes](https://github.com/lookiyam-94/vivaldi-lookiyam-themes).

## License

MIT
