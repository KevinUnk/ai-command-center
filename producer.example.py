#!/usr/bin/env python3
"""
producer.example.py — wires REAL data from this machine into the Command Center.

Contract: this script writes ./live.json next to the dashboard HTML.
The dashboard polls live.json every 10s and swaps every value it contains
(defaults <- config.json <- live.json). No server needed, no secrets ever
written — keep it that way.

One-liner for your cron (every 5 min is plenty):
    */5 * * * *  /usr/bin/python3 /path/to/producer.example.py

Zero magic: every failure renders "—" in the dashboard, never a crash.
Adapt the reads below to YOUR system — screenpipe paths, your memory store,
your GPU box — this file is your starting point, not your destination.
"""
import json, os, subprocess, sys, time, socket

HERE      = os.path.dirname(os.path.abspath(__file__))
OUT       = os.path.join(HERE, "live.json")
DIGEST_DIR = os.environ.get("LIVE_DIGEST_DIR", os.path.expanduser("~/Work/daily-learn"))
DIGEST_GLOB  = ".md"
GPU_HOST     = os.environ.get("LIVE_GPU_HOST", "gpu")   # ssh alias or user@host
GPU_TIMEOUT  = 6
# "name:version_command" pairs — swap in your own agent CLIs
AGENTS = [
    ("CODEX",    ["codex", "--version"]),
    ("CLAUDE",   ["claude", "--version"]),
    ("OPENCODE", ["opencode", "--version"]),
    ("OMP",      ["omp", "--version"]),
    ("PI",       ["pi", "--version"]),
    ("AGENT 6",  None),
]

def run(cmd, timeout=8):
    if not cmd:
        return "—"
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        line = (out.stdout or out.stderr).strip().splitlines()
        return (line[0] if line else "—")[:40]
    except Exception:
        return "—"

def latest_digest():
    try:
        files = sorted(f for f in os.listdir(DIGEST_DIR) if f.endswith(DIGEST_GLOB))
        if not files:
            return None, []
        name = files[-1]
        with open(os.path.join(DIGEST_DIR, name), encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        excerpt = [l.strip() for l in lines if l.strip() and not l.startswith("#")][:4]
        return name, excerpt
    except Exception:
        return None, []

def gpu_status():
    """Real reachability + GPU line; shows the honest STANDBY state when down."""
    try:
        out = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4", GPU_HOST,
             "nvidia-smi -L 2>/dev/null | head -1 || echo online"],
            capture_output=True, text=True, timeout=GPU_TIMEOUT)
        line = (out.stdout or out.stderr).strip().splitlines()
        if not line:
            return "—", "ssh ok but empty"
        s = line[0]
        if "refused" in s or "timeout" in s or "unreachable" in s:
            return "—", "box offline — connection refused"
        if s.lower().startswith("gpu"):
            return s[:48], "reachable"
        return "—", s[:48]
    except Exception:
        return "—", "box offline — unreachable"

def main():
    digest_name, digest_excerpt = latest_digest()

    agents = []
    for name, cmd in AGENTS:
        agents.append({"name": name, "ver": run(cmd), "role": "cli agent"})

    gpu_name, gpu_note = gpu_status()

    payload = {
        "agents": agents,
        "memory": {
            "digest": os.path.join(DIGEST_DIR, digest_name) if digest_name else "—",
            "excerpt": digest_excerpt or ["no digest found yet — point LIVE_DIGEST_DIR at your memory output"],
        },
        "computeGpu": {
            "addr": GPU_HOST,
            "note": gpu_note,
            "model": gpu_name if gpu_name != "—" else "—",
            "tokLabel": "— for now —",
        },
        "ticker": [
            "[producer] live.json written %s" % time.strftime("%H:%M:%S"),
            "[machine] up %s · %d agents probed" % (run(["sh", "-c", "echo $(( $(cat /proc/uptime | cut -d. -f1) / 3600 ))h"]), len(agents)),
            "[memory] %s" % (digest_name or "no digest"),
            "[gpu] %s" % gpu_note,
        ],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print("wrote %s" % OUT)
    print(json.dumps(payload, indent=2, ensure_ascii=False)[:1200])

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never leave the dashboard blind
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump({"ticker": ["[producer] error: %s" % exc]}, fh, ensure_ascii=False)
        print("producer error: %s" % exc, file=sys.stderr)
        sys.exit(1)