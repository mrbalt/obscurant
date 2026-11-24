#!/bin/sh
# Live microphone test: prints what the recognizer hears. Ctrl+C to stop. For testing only.
exec python3 "$(dirname "$0")/obscurant-voice.py" --model "$HOME/.local/share/obscurant/voice/ggml-base.en.bin" \
  --wake "${1:-hey obscurity}" --standalone --debug-text
