# checklist.md · 质量检查清单(P0/P1/P2)

> 每一条来自真实迭代踩坑。
> 生成前通读一遍;生成后逐项自检 + 跑校验器。

## 🔴 P0 · 一定不能犯

### 0-1. 类名必须在模板 `<style>` 里有定义(最重要)

**现象**:直接粘 layouts 骨架,样式全丢——大标题变非衬线、卡片挤成一坨、图片堆到底部。
**做法**:生成前先 Read `assets/deck.html` 的 `<style>` 块;缺类补模板,不在页面 inline 重写;模板是类名唯一来源。

### 0-2. 必改占位符

- `<title>` 里的 `[必填] 替换为 PPT 标题` → 实际标题
- 自检:`grep "[必填]" index.html` 应无结果(validate_deck.py 会拦)

### 0-3. 中文大标题不能一字一行
> 字号均为 1280×720 基准(rem 随窗口等比缩放,比例不变)

- 一行 ≤5 字用 `.t-hero`(4rem);更长标题手工 `<br>` 断行或降到 `.t-title` 档
- 长标题每行 ≤9 个中文字符;先压文案再降字号,不要硬塞

### 0-4. 字号下限(投屏可读)

| 文本                     | 下限                              |
| ------------------------ | --------------------------------- |
| 正文段落                 | ≥16px(`.t-body` 即 16px,不要再压) |
| 卡片描述 / 图注 / 列表   | ≥14px(`.t-note`)                  |
| meta / kicker / 图表标签 | ≥13px(`.t-meta`)                  |

内容放不下 → 删文案 / 拆页 / 换版式,禁止 10-12px 硬塞。

### 0-5. 图片纪律

- 网格内多图:**固定 `height:Xvh/Xpx`,不用 aspect-ratio**(会撑破)
- 单张主视觉:可用 `.r-16x9` 等比例类
- 只裁底不裁顶(object-position:top 已预设);UI 截图保真优先
- 标准比例:16:9 / 16:10 / 4:3 / 3:2 / 1:1;同组图片统一高度
- 不要 `align-self:end` 贴底;图片容器直角、无阴影、无厚边框

### 0-6. 不用 emoji 当图标

用 Lucide:`<i data-lucide="target"></i>` + 模板已带 `lucide.createIcons()`。emoji 在投屏上破坏格调(validate_deck.py 会拦常见 emoji)。

### 0-7. 每页必须有 data-anim 标记

**现象**:翻页时内容"啪"一下全出,没有节奏感。
**做法**:正文页至少给 kicker / 标题 / lead / 卡片 / 图 加 `data-anim`;hero 页所有核心块都加。
**自检**:`grep -c 'data-anim' index.html` ≥ 页数 × 3;四类特殊页加 `data-animate="quote|directional|pipeline|bars"`。

### 0-8. 主题节奏(见 narrative.md §4)

每页必须带主题 class;连续 3 页同主题不允许;全 light 没有呼吸 = 不合格。
自检:`grep -oE 'class="slide[^"]*"' index.html` 逐页看。

### 0-9. 演讲备注一致性(有备注时)

`data-slide-id` 唯一稳定;`SPEAKER_NOTES` 数量、顺序、id 与页面逐条一致(引擎按 id 匹配,id 错备注串页)。

## 🟡 P1 · 排版节奏

- hero 与非 hero 交替;大字报与密集页交替
- kicker 在大标题**上方**(`.head` 纵向堆叠),不许左右并排
- 标题与正文间距 ≥36px(`.head` 自带 margin-bottom)
- chrome(页眉小字)与 kicker 不写同一句话——chrome 跨页重复(栏目名),kicker 是本页独一份
- 术语统一:同一个词一个写法,不硬翻译
- 底部 `.foot` 贴底内容用 bottom:56px(模板预设),不要手写 bottom:0/2vh 碰 chrome

## 🟢 P2 · 视觉打磨

- 数字滚动 `[data-count]` 必须有真实来源
- 卡片同页同类型;突出一张才换 `card-accent`
- hairline 够用,不加粗不加阴影
- 图片微圆角都不要(直角到底);最多 1px 极淡描边
- 大引用页引文 ≤2 行,出处必须有

## 🧪 最终自检清单

```
预检(生成前)
  □ 已读 deck.html 的 <style>,确认所需类存在
  □ 三表对齐(页面计划 / 版式计划 / 主题节奏表)
  □ <title> 已改(grep "[必填]" 无结果)
内容
  □ 每页 data-slide-id 唯一;SPEAKER_NOTES 与页面一致
  □ 无 emoji 图标;术语统一
排版
  □ 大标题无一字一行;字号下限达标
  □ 图片标准比例;网格固定 height;无贴底图片
动效
  □ data-anim 数 ≥ 页数×3;特殊页 data-animate 就位
  □ grep ./bs-motion.js 同级存在(离线兜底)
验证
  □ python3 {SKILL_DIR}/scripts/validate_deck.py index.html 通过(静态 18 项)
  □ python3 {SKILL_DIR}/scripts/check_render.py index.html 通过(渲染实测:溢出/安全区/字号/对比度)
  □ 拉宽窗口到非 16:9 复验一次:满屏无黑边无邻页泄露(流式架构)
  □ python3 {SKILL_DIR}/scripts/check_render.py index.html --interaction --pdf(键位矩阵 + PDF 页数)
  □ 双屏:第二窗口打开同一文件,任一边翻页两边同步(BroadcastChannel/storage 自动镜像)
  □ 多图布局(见 image-layouts.md):2 图=对称对开或主次7:5;3 图=三等分或一主两辅;4 图=2×2或一大三小;同组比例/高度/caption 密度统一
  □ 插图纪律:无渐变/阴影/3D;≤2 个饱和色;红只表示错误/瓶颈;文字保持 <text> 不转路径
  □ 浏览器逐页截图核对;翻页/缩放/动效实测
  □ 马良门禁(references/maliang-gate.md)通过
```

全勾完,才是合格的 deck。
