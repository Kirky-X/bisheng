# image-layouts.md · 多图页面布局(2 / 3 / 4 图)

> 多图布局规范。面板规模统计：2 图 23%、3 图 24%、4 图 15%，是最常见的三种多图规模。
> 本文件只讲**图片布局**；单图主视觉见 layouts.md L4，纯文字版式见 layouts.md 其余编号。

## 0. 通用纪律（所有多图页必须通过）

1. **同组统一**：同一页图片用同一比例、同一高度、同一 caption 密度、同一描边风格。禁止一张 16:9 一张 4:3，或混用 `object-fit:cover/contain`。
2. **标准比例**：16:9 / 16:10 / 4:3 / 3:2 / 1:1；禁止原图奇葩比例（如 `2592/1798`）。
3. **只裁底**：`<img>` 默认 `object-fit:cover; object-position:top`，顶部与左右完整；UI 截图 / 信息图加 `.fit-contain`，防文字被裁。
4. **贴顶不贴底**：网格内图片自然贴 cell 顶端；禁止 `align-self:end` 贴底碰 chrome。
5. **Caption**：每张图配一行 ≤20 字的图注，颜色用 `.t-note`（读得到但不抢图）；无 caption 时整组统一省略。
6. **响应式**：≤760px 时多图网格自动降为 1–2 列（引擎内置 `@media (max-width:760px)`）。

## 1. 两张图（L-IMG-2）

两种骨架，按内容关系选：

### A. 对称对开（before/after、对比、A/B）

```
<div class="img-grid img-grid-2">
  <figure class="frame-img r-16x10" data-anim><img src="images/xx-a.png" alt=""></figure>
  <figure class="frame-img r-16x10" data-anim><img src="images/xx-b.png" alt=""></figure>
</div>
```

- 两图等宽，比例一致，gap 用 `1.5rem`。
- 上方各加一个 `.t-meta` 小标（如 `BEFORE` / `AFTER`），不要再写一句解释。

### B. 主次 7:5（主图 + 佐证图）

```
<div class="img-grid img-grid-2" style="grid-template-columns:7fr 5fr">
  <figure class="frame-img r-16x10" data-anim>…</figure>
  <figure class="frame-img r-4x3" data-anim>…</figure>
</div>
```

- 主图占 7，佐证占 5；两者高度可不同，但顶边必须对齐（`align-items:start` 已预设）。

## 2. 三张图（L-IMG-3）

### A. 三等分（同组证据、三主题、三阶段）

```
<div class="img-grid img-grid-3">
  <figure class="frame-img r-16x10" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
</div>
```

- 这是现有 L5 的骨架；比例统一，不要一张 21:9 一张 1:1。

### B. 一主两辅（7:5:5 不行时用 2fr 1fr 1fr 三层）

```
<div class="img-grid" style="grid-template-columns:2fr 1fr;grid-template-rows:1fr 1fr">
  <figure class="frame-img" style="grid-row:span 2" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
</div>
```

- 主图跨两行；辅图等高、右列对齐。

## 3. 四张图（L-IMG-4）

### A. 2×2 网格（最常见，四图等权）

```
<div class="img-grid img-grid-4">
  <figure class="frame-img r-16x10" data-anim>…</figure>
  …×4
</div>
```

- 统一比例与高度；gap `1.5rem`；最多给一张强调（加 `.accent-outline`，不要让四张都抢眼）。

### B. 一大三小（主视觉 + 三个细节）

```
<div class="img-grid" style="grid-template-columns:2fr 1fr;grid-template-rows:1fr 1fr 1fr">
  <figure class="frame-img" style="grid-row:span 3" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
  <figure class="frame-img r-16x10" data-anim>…</figure>
</div>
```

- 三张小图等高、贴右列；主图跨三行。

## 4. 与标题的组合

多图页的标题区用 `.head`（kicker 在上、标题在下），图片区包 `.body-fill` 垂直居中：

```
<section class="slide light" data-slide-id="gallery" data-layout="L5">
  <div class="head"><span class="t-kicker" data-anim>EVIDENCE</span><h2 class="t-title" data-anim>四张实证</h2></div>
  <div class="body-fill">
    <div class="img-grid img-grid-4">…</div>
    <p class="t-note" style="margin-top:1rem">图注或来源 · 赛前核实</p>
  </div>
</section>
```

## 5. 交付前检查（加到 checklist 0-5）

- [ ] 同组比例/高度/caption 密度一致
- [ ] 无奇葩比例；截图已加 `.fit-contain`
- [ ] 图片贴顶不贴底；最小字号 ≥13px（渲染实测）
- [ ] 2 图确认为对称或 7:5；3 图确认为三等分或一主两辅；4 图确认为 2×2 或一大三小
- [ ] `check_render.py --page N` 通过（无溢出/安全区失败）
