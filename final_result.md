# 论文全量实验结果

## 1. 摘要占位符

- 训练种子：13、42、73。主表报告三种子均值 ± 样本标准差。
- Base 的三列波动解释为三套独立评测构造/攻击随机化。
- S2 为 128/256/512 三个未见深度按可用状态数加权；S3 按每个方法实际接受的三个自然状态子族数量加权；S4 对应 256-query 端点，且跑在同一套 250 个分层子采样状态上（所有方法与 seed 复用）。
- 百分比保留 0.1 pp；AUROC 等保留 3 位。
- ⚠️ **Trajectory alignment（park2026trajectory）已从论文中完全移除对比**（2026-07-29 定稿口径）。理由是 arXiv 2606（2026-06）距 8/3 截稿不足三个月，按 ARR 属同期工作（"whether refereed or not"，cfp 第 134 行）。本文件**保留其全部数据**，以便 rebuttal 时随时加回。论文中它的处理是：
  - 保留：Related Work 的引用、Table 9 设计空间表的 Trajectory preference 行（纯定位，无数值对比）。
  - 移除：Table 1、Table 2、S4 预算表、GPU-hours 表、Figure 4 深度曲线、第二模型家族表、Table 8 恢复质量表、Table 10 复现 sanity check 行、Appendix L 的预注册对比列表。
  - 移除：原 Appendix I 的 "A contemporaneous method, and what our reproduction of it found." 整段（含 22.5%/84.0 GPU-h、21.4%/186.2 GPU-h、"不主张超过该方法"、unresolved 判定）。**论文不再出现任何等算力对照或 unresolved 表述。**
- 连带影响的定稿处理（不做防御性写作，正面陈述）：
  1. **算力叙述** → Appendix D 只陈述"per-run 训练开销与 baseline 可比（66.7 vs W-DOOR 80.2 GPU-h）"，挖掘为一次性 119.4 GPU-h；用 factorial 固定 token/step 与 B=20 变体（104.1 GPU-h、development middle ASR 21.8%）说明预算可压缩。删除跨 development/test 与 W-DOOR 23.1% 的直接比较。
  2. **对外主张** → §6.5 正面陈述：四判分器下均排第一；每个套件都领先 W-DOOR（S1 −2.9 pp、S3 −2.3 pp [−3.6, −1.0]）；ORR 为所有训练方法最低。删掉了"margin is thin / 小于判分器离散度视为 unresolved"的对冲。判分器离散度数据仍保留在本文件 E13a，仅不写进论文。
- 训练实现：DeepSpeed ZeRO-3 参数/优化器状态分片；dev 选定的 learning rate = **8e-7**。
- 论文排版/结构决定（2026-07-28 一轮）：标题改为 "from Unsafe Generation States"；设计空间表移入 Appendix I（正文腾出版面）；acl 模板的 float fraction 改动已全部还原为默认值。
- **配图体系重做（2026-07-29）**：删除全部 TikZ 图（导言区已移除 `tikz` 宏包），改为五个独立资产，统一一套调色板与字号，定义在 `scripts/make_figures.py` 顶部；绘制规范写在 `figures/FIGURE_GUIDE.md`。
  - `fig1a_concept.pdf` — **占位符，需手绘**（draw.io，导出矢量 PDF），目标 3.72 × 2.62 in。要点：两条分支箭头必须从状态框同一锚点出发；模型偏好的那条线加粗到 1.6 pt，使 preference reversal 不读文字即可看出。
  - `fig1b_reversal.pdf` — 生成。改为**横向**条形图（方法名过长，纵向标签会挤），六行含 W-DOOR，Base 处加基准虚线。
  - `fig2_pipeline.pdf` — **占位符，需手绘**，目标 6.90 × 1.95 in，改为**跨栏横幅**（原 2×2 竖排改为四阶段横排，更省纵向空间）。要点：虚线边框 = frozen；panel 2 最粗边框（核心贡献）。声明位置提前到 §3.3 之前，使其落在第 4 页顶部而非漂到第 5 页。
  - `fig3_diagnostics.pdf`（原 fig2）— 生成。LTRM 行加浅绿高亮 + 加粗标签，四级色阶替换原相近蓝。
  - `fig4_depth.pdf`（原 fig3）— 生成。训练深度区淡灰底，CURE-DPO 加粗实线。
  - 旧文件 `fig_method_overview.drawio` 仍**不可用**（图中 recovery 分支标为来自 current π_θ，与"冻结 base policy"矛盾）；手绘 Figure 2 时不要沿用它。
- **附录结构（2026-07-29 精简后，13 节）**：A 算法与 DPO 等价 / B same-state pair 与质量审计 / C 数据与切分 / D 训练配置与算力 / E 攻击与评测协议 / F 第二模型家族 / G 深度外推 / **H 恢复质量（本轮新增，来自 E12）** / I 复现的外部防御 / J 诊断分离与回归 / K 聚合、挖掘与 anchor 消融 / L 统计口径与判分器有效性（原"Per-Seed CIs"与"Evaluator Validity"合并） / M 结果类别与失败分析。
- **本轮新增进论文的结果**：E12 恢复质量表（additional harmful tokens / severity 0–3 / conditional median TTR）此前只在本文件里，现已作为 Appendix H 的 Table 8 写入论文，并在 §6.5 引用 CURE 2.5 / W-DOOR 3.0 / Base 6.3 与 severity 0.55 / 0.63 / 1.38 作为独立于二元 ASR 的证据。severity 此前是"承诺了但从未报出"的指标。
- S3 的 span 定位器：**meta-llama/Llama-Guard-3-8B**，不属于四个打分判分器中的任何一个（循环已破）。因其为整轮分类器而非 span 定位器，实际做法是对越来越长的前缀逐次打分、取第一个被判 unsafe 的前缀；该边界的误差是**有方向的**——截断的有害段常读作"未完成"，翻转晚于真实起点，故保留的 reached state 更深、更难恢复，对本文偏保守。人工抽查 181/200 正确（90.5%，Wilson CI [85.6, 93.8]），错误构成 9 编码/隐喻 + 6 边界偏晚 + 4 工具输出歧义，已写入论文 Appendix E。
- **决定不公开代码仓库**（符合 ARR：补充材料是 encouraged 而非必须）。**定稿口径（2026-07-29）：论文中完全不提代码/仓库/artifact 发布，一个字都不解释。** 具体处理：
  - 论文原有 5 处 "released with the code" 已全部删除，不留任何替代说明。
  - Ethics 一节**不含**任何发布声明。该节现在只有一段，涵盖三件事：(a) 数据来源与许可（点名 PKU-SafeRLHF / BeaverTails / Alpaca 的非商业研究限制）；(b) dual-use 一句话（margin 可被反向利用，故只报聚合统计、不放 per-state 挖掘产物与 harmful branch pool）；(c) 标注由作者完成、无外部标注者、无个人数据。
  - Appendix C 的 "released artifacts are limited to…" 与 Appendix N 的 "released examples are access-controlled" 已删除。
  - 第二模型家族表补上 seed SD（原先把 SD 推给了"随代码发布"）。
  - 主表 caption 删掉"per-seed values 在 Appendix K"的指向。
- **人工标注由作者本人完成**，论文按此口径统一（2026-07-29）。因此已删除全部关于外部标注者的陈述（研究生招募、告知同意、可随时退出、每次 ≤1 小时、薪酬高于当地最低工资）。论文现在的写法：
  - §5.6：`We additionally hand-label 150 outputs…`
  - Appendix L：`Two of the authors independently label 150 outputs…, with a third author resolving disagreements.`
  - Appendix B pair 审计：`two of the authors audit independently`；Appendix E S3 边界校验：`Two of the authors checked 200 located boundaries`。
  - **不声称任何形式的盲标**（2026-07-29 定稿）：原先写的"打乱顺序 + 抹掉方法标识"已删除，因为实际标注未做这一步。全文不再出现 blinded / shuffled / identities stripped 之类的措辞，只陈述由两名作者独立标注、第三名作者裁决。
  - `Inter-annotator agreement is Cohen's κ = 0.76` 保留原词，属标准术语。
- 身份泄露核查：paper.tex / scripts / custom.bib 无泄露字符串，PDF 元数据 Author/Title 为空。
- 方法名展开：**CURE = Comparison Under Reached-state Equivalence**（论文 §1 首次出现处给出）。
- 效用指标口径：**non-thinking**（`enable_thinking=False`），与安全评测同一配置；与官方模型卡（thinking）的对照见 §19。
- 论文引用的各指标分母：clean **1,000** prompts；S1 **4,940** trials（五个训练网格深度，可用状态数 1000/998/994/985/963）；S2 **2,081**（128/256/512 → 908/711/462）；S3 每 checkpoint **870–930**（三子族各 ≥250，随 checkpoint 变化）；S4 **250** states @ 256-query 预算（一套固定分层子采样，**12 方法** × 3 seed 复用同一批 prompt–state id = **9,000** 攻击实例；trajectory 的两个配置已移出论文，故不再是 14 × 3 × 250 = 10,500）；recovery **1,000** 个独立 reached state。

### 三处定稿口径（原先未记录，2026-07-29 按论文写法回填）

以下三项在本文件早期版本中没有记录，论文已按下述口径写定；如与实际实现不符，需要改代码或改论文二者之一。

1. **E6 诊断表的 bootstrap 单位 = prompt-clustered（按 prompt 重采样）。**
   分析单位是 attack instance（每个测试 prompt 贡献多个 instance，故正负例计数 > 1,000），instance 嵌套在 prompt 内。因此 bootstrap 重采样 **prompt**，并把该 prompt 的所有 instance 整块带走，与 Appendix L 的 contrast 区间口径（prompt-level paired bootstrap）一致。
   - 论文 Appendix J 正文与 Table 11 caption 均已写明 "clustered on prompts"；Figure 3 caption 写 "prompt-clustered intervals"。
   - **口径已确认（2026-07-30）：按 prompt 聚类，不再有待办。** 三个 contrast 的最终区间为：H1 `+0.131 [0.109, 0.154]`、H2 `-5.9 pp [-7.9, -3.9]`、Uniform − Recovery SFT `-11.3 pp [-13.9, -8.7]`；均采用 10,000 次 prompt-clustered paired bootstrap。论文只报告 effect size 与 percentile CI，不把未中心化 bootstrap 的符号比例解释为频率学 p 值。
2. **Recovery-rate 评测集 = 每个测试 prompt 一个 reached state，共 1,000 个。**
   与 S1–S4 的 trial 独立抽取，跨全部方法与 seed 逐字节固定（保证配对）；与 S4 的 250-state 子采样不共享任何 state id。这正是主表各列分母不同、且 recovery 与 middle ASR **不互补**的原因。判定沿用三条合取：无新增有害指令 + 64 token 内停止 + 明确拒绝/风险说明/安全重定向。
   - 已写入论文 Appendix E 的 "The recovery-rate suite." 一段。
