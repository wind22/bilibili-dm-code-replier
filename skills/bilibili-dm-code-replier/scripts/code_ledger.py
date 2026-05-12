#!/usr/bin/env python3
"""Allocate and record redemption codes for Bilibili DM replies."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path


LEDGER_FIELDS = ["code", "recipient", "sent_at", "source", "note"]


def read_codes(path: Path, code_column: str | None) -> list[str]:
    if not path.exists():
        raise SystemExit(f"codes file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    rows = [row for row in rows if row and any(cell.strip() for cell in row)]
    if not rows:
        return []

    header = [cell.strip() for cell in rows[0]]
    header_lower = [cell.lower() for cell in header]

    if code_column:
        if code_column not in header:
            raise SystemExit(f"code column '{code_column}' not found in {path}")
        index = header.index(code_column)
        data_rows = rows[1:]
    elif "code" in header_lower:
        index = header_lower.index("code")
        data_rows = rows[1:]
    elif len(rows[0]) == 1:
        first = rows[0][0].strip()
        data_rows = rows[1:] if first.lower() == "code" else rows
        index = 0
    else:
        raise SystemExit("multi-column CSV requires --code-column or a 'code' column")

    codes: list[str] = []
    seen: set[str] = set()
    for row in data_rows:
        if index >= len(row):
            continue
        code = row[index].strip()
        if code and code not in seen:
            codes.append(code)
            seen.add(code)
    return codes


def read_used_codes(path: Path) -> set[str]:
    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return set()
        if "code" not in reader.fieldnames:
            raise SystemExit(f"ledger missing 'code' column: {path}")
        return {row["code"].strip() for row in reader if row.get("code", "").strip()}


def ensure_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()


def command_next(args: argparse.Namespace) -> int:
    codes = read_codes(Path(args.codes), args.code_column)
    used = read_used_codes(Path(args.ledger))
    for code in codes:
        if code not in used:
            print(code)
            return 0
    print("no unused codes available", file=sys.stderr)
    return 2


def command_mark_sent(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    used = read_used_codes(ledger)
    if args.code in used:
        print(f"code already recorded: {args.code}", file=sys.stderr)
        return 2

    ensure_ledger(ledger)
    with ledger.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writerow(
            {
                "code": args.code,
                "recipient": args.recipient,
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "source": args.source or "",
                "note": args.note or "",
            }
        )
    print(f"recorded {args.code}")
    return 0


def command_stats(args: argparse.Namespace) -> int:
    codes = read_codes(Path(args.codes), args.code_column)
    used = read_used_codes(Path(args.ledger))
    unused = [code for code in codes if code not in used]
    print(f"total_codes={len(codes)}")
    print(f"used_codes={len(used)}")
    print(f"unused_codes={len(unused)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    next_parser = subparsers.add_parser("next", help="print the next unused code")
    next_parser.add_argument("--codes", required=True, help="CSV file containing codes")
    next_parser.add_argument("--ledger", required=True, help="CSV ledger of sent codes")
    next_parser.add_argument("--code-column", help="code column name when not 'code'")
    next_parser.set_defaults(func=command_next)

    mark_parser = subparsers.add_parser("mark-sent", help="append a successful send record")
    mark_parser.add_argument("--ledger", required=True, help="CSV ledger of sent codes")
    mark_parser.add_argument("--code", required=True, help="code that was sent")
    mark_parser.add_argument("--recipient", required=True, help="recipient display name or id")
    mark_parser.add_argument("--source", help="source codes CSV path")
    mark_parser.add_argument("--note", help="optional note")
    mark_parser.set_defaults(func=command_mark_sent)

    stats_parser = subparsers.add_parser("stats", help="show code counts")
    stats_parser.add_argument("--codes", required=True, help="CSV file containing codes")
    stats_parser.add_argument("--ledger", required=True, help="CSV ledger of sent codes")
    stats_parser.add_argument("--code-column", help="code column name when not 'code'")
    stats_parser.set_defaults(func=command_stats)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
