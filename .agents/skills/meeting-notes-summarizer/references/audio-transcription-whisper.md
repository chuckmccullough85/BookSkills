# Multichannel MP3 transcription

Use this only when each audio channel contains a separate speaker. A stereo recording with mixed speakers does not meet that assumption.

Requires `ffmpeg`, `ffprobe`, the Whisper CLI, and Python 3 on PATH. Transcription can contain errors, so review names, dates, and commitments against the recording when accuracy matters.

Run from the skill directory:

```bash
python scripts/build_input_from_multichannel_mp3.py meeting.mp3 --speaker-map channel_1=Alex --speaker-map channel_2=Riley --output meeting_input.json
```

The script detects channels, transcribes each separately, and writes JSON. Read its `meeting_text` field for the summary. Omit `--speaker-map` when names are unknown; the transcript will use `Speaker 1`, `Speaker 2`, and so on. The default Whisper model is `small` and the default language is English; use `--model` or `--language` when needed.

If a required command fails or the transcript is empty, report the problem and ask for notes or a transcript rather than inventing a recap.

