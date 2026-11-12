---
name: meeting-notes-summarizer
description: Summarize meeting notes into a consistent output template, prompting for missing inputs and optionally transcribing multichannel MP3 audio with Whisper.
---

# Meeting Notes Summarizer

Use this skill to turn meeting notes, transcript text, or audio-derived transcript text into a consistent summary output.

## When to use this skill

Use this skill when someone needs:

- concise meeting summaries
- clear decision tracking
- action items with owners and due dates
- risk and open-question capture

## Inputs

Expected inputs:

- `meeting_text` or `meeting_file_path` (required unless input is mp3)
- `audience` (optional, default: `team`)
- `max_summary_bullets` (optional, default: `10`)
- `action_item_owner_policy` (optional, default: `keep_as_stated`)
- `input_format` (optional: `text`, `transcript`, `mp3`)

If input is MP3, also expect:

- `audio_path`
- `speaker_map` (optional map, for example: `channel_1=Alex`, `channel_2=Riley`)
- `whisper_model` (optional, default: `small`)
- `whisper_language` (optional, default: `en`)

## Prompting for missing inputs

When required inputs are missing, ask once with this pattern:

1. List exactly what is missing.
2. Offer defaults where available.
3. Ask for confirmation before proceeding.

Example prompt:

`I am missing audience and max_summary_bullets. Use defaults (team, 10), or provide custom values?`

If only optional values are missing and defaults exist, continue using defaults and state which defaults were applied.

## Workflow

1. Validate input type.
2. If input is `text` or `transcript`, proceed to summarization.
3. If input is `mp3`, run transcription pre-step before summarization:
   - split multichannel audio (one speaker per channel)
   - transcribe each channel with Whisper
   - merge channel transcripts into one speaker-labeled transcript
4. Normalize entities (people, dates, action owners).
5. Generate output in the required template.
6. If an owner or due date is unclear, mark explicitly as `unknown` instead of guessing.

## Output template (required)

Always produce output in this structure:

```markdown
# Meeting Summary

## Summary
- ...

## Decisions
- Decision: ...
  - Context: ...

## Action Items
- Action: ...
  - Owner: ...
  - Due: ...
  - Status: open

## Risks
- ...

## Open Questions
- ...

## Applied Defaults
- audience: ...
- max_summary_bullets: ...
- action_item_owner_policy: ...
```

## Deterministic script usage

Use the scripts in `scripts/` for deterministic preparation:

- `build_input_from_notes.py`: build normalized input JSON from text notes/transcript.
- `build_input_from_multichannel_mp3.py`: split channels, transcribe with Whisper, merge speaker lines, and emit normalized input JSON.

## References (load on demand)

Most usage will be text input. Only load audio reference when `input_format=mp3`:

- `references/audio-transcription-whisper.md`

Load edge-case guidance as needed:

- `references/edge-cases.md`

