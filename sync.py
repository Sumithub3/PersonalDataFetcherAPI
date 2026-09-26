#!/usr/bin/env python3
"""Pulls SMS and call log via Termux:API and writes sms.csv / calls.csv next to this script."""
import csv
import json
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent


def run_termux_api(*args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30, check=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Failed to run {' '.join(args)}: {e}", file=sys.stderr)
        return []


def write_csv(filename, records):
    if not records:
        print(f"No records for {filename}, skipping write")
        return
    fieldnames = []
    seen = set()
    for r in records:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)
    path = OUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"Wrote {len(records)} rows to {path}")


def main():
    sms = run_termux_api("termux-sms-list", "-l", "2000")
    write_csv("sms.csv", sms)

    calls = run_termux_api("termux-call-log", "-l", "2000")
    write_csv("calls.csv", calls)


if __name__ == "__main__":
    main()