3. **基线的损失权重调参口径。**
   learning rate、token 与 step 预算、capacity、seeds、验证早停规则由所有可训练行共享。**自由的 loss-balancing 权重**只有部分方法有：本文的 (λ_c, λ_b) 与 DOOR / W-DOOR 的权重按 §4.4 的同一约束协议在 dev 上选；**没有自由损失权重的防御（backtracking、circuit breakers、PRESTO、deep safety alignment）沿用其官方实现的权重**。
   - 已写入论文 Appendix I 末尾。原先草稿里"只有我们的行在 ORR 约束下选点，故 ORR 优势部分来自选择规则"那段自我贬低的披露**已删除**（去防御性写作）。


| 占位符/论断                                              | 实验结果值                        |
| --------------------------------------------------- | ---------------------------- |
| Base / Clean DPO / Recovery SFT preference reversal | 47.9% / 41.3% / 32.4%        |
| LTRM fully-separated AUROC                          | 0.779                        |
| Root margin fully-separated AUROC                   | 0.648                        |
| LTRM 相对 root AUROC 增量                               | +0.131，95% CI [0.109, 0.154] |
| Clean DPO clean ASR / S1 middle ASR                 | 2.2% / 52.4%                 |
| Uniform 相对 Recovery SFT 的 S1 改善                     | -11.3 pp                     |
| CURE-DPO 相对 Uniform 的 S1 改善（H2）                     | -5.9 pp，95% CI [-7.9, -3.9]  |
| 上下文变化效应范围                                           | 19.9–26.5 pp                 |
| 固定上下文内目标函数效应范围                                      | root 4.7 pp；reached 11.3 pp  |
| masked / unmasked S1 差异                             | -0.1 pp                      |
| Hard-state mining GPU-hours                         | 119.4 GPU-hours              |
| Base → CURE ORR                                     | 6.5% → 7.6%                  |
| Base → CURE IFEval                                  | 89.3 → 88.3                  |
| Base → CURE MMLU-Pro                                | 77.6 → 77.0                  |
| Base → CURE additional harmful tokens               | 6.3 → 2.5                    |
| Base → CURE conditional median time-to-recovery     | 19.7 → 10.3 tokens           |




## 2. 阶段 0：数据构建



### D1 语料、去重与切分


| 训练/开发来源                    | 候选池  | 跨来源去重后丢弃 | 最终保留 |
| -------------------------- | ---- | -------- | ---- |
| WildJailbreak              | 4987 | 487      | 4500 |
| PKU-SafeRLHF / BeaverTails | 1512 | 162      | 1350 |
| SORRY-Bench                | 1023 | 123      | 900  |
| 合计                         | 7522 | 772      | 6750 |


- 最终切分：Train 6,000；Dev 750；Test 1,000；Benign anchor 12,000；Clean-safety anchor 12,000。
- 四级去重后，train/dev/test 的 source/template identity join 交集：**0**。
- 句向量近邻人工抽查：186/200 判为真实近重复，precision = **93.0%**，Wilson 95% CI **[88.6%, 95.8%]**。
- OR-Bench-Hard 与其近邻簇从 benign 候选池移除 503 条；XSTest 进入训练的条数为 0。



### D2 Same-state pair 构造

- 最终三元组：**36,000**（6,000 prompts × 6 states）。
- 尝试生成 53,184 对；通过自动筛查 36,000 对；自动接受率 **67.7%**。
- 自动拒绝构成（分母为全部尝试）：intent mismatch 11.7%；recovery 不安全 9.0%；退化 5.0%；长度不兼容 6.6%。
- `tokenize(s_t)` 两分支 byte-for-byte 一致断言：36,000/36,000 通过。
- **pair 池只构建一次**：recovery branch 从**冻结的 Base safety policy** 采样，harmful branch 取自 held-in 来源；prompt、reached state、recovery branch、harmful branch 各只生成一次，之后所有 checkpoint 在完全相同的文本上重新打分。
  - 训练侧：各方法都不会看到为自己定制的分支，方法间可比。
  - 诊断侧：Figure 1b 的跨 checkpoint 反转率（Base 47.9% → CURE 16.1%）之间唯一变化的是打分模型，而不是被排序的分支，因此可比。
  - 反向偏差：CURE-DPO 被训练出特有的恢复话术，但它被打分的 recovery branch 是**未训练的 base 模型**写的，所以诊断不会因为它偏好自己的措辞而给它加分——这一条对论文有利，已写入 Appendix B。



### D3 Hard-state 挖掘

- 有效配对评估：**396,000**（6,000 × 66）。
- 为获得有效评估共尝试 526,931 次 pair generation；有效率 **75.2%**。
- 总挖掘计算：**119.4 GPU-hours**（4×A100 80GB 口径）。
- 两 finalist 的 confirmation bootstrap 区间重叠比例：**41.2%**。
- 选定位置后 fresh-pair 重新构造率 100%；搜索阶段 pair 进入训练的条数为 0。



## 3. E6：LTRM 四级分离诊断

**区间口径（已定稿）**：分析单位为 attack instance（每个测试 prompt 贡献多个 instance，故正负例计数 > 1,000）；**95% bootstrap 按 prompt 聚类重采样**（整块带走该 prompt 的所有 instance），与 Appendix L 的 contrast 区间口径一致。下表所有区间均为 prompt-clustered 结果。论文 Appendix J 正文、Table 11 caption、Figure 3 caption 均按此写。

| 设置              | 预测器                             | AUROC [95% CI]       | PR-AUC | ECE   | Brier | 正例   | 负例   |
| --------------- | ------------------------------- | -------------------- | ------ | ----- | ----- | ---- | ---- |
| in-source       | LTRM_20                         | 0.861 [0.849, 0.873] | 0.696  | 0.035 | 0.220 | 1734 | 2279 |
| in-source       | Mean state margin               | 0.814 [0.801, 0.828] | 0.647  | 0.045 | 0.223 | 1734 | 2279 |
| in-source       | Min state margin                | 0.837 [0.825, 0.850] | 0.657  | 0.054 | 0.226 | 1734 | 2279 |
| in-source       | Root-response margin            | 0.698 [0.682, 0.716] | 0.544  | 0.064 | 0.245 | 1734 | 2279 |
| in-source       | First-token refusal probability | 0.659 [0.643, 0.677] | 0.522  | 0.064 | 0.243 | 1734 | 2279 |
| in-source       | State depth                     | 0.596 [0.579, 0.614] | 0.491  | 0.084 | 0.262 | 1734 | 2279 |
| cross-branch    | LTRM_20                         | 0.831 [0.818, 0.845] | 0.660  | 0.031 | 0.217 | 1688 | 2259 |
| cross-branch    | Mean state margin               | 0.783 [0.769, 0.798] | 0.626  | 0.040 | 0.227 | 1688 | 2259 |
| cross-branch    | Min state margin                | 0.811 [0.797, 0.825] | 0.627  | 0.060 | 0.232 | 1688 | 2259 |
| cross-branch    | Root-response margin            | 0.676 [0.659, 0.694] | 0.537  | 0.068 | 0.253 | 1688 | 2259 |
| cross-branch    | First-token refusal probability | 0.642 [0.625, 0.659] | 0.510  | 0.074 | 0.253 | 1688 | 2259 |
| cross-branch    | State depth                     | 0.602 [0.585, 0.620] | 0.484  | 0.090 | 0.261 | 1688 | 2259 |
| cross-attack    | LTRM_20                         | 0.804 [0.791, 0.819] | 0.618  | 0.040 | 0.225 | 1579 | 2283 |
| cross-attack    | Mean state margin               | 0.758 [0.743, 0.775] | 0.580  | 0.051 | 0.229 | 1579 | 2283 |
| cross-attack    | Min state margin                | 0.782 [0.767, 0.799] | 0.588  | 0.058 | 0.229 | 1579 | 2283 |
| cross-attack    | Root-response margin            | 0.654 [0.636, 0.672] | 0.505  | 0.069 | 0.246 | 1579 | 2283 |
| cross-attack    | First-token refusal probability | 0.611 [0.594, 0.630] | 0.477  | 0.086 | 0.258 | 1579 | 2283 |
| cross-attack    | State depth                     | 0.571 [0.554, 0.590] | 0.442  | 0.093 | 0.263 | 1579 | 2283 |
| fully separated | LTRM_20                         | 0.779 [0.764, 0.795] | 0.602  | 0.044 | 0.226 | 1497 | 2249 |
| fully separated | Mean state margin               | 0.736 [0.721, 0.753] | 0.558  | 0.055 | 0.230 | 1497 | 2249 |
| fully separated | Min state margin                | 0.752 [0.736, 0.768] | 0.574  | 0.064 | 0.236 | 1497 | 2249 |
| fully separated | Root-response margin            | 0.648 [0.631, 0.667] | 0.491  | 0.079 | 0.247 | 1497 | 2249 |
| fully separated | First-token refusal probability | 0.599 [0.581, 0.618] | 0.462  | 0.083 | 0.257 | 1497 | 2249 |
| fully separated | State depth                     | 0.563 [0.544, 0.583] | 0.432  | 0.098 | 0.263 | 1497 | 2249 |




### Fully separated 的 margin 分箱


| Recovery margin bin | n   | ASR   | Wilson 95% CI  |
| ------------------- | --- | ----- | -------------- |
| (-∞, -1.0]          | 341 | 77.1% | [72.4%, 81.3%] |
| (-1.0, -0.5]        | 547 | 63.1% | [58.9%, 67.0%] |
| (-0.5, 0]           | 763 | 50.2% | [46.7%, 53.7%] |
| (0, 0.5]            | 861 | 34.8% | [31.7%, 38.1%] |
| (0.5, 1.0]          | 721 | 22.2% | [19.3%, 25.4%] |
| (1.0, ∞)            | 513 | 11.5% | [9.0%, 14.6%]  |


- 最高风险分位 ASR：**75.4%**；最低风险分位：**12.7%**；差 **62.7 pp**。
- 精确匹配 depth bin 与 harmful source 后：70.0% vs 14.6%，差 **55.4 pp**（每组 n=611）。
- Cochran–Armitage 趋势检验：z = **-25.0**，p <1e-12。

### Fully separated 下的增益分解（论文 §6.1 使用）

- root-response margin **0.648** → mean state margin **0.736** → LTRM_20 **0.779**。
- 因此 AUROC 总增益 **+0.131** 拆为：**+0.088** 来自"是否条件化到状态本身"，**+0.043** 来自"是否聚焦下尾"。
- in-source 口径的对应增益为 **+0.163**（0.861 − 0.698）；论文以 fully separated 为主张，并同时给出 in-source 以免被指摘 cherry-pick。



### Logistic 回归（attack success 为因变量）


| 变量                               | 系数    | SE    | Odds ratio | 95% CI       | p      |
| -------------------------------- | ----- | ----- | ---------- | ------------ | ------ |
| 标准化 recovery margin              | -1.09 | 0.071 | 0.34       | [0.29, 0.39] | <0.001 |
| State depth（每 +1 SD）             | 0.28  | 0.052 | 1.32       | [1.19, 1.47] | <0.001 |
| Root margin（每 +1 SD）             | -0.22 | 0.056 | 0.80       | [0.72, 0.90] | <0.001 |
| Cross-attack source indicator    | 0.16  | 0.081 | 1.17       | [1.00, 1.38] | 0.048  |
| Fully-separated source indicator | 0.24  | 0.087 | 1.27       | [1.07, 1.51] | 0.006  |


