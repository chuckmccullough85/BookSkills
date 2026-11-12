#!/usr/bin/env python3
"""
Create normalized input JSON for the meeting-notes-summarizer skill from text notes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build normalized meeting input JSON from a text notes file."
    )
    parser.add_argument("notes_file", help="Path to transcript/notes text file")
    parser.add_argument("--audience", default="team")
    parser.add_argument("--max-bullets", type=int, default=10)
    parser.add_argument("--action-item-owner-policy", default="keep_as_stated")
    parser.add_argument("--output", default="meeting_input.json")
    args = parser.parse_args()

    notes = Path(args.notes_file).read_text(encoding="utf-8")

    payload = {
        "input_format": "text",
        "meeting_text": notes,
        "audience": args.audience,
        "max_summary_bullets": args.max_bullets,
        "action_item_owner_policy": args.action_item_owner_policy,
        "sections_required": [
            "Summary",
            "Decisions",
            "Action Items",
            "Risks",
            "Open Questions",
        ],
        "defaults_if_missing": {
            "audience": "team",
            "max_summary_bullets": 10,
            "action_item_owner_policy": "keep_as_stated",
        },
    }

    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

