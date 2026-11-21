#!/usr/bin/env python3
"""watch_deck.py · deck 门禁主动监控(文件变更 → 自动校验)

用法:
    python3 watch_deck.py <deck目录>/index.html [--interval 2] [--debounce 1]
    python3 watch_deck.py <deck目录>/index.html --once        # 只跑一次,退出码 0/1/2
    python3 watch_deck.py <deck目录>/index.html --hook        # 供 hook 调用:只输出结果,不常驻

机制:轮询 index.html 与同级 assets/images(含 SVG) 的 mtime+size;
变更(防抖后)自动跑 validate_deck.py + check_render.py(--page 1 快检);
结果写入 <deck目录>/.maliang/gate-status.md,并在 stdout 打印 RESULT 行。

退出码:watch 模式常驻(Ctrl+C 退出);--once/--hook 模式 0 通过 / 1 有发现 / 2 没能检查。
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATE = HERE / "validate_deck.py"
RENDER = HERE / "check_render.py"


def snapshot(deck):
    """返回被监控文件的 (mtime, size) 摘要"""
    sig = {}
    folder = deck.parent
    files = [deck]
    for sub in ("images", "assets"):
        d = folder / sub
        if d.is_dir():
            files.extend(p for p in d.rglob("*") if p.is_file())
    for p in files:
        try:
            st = p.stat()
            sig[str(p.relative_to(folder)).replace("\\", "/")] = (st.st_mtime_ns, st.st_size)
        except OSError:
            pass
    return sig


def run_gates(deck, quick=True):
    """跑校验器,返回结果文本与退出码"""
    out, codes = [], {}
    for name, cmd in [
        ("validate", [sys.executable, str(VALIDATE), str(deck)]),
        ("render", [sys.executable, str(RENDER), str(deck), "--page", "1", "--viewport", "1280x800"] if quick
         else [sys.executable, str(RENDER), str(deck), "--viewport", "1280x800"]),
    ]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            codes[name] = r.returncode
            tail = (r.stdout + r.stderr).strip().splitlines()
            out.append("### %s (exit %d)\n%s" % (name, r.returncode, "\n".join(tail[-25:])))
        except subprocess.TimeoutExpired:
            codes[name] = 2
            out.append("### %s (timeout)" % name)
    fail = codes.get("validate") == 1 or codes.get("render") == 1
    cannot = codes.get("validate") == 2 and codes.get("render") == 2
    status = "CANNOT-CHECK" if cannot else ("FAIL" if fail else "PASS")
    body = "# Gate status\n\n%s\n\n%s\n" % (status, "\n\n".join(out))
    sf = deck.parent / ".maliang" / "gate-status.md"
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(body, encoding="utf-8")
    print("[watch] %s  %s  (status: %s)" % (time.strftime("%H:%M:%S"), deck.name, status), flush=True)
    return codes, status


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", help="deck 的 index.html 路径")
    ap.add_argument("--interval", type=float, default=2.0, help="轮询间隔秒(默认 2)")
    ap.add_argument("--debounce", type=float, default=1.0, help="变更防抖秒(默认 1)")
    ap.add_argument("--full", action="store_true", help="render 跑全量页,不只第 1 页")
    ap.add_argument("--once", action="store_true", help="只跑一次")
    ap.add_argument("--hook", action="store_true", help="hook 模式:同 --once,不常驻")
    args = ap.parse_args()

    deck = Path(args.deck)
    if not deck.is_file():
        print("FAIL  deck 不存在:", deck)
        sys.exit(2)

    if args.once or args.hook:
        codes, status = run_gates(deck, quick=not args.full)
        sys.exit(0 if status == "PASS" else (2 if status == "CANNOT-CHECK" else 1))

    print("[watch] 启动: %s (Ctrl+C 退出)" % deck, flush=True)
    last = snapshot(deck)
    codes, status = run_gates(deck, quick=not args.full)  # 启动即跑一次,建立基线
    try:
        while True:
            time.sleep(max(0.5, args.interval))
            cur = snapshot(deck)
            if cur == last:
                continue
            time.sleep(max(0.2, args.debounce))
            if snapshot(deck) == cur:  # 防抖:确认稳定
                last = cur
                codes, status = run_gates(deck, quick=not args.full)
    except KeyboardInterrupt:
        print("[watch] 退出", flush=True)


if __name__ == "__main__":
    main()
