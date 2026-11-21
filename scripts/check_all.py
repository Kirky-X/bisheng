#!/usr/bin/env python3
"""check_all.py · bisheng deck 一键缺陷检查(统一入口)

用法: python3 check_all.py <deck目录>/index.html [--json]

一条命令跑完 4 项:
  1. validate_deck.py            静态结构(占位符/slide/id/动效配对/备注/图片引用/
                                 读屏关键件/主题节奏/hero 断行/硬编码 hex/贴底风险)
  2. check_render.py             逐页渲染(溢出/安全区/标题间距/字体/对比度/JS 错误)
  3. check_render.py --interaction  键位矩阵(翻页/总览/备注/低功耗/鼠标)
  4. check_render.py --pdf       PDF 导出页数

输出每项一行 [PASS]/[FAIL]/[WARN],末尾 RESULT 汇总。
退出码: 0 全过 / 1 有 FAIL / 2 没能检查。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    deck = Path(args.deck)
    if not deck.is_file():
        print("FAIL  deck 不存在:", deck)
        sys.exit(2)

    specs = [
        ("静态结构", [sys.executable, str(HERE / "validate_deck.py"), str(deck)]),
        ("渲染+交互+PDF", [sys.executable, str(HERE / "check_render.py"), str(deck),
                       "--viewport", "1280x800", "--interaction", "--pdf"]),
    ]
    rows, findings, codes = [], [], {}
    for name, cmd in specs:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
        except subprocess.TimeoutExpired:
            codes[name] = 2
            rows.append("[FAIL] %s: 超时" % name)
            findings.append({"check": name, "level": "FAIL", "text": "超时"})
            continue
        codes[name] = r.returncode
        text = (r.stdout or "") + ("\n" + (r.stderr or ""))
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("RESULT:"):
                continue
            level = None
            if (s.startswith(("FAIL", "iFAIL", "pdf    FAIL", "CANNOT-CHECK"))
                    or (len(s) > 3 and s[:3].isdigit() and " FAIL" in s)
                    or s.startswith("p") and " FAIL " in s):
                level = "FAIL"
            elif (s.startswith(("WARN", "pdf    WARN"))
                  or (s.startswith("p") and " WARN " in s)):
                level = "WARN"
            if level:
                findings.append({"check": name, "level": level, "text": s})
                rows.append("[%s] %s: %s" % (level, name, s))
        if r.returncode == 2 or "CANNOT-CHECK" in text:
            rows.append("[FAIL] %s: 未能检查" % name)

    # 去重:同一缺陷在多检查项中重复出现时只报一次(取首次)
    seen, uniq = set(), []
    for f in findings:
        key = (f["level"], f["text"])
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    findings = uniq
    rows = ["[%s] %s: %s" % (f["level"], f["check"], f["text"]) for f in findings]
    if not rows:
        rows = ["[PASS] 全部检查通过"]
    fails = sum(1 for f in findings if f["level"] == "FAIL")
    warns = sum(1 for f in findings if f["level"] == "WARN")
    cannot = any(c == 2 for c in codes.values())
    result = "CANNOT-CHECK" if cannot else ("FAIL" if fails else ("WARN" if warns else "PASS"))
    print("\n".join(rows) if rows else "[PASS] 全部检查通过")
    print("\nRESULT: %s (%d FAIL · %d WARN)" % (result, fails, warns))
    if args.json:
        print(json.dumps({"result": result, "fails": fails, "warns": warns,
                          "codes": codes, "findings": findings}, ensure_ascii=False, indent=2))
    sys.exit(2 if cannot else (1 if fails else 0))


if __name__ == "__main__":
    main()
