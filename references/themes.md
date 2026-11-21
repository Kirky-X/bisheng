# themes.md · 主题与颜色

> 颜色搭配错了画面瞬间变丑。**不直接使用用户给的任意颜色值**;默认从预设里选一套。

## 预设(模板内置,html 的 data-theme 切换)

| #   | 主题 id            | 色感                             | 适合                              |
| --- | ------------------ | -------------------------------- | --------------------------------- |
| 1   | `ink` 墨与纸(默认) | 暖纸白 + 墨黑 + 朱红 #B23A17     | 通用 / 商业 / 人文;不知道选啥就它 |
| 2   | `indigo` 靛蓝      | 冷灰白 + 深蓝黑 + 电光靛 #3D5AFE | 科技产品 / 数据汇报 / 发布会      |
| 3   | `forest` 森林墨    | 灰绿白 + 墨绿黑 + 松绿 #1F7A4A   | 自然 / 可持续 / 文化              |
| 4   | `kraft` 牛皮纸     | 暖米黄 + 深褐 + 锈橙 #B4552D     | 怀旧 / 手作 / 独立小众            |

每套主题自带 light / dark 两态变量,slide 用 `light` / `dark` class 取用;`accent` 整页强调色留给封面 / 收束 / 大引用。

## 颜色变量契约(页面里只用这些,不写 hex)

- 文字:`--fg`(主) / `.t-body`(正文自动 78% 混合) / `--muted`(次要) / `--faint`(角标)
- 线:`--line` / `--line-strong`
- 强调:`--accent`(色块与大字) / `--accent-ink`(小字强调) / `--accent-on`(accent 底上的文字)
- 页面级想局部换主题:给该 `<section>` 加 `data-theme="indigo"` 即可(变量落在 section 层生效)

## 硬规则

- 一份 deck 只用一套主题,不要中途换色
- `accent` 页上强调字直接用 `--fg`(反白),不要 `--accent`(同色相叠看不见)
- 一个 deck 只允许一个强调色;多色高亮拼贴 = 立刻掉价
- 描边卡片 / 填充卡片 / accent 卡片三类不同页混排可以,同页并列的卡片必须同类型(突出一张时可单独换 accent)

## 马良 DESIGN.md 桥接(可选,设计系统驱动)

项目里有 `.maliang/DESIGN.md` 时,把它 YAML token 映射为自定义主题,贴在模板 `<style>` 末尾:

```css
[data-theme="brand"] {
  --bg-l: #fbfaf8;
  --fg-l: #212121;
  --bg-d: #121212;
  --fg-d: #f5f5f5;
  --accent: #4d6bfe;
  --accent-on: #ffffff;
}
```

再把 `<html data-theme="brand">`。没有 DESIGN.md 时走预设,不要临时发明主题。
