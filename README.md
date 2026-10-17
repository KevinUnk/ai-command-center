# AI Command Center — v2 (generic template)

A self-contained, dark-themed live dashboard that visualizes an AI-agent stack
on screen: voice/capture input → your runtime → your herd of CLI agents →
memory + CRM → compute (local rig vs rented GPU box).

This repository has been **sanitized and published as a clean, single-page
template (`index.html`)**. All personal details, IPs, or specific model
references have been scrubbed or moved to `config.json` so anyone can flip
it into their own asset.

## Files

- `index.html` — the app. One file, zero dependencies, works
  offline by double-click, or over any static host.
- `config.example.json` — template config with placeholders.
- `config.json` — YOUR config (make your copy from the example). The page
  loads this automatically when served over http(s). No file = clean
  built-in defaults.

## Make it yours

1. Copy `config.example.json` → `config.json` and edit:

   | key | what it controls |
   | --- | --- |
   | `brand.title / meta / runtime / hub / memoryName / crmName` | header + map labels, runtime node, memory and CRM node names |
   | `agents[]` | your CLI agents: name, version, role. Keep 4-6 for the stock map layout |
   | `computeLocal.*` | your rig spec, local model name, real tok/s (bar animates), monthly cost |
   | `computeGpu.*` | your rented box ip:port, gpu model, real tok/s, cost, status note |
   | `memory.*` | digest file path, excerpt lines, pipeline steps |
   | `cta.*` | join headline, your link, comment tag |
   | `ticker[]` | the rotating status strip (keep them true statements) |

2. Open `index.html` (double-click or serve it). Refresh after
   editing config.

## Wire it to your real system (LIVE mode)

The dashboard polls `live.json` (same folder) every 10 seconds. Whatever it
contains overrides the config — real versions, real digests, real throughput,
real status. The footer chip flips to a green **LIVE** when a source is
present and says **DEMO** when it's not — so the screen never lies about it.

- `producer.example.py` — a ready-made, stdlib-only producer that reads real
  data off any machine: agent versions (runs `--version` on each CLI), your
  latest memory digest (first lines), and GPU-box reachability (an ssh
  check that reports the honest "offline" state). Run it once or on cron:
  `*/5 * * * *  /usr/bin/python3 /path/to/producer.example.py`
- env overrides: `LIVE_DIGEST_DIR`, `LIVE_GPU_HOST`; swap the `AGENTS` list
  for your own CLIs.
- Or skip the script entirely: any of YOUR systems (cron, a watcher, your
  agents) can write `live.json` with the same shape — the dashboard doesn't
  care who wrote it.
- `live.json` is yours to generate; `config.example.json` is per-user static
  defaults; merge order is defaults ← config.json ← live.json.
- Never write secrets into live.json — the file sits next to public HTML.

## Keys

- `1`-`6` — scenes (map, demo, memory, compute, business, CTA)
- `N` — presenter cue card
- `H` — this guide overlay

## Honesty rule

The compute scene shows real values or "—", never invented numbers. If you
haven't benchmarked tok/s yet, leave `tok_s: 0` and it renders an empty bar.

## Host it

Any static server: GitHub Pages, S3/Cloudflare R2, `python3 -m http.server`,
or just email the HTML file. `config.json` only loads over http(s) — when
opened from `file://` the page uses its built-in defaults, so for a plain
file handoff, edit the defaults or attach the config alongside.

## Flip it

Rebrand it (scene 1 map, header), point the CTA at your funnel, replace the
ticker with your own ops status. v1 shows the full production version this
template was cut from — both files are MIT-style: do whatever you want with
them.