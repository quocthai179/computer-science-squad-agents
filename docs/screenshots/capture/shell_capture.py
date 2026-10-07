#!/usr/bin/env python3
"""Run a list of shell commands in a real interactive bash inside pyte; save the final screen.

usage: shell_capture.py --cwd DIR --out FRAME.json --cmds FILE [--cols 118 --rows 50]
Lines in FILE starting with '#!' are run silently before capture (setup); a line '#clear' clears the screen.
"""
import argparse, fcntl, json, os, pty, select, struct, termios, time
import pyte

ap = argparse.ArgumentParser()
ap.add_argument("--cwd", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--cmds", required=True)
ap.add_argument("--cols", type=int, default=118)
ap.add_argument("--rows", type=int, default=50)
a = ap.parse_args()

screen = pyte.Screen(a.cols, a.rows)
stream = pyte.ByteStream(screen)
pid, fd = pty.fork()
if pid == 0:
    os.chdir(a.cwd)
    env = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"], "TERM": "xterm-256color", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
           "PS1": "\\[\\e[1;32m\\]~/ls-project\\[\\e[0m\\] \\[\\e[1;34m\\]$\\[\\e[0m\\] "}
    os.execvpe("bash", ["bash", "--noprofile", "--norc", "-i"], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", a.rows, a.cols, 0, 0))


def pump(secs):
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            stream.feed(os.read(fd, 65536))


def run(line, wait):
    for ch in line:
        os.write(fd, ch.encode()); pump(0.005)
    os.write(fd, b"\r")
    pump(0.4)
    end = time.time() + 120
    while time.time() < end:
        cur = screen.display[screen.cursor.y].rstrip()
        if cur.endswith("$") and "ls-project" in cur:
            break
        pump(0.2)
    pump(0.2)


pump(0.5)
for line in open(a.cmds).read().splitlines():
    if not line.strip():
        continue
    if line.startswith("#!"):
        run(line[2:].strip() + " >/dev/null 2>&1", 1.0)
    elif line.strip() == "#clear":
        run("clear", 0.5)
    else:
        run(line, 2.5)
pump(1)
rows = [[[c.data, c.fg, c.bg, c.bold, c.italics, c.reverse] for c in (screen.buffer[y][x] for x in range(a.cols))]
        for y in range(a.rows)]
json.dump({"t": 0, "rows": rows, "text": "\n".join(screen.display)}, open(a.out, "w"))
print("\n".join(l.rstrip() for l in screen.display))
