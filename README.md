# bisheng（毕昇）— HTML 网页 PPT 技能

> 活字排版，一页一版。生成单文件 HTML 网页 PPT：满屏分页、响应式布局、传统翻页逻辑、自研动效、缩略总览、演讲备注、双屏镜像、PDF 导出。

[![version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)](SKILL.md) [![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE) [![python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)](scripts/)
[![deck](https://img.shields.io/badge/deck-single--file-orange?style=flat-square)](assets/deck.html) [![checks](https://img.shields.io/badge/checks-4--in--1-brightgreen?style=flat-square)](scripts/check_all.py)

中文 | [English](README_EN.md)

## ✨ 功能特性

- **流式响应式满屏**：slide 恒为 100vw×100vh；`html font-size = min(100vw/80, 100vh/45)`，排版全用 rem 随窗口等比缩放；≤760px 自动切单列。任何窗口、投影、电视都满屏无黑边
- **传统 PPT 翻页**：单击/Shift+单击、方向键、Space、PageUp/Down、Home/End、1-9 跳页、滚轮、触屏滑动
- **进阶交互**：Esc 缩略宫格（左对齐、终态数字）并点击跳页、F 全屏、P 备注抽屉、B 低功耗静态、A 自动放映、双窗口镜像同步
- **自研动效**：`data-anim` 叶子标记 + 四类 recipe（quote / directional / pipeline / bars）+ `data-count` 数字滚动；只动 transform/opacity；`prefers-reduced-motion` 降级；动效内核缺失时内容全部可见
- **主题系统**：4 套预设（墨与纸 / 靛蓝 / 森林 / 牛皮纸），light/dark/accent 三态；页面只用 CSS 变量不写 hex；品牌色脚本做 WCAG 明度收敛
- **多图布局**：2 图对称对开/主次 7:5、3 图三等分/一主两辅、4 图 2×2/一大三小；同组统一比例与高度
- **一键缺陷检查**：`check_all.py` 一条命令跑完静态结构 + 逐页渲染 + 键位交互 + PDF 导出，输出 `[FAIL]/[WARN]` 清单与退出码；对比度失败带元素 id
- **马良评审门禁**：交付前强制设计评审（Nielsen 启发式 + persona 走查），机械检查通过不等于设计过关

## 📦 安装

```bash
# 方式 1：从工作区同步（在 bisheng/ 与 scripts/ 同层的根目录执行）
python3 scripts/sync_install.py

# 方式 2：手动拷贝到 agent 技能目录
cp -r bisheng/ ~/.zcode/skills/bisheng/
```

首跑依赖：Python 3.8+；渲染检查需 playwright（自动降级用系统 Edge/Chrome）。

## 🚀 快速开始

在支持 skills 的 agent 会话中用自然语言触发：

```text
做一个 10 页的 AI 产品发布 PPT        # 触发 → 生成 HTML deck
把这个 PPT 改成瑞士风格                 # 触发 → 换主题/改版式
给第 4 页加一张三层架构图               # 触发 → 生成 SVG 并嵌入
```

生成流程（7 步，见 [SKILL.md](SKILL.md)）：

```text
1. 结构先行   → 页面计划 / 版式计划 / 主题节奏表三表对齐
2. 建目录拷模板 → index.html + bs-motion.js + images/
3. 填充内容   → L1-L10 骨架 + data-anim 标记 + SPEAKER_NOTES
4. 一键检查   → python3 scripts/check_all.py <deck>/index.html
5. 浏览器实测 → 逐页截图、翻页、缩放、动效、PDF
6. 设计评审   → 马良 critique 门禁
7. 迭代交付   → 修问题 → 复跑 → 交付说明
```

## ✅ 测试与验证

```bash
python3 -m unittest discover -s tests -v       # 7 个黄金样本：validator 正反例 + render 冒烟/溢出捕获
python3 scripts/check_all.py <deck>/index.html  # 一键门禁：退出码 0 过 / 1 有缺陷 / 2 没能检查
```

负向验证已实测：删除强调卡标题的白色覆盖后，`check_all` 报 `.t-sub 对比度 3.57:1(<4.5) @card card-accent`，退出码 1。

校验器覆盖：占位符、slide 数、id 唯一、动效 mark 密度、主题节奏、hero 断行、recipe 配对、备注字段、图片引用、读屏关键件、硬编码 hex、贴底风险、溢出、安全区、标题间距、渲染字号、对比度、JS 错误、键位矩阵、PDF 页数。

## 📁 目录结构

```text
bisheng/
├── SKILL.md                  # 入口：工作流 7 步 + 门禁 + 禁止事项
├── assets/
│   ├── deck.html             # 引擎模板（类名与键位的唯一来源）
│   └── bs-motion.js          # 自研动效内核
├── references/
│   ├── narrative.md          # 叙事弧 + 三表对齐 + 主题节奏 + 备注/图片约定
│   ├── layouts.md            # L1-L10 版式骨架（可粘贴）
│   ├── themes.md             # 主题预设 + 颜色变量契约 + 品牌色生成
│   ├── image-layouts.md      # 多图页面布局（2/3/4 图六种骨架）
│   ├── checklist.md          # P0/P1/P2 质量清单
│   └── maliang-gate.md       # 设计评审门禁流程与降级路径
├── scripts/
│   ├── check_all.py          # 一键检查统一入口
│   ├── validate_deck.py      # 静态结构校验
│   ├── check_render.py       # 渲染/对比度/键位/PDF 实测
│   ├── brand_theme.py        # 品牌色 → 受约束主题
│   ├── sync_install.py       # 开发副本 → 已装副本同步（--check 报漂移）
│   ├── watch_deck.py         # 文件变更自动校验（可选）
│   └── gate-hook.py          # PostToolUse 触发校验（可选）
├── tests/                    # unittest 黄金样本
└── examples/demo/            # 示例 deck（8 页，含多图页）
```

## 🔮 边界

- **不替代协作工具**：飞书 PPT 用 lark，PPT 文件转 Markdown 用 lizhu，多人实时协作文档用其他工具
- **不做数据图表**：大段表格与数据图表用常规工具；本 skill 做演示型页面
- **不写死尺寸**：排版用 rem，唯一断点是引擎内置 ≤760px 单列降级
- **机械检查过不等于设计过关**：交付必须过设计评审门禁

## 📄 License

MIT License（© 2026 Kirky-X）。
