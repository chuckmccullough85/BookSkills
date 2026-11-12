# Audio transcription with Whisper (load on demand)

Load this reference only when `input_format=mp3`.

## Assumptions

- Input MP3 is multichannel.
- One channel represents one speaker.
- `ffmpeg`, `ffprobe`, and `whisper` CLI are installed and on PATH.

## Steps

1. Detect channel count from the audio stream.
2. Split each channel to mono WAV:
   - `channel_1.wav`, `channel_2.wav`, and so on.
3. Transcribe each WAV with Whisper to SRT.
4. Parse each SRT and attach speaker label:
   - `channel_1` -> `Speaker 1` unless mapped by `speaker_map`.
5. Merge all lines by timestamp ascending into one transcript.
6. Pass merged transcript as `meeting_text` into the summarization flow.

## Suggested command shape

```text
whisper <wav_file> --model small --language en --output_format srt --temperature 0
```

## Failure handling

- If no channels are detected, fail with explicit error.
- If Whisper fails for any channel, stop and report that channel.
- If timestamps are malformed, skip malformed block and continue, then report skipped count.

## Notes

- Audio processing is heavier than text flow, so keep it out of the default skill path.
- Use `speaker_map` when known names are available to improve summary quality.

