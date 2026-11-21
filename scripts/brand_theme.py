#!/usr/bin/env python3
"""brand_theme.py · 品牌色 → bisheng 受约束主题(WCAG 校验 + 自动调明度)

用法:
    python3 brand_theme.py "#4D6BFE" [--bg "#F2F3F7"] [--bgdark "#0E1220"] [--name brand]
    python3 brand_theme.py --design-md ".maliang/DESIGN.md" [--name brand]

逻辑:
    1. 品牌色明度 ±24% 步进扫描,筛出"白字或黑字对 accent ≥4.5"的候选
    2. 候选中优先"accent 对亮底 ≥3.0(AA 大字)"且对比最大者;无则取亮底对比最大者并告警
    3. 输出可直接粘贴的 [data-theme] CSS 块 + 对比度表
    4. --design-md:从 maliang DESIGN.md 提取首个主色 hex(含 color/primary/accent 关键字的行)

诚实口径:单一 accent 同时满足"亮底 4.5 + 暗底 4.5"数学上通常不可行(亮度带冲突)。
深色页小字用 var(--accent-ink)(引擎 color-mix 自动衍生),本脚本只报告不强制。
退出码:0 成功 / 1 收敛失败(建议换色或仅大字使用) / 2 参数错误
"""
import argparse
import colorsys
import re
import sys
from pathlib import Path


def hx2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h or ""):
        raise ValueError("bad hex: " + str(h))
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hx(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def shift(hex_color, dl):
    r, g, b = hx2rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    l = max(0.0, min(1.0, l + dl))
    return rgb2hx(tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s)))


def lum(c):
    f = lambda v: (v / 255 / 12.92) if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def cr(a, b):
    hi, lo = max(lum(a), lum(b)), min(lum(a), lum(b))
    return round((hi + 0.05) / (lo + 0.05), 2)


def first_hex_design_md(text):
    for line in text.splitlines():
        if re.search(r"(primary|accent|主色|品牌)", line, re.I) and "# " not in line[:6]:
            m = re.search(r"#([0-9a-fA-F]{6})\b", line)
            if m:
                return "#" + m.group(1)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brand", nargs="?", default=None, help="品牌主色 hex,如 #4D6BFE")
    ap.add_argument("--bg", default="#F7F5F0", help="亮背景(默认 ink 纸白)")
    ap.add_argument("--bgdark", default="#141412", help="暗背景(默认 ink 墨黑)")
    ap.add_argument("--name", default="brand", help="主题 id")
    ap.add_argument("--design-md", default=None, help="从 maliang DESIGN.md 提取主色")
    args = ap.parse_args()

    brand = args.brand
    if args.design_md:
        p = Path(args.design_md)
        if not p.is_file():
            print("FAIL  design-md 不存在:", p)
            return 2
        brand = brand or first_hex_design_md(p.read_text(encoding="utf-8"))
        if not brand:
            print("FAIL  DESIGN.md 未找到主色 hex(需含 color/primary/accent 关键字的行)")
            return 2
    if not brand:
        print(__doc__)
        return 2

    try:
        base = hx2rgb(brand)
        bgl, bgd = hx2rgb(args.bg), hx2rgb(args.bgdark)
    except ValueError as e:
        print("FAIL", e)
        return 2

    white, black = (255, 255, 255), (17, 17, 16)
    cands = []
    for step in range(-24, 25):
        c = hx2rgb(shift(brand, step * 0.01))
        on = white if cr(white, c) >= 4.5 else (black if cr(black, c) >= 4.5 else None)
        if on is None:
            continue
        cands.append({"step": step, "c": c, "on": on, "cr_l": cr(c, bgl), "cr_d": cr(c, bgd),
                      "cr_on": cr(on, c)})
    if not cands:
        print("FAIL  收敛失败:白字黑字都无法对 accent 达到 4.5——换色(建议中明度色)")
        return 1

    good = [x for x in cands if x["cr_l"] >= 3.0]
    if good:
        best = max(good, key=lambda x: (x["cr_on"], x["cr_l"]))
        note = ""
    else:
        best = max(cands, key=lambda x: x["cr_l"])
        note = "⚠️ 无候选达到亮底 3.0——本主题 accent 仅建议用于大字/色块,小字请用 var(--fg)"

    accent_hx = rgb2hx(best["c"])
    print('/* brand_theme.py 生成 · 品牌色 %s 明度步 %+d%% → %s */' % (brand.upper(), best["step"] * 1, accent_hx))
    print('[data-theme="%s"]{ --bg-l:%s; --fg-l:#1A1A18; --bg-d:%s; --fg-d:#F2EFE9; --accent:%s; --accent-on:%s; }'
          % (args.name, args.bg, args.bgdark, accent_hx, rgb2hx(best["on"])))
    print()
    print("对比度校验(实测):")
    print("  accent vs 亮底 %s = %s:1  %s" % (args.bg, best["cr_l"], "≥3.0 AA大字 ✓" if best["cr_l"] >= 3.0 else "✗ <3.0"))
    print("  accent vs 暗底 %s = %s:1  (深色页小字用 var(--accent-ink),引擎自动衍生)" % (args.bgdark, best["cr_d"]))
    print("  accent-on(%s) vs accent = %s:1  %s" % (rgb2hx(best["on"]), best["cr_on"],
          "≥4.5 ✓" if best["cr_on"] >= 4.5 else "✗"))
    if note:
        print("  " + note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
