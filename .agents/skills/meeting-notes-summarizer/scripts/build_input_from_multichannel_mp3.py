#!/usr/bin/env python3
"""
Build normalized input JSON from multichannel MP3:
1) Detect channel count
2) Split channels to mono WAV files
3) Run Whisper per channel
4) Merge channel transcripts into one speaker-labeled transcript
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

TIME_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})"
)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def run_text(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def get_channel_count(mp3: Path) -> int:
    output = run_text(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=channels",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(mp3),
        ]
    )
    return int(output)


def split_channels(mp3: Path, workdir: Path, channels: int) -> list[Path]:
    files: list[Path] = []
    for index in range(channels):
        wav_file = workdir / f"channel_{index + 1}.wav"
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(mp3),
                "-filter_complex",
                f"[0:a]pan=mono|c0=c{index}[a]",
                "-map",
                "[a]",
                str(wav_file),
            ]
        )
        files.append(wav_file)
    return files


def transcribe_channel(wav_file: Path, model: str, language: str, outdir: Path) -> Path:
    run(
        [
            "whisper",
            str(wav_file),
            "--model",
            model,
            "--language",
            language,
            "--output_format",
            "srt",
            "--output_dir",
            str(outdir),
            "--temperature",
            "0",
        ]
    )
    return outdir / f"{wav_file.stem}.srt"


def parse_srt_entries(srt_file: Path, speaker_name: str) -> list[tuple[int, str, str]]:
    lines = srt_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    entries: list[tuple[int, str, str]] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit() and i + 2 < len(lines):
            time_line = lines[i + 1].strip()
            match = TIME_RE.match(time_line)
            if match:
                start_ms = (
                    int(match.group(1)) * 3600000
                    + int(match.group(2)) * 60000
                    + int(match.group(3)) * 1000
                    + int(match.group(4))
                )
                text_parts: list[str] = []
                j = i + 2
                while j < len(lines) and lines[j].strip():
                    text_parts.append(lines[j].strip())
                    j += 1
                content = " ".join(text_parts)
                if content:
                    entries.append((start_ms, speaker_name, content))
                i = j
            else:
                i += 1
        else:
            i += 1
    return entries


def resolve_speaker_name(channel_index: int, speaker_map: dict[str, str]) -> str:
    key = f"channel_{channel_index}"
    return speaker_map.get(key, f"Speaker {channel_index}")


def parse_speaker_map(values: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(
                f"Invalid speaker mapping '{item}'. Use channel_n=Name format."
            )
        key, value = item.split("=", 1)
        mapping[key.strip()] = value.strip()
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build normalized meeting input JSON from multichannel MP3."
    )
    parser.add_argument("mp3_file", help="Path to multichannel MP3")
    parser.add_argument("--audience", default="team")
    parser.add_argument("--max-bullets", type=int, default=10)
    parser.add_argument("--action-item-owner-policy", default="keep_as_stated")
    parser.add_argument("--model", default="small", help="Whisper model name")
    parser.add_argument("--language", default="en", help="Whisper language code")
    parser.add_argument(
        "--speaker-map",
        action="append",
        default=[],
        help="Map a channel to a speaker name, e.g. channel_1=Alex",
    )
    parser.add_argument("--workdir", default=".audio_work")
    parser.add_argument("--output", default="meeting_input.json")
    args = parser.parse_args()

    mp3_path = Path(args.mp3_file).resolve()
    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    speaker_map = parse_speaker_map(args.speaker_map)

    channel_count = get_channel_count(mp3_path)
    if channel_count < 2:
        parser.error("Expected an MP3 with at least two separate speaker channels.")
    wav_files = split_channels(mp3_path, workdir, channel_count)

    all_entries: list[tuple[int, str, str]] = []
    for index, wav_file in enumerate(wav_files, start=1):
        srt_file = transcribe_channel(wav_file, args.model, args.language, workdir)
        speaker_name = resolve_speaker_name(index, speaker_map)
        all_entries.extend(parse_srt_entries(srt_file, speaker_name))

    all_entries.sort(key=lambda item: item[0])
    if not all_entries:
        parser.error("Whisper produced no readable transcript entries.")
    merged_transcript = "\n".join(
        f"[{speaker}] {content}" for _, speaker, content in all_entries
    )

    payload = {
        "input_format": "mp3",
        "source_audio": str(mp3_path),
        "speaker_channels_detected": channel_count,
        "meeting_text": merged_transcript,
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
            "model": "small",
            "language": "en",
        },
    }

    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

