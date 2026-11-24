#!/usr/bin/env python3
"""Obscurant voice helper: wake word + command capture, entirely on this computer.

Reads the microphone through PipeWire/PulseAudio (parecord), cuts speech into utterances with a
simple energy gate, and runs whisper.cpp on each one inside a sandbox that has no network and no
file access beyond the model. Speech that does not start with the wake phrase is thrown away
immediately: nothing is saved, logged or sent. Only recognised commands are written to stdout as
JSON lines. The browser can send {"arm": seconds} on stdin to take the next utterance without a
wake phrase (used for yes/no answers).

  obscurant-voice.py --model M --whisper whisper-cli --wake "hey browser"
  obscurant-voice.py --input some.wav ...        (feed a recording instead of the microphone)
  obscurant-voice.py --check-wake "hey browser open youtube" --wake "hey browser"
"""
import argparse, difflib, hashlib, json, os, re, shutil, signal, subprocess, sys, threading, time, wave
import numpy as np

RATE = 16000
FAST = ["-bs", "1", "-bo", "1", "-nf", "-ac", "768", "-t", "8"]
# Whisper decodes short, noisy clips far better when it is told what kind of words to expect.
PROMPT = ("Hey Obscurity. New tab. Close tab. Scroll down. Scroll up. Go back. Reload. "
          "Open YouTube. Search for. Zoom in. Yes. No. Stop listening.")
FRAME = 480                      # 30 ms
MIN_SPEECH_S = 0.3
MAX_UTTERANCE_S = 7.0
END_SILENCE_S = 0.45
PINNED = {"ggml-base.en.bin": "a03779c86df3323075f5e796cb2ce5029f00ec8869eee3fdfb897afe36c6d002"}


