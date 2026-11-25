# NTCHELP, INC.

Corporate site for **NTCHELP, INC.** — the parent company behind the
[NanoTech Computing](/nanotech/) and [SASSYSQRL](/sassysqrl/) brands.
Hosted on GitHub Pages at <https://ntchelp.com>.

## Structure

| Path | What it is |
|------|------------|
| `/` | Corporate homepage (brands, history, leadership) |
| `/nanotech/` | NanoTech Computing — remote business tech support (DBA) |
| `/nanotech/testimonials/` | Client testimonials |
| `/sassysqrl/` | SASSYSQRL — organic dry shampoo (DBA) |
| `/blog/` | Product notes & reviews |
| `/legal` | Legal / Amazon affiliate disclosure |
| `/accolades` | Redirects to testimonials |
| `/cam` | Live camera stream (HLS) |

### Games

Single-file, dependency-free HTML5 canvas games (no build step — drop in a
`.html` and it ships):

- `/space-breakout` — Space Breakout
- `/asteroids` — Asteroids
- `/tetris` — Tetris
- `/snake` — Snake
- `/flappy` — Flappy (rocket)

All share one design language (dark space theme, CSS-variable palette, HUD,
procedural WebAudio SFX, localStorage high score, touch controls).

## Building

- **Jekyll** static site (`_config.yml`, `_layouts/`, `_includes/`), deployed
  automatically by GitHub Pages from `main` (CNAME → `ntchelp.com`).
- Games and `cam.html` are plain static files — Jekyll copies them through
  as-is.
- The `blog` symlink → `BLOG/` (posts live in `BLOG/*.md`).

## Notes

- `.gitignore` excludes `local/`, `__pycache__`, `.log`. Keep secrets out of
  the repo — deploy auth lives in `~/.git-credentials`, never committed.
- To add a game: create `<name>.html`, commit, push. It's live after the
  Pages build.
