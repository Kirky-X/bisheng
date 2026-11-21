# layouts.md · 页面版式骨架(可整段粘贴)

> **Pre-flight 硬规则**:骨架里的类名必须在 `assets/deck.html` 的 `<style>` 里有定义。
> 动手前先 Read 模板的 `<style>` 块确认;缺类先在模板里补,不要在页面里 inline 重写。
> 每页 `<section class="slide ...">` 必须带 `data-slide-id`(唯一稳定)与主题 class。

**动效标记**:叶子元素(kicker / 标题 / lead / 卡片 / 图)加 `data-anim`;
整页特殊节奏在 `<section>` 加 `data-animate="quote|directional|pipeline|bars"`;
数字滚动用 `data-count`(值可写 `1234` 或 `45%` 或 `1,200 万`)。
默认 cascade 已足够,四类 recipe 才需要 data-animate。

---

## L1 · 开场封面(hero dark)

```html
<section class="slide dark hero" data-slide-id="cover" data-layout="L1">
  <div class="l-center" style="gap:20px">
    <span class="t-kicker" data-anim>SHARE · 2026.11</span>
    <h1 class="t-hero" data-anim>用 HTML 做<br />下一代演示文稿</h1>
    <p class="t-sub t-kicker-dim" data-anim>bisheng · 毕昇</p>
  </div>
  <div class="foot"><span>kirky.dev</span><span>2026.11</span></div>
</section>
```

要点:封面大字 ≤5 字一行;`accent` 页(满屏强调色)替代 `dark` 可做高冲击开场;封面不要写页码大字(chrome 已有 01/N)。

## L2 · 章节幕封(hero light / hero dark)

```html
<section class="slide light" data-slide-id="act-1" data-layout="L2">
  <div class="l-center" style="gap:16px">
    <span class="t-meta" data-anim>ACT 01</span>
    <h2 class="t-title" style="font-size:3.5rem" data-anim>为什么换载体</h2>
    <span class="hr-strong" style="width:64px" data-anim></span>
  </div>
</section>
```

## L3 · 数据大字报(light)

```html
<section class="slide light" data-slide-id="stats" data-layout="L3">
  <div class="head">
    <span class="t-kicker" data-anim>BY THE NUMBERS</span>
    <h2 class="t-title" data-anim>三个事实</h2>
  </div>
  <div class="body-fill">
  <div class="stat-row">
    <div data-anim>
      <div class="num-hero accent-text" data-count="1280">0</div>
      <p class="t-note">设计画布宽度 px</p>
    </div>
    <div data-anim>
      <div class="num-hero" data-count="98">0</div>
      <p class="t-note">窗口适配覆盖率 %</p>
    </div>
    <div data-anim>
      <div class="num-hero" data-count="60">0</div>
      <p class="t-note">动效帧率目标 fps</p>
    </div>
  </div>
</section>
```

要点:大字报页信息必须少;三个数字以内;数字必须有真实来源,不硬编。

## L4 · 左文右图 / 图文混排(light,3:7 或 7:3)

```html
<section class="slide light" data-slide-id="story" data-layout="L4">
  <div class="l-split-37">
    <div style="display:flex;flex-direction:column;gap:16px">
      <span class="t-kicker" data-anim>ORIGIN</span>
      <h2 class="t-title" data-anim>从活字印刷说起</h2>
      <p class="t-body" data-anim>
        版式复用、单页成章——六百年前的思路,今天的 slide 引擎仍在沿用。
      </p>
    </div>
    <figure class="frame-img r-16x10" data-anim>
      <img src="images/04-letterpress.jpg" alt="活字印刷版面" />
    </figure>
  </div>
</section>
```

要点:正文区用 `.body-fill` 垂直居中;图片永远标准比例;只用 `object-fit:cover`,默认裁底不裁顶;不要 `align-self:end` 贴底。

## L5 · 图片网格(light)

```html
<section class="slide light" data-slide-id="gallery" data-layout="L5">
  <div class="head">
    <span class="t-kicker" data-anim>EVIDENCE</span>
    <h2 class="t-title" data-anim>同一引擎,四种画面</h2>
  </div>
  <div class="cards-3" style="display:grid;gap:20px">
    <figure class="frame-img" style="height:30vh" data-anim>
      <img src="images/05-a.jpg" alt="墨与纸主题" />
    </figure>
    <figure class="frame-img" style="height:30vh" data-anim>
      <img src="images/05-b.jpg" alt="靛蓝主题" />
    </figure>
    <figure class="frame-img" style="height:30vh" data-anim>
      <img src="images/05-c.jpg" alt="森林主题" />
    </figure>
  </div>
</section>
```

要点:网格内**固定 height,不用 aspect-ratio**(会撑破);同组图片统一高度、比例、caption 密度。

## L6 · 流水线 / 步骤(light,pipeline recipe)

