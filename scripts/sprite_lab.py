#!/usr/bin/env python3
"""Scratch renderer: draw a sprite table to PNG so pixel work can be judged by eye."""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_atelier import PALETTE, pad  # noqa: E402


def png(path: Path, width: int, height: int, rows: list[bytes]) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + row for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


SCENE_BG = (0x1A, 0x1C, 0x22)  # roughly mid-height of the scene sky gradient


def render(sprite: list[str], name: str, scale: int = 14, bg: tuple[int, int, int] = SCENE_BG) -> None:
    sprite = pad(sprite)
    h = len(sprite)
    w = max(len(r) for r in sprite)
    rows: list[bytes] = []
    for y in range(h):
        line = sprite[y].ljust(w, ".")
        for _ in range(scale):
            row = bytearray()
            for ch in line:
                color = PALETTE.get(ch)
                rgb = bytes.fromhex(color[1:]) if color else bytes(bg)
                row.extend(rgb * scale)
            rows.append(bytes(row))
    png(Path(f"/tmp/{name}.png"), w * scale, h * scale, rows)
    print(f"{name}: {w}x{h}")


def compose(layers: list[tuple[list[str], int, int]], name: str, w: int, h: int, scale: int = 14) -> None:
    canvas = [["." for _ in range(w)] for _ in range(h)]
    for sprite, ox, oy in layers:
        sprite = pad(sprite)
        for y, line in enumerate(sprite):
            for x, ch in enumerate(line):
                if ch == ".":
                    continue
                cy, cx = oy + y, ox + x
                if 0 <= cy < h and 0 <= cx < w:
                    canvas[cy][cx] = ch
    render(["".join(row) for row in canvas], name, scale)


def check(name: str, sprite: list[str]) -> None:
    widths = {len(r) for r in sprite}
    flag = "" if len(widths) == 1 else f"  <-- RAGGED {sorted(widths)}"
    print(f"{name}: {max(widths)}x{len(sprite)}{flag}")


if __name__ == "__main__":
    import build_atelier as A

    for name in ("DRAGON_BODY", "DRAGON_WING", "DRAGON_TAIL", "DRAGON_SIT", "DRAGON_IDLE", "FOX_SIT"):
        check(name, getattr(A, name))
        render(getattr(A, name), f"lab_{name.lower().removeprefix('dragon_')}")
        # again on a pale ground: the outline is nearly scene-coloured, so a
        # thickened or ragged border is invisible against the dark background.
        render(getattr(A, name), f"lab_{name.lower().removeprefix('dragon_')}_lit", bg=(0x9A, 0x9A, 0x9A))

    for i, frame in enumerate(A.FIRE_FRAMES):
        render(frame, f"lab_fire{i}", scale=16)

    mouth = A.find_pixels(A.DRAGON_BODY, "M")
    mx = max(x for x, _ in mouth)
    lips = [y for x, y in mouth if x == mx]
    lip_x = A.BODY_AT[0] + mx + 1
    lip_y = A.BODY_AT[1] + round(sum(lips) / len(lips))
    print(f"breath leaves the mouth at cell {(lip_x, lip_y)}")

    biggest = A.FIRE_FRAMES[-1]
    for i in range(len(A.DRAGON_WING_POSES)):
        compose(
            [
                (A.DRAGON_TAIL_POSES[i], *A.TAIL_AT),
                (A.DRAGON_BODY, *A.BODY_AT),
                (A.DRAGON_WING_POSES[i], *A.WING_AT),
                (biggest, lip_x, lip_y - len(biggest) // 2),
            ],
            f"lab_pose{i}",
            w=A.DRAGON_W + 24,
            h=A.DRAGON_H,
            scale=11,
        )

    import dragon_post as D

    # Dragon Post walk cycle: four discrete frames, feet and tail actually change.
    sheet_w, sheet_h = A.DRAGON_W + 8, A.DRAGON_H + 2
    sheet = [["." for _ in range(sheet_w * 4)] for _ in range(sheet_h)]
    for i in range(len(D.DRAGON_FEET_POSES)):
        compose(
            D.walk_layers(i),
            f"lab_walk{i}",
            w=A.DRAGON_W + 16,
            h=A.DRAGON_H + 2,
            scale=12,
        )
        render(D.DRAGON_FEET_POSES[i], f"lab_feet{i}", scale=18, bg=(0x9A, 0x9A, 0x9A))
        render(
            A.DRAGON_TAIL_POSES[D.WALK_TAIL_ORDER[i]],
            f"lab_walk_tail{i}",
            scale=14,
            bg=(0x9A, 0x9A, 0x9A),
        )
        ox = i * sheet_w
        for sprite, sx, sy in D.walk_layers(i):
            sprite = pad(sprite)
            for y, line in enumerate(sprite):
                for x, ch in enumerate(line):
                    if ch == ".":
                        continue
                    cy, cx = sy + y, ox + sx + x
                    if 0 <= cy < sheet_h and 0 <= cx < sheet_w * 4:
                        sheet[cy][cx] = ch
    render(["".join(row) for row in sheet], "lab_walk_sheet", scale=8)