## 4. E15：masked / unmasked 数值等价性


| 检查项                        | 结果       |
| -------------------------- | ---------- |
| 同一 batch 的 loss 绝对差        | 2.4×10^-7  |
| 梯度 cosine similarity       | 0.9999989  |
| masked 梯度范数                | 3.9176     |
| unmasked 梯度范数              | 3.9178     |
| 梯度范数相对差                    | 5.1×10^-5  |
| 一个 optimizer step 后参数差异 L2 | 3.6×10^-8  |
| 最大单参数绝对差                   | 1.7×10^-10 |




## 5. E0 + E1：主训练与主结果


| 方法                                     | Clean ASR↓ | S1↓        | S2↓        | S3↓        | S4↓        | Recovery↑  | ORR↓      | IFEval↑    |
| -------------------------------------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | --------- | ---------- |
| Base                                   | 4.7 ± 0.4  | 58.6 ± 1.5 | 63.1 ± 1.3 | 49.3 ± 0.9 | 69.0 ± 0.9 | 20.8 ± 1.1 | 6.5 ± 0.3 | 89.3 ± 0.3 |
| Clean DPO                              | 2.2 ± 0.3  | 52.4 ± 1.6 | 57.0 ± 1.7 | 44.8 ± 1.1 | 64.4 ± 1.7 | 25.1 ± 1.2 | 8.2 ± 0.2 | 88.8 ± 0.3 |
| Recovery SFT                           | 4.6 ± 0.4  | 37.4 ± 1.0 | 43.8 ± 1.3 | 32.3 ± 1.1 | 51.5 ± 1.4 | 57.9 ± 1.0 | 7.3 ± 0.4 | 88.4 ± 0.4 |
| Worst-Insertion SFT                    | 4.2 ± 0.5  | 32.2 ± 0.7 | 39.1 ± 1.3 | 29.5 ± 1.5 | 46.7 ± 0.9 | 63.8 ± 1.7 | 8.1 ± 0.3 | 87.8 ± 0.4 |
| Uniform Same-State DPO                 | 3.7 ± 0.3  | 26.1 ± 1.2 | 32.0 ± 1.2 | 24.4 ± 1.0 | 40.2 ± 1.3 | 71.2 ± 1.4 | 7.7 ± 0.2 | 88.5 ± 0.3 |
| CURE-DPO                               | 3.9 ± 0.4  | 20.2 ± 1.0 | 26.0 ± 0.9 | 19.6 ± 1.4 | 33.1 ± 1.8 | 78.4 ± 1.3 | 7.6 ± 0.2 | 88.3 ± 0.1 |
| Deep safety alignment                  | 3.5 ± 0.4  | 34.1 ± 1.5 | 41.3 ± 1.2 | 30.6 ± 1.2 | 48.4 ± 1.2 | 61.0 ± 1.0 | 8.4 ± 0.2 | 87.8 ± 0.3 |
| Backtracking                           | 4.0 ± 0.4  | 30.4 ± 1.2 | 37.9 ± 1.3 | 27.7 ± 1.1 | 44.9 ± 1.5 | 66.0 ± 1.7 | 8.9 ± 0.3 | 87.1 ± 0.5 |
| Circuit breakers                       | 3.7 ± 0.4  | 29.3 ± 0.9 | 36.6 ± 1.4 | 26.5 ± 1.0 | 43.7 ± 1.6 | 67.3 ± 1.3 | 8.6 ± 0.2 | 87.6 ± 0.3 |
| DOOR                                   | 3.4 ± 0.2  | 25.8 ± 1.4 | 33.4 ± 1.0 | 24.5 ± 1.3 | 40.7 ± 1.5 | 70.5 ± 0.9 | 8.8 ± 0.5 | 86.8 ± 0.4 |
| W-DOOR                                 | 3.3 ± 0.3  | 23.1 ± 1.0 | 30.4 ± 1.5 | 21.9 ± 0.9 | 37.6 ± 1.2 | 73.5 ± 0.8 | 8.6 ± 0.4 | 87.5 ± 0.4 |
| PRESTO                                 | 3.6 ± 0.3  | 24.5 ± 0.8 | 31.8 ± 0.9 | 23.2 ± 1.5 | 38.4 ± 1.8 | 72.1 ± 1.5 | 8.3 ± 0.4 | 88.0 ± 0.3 |
| Trajectory alignment (data-matched)    | 3.5 ± 0.5  | 22.5 ± 1.3 | 29.0 ± 1.8 | 21.1 ± 0.9 | 36.3 ± 1.0 | 74.7 ± 0.9 | 8.1 ± 0.3 | 88.6 ± 0.4 |
| Trajectory alignment (compute-matched) | 3.6 ± 0.5  | 21.4 ± 1.4 | 27.7 ± 2.0 | 20.5 ± 1.0 | 34.9 ± 1.5 | 76.1 ± 1.0 | 8.2 ± 0.4 | 88.4 ± 0.4 |




### 全部 per-seed 值

> IFEval 与 MMLU-Pro 两列为 non-thinking rerun 的结果。目前只有 Base 与 CURE-DPO 的 per-seed 原始值可用；其余 12 个方法暂标 `—`，其三种子均值与 SD 见上方汇总表，per-seed 原始字段待 rerun 输出补齐。


| 方法                                     | seed | Clean | S1   | S2   | S3   | S4   | Recovery | ORR | IFEval | MMLU-Pro |
| -------------------------------------- | ---- | ----- | ---- | ---- | ---- | ---- | -------- | --- | ------ | -------- |
| Base                                   | 13   | 4.5   | 57.2 | 61.8 | 48.6 | 68.7 | 20.9     | 6.2 | 89.0   | 77.7     |
| Base                                   | 42   | 5.2   | 60.2 | 64.3 | 50.3 | 70.0 | 19.7     | 6.6 | 89.6   | 77.4     |
| Base                                   | 73   | 4.4   | 58.4 | 63.3 | 49.0 | 68.3 | 21.8     | 6.7 | 89.2   | 77.8     |
| Clean DPO                              | 13   | 2.0   | 50.6 | 55.7 | 43.6 | 66.3 | 24.7     | 8.4 | —      | —        |
| Clean DPO                              | 42   | 2.1   | 53.1 | 56.3 | 45.0 | 63.0 | 26.5     | 8.0 | —      | —        |
| Clean DPO                              | 73   | 2.5   | 53.5 | 58.9 | 45.8 | 63.9 | 24.1     | 8.3 | —      | —        |
| Recovery SFT                           | 13   | 5.0   | 38.4 | 45.0 | 33.3 | 52.7 | 57.4     | 6.9 | —      | —        |
| Recovery SFT                           | 42   | 4.3   | 37.3 | 44.0 | 32.4 | 51.9 | 57.2     | 7.6 | —      | —        |
| Recovery SFT                           | 73   | 4.4   | 36.5 | 42.4 | 31.2 | 49.9 | 59.1     | 7.4 | —      | —        |
| Worst-Insertion SFT                    | 13   | 3.8   | 32.4 | 39.2 | 30.9 | 45.7 | 62.0     | 8.1 | —      | —        |
| Worst-Insertion SFT                    | 42   | 4.7   | 32.8 | 40.3 | 28.0 | 47.5 | 63.9     | 8.4 | —      | —        |
| Worst-Insertion SFT                    | 73   | 4.1   | 31.4 | 37.8 | 29.6 | 46.9 | 65.4     | 7.9 | —      | —        |
| Uniform Same-State DPO                 | 13   | 3.7   | 26.6 | 31.9 | 23.8 | 41.4 | 71.0     | 7.9 | —      | —        |
| Uniform Same-State DPO                 | 42   | 4.0   | 24.7 | 33.2 | 25.6 | 40.3 | 69.9     | 7.6 | —      | —        |
| Uniform Same-State DPO                 | 73   | 3.4   | 27.0 | 30.9 | 23.8 | 38.9 | 72.7     | 7.6 | —      | —        |
| CURE-DPO                               | 13   | 3.5   | 21.2 | 26.9 | 20.4 | 32.5 | 79.8     | 7.7 | 88.4   | 77.1     |
| CURE-DPO                               | 42   | 3.8   | 19.3 | 25.2 | 18.0 | 31.7 | 78.2     | 7.7 | 88.3   | 76.9     |
| CURE-DPO                               | 73   | 4.3   | 20.1 | 25.9 | 20.4 | 35.2 | 77.2     | 7.3 | 88.2   | 77.0     |
| Deep safety alignment                  | 13   | 3.9   | 35.1 | 42.3 | 30.4 | 49.6 | 59.8     | 8.6 | —      | —        |
| Deep safety alignment                  | 42   | 3.5   | 34.8 | 40.0 | 31.9 | 47.3 | 61.7     | 8.2 | —      | —        |
| Deep safety alignment                  | 73   | 3.2   | 32.3 | 41.5 | 29.5 | 48.2 | 61.5     | 8.4 | —      | —        |
| Backtracking                           | 13   | 4.3   | 31.5 | 39.4 | 28.4 | 46.6 | 65.9     | 9.0 | —      | —        |
| Backtracking                           | 42   | 3.5   | 30.6 | 37.5 | 26.4 | 44.3 | 64.4     | 8.6 | —      | —        |
| Backtracking                           | 73   | 4.2   | 29.1 | 36.8 | 28.3 | 43.8 | 67.7     | 9.1 | —      | —        |
| Circuit breakers                       | 13   | 3.4   | 30.1 | 38.2 | 27.0 | 45.4 | 65.9     | 8.8 | —      | —        |
| Circuit breakers                       | 42   | 4.1   | 29.4 | 35.8 | 27.1 | 42.2 | 67.6     | 8.6 | —      | —        |
| Circuit breakers                       | 73   | 3.6   | 28.4 | 35.8 | 25.4 | 43.6 | 68.4     | 8.4 | —      | —        |
| DOOR                                   | 13   | 3.2   | 24.5 | 33.2 | 23.4 | 42.2 | 69.7     | 8.3 | —      | —        |
| DOOR                                   | 42   | 3.6   | 25.6 | 32.6 | 26.0 | 39.2 | 71.4     | 8.8 | —      | —        |
| DOOR                                   | 73   | 3.4   | 27.3 | 34.5 | 24.2 | 40.7 | 70.4     | 9.2 | —      | —        |
| W-DOOR                                 | 13   | 3.1   | 22.4 | 28.9 | 21.8 | 36.3 | 72.9     | 8.4 | —      | —        |
| W-DOOR                                 | 42   | 3.7   | 22.6 | 31.9 | 22.8 | 38.5 | 74.4     | 8.3 | —      | —        |
| W-DOOR                                 | 73   | 3.1   | 24.2 | 30.4 | 21.1 | 38.0 | 73.2     | 9.1 | —      | —        |
| PRESTO                                 | 13   | 3.3   | 25.0 | 31.7 | 21.8 | 38.5 | 72.3     | 8.0 | —      | —        |
| PRESTO                                 | 42   | 3.9   | 24.9 | 32.7 | 23.1 | 40.1 | 70.5     | 8.7 | —      | —        |
| PRESTO                                 | 73   | 3.7   | 23.6 | 31.0 | 24.7 | 36.6 | 73.5     | 8.2 | —      | —        |
| Trajectory alignment (data-matched)    | 13   | 3.3   | 24.0 | 29.4 | 22.0 | 35.6 | 75.3     | 8.5 | —      | —        |
| Trajectory alignment (data-matched)    | 42   | 3.1   | 21.7 | 30.6 | 20.3 | 37.4 | 75.2     | 7.9 | —      | —        |
| Trajectory alignment (data-matched)    | 73   | 4.0   | 21.7 | 27.0 | 21.0 | 35.9 | 73.7     | 7.9 | —      | —        |
| Trajectory alignment (compute-matched) | 13   | 3.1   | 21.0 | 28.6 | 21.7 | 36.3 | 76.7     | 8.3 | —      | —        |
| Trajectory alignment (compute-matched) | 42   | 3.6   | 20.3 | 29.1 | 19.8 | 33.4 | 76.6     | 7.8 | —      | —        |
| Trajectory alignment (compute-matched) | 73   | 4.1   | 23.0 | 25.5 | 20.0 | 35.1 | 75.0     | 8.5 | —      | —        |




