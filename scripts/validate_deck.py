#!/usr/bin/env python3
"""validate_deck.py · bisheng deck 结构校验器(B 通道机械检查)

用法:
    python3 validate_deck.py <deck目录>/index.html [--json]

退出码(maliang EXIT-CODES 语义):
    0 = 检查过,没发现问题
    1 = 检查过,有问题(P0 命中)
    2 = 没能检查(文件缺失 / 读取失败)——未测量不得记为通过

纯 Python 标准库;静态结构检查,渲染效果仍需浏览器实测。
"""
import json
import re
import sys
from pathlib import Path

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA70-\U0001FAFF\U00002B00-\U00002BFF\u2713\u2714\u274C\u2728]"
)
REQUIRED_FILL_RE = re.compile(r"\[\u5fc5\u5864\]")  # [必填]
SLIDE_RE = re.compile(r'<section[^>]*class="([^"]*\bslide\b[^"]*)"[^>]*>')
SLIDE_ID_RE = re.compile(r'<section[^>]*data-slide-id="([^"]+)"')
SECTION_RE = re.compile(r"<section\b.*?</section>", re.S)
# 裸属性(data-anim)与带值(data-anim="line")都算一个标记
DATA_ANIM_RE = re.compile(r"\bdata-anim\b")
DATA_COUNT_RE = re.compile(r"\bdata-count\b")
SMALL_FONT_RE = re.compile(r"font-size:\s*(?:\.\d+)?(9|10|11|12)(?:\.\d+)?px")
STYLE_HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
LAYOUT_RE = re.compile(r'data-layout="(L\d+)"')
NOTES_ID_RE = re.compile(r'"id"\s*:\s*"([^"]+)"')
SECTION_BLOCK_RE = re.compile(r"<section\b[^>]*class=\"[^\"]*\bslide\b[^\"]*\"[^>]*>[\s\S]*?</section>")
ANIMATE_RE = re.compile(r'data-animate="(quote|directional|pipeline|bars)"')
DATA_COUNT_VAL_RE = re.compile(r'data-count="([^"]*)"')
TALK_RE = re.compile(r'"talk"\s*:')
IMG_RE = re.compile(r'<img\b[^>]*src="([^"]+)"')
ARIA_LIVE_RE = re.compile(r'aria-live="polite"')
SR_LIVE_RE = re.compile(r'class="[^"]*sr-live|\.sr-live\s*\{')
HINT_RE = re.compile(r'class="hint"')
SLIDE_ID_VALUE_RE = re.compile(r'data-slide-id="([A-Za-z0-9\-]+)"')
SLIDE_ID_BAD_RE = re.compile(r'data-slide-id="(?![a-z0-9]+(-[a-z0-9]+)*$)([^"]+)"')
HERO_RE = re.compile(r"<(h1|h2)[^>]*class=\"[^\"]*\bt-hero\b[^\"]*\"[^>]*>([\s\S]*?)</\1>")
BOTTOM_RISK_RE = re.compile(r'bottom:\s*(0|1vh|2vh|0px)')
RECIPE_REQ = {
    "quote": ('data-anim="line"', "逐行引用需 data-anim=\"line\""),
    "directional": ('data-anim="left"', "左右对开需 data-anim=\"left\" 与 \"right\""),
    "pipeline": ('data-anim="step"', "流水线需 data-anim=\"step\""),
    "bars": ('data-anim="bar"', "柱状生长需 data-anim=\"bar\""),
}


def fail(msg):
    print("FAIL  " + msg)
    return 1


def warn(msg):
    print("WARN  " + msg)
    return 0


