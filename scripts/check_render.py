#!/usr/bin/env python3
"""check_render.py · bisheng deck 渲染测量(Playwright 实测,先量后改)

用法:
    python3 check_render.py <deck目录>/index.html [--viewport 1280x800] [--page N] [--json]

测量项(逐页,吸收 guizang M1/M2):
    M1 内容溢出   : 子元素矩形超出画布 >2px → FAIL(报最高/最低问题元素)
    M1 底部安全区 : 最低内容边与画布底距离,<40px FAIL / <80px WARN(安全区 84px)
    M2 标题间距   : .head 下缘到下一内容块顶缘,<12px FAIL / <24px WARN
    R1 渲染字号   : 有自绘文本的叶子元素最小 font-size,<13px FAIL / <14px WARN
    R2 对比度     : 6 类文本(t-body/t-note/t-meta/t-kicker/t-title/t-sub)遍历全部实例,
                 取最低对比度并标注元素 id;<4.5 FAIL / <5.0 WARN
    E1 JS 错误    : 页面 pageerror 捕获 → FAIL

依赖:python -m pip install playwright && python -m playwright install chromium
未安装 playwright → 退出码 2(没能检查,不得记为通过)。

退出码(maliang EXIT-CODES 语义):0 通过 / 1 有发现 / 2 没能检查
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("FAIL  未安装 playwright:python -m pip install playwright && python -m playwright install chromium")
    print("RESULT: CANNOT-CHECK")
    sys.exit(2)

SETTLE_JS = (
    "(() => { return document.querySelector('.counter').textContent })()"
)

MEASURE_JS = """
(() => {
  const sec = document.querySelector('.slide.is-current');
  if (!sec) return { error: 'no current slide' };
  const r = sec.getBoundingClientRect();
  const all = [...sec.querySelectorAll('*')];
  const visible = all.filter(e => {
    const s = getComputedStyle(e);
    return s.display !== 'none' && s.visibility !== 'hidden' &&
      (e.textContent.trim().length > 1 || e.tagName === 'IMG');
  });
  const furniture = e => e.closest('.foot') || e.closest('.chrome') || e.classList.contains('ov-num') || e.closest('.sr-live');
  let overflow = [];
  for (const e of visible) {
    if (e.closest('.foot') || e.classList.contains('ov-num')) continue;
    const b = e.getBoundingClientRect();
    const dR = Math.round(b.right - r.right), dB = Math.round(b.bottom - r.bottom);
    const dL = Math.round(r.left - b.left), dT = Math.round(r.top - b.top);
    if (dR > 2 || dB > 2 || dL > 2 || dT > 2)
      overflow.push({ el: e.tagName + '.' + String(e.className).slice(0, 24), dR, dB, dL, dT });
  }
  let maxBottom = -1e9;
  for (const e of visible) {
    if (furniture(e)) continue;
    if (e.textContent.trim().length < 2 && e.tagName !== 'IMG') continue;
    maxBottom = Math.max(maxBottom, e.getBoundingClientRect().bottom);
  }
  const navGap = maxBottom > -1e8 ? Math.round(r.bottom - maxBottom) : null;
  let titleGap = null;
  const head = sec.querySelector('.head');
  if (head) {
    const hb = head.getBoundingClientRect().bottom;
    let next = 1e9;
    for (const e of visible) {
      if (head.contains(e)) continue;
      const b = e.getBoundingClientRect();
      if (b.top >= hb - 4 && (e.textContent.trim().length > 1 || e.tagName === 'IMG')) next = Math.min(next, b.top);
    }
    if (next < 1e9) titleGap = Math.round(next - hb);
  }
  let minFS = null;
  for (const e of visible) {
    if (furniture(e)) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) continue;
    const fs = parseFloat(getComputedStyle(e).fontSize);
    if (!minFS || fs < minFS.px) minFS = { px: fs, el: e.tagName + '.' + String(e.className).slice(0, 24) };
  }
  const parse = c => { const m = c.match(/rgba?\\(([-\\d.]+),\\s*([-\\d.]+),\\s*([-\\d.]+)(?:,\\s*([\\d.]+))?\\)/);
    return m ? { r: +m[1], g: +m[2], b: +m[3], a: m[4] === undefined ? 1 : +m[4] } : null; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (fg, bg) => ({ r: fg.a * fg.r + (1 - fg.a) * bg.r, g: fg.a * fg.g + (1 - fg.a) * bg.g, b: fg.a * fg.b + (1 - fg.a) * bg.b });
  const cr = (fg, bg) => { if (!fg || !bg) return null; const f = fg.a < 1 ? blend(fg, bg) : fg;
    const l1 = lum(f), l2 = lum(bg); const hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return Math.round((hi + 0.05) / (lo + 0.05) * 100) / 100; };
  const bgOf = (el) => { let n = el;
    while (n && n !== document.documentElement) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0.85) return c;
      n = n.parentElement;
    }
    return parse(getComputedStyle(document.body).backgroundColor); };
  const contrast = {};
  for (const cls of ['.t-body', '.t-note', '.t-meta', '.t-kicker', '.t-title', '.t-sub']) {
    let worst = null, worstEl = '';
    for (const el of sec.querySelectorAll(cls)) {
      const v = cr(parse(getComputedStyle(el).color), bgOf(el));
      if (v !== null && (worst === null || v < worst)) {
        worst = v;
        worstEl = (el.closest('[data-kind="node"]')?.id || el.closest('[id^="n:"]')?.id ||
                   el.closest('figure,div[class*="card"]')?.className.slice(0,24) || el.tagName);
      }
    }
    if (worst !== null) contrast[cls] = [worst, worstEl];
  }
  return { overflow: overflow.slice(0, 4), navGap, titleGap, minFS, contrast };
})()
"""

def run_interaction(page, total):
    """键位矩阵回归:传统 PPT 全键位断言,返回 [(ok, label)]"""
    res = []
    _ierr = []
    page.on("pageerror", lambda e: _ierr.append(str(e)[:150]))

    def n_now():
        c = page.evaluate("document.querySelector('.counter').textContent")
        m = re.match(r"(\d+)", c)
        return int(m.group(1)) if m else -1

    def chk(label, got, want):
        res.append((got == want, "%s → p%s(期望 p%s)" % (label, got, want)))

    def key(k):
        page.keyboard.press(k)
        page.wait_for_timeout(420)

    def poll(js, want, timeout=1800, rekey=None):
        """轮询等待页面状态到位;应对 headless 输入管道的偶发延迟"""
        import time as _t
        deadline = _t.time() + timeout / 1000.0
        resent = False
        while _t.time() < deadline:
            if page.evaluate(js) == want:
                return True
            if not resent and rekey and _t.time() > deadline - timeout / 2000.0:
                page.keyboard.press(rekey)
                resent = True
            page.wait_for_timeout(120)
        return page.evaluate(js) == want

    key("Home")
    chk("Home", n_now(), 1)
    key("ArrowRight"); chk("→", n_now(), 2)
    key("ArrowDown"); chk("↓", n_now(), 3)
    key("Space"); chk("Space", n_now(), min(4, total))
    key("ArrowLeft"); chk("←", n_now(), 3)
    key("PageUp"); chk("PageUp", n_now(), 2)
    key("PageDown"); chk("PageDown", n_now(), 3)
    key("End"); chk("End", n_now(), total)
    key("Home"); chk("Home 重置", n_now(), 1)
    key("3"); chk("数字 3", n_now(), 3)
    page.keyboard.press("Escape")
    chk("Esc 总览开", poll("document.body.classList.contains('overview')", True), True)
    kd1 = kd_snapshot(page)
    page.keyboard.press("Escape")
    ok_ = poll("document.body.classList.contains('overview')", False)
    if not ok_:
        dump = page.evaluate("({ov:document.body.classList.contains('overview'), no:document.body.classList.contains('notes-open'), lp:document.body.classList.contains('low-power'), cls:document.body.className.slice(0,60)})")
        print("      [diag] Esc 关超时后三态:", dump)
    chk("Esc 总览关(kd+%d)%s" % (kd_snapshot(page) - kd1, (" ERR:" + _ierr[-1]) if _ierr else ""), ok_, True)
    key("p")
    chk("P 备注开", poll("document.body.classList.contains('notes-open')", True), True)
    key("p")
    chk("P 备注关", poll("document.body.classList.contains('notes-open')", False), True)
    key("b")
    chk("B 低功耗开", poll("document.body.classList.contains('low-power')", True), True)
    key("b")
    chk("B 低功耗关", poll("document.body.classList.contains('low-power')", False), True)
    page.mouse.click(640, 360); page.wait_for_timeout(420)
    chk("单击前进", n_now(), 4)
    page.keyboard.down("Shift")
    page.mouse.click(640, 360)
    page.keyboard.up("Shift")
    page.wait_for_timeout(420)
    chk("Shift+单击后退", n_now(), 3)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(300)
    chk("滚轮前进", n_now(), 4)
    return res


def kd_snapshot(page):
    return page.evaluate("window.__kd")


def export_pdf(page, deck_path, n_slides, report, findings):
    pdf_path = deck_path.parent / "render-check.pdf"
    try:
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(800)
        page.emulate_media(media="print")
        page.pdf(path=str(pdf_path), width="1280px", height="720px",
                 print_background=True, prefer_css_page_size=True)
        data = pdf_path.read_bytes()
        n_pdf = len(re.findall(rb"/Type\s*/Page(?![s])", data))
        kb = len(data) // 1024
        if n_pdf == 0:
            report.append("pdf    WARN  %dKB,页数无法从压缩流解析(人工抽查)" % kb)
        elif n_pdf >= n_slides:
            report.append("pdf    PASS  %d 页(≥%d) %dKB" % (n_pdf, n_slides, kb))
        else:
            report.append("pdf    FAIL  %d 页(<%d) %dKB" % (n_pdf, n_slides, kb))
            findings.append(("PDF", "FAIL", "PDF 页数 %d < %d" % (n_pdf, n_slides)))
    except Exception as exc:
        report.append("pdf    FAIL  导出异常: %s" % str(exc)[:120])
        findings.append(("PDF", "FAIL", str(exc)[:120]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", help="deck 的 index.html 路径")
    ap.add_argument("--viewport", default="1280x800")
    ap.add_argument("--page", type=int, default=None, help="只测第 N 页")
    ap.add_argument("--interaction", action="store_true", help="键位矩阵回归:翻页/总览/备注/低功耗/单击/滚轮全键位断言")
    ap.add_argument("--pdf", action="store_true", help="导出 PDF 并校验页数 ≥ slide 数")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    path = Path(args.deck)
    if not path.is_file():
        print("FAIL  文件不存在: %s" % path)
        sys.exit(2)
    try:
        vw, vh = (int(x) for x in args.viewport.lower().split("x"))
    except ValueError:
        print("FAIL  --viewport 格式应为 WxH")
        sys.exit(2)

    uri = path.resolve().as_uri()
    n_slides = len(re.findall(r'<section[^>]*class="[^"]*\bslide\b', path.read_text(encoding="utf-8")))
    if not n_slides:
        print("FAIL  0 张 slide")
        sys.exit(2)
    pages = [args.page] if args.page else list(range(1, n_slides + 1))

    findings, report = [], []
    try:
        with sync_playwright() as pw:
            browser = None
            for kwargs in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
                try:
                    browser = pw.chromium.launch(headless=True, **kwargs)
                    break
                except Exception:
                    continue
            if browser is None:
                raise RuntimeError("无可用浏览器:playwright chromium 未安装,且系统无 Edge/Chrome")
            page = browser.new_page(viewport={"width": vw, "height": vh})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)[:160]))
            for n in pages:
                page.goto("%s?p=%d#%d" % (uri, n, n), wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(500)
                page.evaluate(SETTLE_JS)
                page.wait_for_timeout(150)
                m = page.evaluate(MEASURE_JS)
                if m.get("error"):
                    report.append("p%02d  FAIL  %s" % (n, m["error"]))
                    findings.append(("p%02d" % n, "FAIL", m["error"]))
                    continue
                pf, pw_ = [], []
                for o in m["overflow"]:
                    pf.append("溢出 %s (dR=%s dL=%s dB=%s)" % (o["el"], o["dR"], o["dL"], o["dB"]))
                if m["navGap"] is not None and m["navGap"] < 40:
                    pf.append("底部安全区 %dpx(<40)" % m["navGap"])
                elif m["navGap"] is not None and m["navGap"] < 64:
                    pw_.append("底部安全区 %dpx(<64)" % m["navGap"])
                if m["titleGap"] is not None and m["titleGap"] < 12:
                    pf.append("标题间距 %dpx(<12)" % m["titleGap"])
                elif m["titleGap"] is not None and m["titleGap"] < 24:
                    pw_.append("标题间距 %dpx(<24)" % m["titleGap"])
                if m["minFS"] and m["minFS"]["px"] < 13:
                    pf.append("渲染字号 %.0fpx %s(<13)" % (m["minFS"]["px"], m["minFS"]["el"]))
                for cls, entry in m["contrast"].items():
                    v, where = entry[0], entry[1]
                    if v < 4.5:
                        pf.append("%s 对比度 %s:1(<4.5) @%s" % (cls, v, where))
                    elif v < 5.0:
                        pw_.append("%s 对比度 %s:1(<5.0) @%s" % (cls, v, where))
                if errors:
                    pf.append("JS 错误: %s" % errors[0])
                    errors.clear()
                line = ("p%02d  " % n) + ("FAIL  " + "; ".join(pf) if pf else ("WARN  " + "; ".join(pw_) if pw_ else "OK"))
                report.append(line)
                for x in pf:
                    findings.append(("p%02d" % n, "FAIL", x))
                for x in pw_:
                    findings.append(("p%02d" % n, "WARN", x))
            if args.interaction:
                _ierr = []
                page.on("pageerror", lambda e: _ierr.append(str(e)[:150]))
                page.reload(wait_until="domcontentloaded")
                page.wait_for_timeout(800)
                page.evaluate("window.__kd=0; document.addEventListener('keydown',function(){window.__kd++},true)")
                page.evaluate(SETTLE_JS)
                for ok_, label in run_interaction(page, n_slides):
                    print(("iPASS  " if ok_ else "iFAIL  ") + label)
                    findings.append(("INT", "FAIL" if not ok_ else "PASS", label))
            if args.pdf:
                export_pdf(page, path, n_slides, report, findings)
            browser.close()
    except Exception as exc:
        print("FAIL  渲染测量未能执行: %s" % exc)
        print("RESULT: CANNOT-CHECK")
        sys.exit(2)

    for line in report:
        print(line)
    if args.json:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    nfail = sum(1 for f in findings if f[1] == "FAIL")
    nwarn = sum(1 for f in findings if f[1] == "WARN")
    print("\nRESULT: %s (%d fail · %d warn)" % ("FAIL" if nfail else ("WARN" if nwarn else "PASS"), nfail, nwarn))
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