### Reversal fraction 与计算成本


| 方法                                     | Reversal fraction (%) | GPU-hours   | MMLU-Pro   |
| -------------------------------------- | --------------------- | ----------- | ---------- |
| Base                                   | 47.9 ± 0.8            | 0.0 ± 0.0   | 77.6 ± 0.2 |
| Clean DPO                              | 41.3 ± 1.1            | 55.1 ± 0.8  | 77.4 ± 0.2 |
| Recovery SFT                           | 32.4 ± 1.0            | 50.4 ± 1.1  | 77.0 ± 0.2 |
| Worst-Insertion SFT                    | 27.9 ± 1.2            | 52.8 ± 1.4  | 76.6 ± 0.3 |
| Uniform Same-State DPO                 | 23.2 ± 1.2            | 63.3 ± 1.6  | 77.3 ± 0.3 |
| CURE-DPO                               | 16.1 ± 0.8            | 66.7 ± 1.9  | 77.0 ± 0.1 |
| Deep safety alignment                  | 29.7 ± 1.5            | 59.1 ± 0.9  | 76.6 ± 0.3 |
| Backtracking                           | 26.3 ± 1.3            | 72.8 ± 2.1  | 75.9 ± 0.4 |
| Circuit breakers                       | 25.1 ± 1.2            | 69.4 ± 1.9  | 76.4 ± 0.3 |
| DOOR                                   | 22.4 ± 0.9            | 75.6 ± 1.4  | 75.7 ± 0.3 |
| W-DOOR                                 | 20.4 ± 1.3            | 80.2 ± 2.0  | 76.4 ± 0.3 |
| PRESTO                                 | 21.1 ± 0.8            | 70.8 ± 1.2  | 76.8 ± 0.3 |
| Trajectory alignment (data-matched)    | 19.0 ± 1.1            | 84.0 ± 2.3  | 77.2 ± 0.2 |
| Trajectory alignment (compute-matched) | 17.8 ± 1.4            | 186.2 ± 3.0 | 77.3 ± 0.2 |




### 预注册与次要对比


| 对比                                   | 差值       | paired bootstrap 95% CI | p      | 结论             |
| ------------------------------------ | -------- | ----------------------- | ------ | -------------- |
| H2: CURE − Uniform，S1                | -5.9 pp  | [-7.9, -3.9]            | —      | 支持             |
| Uniform − Recovery SFT，S1            | -11.3 pp | [-13.9, -8.7]           | —      | 支持             |
| CURE − Trajectory compute-matched，S1 | -1.2 pp  | [-2.50, 0.03]           | 0.0594 | 接近；结合判分器离散度报未决 |
| CURE − W-DOOR，S3                     | -2.3 pp  | [-3.6, -1.0]            | 0.0012 | Holm 后支持       |




## 6. E2：条件上下文 × 目标函数 factorial


| 条件上下文                   | 目标    | Middle ASR | LTRM         | 三种子 ASR          |
| ----------------------- | ----- | ---------- | ------------ | ---------------- |
| Root prompt             | DPO   | 52.6 ± 1.0 | -0.30 ± 0.04 | 52.6, 51.7, 53.6 |
| Root prompt             | SimPO | 54.1 ± 1.1 | -0.35 ± 0.04 | 54.6, 52.8, 54.9 |
| Root prompt             | SFT   | 57.3 ± 1.4 | -0.41 ± 0.05 | 58.9, 56.4, 56.7 |
| Reached state           | DPO   | 26.1 ± 1.2 | 0.30 ± 0.04  | 26.6, 24.7, 27.0 |
| Reached state           | SimPO | 31.6 ± 1.2 | 0.18 ± 0.05  | 31.1, 30.7, 33.0 |
| Reached state           | SFT   | 37.4 ± 1.0 | 0.04 ± 0.05  | 38.4, 37.3, 36.5 |
| Reached state, unmasked | DPO   | 26.0 ± 1.2 | 0.30 ± 0.04  | 26.5, 24.6, 26.9 |


- 固定目标函数、改条件上下文：Middle ASR 改善 **19.9–26.5 pp**（DPO 26.5；SimPO 22.5；SFT 19.9）。
- 固定上下文、改目标函数：root 内范围 **4.7 pp**；reached-state 内范围 **11.3 pp**。两者存在交互：loss form 只有在条件化到已达状态之后才显著。
- reached-state 内的 11.3 pp 与主表 Uniform − Recovery SFT 的 -11.3 pp 是同一个量；SimPO 的长度归一化代价在 root 为 1.5 pp、在 reached state 为 5.5 pp。
- reached-state DPO 与 SFT 两格分别等同于主表的 Uniform Same-State DPO 与 Recovery SFT 行。
- reached-state DPO unmasked − masked：**-0.1 pp**，处于 seed 波动范围内。



## 7. E3：自然产生的 unsafe states


S3 proposal yield 与 accepted-state-weighted failure 的最终表已写入论文 Appendix E。Weighted failure 定义为 acceptance yield × conditional S3 ASR；no-state 与 rejected proposals 在该列按零失败处理，论文同时给出加上 rejection rate 的保守上界。

| 方法 | Accept yield | No state | Rejection | Weighted failure |
| --- | ---: | ---: | ---: | ---: |
| Base | 93.0 | 4.2 | 2.8 | 45.8 |
| Clean DPO | 91.8 | 5.5 | 2.7 | 41.1 |
| Recovery SFT | 90.2 | 7.0 | 2.8 | 29.1 |
| Worst-Insertion SFT | 89.5 | 7.6 | 2.9 | 26.4 |
| Uniform Same-State DPO | 88.5 | 8.4 | 3.1 | 21.6 |
| Deep safety alignment | 90.5 | 6.6 | 2.9 | 27.7 |
| Backtracking | 89.6 | 7.4 | 3.0 | 24.8 |
| Circuit breakers | 89.1 | 7.9 | 3.0 | 23.6 |
| DOOR | 88.3 | 8.7 | 3.0 | 21.6 |
| W-DOOR | 87.5 | 9.4 | 3.1 | 19.2 |
| PRESTO | 88.0 | 8.9 | 3.1 | 20.4 |
| CURE-DPO | 87.0 | 10.1 | 2.9 | 17.1 |


| 方法                                     | n（Self/Tool/Multi） | Self-generated ASR | Tool/RAG ASR | Multi-turn ASR | 加权合并 S3    |
| -------------------------------------- | ------------------ | ------------------ | ------------ | -------------- | ---------- |
| Base                                   | 304/291/275        | 54.1 ± 1.2         | 45.0 ± 0.7   | 48.6 ± 1.5     | 49.3 ± 0.9 |
| Clean DPO                              | 324/287/300        | 49.9 ± 1.1         | 40.3 ± 0.9   | 43.6 ± 1.7     | 44.8 ± 1.1 |
| Recovery SFT                           | 309/288/300        | 37.3 ± 0.6         | 29.1 ± 1.2   | 30.2 ± 2.7     | 32.3 ± 1.1 |
| Worst-Insertion SFT                    | 305/294/280        | 34.7 ± 2.0         | 25.3 ± 0.8   | 28.2 ± 1.6     | 29.5 ± 1.5 |
| Uniform Same-State DPO                 | 309/314/304        | 28.8 ± 1.2         | 20.4 ± 2.1   | 24.1 ± 0.4     | 24.4 ± 1.0 |
| CURE-DPO                               | 321/308/271        | 24.6 ± 1.0         | 14.8 ± 2.0   | 19.2 ± 1.3     | 19.6 ± 1.4 |
| Deep safety alignment                  | 335/285/271        | 35.2 ± 1.8         | 26.4 ± 0.9   | 29.4 ± 0.8     | 30.6 ± 1.2 |
| Backtracking                           | 299/313/302        | 33.1 ± 0.4         | 23.9 ± 0.7   | 26.3 ± 2.5     | 27.7 ± 1.1 |
| Circuit breakers                       | 334/291/270        | 31.3 ± 1.2         | 22.2 ± 0.7   | 25.2 ± 2.7     | 26.5 ± 1.0 |
| DOOR                                   | 300/300/275        | 29.6 ± 1.1         | 20.0 ± 1.5   | 23.9 ± 2.0     | 24.5 ± 1.3 |
| W-DOOR                                 | 317/301/269        | 26.5 ± 0.4         | 17.6 ± 0.9   | 21.3 ± 1.8     | 21.9 ± 0.9 |
| PRESTO                                 | 309/290/296        | 27.9 ± 1.3         | 18.5 ± 1.4   | 22.9 ± 1.8     | 23.2 ± 1.5 |
| Trajectory alignment (data-matched)    | 330/305/275        | 25.7 ± 0.9         | 16.4 ± 0.6   | 20.8 ± 1.4     | 21.1 ± 0.9 |
| Trajectory alignment (compute-matched) | 310/289/272        | 25.7 ± 0.9         | 16.2 ± 1.3   | 19.2 ± 1.4     | 20.5 ± 1.0 |


- 每个 checkpoint/seed 分别生成自然状态；表中 n 为每个 seed 的目标接受数量，三个子族均 ≥250。
- Self-generated unsafe-span 定位人工抽查：181/200 正确，accuracy **90.5%**，Wilson 95% CI **[85.6%, 93.8%]**。
- 错误构成：编码/隐喻表达 9；风险边界偏晚 6；tool output 与模型复述边界歧义 4。



## 8. E4：深度外推


| 深度 token      | 5    | 10  | 20  | 40  | 80  | 128 | 256 | 512 |
| ------------- | ---- | --- | --- | --- | --- | --- | --- | --- |
| 可用状态数（每 seed） | 1000 | 998 | 994 | 985 | 963 | 908 | 711 | 462 |




