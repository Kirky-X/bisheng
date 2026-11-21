# maliang-gate.md · 马良评审门禁(交付前必过)

> bisheng 管"deck 建得对不对"(结构 / 键位 / 动效标记),maliang 管"好不好用、像不像样"。
> deck 是**给观众看的界面**,必须由设计评审 skill 过一道,不能自评自过。

## 何时跑

- 每次 deck 初稿生成后、正式交付前,**必跑一次**
- 用户明确说"不用评审 / 快速草稿"时:validate_deck.py 照跑,马良门禁按显式 opt-out 跳过,交付说明首行挂 `⚠️ DEGRADED: maliang-gate skipped (用户显式跳过)`

## 怎么跑(动作序列,agent 按此执行)

1. **先过机械门**:运行 `python3 {SKILL_DIR}/scripts/validate_deck.py <deck目录>/index.html`,退出码必须为 0(1=有问题先修,2=没法检查按失败处理,禁止默认成功)
2. **加载马良**:调用 Skill 工具加载 `maliang`,进入其 **critique 子命令**(输入 = deck 的 index.html + 逐页截图;无截图先按 maliang preview 的取证纪律截图)
3. **模式判定**:deck 按 maliang surface-modes 判定——信息传达型 deck 判 **Read**,发布 / 营销型判 **Persuade**;n/a 项照 maliang 规则写理由并重归一化分母
4. **通道映射**(向 maliang 报告声明):
   - **A 通道(设计评审)照常**:Nielsen 10 启发式 + 认知负荷 8 项 + persona 走查,双评估隔离按 maliang 硬性不变式执行
   - **B 通道(机械检测)用 bisheng 替代**:`validate_deck.py` 的结果作为 B 通道输入(maliang 自带的 preview.py check 面向 ui-markdown 产物,对 deck HTML 不适用——**报告里必须显式声明这个替代**,不得假装跑过 preview.py)
5. **产出落盘**:评分快照落 deck 目录 `.maliang/critique/<date>_<deck名>.md`,判词行(`N critical · M major · K minor`)+ verdict 按 maliang 格式
6. **回修闭环**:critical > 0 禁止交付;major 待修处置后再跑一次门禁;bisheng 侧问题修 index.html,maliang 侧发现回填本 skill 的 checklist(规则沉淀)

## 降级路径

| 情形                          | 动作                                                                                                                                                                                                                   |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| maliang skill 加载失败 / 超时 | ①验证是工具不可用而非用法错;②降级为 bisheng checklist 人工逐项走查 + 五秒三问自测(第一眼记住什么 / 焦点在哪 / 以为是什么);③报告首行挂 `⚠️ DEGRADED: maliang unavailable (<原因>)`;④降级结果不等价于门禁通过,结论里注明 |
| 无浏览器截图能力              | A 通道改走"代码走查 + 结构推理",报告标注"未验证实际视觉",不给视觉打分,不写"已通过"                                                                                                                                     |

## 红线

- 马良评审**未跑 = 未交付**;validate_deck.py 通过 ≠ 门禁通过(机械检查只是 B 通道)
- 不得在报告里混写两个 skill 的结论而不标注来源;通道标注照 maliang(`[评审]` / `[脚本]` / `[双方]`)
- 马良对 deck 的修改建议若涉及引擎类名/键位,回修后必须复跑 validate_deck.py + 重新截图
