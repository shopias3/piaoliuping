# -*- coding: utf-8 -*-
"""生成头像上传测试用的小 PNG（96x96 纯色）。"""
import struct
import zlib

W = H = 96
raw = b"".join(b"\x00" + bytes([80, 140, 247] * W) for _ in range(H))


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw))
       + chunk(b"IEND", b""))
with open(r"D:\piaoliuping\backend\data\test_avatar.png", "wb") as f:
    f.write(png)
print("test png created")