```html
<section
  class="slide light"
  data-slide-id="flow"
  data-layout="L6"
  data-animate="pipeline"
>
  <div class="head">
    <span class="t-kicker" data-anim>WORKFLOW</span>
    <h2 class="t-title" data-anim>从大纲到放映</h2>
  </div>
  <div class="body-fill">
  <div class="cards-3" style="display:grid;gap:1.5rem;margin-top:.5rem">
    <div class="card card-fill" data-anim="step">
      <span class="t-meta">STEP 01</span>
      <h3 class="t-sub" style="font-weight:700">定结构</h3>
      <p class="t-body">叙事弧 + 三表对齐</p>
    </div>
    <div class="card card-fill" data-anim="step">
      <span class="t-meta">STEP 02</span>
      <h3 class="t-sub" style="font-weight:700">填版式</h3>
      <p class="t-body">选 L 编号骨架,贴改文案</p>
    </div>
    <div class="card card-accent" data-anim="step">
      <span class="t-meta">STEP 03</span>
      <h3 class="t-sub" style="font-weight:700">过门禁</h3>
      <p class="t-body">validate + 马良评审</p>
    </div>
  </div>
</section>
```

要点:正文区用 `.body-fill` 垂直居中(防头重脚轻);`data-animate="pipeline"` 让步骤逐个点亮;卡片填充类型互斥——`card-fill` / `card-accent` / `card-ink` / 描边 `card` 只突出一张 accent。

## L7 · 对比(before / after,directional recipe)

```html
<section
  class="slide light"
  data-slide-id="compare"
  data-layout="L7"
  data-animate="directional"
>
  <div class="head">
    <span class="t-kicker" data-anim>BEFORE / AFTER</span>
    <h2 class="t-title" data-anim>旧载体的天花板</h2>
  </div>
  <div class="body-fill">
  <div class="l-split" style="height:auto">
    <div class="card" style="opacity:.75" data-anim="left">
      <span class="t-meta">传统 PPT</span>
      <p class="t-body">固定分辨率,投影发虚;特效套壳;协作要传文件</p>
    </div>
    <div class="card card-accent" data-anim="right">
      <span class="t-meta">HTML DECK</span>
      <p class="t-body">矢量等比,任意屏清晰;时间轴动效;URL 即分享</p>
    </div>
  </div>
</section>
```

## L8 · 大引用(hero dark,quote recipe)

```html
<section
  class="slide dark hero"
  data-slide-id="quote"
  data-layout="L8"
  data-animate="quote"
>
  <div class="l-center" style="gap:24px">
    <span class="quote-mark" data-anim>“</span>
    <p class="t-hero" style="font-size:44px;font-weight:700" data-anim="line">
      工具的形态,
    </p>
    <p class="t-hero" style="font-size:44px;font-weight:700" data-anim="line">
      决定表达的边界。
    </p>
    <span class="t-meta" data-anim="line">— 本页作者</span>
  </div>
</section>
```

要点:每行一个 `<p data-anim="line">`;引文 ≤2 行;出处必须有。

## L9 · 时间线 / 演进(light)

```html
<section class="slide light" data-slide-id="timeline" data-layout="L9">
  <div class="head">
    <span class="t-kicker" data-anim>TIMELINE</span>
    <h2 class="t-title" data-anim>三代演示载体</h2>
  </div>
  <div class="body-fill">
  <div class="timeline" style="margin-top:.5rem">
    <div class="tl-node" data-anim>
      <span class="tl-dot"></span>
      <div>
        <h3 class="t-sub" style="font-weight:700">1990s · 幻灯片软件</h3>
        <p class="t-body">页面即位图,特效靠模板</p>
      </div>
    </div>
    <div class="tl-node" data-anim>
      <span class="tl-dot"></span>
      <div>
        <h3 class="t-sub" style="font-weight:700">2010s · 云文档 slides</h3>
        <p class="t-body">协作上云,表现力依旧受限</p>
      </div>
    </div>
    <div class="tl-node" data-anim>
      <span class="tl-dot"></span>
      <div>
        <h3 class="t-sub" style="font-weight:700">2020s · HTML deck</h3>
        <p class="t-body">Web 全部能力:矢量、动效、交互、数据直连</p>
      </div>
    </div>
  </div>
</section>
```

## L10 · 收束页(hero dark / accent)

```html
<section class="slide dark hero" data-slide-id="closing" data-layout="L10">
  <div class="l-center" style="gap:20px">
    <h2 class="t-hero" data-anim>开始排你的<br />第一页</h2>
    <p class="t-lead t-kicker-dim" data-anim>
      bisheng · 结构 → 版式 → 门禁 → 放映
    </p>
    <span class="t-meta" data-anim>Q & A</span>
  </div>
</section>
```

要点:收束给行动或金句,不复述目录;与封面色彩呼应(开 dark 收 dark,开 accent 收 accent)。

---

## 版式多样性硬规则

- 7-8 页 deck 至少用 **5 种不同 L 编号**;10 页以上至少 7 种
- 不允许连续 3 页同一主体结构(如连续三页 head+cards)
- 数据专用版式(L3/L9)必须有真实数据;图文版式(L4/L5)无图就换版式
- 图片页可从 L5 网格改造;单张主视觉用 L4 放大图或 l-center + frame-img.r-16x9
