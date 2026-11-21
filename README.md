# Lookiyam themes for Omarchy

Eight dark, minimal [Omarchy](https://omarchy.org/) themes. Each one is built
around an invented mark and a single point of light: near-black backgrounds,
thin grey line art, and one glowing accent. The original six themes include ten
backgrounds each; Bramble and Vesper include six each.

| Theme | Accent | Background | Motif |
|---|---|---|---|
| [Graphite](themes/graphite) | `#8fbfff` blue | `#191919` | Open "G" ring, honeycomb, night landscapes |
| [Umbra](themes/umbra) | `#a8c8ff` ice blue | `#0d0f14` | Eclipses: crescents, corona, diamond ring |
| [Meridian](themes/meridian) | `#7cc8ff` sky blue | `#101216` | Triangles with a light at the apex |
| [Strata](themes/strata) | `#e6b072` amber | `#14120f` | Stacked horizontal layers |
| [Northline](themes/northline) | `#6ee7b7` mint | `#0c1013` | Vertical lines of light, aurora |
| [Carbon](themes/carbon) | `#ff7b54` ember | `#121212` | Hexagons with one glowing atom |
| [Vesper](themes/vesper) | `#b6a0d6` twilight violet | `#100d15` | Evening star over a setting sun |
| [Bramble](themes/bramble) | `#c791a9` berry | `#140d12` | Thorned cane with one blackberry |

The logos and names (Umbra, Meridian, Strata, Northline, Carbon, Graphite,
Vesper, Bramble) are
made up for these wallpapers and do not belong to any real brand.

## Install

`omarchy theme install` expects one theme per repository, so copy the folders
in by hand:

```bash
git clone https://github.com/lookiyam-94/omarchy-lookiyam-themes
cp -r omarchy-lookiyam-themes/themes/* ~/.config/omarchy/themes/
omarchy theme set umbra        # or graphite, meridian, strata, northline, carbon, vesper, bramble
```

Cycle backgrounds with `omarchy theme bg next` or the background switcher.

## What each theme contains

- `colors.toml` — the palette. Omarchy generates the terminal, Hyprland, btop,
  Neovim, VS Code and the rest from it.
- `backgrounds/` — 3840×2400 wallpapers (Graphite's photographic ones are
  upscaled to 7680×4800). Carbon, Meridian, Northline, Strata and Umbra each
  include minimal nature photographs alongside their abstract wallpapers.
  Bramble and Vesper each have their mark, a dark nature photograph, three
  minimal scenes in the spirit of Graphite's, and a corner lockup.
- `logo.svg` — Bramble's and Vesper's mark as a vector, pale line art plus
  the accent light.
- `preview.png` — the theme switcher preview.
- `shell.lock.toml` — the lock screen: a near-black password card over the
  blurred wallpaper, with a thin border in the accent that turns soft red
  after a wrong password. Omarchy merges it into the `[lock]` section of the
  generated `shell.toml`.
- `unlock.png` — the mark alone on a transparent background, for the boot
  disk-unlock screen (Plymouth).
- `preview-unlock.png` — the unlock screen preview, made with
  `omarchy plymouth preview`. It puts the theme in the unlock switcher
  (_Style > Unlock_ in the Omarchy menu). To use one from the terminal:

  ```bash
  omarchy plymouth set by theme umbra
  ```
- `icons.theme` — the Yaru icon colour that matches the accent.

## Backgrounds

The abstract wallpapers are drawn procedurally with NumPy and Pillow. The
additional nature photographs were generated with OpenAI image
generation and resized to 3840×2400. The later photographs in each theme
take inspiration from Graphite's very dark compositions and restrained light.
Graphite's former `11-orbits.png` is preserved in
[`retired-backgrounds/graphite/`](retired-backgrounds/graphite/) so it is no
longer one of the ten selectable backgrounds.
The procedural scripts are in [`tools/`](tools/):

| Script | Draws |
|---|---|
| `gen_bg.py` | Graphite landscapes (ridges, still lake, halo, night sky) |
| `gen_logo.py` | Graphite mark |
| `gen_pair.py` | Graphite extras, Strata, Northline and Carbon |
| `gen_umbra.py` | Umbra |
| `gen_meridian.py` | Meridian |
| `gen_marks.py` | The first logo studies (Strata, Umbra, Meridian, Northline) |
| `gen_unlock_*.py` | `unlock.png` for each theme, trimmed and centred by `unlock_centre.py` |
| `gen_nature.py` | The first nature theme marks, palettes and photograph crops (superseded for Bramble and Vesper) |
| `gen_bramble_vesper.py` | Bramble and Vesper: `logo.svg`, wallpapers, preview, `unlock.png` and lock card |

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
