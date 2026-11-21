#!/usr/bin/env python3
"""bisheng 门禁黄金样本测试(标准库 unittest)

跑法:python3 -m unittest discover -s tests -v  (在 skill 根目录执行)
覆盖:validate_deck.py 干净样本 PASS / 违规样本 FAIL 且命中指定规则;
      check_render.py --page 1 冒烟(playwright 缺失自动 skip)。
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "examples" / "demo" / "index.html"
VALIDATE = ROOT / "scripts" / "validate_deck.py"
RENDER = ROOT / "scripts" / "check_render.py"

sys.path.insert(0, str(ROOT / "scripts"))


def run(script, target, *args):
    return subprocess.run([sys.executable, str(script), str(target), *args],
                          capture_output=True, text=True)


class TestValidateDeck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="bisheng-test-"))
        shutil.copy(DEMO, cls.tmp / "index.html")
        shutil.copy(ROOT / "examples" / "demo" / "bs-motion.js", cls.tmp / "bs-motion.js")
        # gallery 页引用 images/,测试副本必须带上(否则 false FAIL)
        src_img = ROOT / "examples" / "demo" / "images"
        if src_img.is_dir():
            shutil.copytree(src_img, cls.tmp / "images")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_clean_sample_passes(self):
        r = run(VALIDATE, self.tmp / "index.html")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RESULT: PASS", r.stdout)

    def test_missing_file_exit_2(self):
        r = run(VALIDATE, self.tmp / "nope.html")
        self.assertEqual(r.returncode, 2)

    def test_violations_caught(self):
        bad = self.tmp / "bad.html"
        t = DEMO.read_text(encoding="utf-8")
        # 注入到 slide 内容区(foot 之前):静态校验范围 = section 内容
        t = t.replace('<div class="foot"><span>bisheng skill</span>',
                      '<span style="font-size:10px">小</span><span>🎯</span><div class="foot"><span>bisheng skill</span>', 1)
        bad.write_text(t, encoding="utf-8")
        r = run(VALIDATE, bad)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("emoji", r.stdout)
        self.assertIn("font-size:10px", r.stdout)

    def test_hero_no_break_caught(self):
        bad = self.tmp / "bad2.html"
        t = DEMO.read_text(encoding="utf-8").replace("毕昇<br>", "毕昇")
        bad.write_text(t, encoding="utf-8")
        r = run(VALIDATE, bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("无 <br>", r.stdout)

    def test_recipe_pairing_caught(self):
        bad = self.tmp / "bad3.html"
        t = DEMO.read_text(encoding="utf-8")
        t = t.replace('data-animate="quote"', 'data-animate="quote" data-x="1"', 1)
        t = t.replace('data-anim="line"', 'data-anim="ln"', 1)  # 第一处 line 改名
        t = re.sub(r'data-anim="line"', 'data-anim="ln"', t)   # 其余全部改名
        bad.write_text(t, encoding="utf-8")
        r = run(VALIDATE, bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("data-animate=quote 页缺", r.stdout)


@unittest.skipUnless(RENDER.is_file(), "check_render.py missing")
class TestCheckRenderSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="bisheng-rt-"))
        shutil.copy(DEMO, cls.tmp / "index.html")
        shutil.copy(ROOT / "examples" / "demo" / "bs-motion.js", cls.tmp / "bs-motion.js")
        # gallery 页引用 images/,测试副本必须带上(否则 false FAIL)
        src_img = ROOT / "examples" / "demo" / "images"
        if src_img.is_dir():
            shutil.copytree(src_img, cls.tmp / "images")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _has_browser(self):
        try:
            import playwright  # noqa: F401
            return True
        except ImportError:
            return False

    def test_demo_page1_passes(self):
        if not self._has_browser():
            self.skipTest("playwright 未安装")
        r = run(RENDER, self.tmp / "index.html", "--page", "1")
        self.assertIn(r.returncode, (0, 1), r.stdout + r.stderr)  # 1 = 有发现但能测
        self.assertNotIn("CANNOT-CHECK", r.stdout)

    def test_overflow_caught(self):
        if not self._has_browser():
            self.skipTest("playwright 未安装")
        bad = self.tmp / "bad.html"
        t = DEMO.read_text(encoding="utf-8")
        t = t.replace('<div class="foot"><span>bisheng skill</span>',
                      '<div style="position:absolute;bottom:0">贴底标注</div><div class="foot"><span>bisheng skill</span>', 1)
        bad.write_text(t, encoding="utf-8")
        r = run(RENDER, bad, "--page", "1")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("底部安全区", r.stdout)


if __name__ == "__main__":
    unittest.main()