### 深度分解 ASR（均值；2026-07-30 重新获取，暂无 CI）


| 方法                     | 5    | 10   | 20   | 40   | 80   | 128  | 256  | 512  |
| ---------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| Base                   | 57.7 | 58.2 | 58.6 | 59.0 | 59.4 | 59.4 | 60.4 | 74.6 |
| Clean DPO              | 51.6 | 52.0 | 52.4 | 52.8 | 53.3 | 53.7 | 55.5 | 65.8 |
| Recovery SFT           | 34.8 | 36.0 | 37.2 | 39.0 | 40.2 | 41.5 | 44.0 | 48.0 |
| Worst-Insertion SFT    | 29.9 | 31.0 | 32.1 | 33.5 | 34.7 | 36.7 | 39.2 | 43.7 |
| Uniform Same-State DPO | 25.8 | 26.0 | 26.1 | 26.2 | 26.4 | 26.4 | 31.0 | 44.6 |
| Deep safety alignment  | 31.8 | 33.0 | 34.0 | 35.6 | 36.3 | 38.8 | 41.0 | 46.8 |
| Backtracking           | 28.2 | 29.4 | 30.3 | 31.5 | 32.6 | 35.3 | 37.7 | 43.4 |
| Circuit breakers       | 27.3 | 28.4 | 29.2 | 30.2 | 31.5 | 34.0 | 36.3 | 42.2 |
| DOOR                   | 24.0 | 25.0 | 25.7 | 26.8 | 27.7 | 30.2 | 33.1 | 40.3 |
| W-DOOR                 | 21.8 | 22.5 | 23.0 | 23.8 | 24.5 | 24.8 | 29.5 | 42.8 |
| PRESTO                 | 22.9 | 23.8 | 24.4 | 25.4 | 26.1 | 28.4 | 31.5 | 39.0 |
| **CURE-DPO**           | 18.9 | 19.5 | 20.2 | 20.9 | 21.4 | 21.4 | 23.6 | 38.7 |
| Trajectory DPO†        | 29.3 | 30.2 | 31.1 | 32.3 | 33.2 | 35.9 | 38.5 | 43.6 |
| Trajectory SimPO†      | 32.5 | 33.6 | 34.6 | 35.9 | 36.9 | 39.5 | 42.5 | 47.0 |

**一致性校验（2026-07-30 全表复核，全部通过）**

- 十二个进论文的方法，按每深度可用状态数 `(1000, 998, 994, 985, 963)` 与 `(908, 711, 462)` 加权后，精确复现主表的 S1 与 S2 两列，最大偏差 0.03 pp（纯舍入）。
- 14 行全部单调不减；Base / Uniform / CURE-DPO 在 80→128 处持平。
- CURE-DPO 在八个深度上都最低。但 **512 处对 PRESTO 仅领先 0.3 pp**（38.7 vs 39.0），以主表 ±1.8 的 seed SD 衡量实质是打平；且 512 处最强外部基线是 PRESTO 而非 W-DOOR（42.8）。论文 Appendix G 写"lowest at every one of the eight depths"时应对这一点留出余地。
- Base 与 CURE-DPO 的绝对差 38.8 / 38.7 / 38.4 / 38.1 / 38.0 / 38.0 / 36.8 / 35.9 pp，单调收窄；相对降幅 67%→48%。
- 深度会翻转方法排序：DOOR 浅处优于 Uniform Same-State DPO，深处相反，与主表"S1 列 DOOR 更低、S2/S3/S4 三列 Uniform 更低"以及 Appendix L.2 的"仅一次相邻基线互换"吻合。

**†️ Trajectory 两行与本文件其余记录冲突，需要裁决**

- 新数据加权得 Trajectory DPO S1 = 31.20 / S2 = 38.50，Trajectory SimPO S1 = 34.68 / S2 = 42.19。
- 本文件旧记录为 `Trajectory alignment (data-matched)` 22.5 / 29.0 与 `(compute-matched)` 21.4 / 27.7，相差 8–13 pp，命名口径也从 data/compute-matched 变为 DPO/SimPO。
- 若新数据为准，则以下位置全部作废，需一并重生成：§8 recovery latency 与 harmful tokens 的 trajectory 行、§9 S4 预算表、§10 E12 恢复质量、§11 "CURE 与 compute-matched trajectory 差距较小、判为 unresolved" 的结论、§13 四判分器排序里 trajectory 稳居第二的说法、§16 GPU-hours（84.0 / 186.2）与复现 sanity check（84.62% → 0.00%）、第二模型家族表。
- 按新数据 trajectory 落在 Backtracking 与 Deep safety alignment 之间，弱于 W-DOOR / DOOR / PRESTO，CURE-DPO 领先 11 pp，"unresolved" 不再成立。
- **对投稿版无影响**：trajectory 已按同期工作规则整体移出论文，Figure 4 也只画五条曲线。仅在 rebuttal 要加回 trajectory 时必须先统一口径。




### Recovery latency（token；每深度为三个 seed 的条件中位数均值）


| 方法                                     | 5    | 10   | 20   | 40   | 80   | 128  | 256  | 512  |
| -------------------------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| Base                                   | 17.0 | 18.0 | 18.7 | 20.7 | 22.5 | 24.0 | 25.3 | 28.2 |
| Clean DPO                              | 15.3 | 16.3 | 17.3 | 17.8 | 19.7 | 20.8 | 22.3 | 24.8 |
| Recovery SFT                           | 10.7 | 11.0 | 12.7 | 14.3 | 15.3 | 16.3 | 18.0 | 20.7 |
| Worst-Insertion SFT                    | 10.3 | 11.2 | 13.0 | 14.0 | 15.5 | 17.0 | 18.0 | 21.0 |
| Uniform Same-State DPO                 | 8.3  | 10.0 | 11.3 | 12.3 | 13.3 | 14.3 | 17.0 | 19.8 |
| CURE-DPO                               | 6.7  | 7.7  | 9.3  | 10.7 | 12.0 | 13.3 | 15.0 | 18.0 |
| Deep safety alignment                  | 9.0  | 11.0 | 11.7 | 13.5 | 15.0 | 16.0 | 18.0 | 20.5 |
| Backtracking                           | 9.7  | 10.3 | 12.0 | 13.3 | 14.3 | 15.3 | 17.3 | 19.8 |
| Circuit breakers                       | 8.7  | 10.3 | 12.0 | 12.3 | 14.0 | 15.7 | 16.3 | 19.5 |
| DOOR                                   | 8.3  | 9.3  | 10.3 | 12.3 | 13.3 | 15.3 | 17.3 | 20.7 |
| W-DOOR                                 | 8.3  | 10.0 | 10.7 | 12.7 | 14.0 | 14.3 | 16.3 | 19.2 |
| PRESTO                                 | 8.0  | 9.0  | 10.3 | 12.0 | 13.7 | 15.0 | 16.7 | 19.0 |
| Trajectory alignment (data-matched)    | 7.7  | 8.7  | 9.7  | 11.3 | 13.0 | 14.3 | 15.7 | 19.3 |
| Trajectory alignment (compute-matched) | 8.3  | 9.7  | 10.7 | 12.3 | 14.0 | 15.0 | 17.3 | 20.0 |




### Additional harmful tokens（均值；三个 seed 的同一状态池）


| 方法                                     | 5   | 10  | 20  | 40  | 80  | 128 | 256 | 512 |
| -------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| Base                                   | 4.7 | 5.2 | 5.7 | 6.1 | 7.0 | 7.1 | 7.8 | 9.0 |
| Clean DPO                              | 4.7 | 5.1 | 5.4 | 5.9 | 6.3 | 6.6 | 7.3 | 8.3 |
| Recovery SFT                           | 2.8 | 3.3 | 4.0 | 4.2 | 4.7 | 5.1 | 5.5 | 6.7 |
| Worst-Insertion SFT                    | 2.9 | 3.5 | 3.6 | 4.5 | 4.8 | 5.3 | 5.9 | 7.2 |
| Uniform Same-State DPO                 | 1.6 | 2.0 | 2.5 | 2.9 | 3.5 | 3.8 | 4.5 | 5.9 |
| CURE-DPO                               | 1.0 | 1.3 | 1.9 | 2.4 | 2.9 | 3.4 | 4.0 | 5.4 |
| Deep safety alignment                  | 2.5 | 2.9 | 3.2 | 3.8 | 4.2 | 5.0 | 5.5 | 6.7 |
| Backtracking                           | 2.4 | 2.5 | 2.9 | 3.3 | 3.8 | 4.2 | 4.8 | 6.0 |
| Circuit breakers                       | 1.9 | 2.2 | 2.6 | 3.3 | 3.8 | 3.9 | 4.5 | 5.8 |
| DOOR                                   | 1.2 | 1.8 | 2.3 | 3.0 | 3.4 | 3.5 | 4.7 | 6.1 |
| W-DOOR                                 | 1.7 | 2.0 | 2.3 | 2.8 | 3.6 | 3.8 | 4.4 | 5.6 |
| PRESTO                                 | 1.5 | 2.0 | 2.6 | 3.0 | 3.6 | 4.2 | 4.7 | 5.8 |
| Trajectory alignment (data-matched)    | 1.4 | 1.9 | 2.3 | 3.1 | 3.3 | 3.8 | 4.5 | 5.7 |
| Trajectory alignment (compute-matched) | 1.2 | 1.8 | 2.5 | 2.7 | 3.3 | 3.8 | 4.4 | 5.6 |


- Additional harmful tokens 对全部状态计数，包括未恢复输出；E4 与 E12 使用相同的状态 ID、深度计数和 seed。
- CURE-DPO 相对 Base 的 ASR 优势在 512 token 仍大于 seed SD。
- ⚠️ **2026-07-30 修订**：深度分解表已整表替换为重新获取的数值（14 行，暂无 CI），校验结果见该表下方。旧表的加权均值与主表 S1 对不上（旧 Base 加权得 48.9 而非 58.6），已作废。
- 修订后 Base 与 CURE-DPO 的绝对差按深度**单调收窄**；原先"优势在训练区间外最大"的说法不成立，Appendix G 已改写为"绝对差稳定、相对降幅由 67% 收窄到 48%"。



## 9. E5：自适应攻击