def out(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def norm(text):
    text = text.lower()
    text = re.sub(r"\[[^\]]*\]|\([^)]*\)", " ", text)       # [BLANK_AUDIO], (music)
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def aliases(wake):
    base = norm(wake)
    out = [base]
    if base.startswith("hey "):
        word = base[4:]
        out += ["a " + word, word]
        if word == "obscurity":
            out += ["obscured"]
    return out


def split_wake(text, wake):
    """('rest', True) when the text holds the wake phrase in its first few words, else ('', False).
    The command is what follows it, up to the next wake phrase. Strict on purpose: a near miss
    like 'hey brother' must not wake it. One extra word is tried because the recogniser sometimes
    splits one word in two ('obscure city')."""
    words = norm(text).split()
    phrases = aliases(wake)

    def match_at(i):
        for phrase in phrases:
            n = len(phrase.split())
            squashed = phrase.replace(" ", "")
            for k in (n, n + 1):
                if i + k <= len(words) and difflib.SequenceMatcher(None, "".join(words[i:i + k]), squashed).ratio() >= 0.92:
                    return k
        return 0

    for start in range(min(3, len(words))):
        k = match_at(start)
        if k:
            rest, i = [], start + k
            while i < len(words) and not match_at(i):
                rest.append(words[i])
                i += 1
            return " ".join(rest), True
    return "", False


def sandbox_cmd(whisper, model, prompt):
    """(is_sandboxed, argv). The argv contains FD, replaced by a pipe carrying the audio, which
    bwrap turns into a file that exists only inside the sandbox's memory-backed /tmp."""
    bwrap = shutil.which("bwrap")
    flags = ["-m", "/model.bin", "-f", "/tmp/in.wav", "-nt", "-np", "-ng", "-l", "en", "--prompt", prompt, *FAST]
    if not bwrap:
        return None, None
    exe = os.path.realpath(whisper if whisper.startswith("/") else (shutil.which(whisper) or whisper))
    cmd = [
        bwrap, "--unshare-all", "--die-with-parent", "--new-session",
        "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib", "/lib64",
        "--symlink", "usr/bin", "/bin", "--ro-bind", model, "/model.bin",
        "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--cap-drop", "ALL",
        "--file", "FD", "/tmp/in.wav", exe,
    ] + flags
    return True, cmd


def boost(audio):
    """Bring a quiet microphone up to a level the recogniser likes. The gain follows how loud the
    speech is (90th percentile of 30 ms frames), not the highest click, and is capped."""
    n = (len(audio) // FRAME) * FRAME
    if n < FRAME:
        return audio.astype(np.int16)
    rms = np.sqrt((audio[:n].reshape(-1, FRAME) ** 2).mean(axis=1))
    loud = float(np.percentile(rms, 90)) or 1.0
    gain = float(np.clip(3500.0 / loud, 1.0, 60.0))
    return np.clip(audio * gain, -32000, 32000).astype(np.int16)


def wav_bytes(samples):
    import io
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(samples.tobytes())
    return buf.getvalue()


def transcribe(cmd, samples):
    data = wav_bytes(samples)
    try:
        if "FD" in cmd:                                   # sandboxed: audio goes through a pipe
            r_fd, w_fd = os.pipe()
            argv = [str(r_fd) if x == "FD" else x for x in cmd]
            p = subprocess.Popen(argv, pass_fds=[r_fd], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            os.close(r_fd)
            def feed():
                with os.fdopen(w_fd, "wb") as w:
                    try: w.write(data)
                    except BrokenPipeError: pass
            threading.Thread(target=feed, daemon=True).start()
            stdout, _ = p.communicate(timeout=40)
            return stdout.decode("utf-8", "replace").strip()
        # no bwrap: a RAM-backed file (/dev/shm), mode 0600, removed straight away
        path = f"/dev/shm/obscurant-voice-{os.getpid()}.wav"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        try:
            r = subprocess.run(cmd + ["-f", path], capture_output=True, timeout=40)
        finally:
            os.unlink(path)
        return r.stdout.decode("utf-8", "replace").strip()
    except Exception as ex:
        out({"type": "error", "message": f"recognizer failed: {ex}"})
        return ""


def frames_from_mic():
    p = subprocess.Popen(["parecord", "--raw", f"--rate={RATE}", "--channels=1", "--format=s16le", "--latency-msec=60"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        while True:
            b = p.stdout.read(FRAME * 2)
            if len(b) < FRAME * 2:
                return
            yield np.frombuffer(b, dtype=np.int16)
    finally:
        p.terminate()


def frames_from_file(path):
    with wave.open(path, "rb") as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    data = np.concatenate([np.zeros(RATE // 2, np.int16), data, np.zeros(RATE * 2, np.int16)])
    for i in range(0, len(data) - FRAME, FRAME):
        yield data[i:i + FRAME]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--whisper", default="whisper-cli")
    ap.add_argument("--wake", default="hey obscurity"); ap.add_argument("--input")
    ap.add_argument("--check-wake"); ap.add_argument("--no-sandbox", action="store_true"); ap.add_argument("--debug", action="store_true"); ap.add_argument("--debug-text", action="store_true"); ap.add_argument("--standalone", action="store_true"); ap.add_argument("--once", action="store_true"); ap.add_argument("--vocab", default=""); ap.add_argument("--arm-start", type=float, default=0.0)
    a = ap.parse_args()

    if a.check_wake is not None:
        rest, ok = split_wake(a.check_wake, a.wake)
        print(json.dumps({"wake": ok, "rest": rest})); return

    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:   # die with the browser
        import ctypes; ctypes.CDLL("libc.so.6").prctl(1, signal.SIGTERM)
    except Exception:
        pass
    if not a.model or not os.path.isfile(a.model):
        out({"type": "error", "message": "model file missing"}); return 2
    want = PINNED.get(os.path.basename(a.model))
    if want:
        st = os.stat(a.model)
        marker = a.model + ".verified"
        known = False
        try:
            with open(marker) as f:
                m = json.load(f)
            known = m.get("size") == st.st_size and m.get("mtime_ns") == st.st_mtime_ns and m.get("sha256") == want
        except Exception:
            pass
        if not known:
            h = hashlib.sha256()
            with open(a.model, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            if h.hexdigest() != want:
                out({"type": "error", "message": "model file does not match its pinned checksum; refusing to run it"}); return 3
            try:
                with open(marker, "w") as f:
                    json.dump({"size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": want}, f)
            except OSError:
                pass
    sandboxed, cmd = (None, None)
    if not a.no_sandbox:
        prompt = (PROMPT + " " + a.vocab.strip())[:900]
        sandboxed, cmd = sandbox_cmd(a.whisper, a.model, prompt)
    if cmd is None or sandboxed is None:
        cmd = [a.whisper, "-m", a.model, "-nt", "-np", "-ng", "-l", "en", "--prompt", (PROMPT + " " + a.vocab.strip())[:900], *FAST]
        out({"type": "warning", "message": "running without a sandbox (bwrap not found)"})

    armed_until = [0.0]
    sticky = [False]
    def stdin_reader():
        for line in sys.stdin:
            try:
                m = json.loads(line)
                if "arm" in m:
                    armed_until[0] = time.time() + float(m["arm"])
                    sticky[0] = bool(m.get("sticky"))
            except Exception:
                pass
        if not a.standalone:
            os._exit(0)
    threading.Thread(target=stdin_reader, daemon=True).start()

    if a.arm_start:
        armed_until[0] = time.time() + a.arm_start
    out({"type": "state", "state": "listening", "sandboxed": bool(sandboxed)})
    # Microphones often carry a constant offset (yours is ~6000). It must come off before anything
    # is measured, and the thresholds are relative to the room's own noise, not fixed numbers.
    dc, noise = None, 40.0
    buf, speech_frames, silent, in_speech = [], 0, 0, False
    src = frames_from_file(a.input) if a.input else frames_from_mic()
    n_frames, last_dbg = 0, time.time()
    for raw in src:
        f = raw.astype(np.float32)
        m = float(f.mean())
        dc = m if dc is None else 0.995 * dc + 0.005 * m
        fr = f - dc
        e = float(np.sqrt(np.mean(fr ** 2)))
        start_thr = max(noise * 2.6, 90.0)
        keep_thr = max(noise * 1.7, 60.0)
        n_frames += 1
        if a.once and not in_speech and time.time() > armed_until[0] + 1.0 and n_frames > 20:
            break
        if a.debug and time.time() - last_dbg > 2:
            last_dbg = time.time()
            sys.stderr.write(f"level {e:.0f} noise {noise:.0f} start>{start_thr:.0f} dc {dc:.0f}\n"); sys.stderr.flush()
        if not in_speech:
            noise = 0.97 * noise + 0.03 * min(e, noise * 3 + 30)      # tracks the room, ignores speech bursts
            if e > start_thr and n_frames > 20:
                in_speech, buf, speech_frames, silent = True, [fr], 1, 0
            continue
        buf.append(fr)
        loud = e > keep_thr
        speech_frames += 1 if loud else 0
        silent = 0 if loud else silent + 1
        dur = len(buf) * FRAME / RATE
        if silent * FRAME / RATE >= END_SILENCE_S or dur >= MAX_UTTERANCE_S:
            in_speech = False
            if speech_frames * FRAME / RATE >= MIN_SPEECH_S:
                audio = np.concatenate(buf)
                audio = boost(audio)
                text = transcribe(cmd, audio)
                armed = time.time() < armed_until[0]
                if a.debug_text:        # developer test only: shows the recognizer's raw text
                    sys.stderr.write(f"TEXT: {text!r}\n"); sys.stderr.flush()
                if a.debug:
                    sys.stderr.write(f"utterance {dur:.1f}s heard={'yes' if text else 'nothing'}\n"); sys.stderr.flush()
                if armed:
                    if not sticky[0]:
                        armed_until[0] = 0.0
                    out({"type": "command", "text": norm(text), "armed": True})
                    if a.once:
                        break
                else:
                    rest, ok = split_wake(text, a.wake)
                    if ok and rest:
                        out({"type": "wake"})
                        out({"type": "command", "text": rest, "armed": False})
                    elif ok:
                        armed_until[0] = time.time() + 6.0
                        out({"type": "state", "state": "armed"})
                # anything else: dropped here, never stored or reported
            buf = []
    out({"type": "state", "state": "stopped"})


if __name__ == "__main__":
    sys.exit(main() or 0)