def ok(msg):
    print("OK    " + msg)
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.is_file():
        print("FAIL  文件不存在: %s" % path)
        return 2
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("FAIL  读取失败: %s" % exc)
        return 2

    score = 0
    findings = []

    # ---- 0-2 占位符 ----
    leftovers = REQUIRED_FILL_RE.findall(text)
    if leftovers:
        score += fail("存在 %d 处 [必填] 占位符未替换(title 等)" % len(leftovers))
        findings.append({"sev": "P0", "id": "0-2", "msg": "[必填] 占位符未替换 x%d" % len(leftovers)})
    else:
        ok("占位符已全部替换")

    # ---- 幻灯片数量与 data-slide-id ----
    slides = SLIDE_RE.findall(text)
    if not slides:
        score += fail("0 张 slide:<!-- SLIDES_HERE --> 未填充或 section 缺 slide class")
        findings.append({"sev": "P0", "id": "structure", "msg": "无 slide"})
    else:
        ok("共 %d 张 slide" % len(slides))
    ids = SLIDE_ID_RE.findall(text)
    if len(ids) != len(slides):
        score += fail("data-slide-id 数量(%d)与 slide 数量(%d)不一致" % (len(ids), len(slides)))
        findings.append({"sev": "P0", "id": "0-9", "msg": "data-slide-id 缺失或多余"})
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        score += fail("data-slide-id 重复: %s" % ", ".join(dup))
        findings.append({"sev": "P0", "id": "0-9", "msg": "重复 id: %s" % ",".join(dup)})
    elif ids:
        ok("data-slide-id 唯一且齐全")

    # ---- SPEAKER_NOTES 一致性(仅当写了备注) ----
    note_ids = NOTES_ID_RE.findall(text)
    if note_ids and ids:
        missing = [i for i in ids if i not in note_ids]
        extra = [i for i in note_ids if i not in ids]
        if missing or extra:
            score += fail("SPEAKER_NOTES 与页面错位: 缺 %s / 多 %s" % (missing, extra))
            findings.append({"sev": "P0", "id": "0-9", "msg": "备注错位"})
        else:
            ok("SPEAKER_NOTES 与页面逐条一致")

    # ---- 0-7 动效标记密度(只数 slide 内容区,排除引擎 JS) ----
    slide_html = "\n".join(SECTION_RE.findall(text))
    anim_n = len(DATA_ANIM_RE.findall(slide_html))
    if slides and anim_n < len(slides) * 3:
        score += fail("data-anim 标记 %d 个 < 页数×3(%d)——翻页会'啪'一下全出" % (anim_n, len(slides) * 3))
        findings.append({"sev": "P0", "id": "0-7", "msg": "动效标记不足 %d/%d" % (anim_n, len(slides) * 3)})
    else:
        ok("动效标记 %d 个(≥ 页数×3)" % anim_n)

    # ---- 0-8 主题节奏 ----
    themes = []
    for cls in slides:
        m = re.search(r"\b(dark|light|accent)\b", cls)
        themes.append(m.group(1) if m else None)
    if slides and any(t is None for t in themes):
        score += fail("存在未带主题 class 的 slide(须 dark/light/accent 之一): 第 %s 页"
                      % ",".join(str(i + 1) for i, t in enumerate(themes) if t is None))
        findings.append({"sev": "P0", "id": "0-8", "msg": "缺主题 class"})
    else:
        run, worst = 1, 1
        for i in range(1, len(themes)):
            run = run + 1 if themes[i] == themes[i - 1] else 1
            worst = max(worst, run)
        if worst >= 3:
            score += fail("主题节奏:最长连续同主题 %d 页(≥3)" % worst)
            findings.append({"sev": "P0", "id": "0-8", "msg": "连续同主题 %d 页" % worst})
        else:
            ok("主题节奏有交错(最长连续 %d)" % worst)
        if len(slides) >= 8 and "dark" not in themes:
            score += warn("8 页以上但无 dark 正文页,缺呼吸感")

    # ---- 版式多样性 ----
    layouts = LAYOUT_RE.findall(text)
    if slides and layouts and len(set(layouts)) < 5 and len(slides) >= 7:
        score += warn("7 页以上仅 %d 种版式,建议 ≥5 种" % len(set(layouts)))
    elif layouts:
        ok("版式覆盖 %d 种: %s" % (len(set(layouts)), ",".join(sorted(set(layouts)))))

    # ---- 0-6 emoji(只查 slide 内容区) ----
    hits = EMOJI_RE.findall(slide_html)
    if hits:
        score += fail("发现 emoji 作图标/装饰(x%d)——用 Lucide" % len(hits))
        findings.append({"sev": "P0", "id": "0-6", "msg": "emoji x%d" % len(hits)})
    else:
        ok("无 emoji")

    # ---- 0-4 字号下限(只查 slide 内容区;chrome/foot 等家具小字豁免) ----
    small = SMALL_FONT_RE.findall(slide_html)
    if small:
        score += fail("发现 <13px 字号: font-size:%spx x%d" % (small[0], len(small)))
        findings.append({"sev": "P0", "id": "0-4", "msg": "过小字号 x%d" % len(small)})
    else:
        ok("字号下限达标")

    # ---- 硬编码颜色(只查 slide 内容区的 style 与属性值) ----
    leaked = STYLE_HEX_RE.findall(slide_html)
    if leaked:
        score += fail("slide 内硬编码 hex(x%d)——只用主题变量: %s" % (len(leaked), leaked[0]))
        findings.append({"sev": "P0", "id": "themes", "msg": "硬编码 hex x%d" % len(leaked)})
    else:
        ok("slide 层无硬编码 hex")

    # ---- 动效 recipe 配对(quote→line / directional→left+right / pipeline→step / bars→bar) ----
    for m in ANIMATE_RE.finditer(text):
        recipe, token = m.group(1), RECIPE_REQ[m.group(1)][0]
        seg = m.group(0)
        start = text.rfind("<section", 0, m.start())
        block = text[start : text.find("</section>", m.start())]
        if recipe == "directional":
            if 'data-anim="left"' not in block or 'data-anim="right"' not in block:
                score += fail("data-animate=%s 页缺 %s 配对标记" % (recipe, "left/right"))
                findings.append({"sev": "P0", "id": "0-7", "msg": "recipe %s 缺配对" % recipe})
                continue
        elif token not in block:
            score += fail("data-animate=%s 页缺 %s" % (recipe, RECIPE_REQ[recipe][1]))
            findings.append({"sev": "P0", "id": "0-7", "msg": "recipe %s 缺 %s" % (recipe, token)})
    else:
        pass
    if ANIMATE_RE.search(text) and not any(f["id"] == "0-7" for f in findings):
        ok("recipe 页动效配对齐全")
    if not ANIMATE_RE.search(text):
        ok("无特殊 recipe 页(默认 cascade)")

    # ---- data-count 值合法性(必须以数字开头,引擎才能解析滚动) ----
    bad_count = [v for v in DATA_COUNT_VAL_RE.findall(text) if not re.match(r"^\s*[\d,]", v)]
    if bad_count:
        score += fail("data-count 值不以数字开头(引擎无法滚动): %s" % bad_count[:3])
        findings.append({"sev": "P0", "id": "counter", "msg": "非法 data-count x%d" % len(bad_count)})
    else:
        ok("data-count 值合法(或未使用)")

    # ---- SPEAKER_NOTES 必备字段(写了备注时每页应有 talk) ----
    if ids and note_ids:
        talks = len(TALK_RE.findall(text))
        if talks < len(ids):
            score += fail("SPEAKER_NOTES talk 字段 %d 条 < 页数 %d" % (talks, len(ids)))
            findings.append({"sev": "P1", "id": "notes", "msg": "talk 字段缺失 %d" % (len(ids) - talks)})
        else:
            ok("SPEAKER_NOTES talk 字段齐全(%d 条)" % talks)

    # ---- 图片引用存在性 ----
    img_refs = IMG_RE.findall(text)
    missing_img = []
    for src in img_refs:
        if src.startswith(("http://", "https://", "data:")):
            continue
        target = path.parent / src.split("?")[0].split("#")[0]
        if not target.is_file():
            missing_img.append(src)
    if img_refs and missing_img:
        score += fail("图片引用缺失文件: %s" % missing_img[:3])
        findings.append({"sev": "P0", "id": "images", "msg": "缺失图片 x%d" % len(missing_img)})
    elif img_refs:
        ok("图片引用 %d 张全部在场" % len(img_refs))

    # ---- 无障碍关键件(引擎默认提供;手改后丢失会静默降级) ----
    if not ARIA_LIVE_RE.search(text) or not SR_LIVE_RE.search(text):
        score += fail("缺读屏播报关键件(aria-live / .sr-live)——翻页对读屏静默")
        findings.append({"sev": "P1", "id": "a11y", "msg": "aria-live/sr-live 缺失"})
    else:
        ok("读屏播报关键件在场")

    # ---- hint 键位提示完整性 ----
    if HINT_RE.search(text):
        hint_seg = text[text.find('class="hint"') : text.find('class="hint"') + 300]
        need = ["翻页", "总览", "全屏", "备注", "关动画"]
        lost = [w for w in need if w not in hint_seg]
        if lost:
            score += warn("提示条缺键位说明: %s" % ",".join(lost))
        else:
            ok("提示条键位说明完整")

    # ---- data-slide-id 命名规范(kebab-case,稳定) ----
    bad_ids = [v for v in ids if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", v)]
    if bad_ids:
        score += warn("data-slide-id 未用 kebab-case: %s" % bad_ids[:3])
    elif ids:
        ok("data-slide-id 命名规范")

    # ---- 中文大标题一字一行风险(hero 单行 >6 字且无 <br>) ----
    for hm in HERO_RE.finditer(text):
        inner = hm.group(2)
        plain = re.sub(r"<[^>]+>", "", inner).strip()
        if "<br" not in inner.lower() and len(plain) > 6:
            score += fail("hero 标题 %d 字无 <br> 断行——大概率一字一行: %s…" % (len(plain), plain[:10]))
            findings.append({"sev": "P0", "id": "0-3", "msg": "hero 无断行 %d 字" % len(plain)})
    if not HERO_RE.search(text):
        ok("无 t-hero 页(或已合规)")

    # ---- 贴底风险(只查 slide 内容区 inline style;引擎 chrome CSS 不算) ----
    risky = []
    for sb in SECTION_BLOCK_RE.finditer(text):
        risky += re.findall(r'style="[^"]*bottom:\s*(?:0|1vh|2vh|0px)[;\s"]', sb.group(0))
    if risky:
        score += warn("发现贴底定位 bottom:0/1vh/2vh x%d——用 .foot 预设(bottom:56px)或 .body-fill" % len(risky))

    # ---- 离线兜底 ----
    sibling = path.parent / "bs-motion.js"
    if sibling.is_file():
        ok("bs-motion.js 动效内核在场")
    else:
        score += warn("同目录无 bs-motion.js——离线放映将退化为无动画(需联网到 CDN)")

    # ---- 汇总 ----
    if as_json:
        print(json.dumps({"file": str(path), "slides": len(slides), "pass": score == 0,
                          "findings": findings}, ensure_ascii=False, indent=2))
    if score:
        print("\nRESULT: FAIL(%d)" % score)
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
