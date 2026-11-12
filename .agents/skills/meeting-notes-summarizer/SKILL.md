---
name: meeting-notes-summarizer
description: Turn meeting notes or transcripts into a concise summary of decisions, action items, risks, and open questions. Use for meeting recap requests, including multichannel MP3 recordings when transcription tools are available.
---

# Meeting notes summarizer

Use the notes or transcript the user provides. If neither is available, ask for it. Follow any audience, length, or format preferences in the request; otherwise write a brief recap for meeting participants.

## Workflow

1. Read the source and distinguish decisions from proposals, and commitments from suggestions.
2. Extract the main discussion points, decisions, action items, risks, and unresolved questions. Combine duplicates without losing distinct owners or deadlines.
3. Check each claim against the source. Keep names and dates as stated. Mark an action item's missing owner or due date as `unknown`; do not invent one.
4. Write the recap using the template below. Use `None recorded` for an empty section, and omit sections the user explicitly does not want.

If the source is a multichannel MP3 with one speaker per channel, read [the audio guide](references/audio-transcription-whisper.md) and use `scripts/build_input_from_multichannel_mp3.py` to prepare a speaker-labeled transcript. The helper requires `ffmpeg`, `ffprobe`, and the Whisper CLI. For other audio, use an available transcription method and label speakers only when supported by the recording.

## Output template

```markdown
# Meeting Summary

## Summary
- [Key point]

## Decisions
- [Decision and relevant context]

## Action Items
- [Action] — Owner: [name or unknown]; Due: [date or unknown]

## Risks
- [Risk]

## Open Questions
- [Unresolved question]
```

Before finishing, verify that every decision and action item is supported by the source, and that uncertain attribution or conflicting statements are flagged in Open Questions.

