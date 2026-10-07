#!/usr/bin/env python3
"""Drive an interactive `claude` TUI in a pty, emulate the screen with pyte,
and save colored snapshots (JSON) periodically.

usage: tui_capture.py --cwd DIR --out DIR --prompt TEXT [--cols 110 --rows 42 --timeout 900]
"""
import argparse, fcntl, json, os, pty, select, signal, struct, sys, termios, time
import pyte

ap = argparse.ArgumentParser()
ap.add_argument("--cwd", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--prompt", required=True)
ap.add_argument("--plugin-dir", default="lab")
ap.add_argument("--cols", type=int, default=110)
ap.add_argument("--rows", type=int, default=42)
ap.add_argument("--timeout", type=int, default=900)
ap.add_argument("--idle", type=int, default=45, help="seconds of unchanged screen (not busy) to stop")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

screen = pyte.Screen(a.cols, a.rows)
stream = pyte.ByteStream(screen)

cmd = ["claude", "--plugin-dir", a.plugin_dir,
       "--allowedTools", "Bash", "Read", "Write", "Edit", "Glob", "Grep", "Agent", "Skill", "WebSearch", "WebFetch"]
pid, fd = pty.fork()
if pid == 0:
    os.chdir(a.cwd)
    os.environ.pop("CLAUDE_CODE_CHILD_SESSION", None)
    os.environ.update(TERM="xterm-256color", COLORTERM="truecolor", COLUMNS=str(a.cols), LINES=str(a.rows))
    os.execvp(cmd[0], cmd)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", a.rows, a.cols, 0, 0))


def text():
    return "\n".join(screen.display)


def snap(i):
    rows = []
    for y in range(screen.lines):
        line = screen.buffer[y]
        rows.append([[line[x].data, line[x].fg, line[x].bg, line[x].bold, line[x].italics, line[x].reverse]
                     for x in range(screen.columns)])
    with open(os.path.join(a.out, f"frame-{i:04d}.json"), "w") as f:
        json.dump({"t": round(time.time() - t0, 1), "rows": rows, "text": text()}, f)


def send(s, delay=0.03):
    for ch in s:
        os.write(fd, ch.encode())
        time.sleep(delay)


t0 = time.time()
state = "boot"
last_text, last_change, frame, last_snap = "", time.time(), 0, 0.0
handled_prompts = 0
boot_enters = 0
while time.time() - t0 < a.timeout:
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            data = os.read(fd, 65536)
        except OSError:
            break
        if not data:
            break
        stream.feed(data)
    tx = text()
    low = tx.lower()
    if tx != last_text:
        last_text, last_change = tx, time.time()
    # boot: accept default of every onboarding / trust dialog until the input box is ready
    ready = "? for shortcuts" in low or "for shortcuts" in low
    if state == "boot" and not ready and time.time() - last_change > 2.5 and tx.strip():
        if boot_enters < 12:
            if "yes, i trust this folder" in low and "❯ no, exit" in low:
                send("\x1b[B"); time.sleep(0.4)
            send("\r"); boot_enters += 1; last_change = time.time()
        continue
    if state == "boot" and ready and time.time() - last_change > 2:
        send(a.prompt, 0.02)
        time.sleep(1.0)
        snap(frame); frame += 1
        send("\r")
        time.sleep(0.8)
        tt = text().lower()
        if a.prompt.startswith("/") and "esc to interrupt" not in tt and a.prompt.split()[0].lower() in tt:
            send("\r")
        state = "running"
        last_change = time.time()
        continue
    if state == "running" and "do you want to" in low and "1. yes" in low:
        time.sleep(0.8); snap(frame); frame += 1; send("\r"); handled_prompts += 1; time.sleep(1); continue
    if time.time() - last_snap > 2:
        snap(frame); frame += 1; last_snap = time.time()
    busy = "esc to interrupt" in low or "running" in low and "agent" in low
    if state == "running" and not busy and time.time() - last_change > a.idle:
        break

snap(frame)
print(f"frames={frame + 1} elapsed={time.time() - t0:.0f}s permission_prompts={handled_prompts}")
try:
    os.kill(pid, signal.SIGTERM)
except ProcessLookupError:
    pass