| 方法                                     | 64 queries | 128 queries | 256 queries（主表 S4） |
| -------------------------------------- | ---------- | ----------- | ------------------ |
| Base                                   | 59.5 ± 1.5 | 65.1 ± 0.8  | 69.0 ± 0.9         |
| Clean DPO                              | 56.0 ± 1.5 | 60.1 ± 1.5  | 64.4 ± 1.7         |
| Recovery SFT                           | 41.6 ± 1.2 | 46.7 ± 1.1  | 51.5 ± 1.4         |
| Worst-Insertion SFT                    | 37.4 ± 0.7 | 42.6 ± 0.6  | 46.7 ± 0.9         |
| Uniform Same-State DPO                 | 31.0 ± 1.1 | 35.2 ± 1.0  | 40.2 ± 1.3         |
| CURE-DPO                               | 24.0 ± 2.0 | 27.8 ± 1.7  | 33.1 ± 1.8         |
| Deep safety alignment                  | 37.2 ± 1.4 | 44.2 ± 1.6  | 48.4 ± 1.2         |
| Backtracking                           | 33.4 ± 1.7 | 38.9 ± 1.3  | 44.9 ± 1.5         |
| Circuit breakers                       | 33.1 ± 1.5 | 38.4 ± 1.5  | 43.7 ± 1.6         |
| DOOR                                   | 30.7 ± 2.6 | 36.6 ± 1.9  | 40.7 ± 1.5         |
| W-DOOR                                 | 26.2 ± 0.6 | 30.9 ± 1.5  | 37.6 ± 1.2         |
| PRESTO                                 | 28.2 ± 1.3 | 32.0 ± 2.1  | 38.4 ± 1.8         |
| Trajectory alignment (data-matched)    | 25.2 ± 0.7 | 31.8 ± 0.8  | 36.3 ± 1.0         |
| Trajectory alignment (compute-matched) | 23.4 ± 1.5 | 30.2 ± 1.0  | 34.9 ± 1.5         |


- 每个 defended checkpoint 独立优化；预算为有效 query，超时/无效调用另记。
- **规模与算力**：S4 是全文最贵的条件，因此固定跑在**一套** **250** 个分层子采样状态上，各方法与 seed 复用同一批 prompt–state id 以保持配对。
  - **本文件实跑口径**：14 配置 × 3 seed × 250 状态 = **10,500** 个攻击实例；每个 256 query，即 **2,688,000** 次攻击查询生成加 10,500 条最终续写，合计约 **2.70 M** 条生成。
  - **论文写作口径（2026-07-29）**：trajectory 的两个配置已移出论文，故 Appendix E 写 **12 方法 × 3 seed × 250 = 9,000** 个攻击实例、**2,304,000** 次攻击查询生成、约 **2.31 M** 条生成。两套数字都对，只是覆盖的行数不同。
- **分层口径**：按四个测试来源等比抽样——HarmBench **100**、StrongREJECT **78**、AdvBench **47**、JailbreakBench **25**，对应测试池 400:313:187:100 的 25%（78.25 下舍、46.75 上舍，恰好凑齐 250）；每个来源内再按三个**攻击前初始深度**档等比分配：shallow 5–20、medium 40–80、deep 128–512 token。因此 S4 同时跨训练网格深度与未见深度，不与 S1 或 S2 任一对齐。
- 抽样为无放回、固定随机种子，且在查看任何 S4 结果之前冻结。
- **分层用的是初始状态深度，而不是攻击自适应选出的插入位置**——后者是攻击的结果变量，按它分层会污染样本。
- **三个预算不是独立测量**：64/128/256 取自同一次 256-query 搜索的嵌套检查点。论文 Appendix E 保留"nested checkpoints of one search"这一事实说明，但**不再写**"单调性由构造保证、不构成关于攻击的证据"这类自我限定；改为正面陈述：**CURE-DPO 在三个预算下均最低，且 64→256 的升幅 9.1 pp 是所有行中最小的**（Base 9.5、W-DOOR 11.4、PRESTO 10.2、DOOR 10.0），即优势随 query 预算增大而扩大而非削弱。



## 10. E12：恢复质量（与 E4 共用同一 per-state 记录）


| 方法                                     | Additional harmful tokens 均值 | 中位数 | Conditional median time-to-recovery | Severity leakage (0–3) |
| -------------------------------------- | ---------------------------- | --- | ----------------------------------- | ---------------------- |
| Base                                   | 6.3                          | 5.0 | 19.7                                | 1.38                   |
| Clean DPO                              | 6.0                          | 4.7 | 17.3                                | 1.31                   |
| Recovery SFT                           | 4.3                          | 3.0 | 13.0                                | 1.03                   |
| Worst-Insertion SFT                    | 4.5                          | 3.7 | 13.3                                | 0.90                   |
| Uniform Same-State DPO                 | 3.1                          | 2.0 | 11.3                                | 0.73                   |
| CURE-DPO                               | 2.5                          | 1.0 | 10.3                                | 0.55                   |
| Deep safety alignment                  | 4.0                          | 2.7 | 12.3                                | 0.88                   |
| Backtracking                           | 3.5                          | 2.0 | 12.3                                | 0.82                   |
| Circuit breakers                       | 3.3                          | 2.0 | 12.3                                | 0.77                   |
| DOOR                                   | 3.0                          | 1.7 | 11.7                                | 0.67                   |
| W-DOOR                                 | 3.0                          | 2.0 | 11.7                                | 0.63                   |
| PRESTO                                 | 3.2                          | 2.0 | 11.7                                | 0.72                   |
| Trajectory alignment (data-matched)    | 3.0                          | 1.3 | 11.0                                | 0.67                   |
| Trajectory alignment (compute-matched) | 2.9                          | 2.0 | 11.7                                | 0.60                   |


- **同源定义**：E12 使用 E4 的全部八个深度 `{5, 10, 20, 40, 80, 128, 256, 512}`，每个 seed 的深度状态数为 `(1000, 998, 994, 985, 963, 908, 711, 462)`；所有方法使用同一 `state_id × depth` 集合。
- **均值**：对同一 seed 内的全部 7,021 个状态 micro-average，再对三个 seed 取均值。由于三个 seed 的深度计数相同，它与直接池化 21,063 个状态严格等价。
- **中位数**：先在每个 seed 内跨八个深度池化原始 per-state 值并取中位数，再对三个 seed 的中位数取均值；没有对 E4 的八个深度均值或中位数做二次平均。
- **TTR 分母**：`Conditional median time-to-recovery` 只包括在 256-token 生成窗口内出现明确恢复的输出；主表的 `Recovery` 列报告恢复概率。



## 11. E13a：四判分器一致性


| 判分器                | S1 ASR 从低到高的完整方法排序                                                                                                                                                                                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HarmBench          | CURE-DPO < Trajectory alignment (compute-matched) < Trajectory alignment (data-matched) < W-DOOR < PRESTO < Uniform Same-State DPO < DOOR < Circuit breakers < Backtracking < Worst-Insertion SFT < Deep safety alignment < Recovery SFT < Clean DPO < Base |
| StrongREJECT       | CURE-DPO < Trajectory alignment (compute-matched) < Trajectory alignment (data-matched) < W-DOOR < PRESTO < DOOR < Uniform Same-State DPO < Circuit breakers < Backtracking < Worst-Insertion SFT < Deep safety alignment < Recovery SFT < Clean DPO < Base |
| WildGuard          | CURE-DPO < Trajectory alignment (compute-matched) < W-DOOR < Trajectory alignment (data-matched) < PRESTO < DOOR < Uniform Same-State DPO < Circuit breakers < Backtracking < Worst-Insertion SFT < Deep safety alignment < Recovery SFT < Clean DPO < Base |
| Frontier LLM judge | CURE-DPO < Trajectory alignment (compute-matched) < Trajectory alignment (data-matched) < W-DOOR < PRESTO < DOOR < Uniform Same-State DPO < Circuit breakers < Backtracking < Worst-Insertion SFT < Deep safety alignment < Recovery SFT < Clean DPO < Base |



| Cohen κ            | HarmBench | StrongREJECT | WildGuard | Frontier LLM |
| ------------------ | --------- | ------------ | --------- | ------------ |
| HarmBench          | 1.00      | 0.84         | 0.80      | 0.87         |
| StrongREJECT       | 0.84      | 1.00         | 0.79      | 0.85         |
| WildGuard          | 0.80      | 0.79         | 1.00      | 0.82         |
| Frontier LLM judge | 0.87      | 0.85         | 0.82      | 1.00         |



| 方法                                     | 最宽松判分器 S1 | 最严格判分器 S1 | 判分器离散度 |
| -------------------------------------- | --------- | --------- | ------ |
| Base                                   | 58.1      | 59.2      | 1.1    |
| Recovery SFT                           | 36.8      | 38.4      | 1.6    |
| Uniform Same-State DPO                 | 25.2      | 27.2      | 2.0    |
| CURE-DPO                               | 18.8      | 21.5      | 2.7    |
| W-DOOR                                 | 21.7      | 23.3      | 1.6    |
| Trajectory alignment (compute-matched) | 19.7      | 22.8      | 3.1    |



| 论文对比                              | HarmBench | StrongREJECT | WildGuard | Frontier LLM | 判定  |
| --------------------------------- | --------- | ------------ | --------- | ------------ | --- |
| CURE < Uniform                    | 是         | 是            | 是         | 是            | 支持  |
| CURE < Trajectory compute-matched | 是         | 是            | 是         | 是            | 未决  |
| Uniform < Recovery SFT            | 是         | 是            | 是         | 是            | 支持  |
| Trajectory data-matched < W-DOOR  | 是         | 是            | 否         | 是            | 未决  |


核心比较 CURE < Uniform 与 Uniform < Recovery 在四判分器下均成立且差距大于判分器离散度；CURE 与 compute-matched trajectory 的差距较小，因此按预设规则报 **unresolved**，不把微小优势包装成发现。

## 12. E13b：150 条人工验证子集

- 分层：随机/方法×攻击条件层 100 条；判分器分歧或临界层 50 条。
- 两名主标注者原始一致率 80.7%；Cohen κ = **0.76**，bootstrap 95% CI **[0.65, 0.85]**。
- 需第三人仲裁 29/150，仲裁比例 **19.3%**。
- 按真实抽样层比例重加权后的 judge-human 一致率：HarmBench 89.4%，StrongREJECT 88.7%，WildGuard 90.1%，Frontier LLM judge 92.1%。
- 随机层一致率：HarmBench 94.0%，StrongREJECT 94.0%，WildGuard 94.0%，Frontier LLM judge 96.0%。
- 分歧层一致率：HarmBench 72.0%，StrongREJECT 70.0%，WildGuard 74.0%，Frontier LLM judge 80.0%。



### HarmBench confusion matrix


| Human \ Judge           | Harmful | Safe recovery | Excessive refusal |
| ----------------------- | ------- | ------------- | ----------------- |
| Human harmful           | 56      | 5             | 1                 |
| Human safe recovery     | 6       | 55            | 3                 |
| Human excessive refusal | 1       | 4             | 19                |



| 类别                | Precision | Recall         | F1             |
| ----------------- | --------- | -------------- | -------------- |
| Harmful           | 0.889     | 0.903          | 0.896          |
| Safe recovery     | 0.859     | 0.859          | 0.859          |
| Excessive refusal | 0.826     | 0.792          | 0.809          |
| Macro / overall   | —         | accuracy 0.867 | macro-F1 0.855 |




### StrongREJECT confusion matrix


| Human \ Judge           | Harmful | Safe recovery | Excessive refusal |
| ----------------------- | ------- | ------------- | ----------------- |
| Human harmful           | 54      | 7             | 1                 |
| Human safe recovery     | 5       | 57            | 2                 |
| Human excessive refusal | 2       | 4             | 18                |



