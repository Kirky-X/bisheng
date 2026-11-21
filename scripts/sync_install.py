#!/usr/bin/env python3
"""sync_install.py · bisheng dev 副本 → 已装副本同步器

用法:
    python3 sync_install.py [--check]

源 = 本脚本所在目录的上一级(dev 仓库);目标 = ~/.zcode/skills/bisheng。
同步范围:SKILL.md / LICENSE / .gitignore / assets / references / scripts(排除
examples/、__pycache__/ 与本脚本)。--check 只对比 SHA256 报告漂移,不写入。

退出码:0 已一致(或已同步) / 1 存在漂移(--check 模式) / 2 没能检查
"""
import hashlib
import shutil
import sys
from pathlib import Path

SKIP_DIRS = {"__pycache__", ".git", ".maliang", "specmark", "examples"}
REL_FILES = ["SKILL.md", "README.md", "README_EN.md", "LICENSE", ".gitignore"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect(root):
    out = {}
    for rel in REL_FILES:
        fp = root / rel
        if fp.is_file():
            out[rel] = fp
    for sub in ["assets", "references", "scripts"]:
        d = root / sub
        if not d.is_dir():
            continue
        for fp in d.rglob("*"):
            if fp.is_file() and "__pycache__" not in fp.parts:
                out[str(fp.relative_to(root)).replace("\\", "/")] = fp
    return out


def main():
    dev = Path(__file__).resolve().parent.parent
    inst = Path.home() / ".zcode" / "skills" / "bisheng"
    if not (dev / "SKILL.md").is_file():
        print("FAIL  源目录异常: %s" % dev)
        return 2
    check_only = "--check" in sys.argv
    src = collect(dev)
    drift, copied = [], 0
    for rel, sp in sorted(src.items()):
        ip = inst / rel
        if not ip.is_file():
            drift.append(("missing", rel))
        elif sha(sp) != sha(ip):
            drift.append(("changed", rel))
    extra = [str(r.relative_to(inst)).replace("\\", "/") for r in inst.rglob("*")
             if r.is_file() and r.relative_to(inst).as_posix() not in src
             and "__pycache__" not in r.parts and not any(d in r.parts for d in SKIP_DIRS)]
    if check_only:
        for kind, rel in drift:
            print("%-8s %s" % (kind, rel))
        for rel in extra:
            print("%-8s %s" % ("extra", rel))
        if drift:
            print("RESULT: DRIFT (%d)" % len(drift))
            return 1
        print("RESULT: IN-SYNC")
        return 0
    if not drift:
        print("RESULT: IN-SYNC (无漂移,未写入)")
        return 0
    for kind, rel in drift:
        sp, ip = src[rel], inst / rel
        ip.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sp, ip)
        copied += 1
        print("synced  %s (%s)" % (rel, kind))
    print("RESULT: SYNCED (%d 文件)" % copied)
    return 0


if __name__ == "__main__":
    sys.exit(main())
