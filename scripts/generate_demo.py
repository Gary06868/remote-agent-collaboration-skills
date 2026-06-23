from __future__ import annotations

import hashlib
import html
import json
import os
import struct
import subprocess
import sys
import tempfile
import textwrap
import zlib
from pathlib import Path


WIDTH = 900
HEIGHT = 520
SCALE = 2

PALETTE = [
    (248, 250, 252),  # 0 canvas
    (15, 23, 42),     # 1 terminal
    (30, 41, 59),     # 2 terminal chrome
    (226, 232, 240),  # 3 muted line
    (236, 253, 245),  # 4 terminal text
    (20, 184, 166),   # 5 teal
    (37, 99, 235),    # 6 blue
    (249, 115, 22),   # 7 orange
    (239, 68, 68),    # 8 red
    (34, 197, 94),    # 9 green
    (250, 204, 21),   # 10 yellow
    (100, 116, 139),  # 11 slate
    (255, 255, 255),  # 12 white
    (219, 234, 254),  # 13 blue pale
    (204, 251, 241),  # 14 teal pale
    (255, 237, 213),  # 15 orange pale
]

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "\\": ["10000", "01000", "01000", "00100", "00010", "00010", "00001"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
    "=": ["00000", "11111", "00000", "11111", "00000", "00000", "00000"],
    ">": ["10000", "01000", "00100", "00010", "00100", "01000", "10000"],
    "<": ["00001", "00010", "00100", "01000", "00100", "00010", "00001"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "#": ["01010", "11111", "01010", "01010", "11111", "01010", "01010"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def write_text_lf(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def run_cli(work: Path, args: list[str]) -> tuple[str, bool]:
    env = os.environ.copy()
    src = repo_root() / "src"
    env["PYTHONPATH"] = str(src) + os.pathsep + env.get("PYTHONPATH", "")
    env["RAC_FIXED_TIME_UTC"] = "2026-06-23T07:00:00Z"
    cmd = [sys.executable, "-m", "remote_agent_collaboration.cli", *args]
    result = subprocess.run(cmd, cwd=work, check=False, text=True, capture_output=True, env=env)
    output = (result.stdout or result.stderr).strip()
    line = "$ collabctl " + " ".join(args)
    return line + "\n" + (output or f"exit {result.returncode}"), result.returncode == 0


def build_transcript() -> tuple[str, list[str]]:
    root = repo_root()
    blocks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="rac-demo-") as tmp:
        work = Path(tmp)

        lead_skill = root / "skills" / "team-lead-collaboration" / "SKILL.md"
        member_skill = root / "skills" / "team-member-collaboration" / "SKILL.md"
        lead_yaml = (root / "skills" / "team-lead-collaboration" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        member_yaml = (root / "skills" / "team-member-collaboration" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        skill_check = [
            "$ verify bundled Skills",
            f"OK team-lead-collaboration: {lead_skill.exists()}",
            f"OK team-member-collaboration: {member_skill.exists()}",
            f"OK allow_implicit_invocation=false: {'allow_implicit_invocation: false' in lead_yaml and 'allow_implicit_invocation: false' in member_yaml}",
        ]
        blocks.append("\n".join(skill_check))

        commands = [
            ["init", "--project-id", "demo", "--yes"],
            ["actor", "bootstrap", "--actor-id", "lead", "--role", "lead", "--yes"],
            ["session", "activate", "--session-id", "thread-lead", "--role", "lead", "--skill", "team-lead-collaboration", "--actor-id", "lead"],
            ["member", "add", "--session-id", "thread-lead", "--actor-id", "member", "--role", "member", "--modules", "docs"],
            ["module", "add", "--session-id", "thread-lead", "--module-id", "docs", "--members", "member", "--allowed-paths", "docs"],
            ["session", "activate", "--session-id", "thread-lead", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "member"],
            ["session", "activate", "--session-id", "thread-member", "--role", "member", "--skill", "team-member-collaboration", "--actor-id", "member"],
            ["announce", "publish", "--session-id", "thread-lead", "--announcement-id", "ann-1", "--title", "Release-plan", "--summary", "Read-before-work", "--acknowledgement-required"],
            ["announce", "acknowledge", "--session-id", "thread-member", "--announcement-id", "ann-1"],
            ["task", "create", "--session-id", "thread-lead", "--task-id", "task-1", "--title", "Docs-update", "--module-id", "docs", "--owner", "member"],
            ["task", "accept", "--session-id", "thread-member", "--task-id", "task-1"],
            ["task", "start", "--session-id", "thread-member", "--task-id", "task-1"],
            ["log", "append", "--session-id", "thread-member", "--module-id", "docs", "--task-id", "task-1", "--summary", "Updated-docs-fixture"],
            ["request", "create", "--session-id", "thread-member", "--request-id", "req-compact", "--type", "log_compaction", "--summary", "Please-compact-logs"],
            ["log", "compact", "--session-id", "thread-member", "--module-id", "docs"],
            ["log", "compact", "--session-id", "thread-lead", "--module-id", "docs"],
        ]
        for args in commands:
            block, _ok = run_cli(work, args)
            blocks.append(block)

        manifests = sorted((work / ".collaboration" / "logs" / "archive" / "modules" / "docs").glob("*.manifest.json"))
        manifest = json.loads(manifests[-1].read_text(encoding="utf-8"))
        archive = work / manifest["archive_path"]
        actual_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
        blocks.append("\n".join([
            "$ verify archive sha256",
            f"OK manifest archive_sha256: {manifest['archive_sha256']}",
            f"OK recalculated sha256: {actual_hash}",
            f"OK match: {actual_hash == manifest['archive_sha256']}",
        ]))

    return "\n\n".join(blocks) + "\n", blocks


def wrap_lines(blocks: list[str], max_lines: int = 19) -> list[str]:
    lines: list[str] = []
    for block in blocks:
        for raw in block.splitlines():
            prefix = ""
            text = raw
            if raw.startswith("$ "):
                prefix = "$ "
                text = raw[2:]
            width = 72 if prefix else 78
            wrapped = textwrap.wrap(text, width=width, break_long_words=True, subsequent_indent="  ") or [""]
            for i, part in enumerate(wrapped):
                lines.append((prefix if i == 0 else "  ") + part)
    return lines[-max_lines:]


def canvas(fill: int = 0) -> list[bytearray]:
    return [bytearray([fill]) * WIDTH for _ in range(HEIGHT)]


def rect(img: list[bytearray], x: int, y: int, w: int, h: int, color: int) -> None:
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    for yy in range(y0, y1):
        img[yy][x0:x1] = bytes([color]) * (x1 - x0)


def text(img: list[bytearray], x: int, y: int, value: str, color: int, scale: int = SCALE) -> None:
    cx = x
    for char in value.upper():
        glyph = FONT.get(char, FONT["?"])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    rect(img, cx + gx * scale, y + gy * scale, scale, scale, color)
        cx += 6 * scale


def frame(blocks: list[str], index: int) -> list[bytearray]:
    img = canvas(0)
    rect(img, 28, 24, 844, 472, 1)
    rect(img, 28, 24, 844, 44, 2)
    rect(img, 48, 40, 12, 12, 8)
    rect(img, 68, 40, 12, 12, 10)
    rect(img, 88, 40, 12, 12, 9)
    text(img, 126, 39, "REMOTE AGENT COLLABORATION", 4, 2)
    rect(img, 610, 36, 222, 20, 14)
    text(img, 622, 40, "REAL COLLABCTL FIXTURE", 1, 1)

    rect(img, 52, 86, 170, 34, 14)
    text(img, 70, 96, "LEAD THREAD", 1, 2)
    rect(img, 236, 86, 190, 34, 13)
    text(img, 254, 96, "MEMBER THREAD", 1, 2)
    rect(img, 440, 86, 210, 34, 15)
    text(img, 458, 96, "CONFLICT DENIED", 1, 2)

    shown = wrap_lines(blocks[:index])
    y = 146
    for line in shown:
        color = 4
        if "ROLE_SESSION_CONFLICT" in line or "ROLE_NOT_AUTHORIZED" in line:
            color = 8
        elif line.startswith("OK") or "SESSION ACTIVE" in line or "LOG COMPACTED" in line:
            color = 9
        elif line.startswith("$"):
            color = 10
        text(img, 58, y, line, color, 1)
        y += 18
    if index < len(blocks):
        rect(img, 58, 466, 10, 16, 5 if index % 2 else 12)
    return img


def lzw_data(indices: bytes, min_code_size: int = 4) -> bytes:
    clear = 1 << min_code_size
    end = clear + 1
    codes: list[int] = []
    chunk_count = 0
    codes.append(clear)
    for pixel in indices:
        if chunk_count >= 8:
            codes.append(clear)
            chunk_count = 0
        codes.append(pixel)
        chunk_count += 1
    codes.append(end)

    code_size = min_code_size + 1
    bit_buffer = 0
    bit_count = 0
    out = bytearray()
    for code in codes:
        bit_buffer |= code << bit_count
        bit_count += code_size
        while bit_count >= 8:
            out.append(bit_buffer & 0xFF)
            bit_buffer >>= 8
            bit_count -= 8
    if bit_count:
        out.append(bit_buffer & 0xFF)

    blocks = bytearray([min_code_size])
    for i in range(0, len(out), 255):
        chunk = out[i:i + 255]
        blocks.append(len(chunk))
        blocks.extend(chunk)
    blocks.append(0)
    return bytes(blocks)


def gif_bytes(frames: list[list[bytearray]], delay_cs: int = 85) -> bytes:
    data = bytearray()
    data.extend(b"GIF89a")
    data.extend(struct.pack("<HH", WIDTH, HEIGHT))
    data.append(0xF3)
    data.append(0)
    data.append(0)
    for rgb in PALETTE:
        data.extend(bytes(rgb))
    data.extend(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")
    for img in frames:
        data.extend(b"\x21\xF9\x04\x00")
        data.extend(struct.pack("<H", delay_cs))
        data.extend(b"\x00\x00")
        data.extend(b"\x2C\x00\x00\x00\x00")
        data.extend(struct.pack("<HH", WIDTH, HEIGHT))
        data.append(0)
        data.extend(lzw_data(b"".join(img)))
    data.append(0x3B)
    return bytes(data)


def png_bytes(img: list[bytearray]) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    raw = bytearray()
    for row in img:
        raw.append(0)
        for idx in row:
            raw.extend(bytes(PALETTE[idx]))
    payload = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", payload) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def poster_svg(transcript: str) -> str:
    lines = transcript.splitlines()[-24:]
    text_nodes = []
    for i, line in enumerate(lines):
        color = "#F8FAFC"
        if "ROLE_SESSION_CONFLICT" in line or "ROLE_NOT_AUTHORIZED" in line:
            color = "#FCA5A5"
        elif line.startswith("OK") or "Session active" in line or "Log compacted" in line:
            color = "#86EFAC"
        elif line.startswith("$"):
            color = "#FDE68A"
        text_nodes.append(f'<text x="54" y="{150 + i * 24}" fill="{color}" font-size="15" font-family="Consolas, monospace">{html.escape(line[:105])}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760" role="img" aria-label="Remote Agent Collaboration terminal demo">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#F8FAFC"/>
      <stop offset="0.52" stop-color="#ECFDF5"/>
      <stop offset="1" stop-color="#EFF6FF"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="760" fill="url(#bg)"/>
  <rect x="38" y="38" width="1124" height="684" rx="24" fill="#0F172A"/>
  <rect x="38" y="38" width="1124" height="56" rx="24" fill="#1E293B"/>
  <circle cx="72" cy="66" r="8" fill="#EF4444"/>
  <circle cx="98" cy="66" r="8" fill="#FACC15"/>
  <circle cx="124" cy="66" r="8" fill="#22C55E"/>
  <text x="158" y="73" fill="#ECFDF5" font-size="18" font-family="Inter, Segoe UI, Arial, sans-serif" font-weight="700">Real collabctl fixture: role lock, announcements, tasks, log compaction</text>
  <rect x="880" y="54" width="230" height="24" rx="12" fill="#CCFBF1"/>
  <text x="900" y="72" fill="#134E4A" font-size="13" font-family="Inter, Segoe UI, Arial, sans-serif" font-weight="700">generated by scripts/generate_demo.py</text>
  {''.join(text_nodes)}
</svg>
"""


def main() -> int:
    root = repo_root()
    assets = root / "docs" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (root / "demo").mkdir(exist_ok=True)

    transcript, blocks = build_transcript()
    write_text_lf(root / "demo" / "demo-transcript.txt", transcript)
    write_text_lf(assets / "demo-poster.svg", poster_svg(transcript))

    frame_indexes = [1, 3, 5, 7, 10, 13, 16, len(blocks)]
    frames = [frame(blocks, min(i, len(blocks))) for i in frame_indexes]
    (assets / "demo.gif").write_bytes(gif_bytes(frames))
    (assets / "demo-poster.png").write_bytes(png_bytes(frames[-1]))
    print("Generated real collabctl transcript, poster PNG/SVG, and animated GIF.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
