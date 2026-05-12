#!/usr/bin/env python3
"""Append categorized non-code Bilibili DM issue records."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path


FIELDS = ["recipient", "category", "message", "recorded_at", "source_url", "note"]
VALID_CATEGORIES = {"产品体验问题", "加速体验问题", "其他问题"}


def ensure_log(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()


def command_append(args: argparse.Namespace) -> int:
    if args.category not in VALID_CATEGORIES:
        allowed = ", ".join(sorted(VALID_CATEGORIES))
        raise SystemExit(f"invalid category: {args.category}. Allowed: {allowed}")

    log_path = Path(args.log)
    ensure_log(log_path)
    with log_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writerow(
            {
                "recipient": args.recipient,
                "category": args.category,
                "message": args.message,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "source_url": args.source_url or "",
                "note": args.note or "",
            }
        )
    print(f"recorded issue for {args.recipient}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    append_parser = subparsers.add_parser("append", help="append a non-code issue record")
    append_parser.add_argument("--log", required=True, help="CSV issue log path")
    append_parser.add_argument("--recipient", required=True, help="recipient display name or id")
    append_parser.add_argument("--category", required=True, help="产品体验问题, 加速体验问题, or 其他问题")
    append_parser.add_argument("--message", required=True, help="visible other-party message content")
    append_parser.add_argument("--source-url", help="Bilibili DM URL or other source")
    append_parser.add_argument("--note", help="optional note")
    append_parser.set_defaults(func=command_append)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