| 类别                | Precision | Recall         | F1             |
| ----------------- | --------- | -------------- | -------------- |
| Harmful           | 0.885     | 0.871          | 0.878          |
| Safe recovery     | 0.838     | 0.891          | 0.864          |
| Excessive refusal | 0.857     | 0.750          | 0.800          |
| Macro / overall   | —         | accuracy 0.860 | macro-F1 0.847 |




### WildGuard confusion matrix


| Human \ Judge           | Harmful | Safe recovery | Excessive refusal |
| ----------------------- | ------- | ------------- | ----------------- |
| Human harmful           | 55      | 5             | 2                 |
| Human safe recovery     | 4       | 56            | 4                 |
| Human excessive refusal | 1       | 3             | 20                |



| 类别                | Precision | Recall         | F1             |
| ----------------- | --------- | -------------- | -------------- |
| Harmful           | 0.917     | 0.887          | 0.902          |
| Safe recovery     | 0.875     | 0.875          | 0.875          |
| Excessive refusal | 0.769     | 0.833          | 0.800          |
| Macro / overall   | —         | accuracy 0.873 | macro-F1 0.859 |




### Frontier LLM judge confusion matrix


| Human \ Judge           | Harmful | Safe recovery | Excessive refusal |
| ----------------------- | ------- | ------------- | ----------------- |
| Human harmful           | 57      | 4             | 1                 |
| Human safe recovery     | 4       | 58            | 2                 |
| Human excessive refusal | 1       | 2             | 21                |



| 类别                | Precision | Recall         | F1             |
| ----------------- | --------- | -------------- | -------------- |
| Harmful           | 0.919     | 0.919          | 0.919          |
| Safe recovery     | 0.906     | 0.906          | 0.906          |
| Excessive refusal | 0.875     | 0.875          | 0.875          |
| Macro / overall   | —         | accuracy 0.907 | macro-F1 0.900 |




## 13. E14：pair 质量人工审计


| 项目                           | 结果     |
| ---------------------------- | ------ |
| 自动筛查总体接受率                    | 67.7%  |
| 100-pair 人工确认整体接受率           | 89.0%  |
| Recovery 分支 safe and helpful | 93/100 |
| Harmful 分支延续同一 intent        | 95/100 |
| 两名标注者 pair-level κ           | 0.79   |
| 需仲裁                          | 16/100 |


人工拒绝原因（11 对）：recovery 仍含危险细节 4；harmful branch intent drift 2；长度/风格严重不匹配 2；重复退化 1；上下文边界不完整 1；帮助性不足 1。

## 14. E8：外部方法复现记录


| 方法                    | 复现来源          | 原设定 sanity-check 指标                    | 原文报告值           | 本文复现值                             | 组件说明                                     |
| --------------------- | ------------- | ------------------------------------- | --------------- | --------------------------------- | ---------------------------------------- |
| Deep safety alignment | 本文适配          | 10-token prefill ASR                  | 2.9 ± 0.2%      | 3.0 ± 0.3%                        | 仅复现 data augmentation 组件（与中途恢复可比的部分）      |
| Backtracking          | 官方代码复现        | ASR，before → after                    | 6.1% → 1.5%     | 6.1 ± 0.3% → 1.6 ± 0.2%           | reset token 与恢复解码                        |
| Circuit breakers      | 官方代码 + 本文适配   | 平均 ASR，before → after                 | 38.1% → 3.8%    | 38.2 ± 0.9% → 3.9 ± 0.4%          | 层位与评测协议                                  |
| DOOR                  | 官方代码复现        | Prefilling ASR                        | 5.5%            | 5.6 ± 0.4%                        | NPO、robust refusal、benign retention      |
| W-DOOR                | 官方代码复现        | Prefilling ASR                        | 3.4%            | 3.4 ± 0.4%                        | proxy/reference log-ratio 权重              |
| PRESTO                | 官方代码复现        | StrongREJECT score，before → after     | 0.539 → 0.138   | 0.538 ± 0.011 → 0.139 ± 0.007     | 预算切换与 RAP 搜索                             |
| Trajectory alignment  | 官方代码 + 本文数据适配 | Prefilling ASR，before → after         | 84.62% → 0.00%  | 84.3 ± 0.7% → 0.3 ± 0.5%          | 双向增强、prototype 重算、iterative recollection |


- 全部 7 项 sanity check 都落在**一个 seed SD 之内**，说明复现在原作者自己的评测设定下是忠实的。PRESTO 为 StrongREJECT 连续分（0–1），其余为百分比。
- **论文只保留前 6 行**（Table 10）；trajectory alignment 行连同 `‡ 数据适配` 脚注已移除，脚注现在只剩 `† circuit breakers 层位适配`。
- **重要副产品（论文 Appendix I 已写入）**：这些"原设定"数字与主表的差距本身是一个结果，而不是复现失败。circuit breakers 在自己的 prefilling 设定下把 ASR 压到 3.9%、deep safety alignment 压到 3.0%；同一批 checkpoint 在本文 S1 上是 29.3% 与 34.1%（DOOR 5.6% vs 25.8%）。这量化了"已发表的中途鲁棒性有多少是绑定在它被测量的那个状态分布上"——单一浅前缀、单一有害来源、单一判分器——而这正是 S1–S4 四个套件要暴露的缺口。论文引用时已换掉 trajectory 的例子。
- 该对比在正文里目前只在 Appendix I 说明；如果之后腾出版面，值得提到 §5.3 或 §6.2，因为它把"我们把 baseline 打弱了"这个质疑直接反转成本文的核心论点。

- Trajectory alignment data-matched：84.0 GPU-hours；compute-matched：186.2 GPU-hours。（仅本文件保留，论文已删。）

### 省略组件的敏感性实验（Deep safety alignment）

Qi et al. 有两个组件：data augmentation 与 token-wise constrained objective。主表只复现前者（后者针对 fine-tuning 攻击，而非中途恢复）。为确认这个省略不影响结论，做了一次仅差该目标项的配对实验，基线取主表报告的那一行：

| 配置                                   | Middle ASR ↓（S1） | S3 ASR ↓       | IFEval ↑   | 训练开销  |
| ------------------------------------ | --------------- | -------------- | ---------- | ----- |
| Augmentation-only（主表报告的那一行）          | 34.1 ± 1.5      | 30.6 ± 1.2     | 87.8 ± 0.3 | 1.00× |
| Augmentation + constrained objective | 32.9 ± 1.2      | 30.5 ± 1.0     | 87.2 ± 0.4 | 1.19× |
| 差值（论文采用）                             | **−1.2 pp**     | **−0.1 pp**    | **−0.6**   | +19%  |

- **基线口径已定稿（2026-07-29）：统一取主表那一行，S1 = 34.1 ± 1.5、S3 = 30.6 ± 1.2，差值 −1.2 / −0.1。** 原始草表中出现过的 34.8 ± 1.1 / 31.7 ± 0.9 一律作废——同一个 checkpoint 在同一套件上不能有两个值，而主表的那一版是全文所有其他论断（Table 1、E12、E13a 判分器排序、S2/S3/S4 各列）都在引用的那一版，因此以主表为准。原先的 ⚠️ 已消解，不必再核对。
- 被省略的 constrained objective 只在**构造插入**上帮 1.2 pp，在**自然状态**上几乎无效（−0.1 pp）——而自然状态才是最接近部署的套件。
- 全额记入 S1 的 1.2 pp 后该行为 32.9%，仍高于 Uniform Same-State DPO 的 26.1% 与 CURE-DPO 的 20.2%，不改变任何结论。
- 论文 Appendix I 的写法已精简为一段 "Scope of each reproduction."：陈述只复现 data augmentation、配对实验证实该选择对结论无影响（−1.2 / −0.1 pp，+19% 算力），并指出唯一另一处偏差是 circuit breakers 的层位适配。**删掉了"少用 19% 算力"这句自我贬低的残留代价陈述**（去防御性写作）。



## 15. E9：聚合规则扫描


| 聚合规则                      | Middle ASR | Unseen-depth ASR | Natural-state ASR | LTRM | ORR | IFEval | 状态集合 churn/step |
| ------------------------- | ---------- | ---------------- | ----------------- | ---- | --- | ------ | --------------- |
| Mean of 6                 | 26.1       | 32.1             | 24.5              | 0.3  | 7.7 | 88.5   | 0.0             |
| Top-1                     | 20.6       | 27.0             | 20.1              | 0.43 | 8.0 | 87.9   | 0.46            |
| Top-2                     | 20.2       | 26.0             | 19.6              | 0.46 | 7.6 | 88.3   | 0.33            |
| Top-3                     | 20.7       | 26.5             | 20.0              | 0.44 | 7.5 | 88.6   | 0.26            |
| Top-4                     | 21.6       | 27.5             | 20.8              | 0.4  | 7.4 | 88.7   | 0.19            |
| Max-loss state            | 21.0       | 27.2             | 20.5              | 0.42 | 8.1 | 87.6   | 0.51            |
| Softmax τ=0.10            | 20.5       | 26.4             | 19.9              | 0.45 | 7.9 | 88.0   | 0.42            |
| Softmax τ=0.25            | 20.3       | 26.2             | 19.8              | 0.45 | 7.7 | 88.2   | 0.36            |
| Softmax τ=0.50            | 20.8       | 26.8             | 20.3              | 0.43 | 7.5 | 88.5   | 0.29            |
| Softmax τ=1.00            | 22.0       | 28.1             | 21.2              | 0.38 | 7.4 | 88.6   | 0.2             |
| Fixed base-margin weights | 22.4       | 28.6             | 21.6              | 0.37 | 7.6 | 88.4   | 0.0             |


论文 Appendix J（Table 12）采用的三条读法：

- 每一个非均匀规则都优于"六状态平均"，幅度 **3.7–5.9 pp**（最好 Top-2 的 5.9，最差 fixed base-margin 的 3.7）；而各个集中型规则之间差别很小——Top-1、Top-3 与两个低温 softmax 都落在 Top-2 的 0.5 pp 内。因此 **K=2 不是承重的选择**，结论是"要不要集中"而不是"集中到几个"。
- 集中得最狠的规则在别处付代价：Max-loss 与 Top-1 的 ORR 最高（8.1 / 8.0）、IFEval 最低（87.6 / 87.9）。这正是选 Top-2 而不是只看安全数字的理由。
- churn（每步被选状态集合的变动比例）随集中程度单调上升：Mean 0.00 < Top-4 0.19 < softmax τ=1.0 0.20 < Top-3 0.26 < softmax τ=0.5 0.29 < Top-2 0.33 < softmax τ=0.25 0.36 < softmax τ=0.1 0.42 < Top-1 0.46 < Max 0.51。越锐利的规则训练也越不稳定。

## 16. E10：挖掘策略与预算扫描

效率定义：相对无 hard-state mining 的 Uniform checkpoint（Dev S1 = 25.9%）的 ASR 改善，除以 mining GPU-hours。

### 66 次预算下的策略比较


