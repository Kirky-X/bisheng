#!/usr/bin/env python3
"""gate-hook.py · bisheng 门禁 hook(可选接入 PostToolUse)

从 stdin 读 hook payload(JSON),当工具为 Edit|Write 且目标路径是
*.html 且位于已知 deck 目录(含 index.html 同级)时,后台启动 watch_deck.py --once。
非 deck 文件直接放行,不产生任何输出。

接入方式(由用户决定,写入 ~/.zcode/cli/config.json 的 hooks.events.PostToolUse):
  {"type":"command","command":"python3 \"C:/Users/Kirky/.zcode/skills/bisheng/scripts/gate-hook.py\"","enabled":true,"timeout":60}

预期收益:编辑 deck 源码后自动跑 validate+render(第 1 页快检),结果落
<deck>/.maliang/gate-status.md;FAIL 时 hook stdout 打印一行提示。
验证方式:手动 Edit deck 一行 → 检查 gate-status.md 时间戳变化。
"""
import json
import subprocess
import sys
from pathlib import Path

WATCH = Path(__file__).resolve().parent / "watch_deck.py"


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0
    tool = payload.get("tool_name") or payload.get("tool") or ""
    if tool not in ("Edit", "Write", "WriteFile", "StrReplace"):
        return 0
    inp = payload.get("tool_input") or {}
    fp = inp.get("file_path") or inp.get("path") or ""
    p = Path(fp)
    if p.suffix.lower() != ".html" or not p.is_file():
        return 0
    # deck 目录判定:自身是 index.html,或同级存在 index.html(如 screenshots 目录无效)
    deck = p if p.name == "index.html" else (p.parent / "index.html")
    if not deck.is_file():
        return 0
    # 后台跑,不阻塞编辑流程(timeout 内 hook 只负责触发)
    try:
        subprocess.Popen([sys.executable, str(WATCH), str(deck), "--once"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