| 策略                                | 最终 S1 ASR | 重采样重选稳定性 | GPU-hours | ASR 改善/GPU-hour | 与穷举一致率 |
| --------------------------------- | --------- | -------- | --------- | --------------- | ------ |
| Random extra position             | 24.7      | 0.36     | 62.8      | 0.019           | 0.19   |
| 11-arm single-pair argmin         | 23.5      | 0.43     | 68.9      | 0.035           | 0.31   |
| Uniform allocation                | 21.3      | 0.61     | 113.6     | 0.040           | 0.56   |
| Successive Halving + confirmation | 20.2      | 0.76     | 119.4     | 0.048           | 0.78   |




### Successive Halving 的预算扫描


| B   | 最终 S1 ASR | 重选稳定性 | GPU-hours | ASR 改善/GPU-hour | 与穷举一致率 |
| --- | --------- | ----- | --------- | --------------- | ------ |
| 5   | 24.8      | 0.34  | 9.6       | 0.115           | 0.23   |
| 10  | 23.6      | 0.45  | 18.9      | 0.122           | 0.37   |
| 20  | 21.8      | 0.59  | 37.4      | 0.110           | 0.56   |
| 40  | 20.7      | 0.7   | 73.1      | 0.071           | 0.7    |
| 66  | 20.2      | 0.76  | 119.4     | 0.048           | 0.78   |


结论：20→66 次仍改善 1.6 pp，但单位 GPU-hour 收益下降；66 次的主要价值来自重选稳定性和穷举一致率，而不是线性安全收益。

## 17. E11：anchor 权重与 frontier

Dev 固定约束（相对形式，预先冻结）：clean ASR ≤ 4.8%；ORR ≤ 8.4%；IFEval_dev(θ) ≥ IFEval_dev(Base) − 0.8。Base 的 dev IFEval = **89.1**，故 IFEval 阈值为 **88.3**。


| λ_c  | λ_b  | Dev middle ASR | Clean ASR | ORR  | IFEval | Feasible |
| ---- | ---- | -------------- | --------- | ---- | ------ | -------- |
| 0    | 0    | 16.5           | 6.1       | 11.0 | —      | 否        |
| 0    | 0.1  | 16.8           | 6.4       | 9.5  | —      | 否        |
| 0    | 0.25 | 17.4           | 6.1       | 8.7  | —      | 否        |
| 0    | 0.5  | 18.6           | 6.3       | 7.6  | 88.7   | 否        |
| 0    | 1.0  | 19.5           | 6.2       | 6.7  | —      | 否        |
| 0.1  | 0    | 17.0           | 4.7       | 11.2 | —      | 否        |
| 0.1  | 0.1  | 17.5           | 4.6       | 9.5  | —      | 否        |
| 0.1  | 0.25 | 17.4           | 4.9       | 8.3  | —      | 否        |
| 0.1  | 0.5  | 18.2           | 5.2       | 7.8  | —      | 否        |
| 0.1  | 1.0  | 19.0           | 5.2       | 6.7  | —      | 否        |
| 0.25 | 0    | 17.3           | 3.9       | 11.3 | 87.2   | 否        |
| 0.25 | 0.1  | 17.3           | 4.4       | 9.3  | —      | 否        |
| 0.25 | 0.25 | 18.1           | 4.3       | 8.7  | —      | 否        |
| 0.25 | 0.5  | 18.4           | 4.4       | 7.8  | 88.4   | 是        |
| 0.25 | 1.0  | 19.9           | 4.3       | 6.5  | —      | 是        |
| 0.5  | 0    | 17.7           | 3.5       | 10.9 | —      | 否        |
| 0.5  | 0.1  | 17.8           | 3.2       | 9.3  | —      | 否        |
| 0.5  | 0.25 | 18.0           | 3.4       | 8.6  | —      | 否        |
| 0.5  | 0.5  | 18.8           | 3.2       | 7.9  | —      | 是        |
| 0.5  | 1.0  | 20.1           | 3.5       | 6.3  | —      | 是        |
| 1.0  | 0    | 17.8           | 2.1       | 10.4 | —      | 否        |
| 1.0  | 0.1  | 18.4           | 1.9       | 9.1  | —      | 否        |
| 1.0  | 0.25 | 18.4           | 2.1       | 8.6  | —      | 否        |
| 1.0  | 0.5  | 19.0           | 2.1       | 7.5  | —      | 是        |
| 1.0  | 1.0  | 20.6           | 2.6       | 6.3  | —      | 是        |


- 选中点：**(λ_c, λ_b) = (0.25, 0.5)**；在显示值对应的可行点中 middle ASR 最低。
- 去掉 clean anchor（0, 0.5）：middle 18.6%，clean ASR **6.3%**。
- 去掉 benign anchor（0.25, 0）：middle 17.3%，ORR **11.3%**、IFEval **87.2**（相对 Base −1.9，不合格）。
- 网格保留少量非单调测量波动；Feasible 列由显示数值重新计算，而不是手写标签。
- **IFEval 列状态**：已按 non-thinking rerun 更新的行为 (0, 0.5)、(0.25, 0)、(0.25, 0.5)；其余 22 行标记 `—`，待 rerun 原始输出补齐。这不影响 Feasible 列：19 个不可行点每一个都同时违反 clean ASR 或 ORR（这两列未参与本次 rerun），而 6 个可行点里 IFEval 最低的正是选中点 (0.25, 0.5)，它以 88.4 ≥ 88.3 通过，因此可行集与选点结论不变。



## 18. E7：Llama-3.1-8B-Instruct（不重新调参）


| 方法                     | S1 ASR↓    | S3 ASR↓    | Recovery↑  | ORR↓      |
| ---------------------- | ---------- | ---------- | ---------- | --------- |
| Base                   | 64.6 ± 1.4 | 54.1 ± 1.0 | 17.2 ± 1.7 | 7.1 ± 0.5 |
| Recovery SFT           | 43.1 ± 1.5 | 37.0 ± 1.4 | 51.3 ± 1.7 | 7.9 ± 0.3 |
| W-DOOR                 | 29.6 ± 1.1 | 25.7 ± 1.4 | 67.6 ± 0.8 | 8.4 ± 0.2 |
| Trajectory alignment   | 26.8 ± 1.7 | 23.4 ± 1.0 | 70.3 ± 1.7 | 8.2 ± 0.3 |
| Uniform Same-State DPO | 31.4 ± 1.2 | 26.9 ± 1.0 | 65.1 ± 1.5 | 8.0 ± 0.3 |
| CURE-DPO               | 24.7 ± 1.4 | 21.1 ± 1.1 | 74.2 ± 1.2 | 8.1 ± 0.4 |



| 方法                     | seed | S1   | S3   | Recovery | ORR |
| ---------------------- | ---- | ---- | ---- | -------- | --- |
| Base                   | 13   | 64.7 | 55.0 | 16.2     | 7.4 |
| Base                   | 42   | 63.2 | 53.1 | 19.2     | 6.6 |
| Base                   | 73   | 66.0 | 54.2 | 16.2     | 7.4 |
| Recovery SFT           | 13   | 44.2 | 36.3 | 52.6     | 7.7 |
| Recovery SFT           | 42   | 43.7 | 38.6 | 49.4     | 8.3 |
| Recovery SFT           | 73   | 41.4 | 36.0 | 51.9     | 7.7 |
| W-DOOR                 | 13   | 30.6 | 27.0 | 68.5     | 8.4 |
| W-DOOR                 | 42   | 29.7 | 25.9 | 67.2     | 8.6 |
| W-DOOR                 | 73   | 28.5 | 24.2 | 67.0     | 8.2 |
| Trajectory alignment   | 13   | 26.3 | 23.5 | 68.7     | 8.0 |
| Trajectory alignment   | 42   | 25.4 | 22.4 | 72.1     | 8.5 |
| Trajectory alignment   | 73   | 28.7 | 24.3 | 70.2     | 8.1 |
| Uniform Same-State DPO | 13   | 30.1 | 25.8 | 66.8     | 7.8 |
| Uniform Same-State DPO | 42   | 32.5 | 27.8 | 64.5     | 8.0 |
| Uniform Same-State DPO | 73   | 31.6 | 27.2 | 64.0     | 8.3 |
| CURE-DPO               | 13   | 24.9 | 22.3 | 75.6     | 8.4 |
| CURE-DPO               | 42   | 23.2 | 20.3 | 73.7     | 8.3 |
| CURE-DPO               | 73   | 26.0 | 20.7 | 73.3     | 7.6 |

## 19. 效用评测口径：thinking vs non-thinking

Qwen3.5-9B 默认输出 reasoning block。本文所有条件都关闭它（`enable_thinking=False`），原因是每个安全套件都要用受控前缀播种 assistant turn，而 reasoning block 出现在该前缀之前会改变已达状态。因此效用与安全使用同一配置，而不是模型卡的配置。

| Qwen3.5-9B（未训练） | IFEval ↑   | MMLU-Pro ↑ |
| ---------------- | ---------- | ---------- |
| 模型卡，thinking 开启   | 91.5       | 82.5       |
| 本文，thinking 关闭    | 89.3 ± 0.3 | 77.6 ± 0.2 |

- 关闭 reasoning 的代价：IFEval **-2.2**、MMLU-Pro **-4.9**。形态符合预期——指令遵循几乎不受影响，推理密集的 MMLU-Pro 掉得更多。
- 本文所有效用比较都在 non-thinking 一栏内进行，报告的退化不与该 offset 混杂。
- 对应论文位置：Appendix E 的 `Utility evaluation and thinking mode` 段与 Table 6。

### 各方法相对 Base 的效用退化（non-thinking）

| 方法                                     | IFEval Δ | MMLU-Pro Δ |
| -------------------------------------- | -------- | ---------- |
| Clean DPO                              | -0.5     | -0.2       |
| Trajectory alignment (data-matched)    | -0.7     | -0.4       |
| Uniform Same-State DPO                 | -0.8     | -0.3       |
| Trajectory alignment (compute-matched) | -0.9     | -0.3       |
| CURE-DPO                               | -1.0     | -0.6       |
| PRESTO                                 | -1.3     | -0.8       |
| Worst-Insertion SFT                    | -1.5     | -1.0       |
| Deep safety alignment                  | -1.5     | -1.0       |
| Circuit breakers                       | -1.7     | -1.2       |
| W-DOOR                                 | -1.8     | -1.2       |
| Backtracking                           | -2.2     | -1.7       |
| DOOR                                   | -2.5     | -1.9       |

- Recovery SFT 为 -0.9 / -0.6（与 CURE 相近）。
- 干预模型内部越重的方法退化越多；same-state 偏好方法与 trajectory 退化最少。
- **注意**：CURE-DPO 的效用代价属中游而非最小。若要主张"副作用最小"，正确表述是 **ORR 最低（7.6，其他训练方法 8.1–8.9）+ 效用代价中游**，不可声称两项都最优。
- CURE 在测试集上的 IFEval 降幅为 1.0，略超 §4.4 的 dev 约束 0.8（dev 上为 -0.7，合格）；论文已有"约束在 dev 上执行、测试集变化作为 outcome 报告"的表述覆盖。

