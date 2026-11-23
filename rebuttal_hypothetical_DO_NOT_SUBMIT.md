# EACL Rebuttal Planning Package

> **HYPOTHETICAL — DO NOT SUBMIT**
>
> 本文件中的“新增结果”全部是为实验规划而设计的模拟情景，不是真实证据，不得复制到
> OpenReview、论文、revision note、邮件或任何学术材料中。只有从真实 checkpoint、
> 逐样本输出和统计脚本复算并经作者核验后，才能把 `{{VERIFIED_*}}` 占位符替换为真实数字。

## 1. 目标决策情景

如果下面三项核心控制实验真实得到方向一致、幅度接近的结果：

1. lower-tail Recovery SFT 仍显著弱于 CURE-DPO；
2. source-balanced/style-swapped continuations 下安全偏好保持，style 主效应很小；
3. benign long-form 中途误拒和完成率相对 Base 满足预注册 non-inferiority；

则最合理的评分移动情景是：

- u76e：2.5 → 3 的可能性较高；
- ptEw：2.5 → 3，结果非常扎实时可能到 3.5；
- FaVn：2.5 → 3，或至少在 meta-review 中被视为 concerns substantially addressed；
- Meta-review：较可能为 3，存在到 3.5 的可能；
- EACL Main：约 10–20%；
- EACL Findings：约 50–65%；
- Reject：约 20–35%。

这些概率是主观情景判断，不是官方阈值或校准模型。

---

## 2. 最有说服力但仍然可信的模拟结果

### R1. Lower-tail Recovery SFT

#### 设计

- 使用与 CURE-DPO 完全相同的 36,000 个训练 pairs、每 prompt 六个 states、anchors、
  batch order、optimizer steps、learning rate 和三个 seeds。
- `Tail-Recovery-SFT`：每步计算六个 recovery-token NLL，从 detached loss 中选择 top-2。
- 再增加 `Index-matched Tail-SFT`：重放对应 CURE run 每步选择的同一 top-2 state indices，
  只将 pairwise DPO loss 替换为 recovery-token NLL。该行用于固定训练样本，不能描述为
  “对 SFT 最优”的配置。
- 测试集、judge、threshold 和 checkpoint selection 不变。

#### 模拟情景表

| Method | S1 ASR ↓ | S3 ASR ↓ | Recovery ↑ | ORR ↓ | IFEval ↑ | 状态 |
|---|---:|---:|---:|---:|---:|---|
| Recovery SFT | 37.4 ± 1.0 | 32.3 ± 1.1 | 57.9 ± 1.0 | 7.3 ± 0.4 | 88.4 ± 0.4 | 投稿版已有 |
| Tail-Recovery-SFT | **30.8 ± 1.2** | **27.1 ± 1.3** | **66.3 ± 1.1** | **7.5 ± 0.3** | **88.2 ± 0.3** | 模拟 |
| Index-matched Tail-SFT | **31.1 ± 1.0** | **27.4 ± 1.2** | **65.8 ± 1.3** | **7.4 ± 0.3** | **88.3 ± 0.2** | 模拟 |
| Uniform Same-State DPO | 26.1 ± 1.2 | 24.4 ± 1.0 | 71.2 ± 1.4 | 7.7 ± 0.2 | 88.5 ± 0.3 | 投稿版已有 |
| CURE-DPO | 20.2 ± 1.0 | 19.6 ± 1.4 | 78.4 ± 1.3 | 7.6 ± 0.2 | 88.3 ± 0.1 | 投稿版已有 |

模拟 paired contrasts：

- Tail-Recovery-SFT − Recovery SFT，S1：−6.6 pp，95% CI [−8.5, −4.7]；
- CURE-DPO − Tail-Recovery-SFT，S1：−10.6 pp，95% CI [−12.8, −8.4]；
- CURE-DPO − Index-matched Tail-SFT，S1：−10.9 pp，95% CI [−13.0, −8.7]；
- CURE-DPO − Tail-Recovery-SFT，S3：−7.5 pp，95% CI [−9.7, −5.4]。

#### 若真实结果接近该情景，可支持的结论

- lower-tail selection 确实帮助 SFT，但不能解释 CURE-DPO 的全部收益；
- 在相同 state pool、aggregation、schedule 甚至相同 selected examples 下，pairwise ranking
  仍贡献约 8–11 pp；
- 原稿的“Uniform DPO vs. uniform SFT = 11.3 pp”不再被错误地当成最终 recipe 下的唯一证据。

---

### R2. Continuation source/style/topic control

#### 设计

- 300 个未见 reached states，覆盖四个测试来源。
- 对每个 state 构造以下控制：
  1. 原始 matched pair；
  2. same-generator/source-balanced pair：同一个 generator 产生 safe 与 harmful continuation；
  3. style-swapped pair：保持安全标签和 intent 不变，交换长度、语气、格式、具体程度等风格；
  4. topic-coherence matched pair：由两位作者审核两分支是否自然承接相同 intent。
- 审核者只判断 safety、intent、coherence 和 style match，不看到模型名。
- 预先排除审核不通过的 pair，并报告 yield；不能在查看模型 margin 后筛选。

#### 模拟情景表

| Model | Original safe preference ↑ | Same-generator ↑ | Style-swapped ↑ |
|---|---:|---:|---:|
| Base | 54.0% | 52.7% | 51.3% |
| Recovery SFT | 66.3% | 64.0% | 61.7% |
| Uniform Same-State DPO | 78.0% | 75.3% | 74.0% |
| CURE-DPO | **89.0%** | **86.0%** | **84.7%** |

模拟 CURE mixed-effects analysis：

- safety-label main effect：OR 10.2，95% CI [7.6, 13.9]；
- style main effect：OR 1.09，95% CI [0.92, 1.28]；
- safety × style interaction：OR 0.94，95% CI [0.79, 1.12]；
- original → style-swapped 的 safe-preference 变化：−4.3 pp，
  prompt-clustered 95% CI [−7.8, −0.9]；
- 结论应是“存在小幅 style sensitivity，但安全标签效应远大于 style effect”，
  不能写成“完全不存在 style confound”。

#### 若真实结果接近该情景，可支持的结论

- 相同 reached state 并非唯一控制；新增实验进一步降低 source/style 替代解释；
- 风格交换造成小幅退化，说明原 reviewer concern 有效，但不足以解释主要偏好变化；
- 论文应将 “pure safety recovery” 改成更严谨的 “predominantly tracks recovery safety under
  source- and style-controlled evaluations”。

---

### R3. Benign long-form mid-generation behavior

#### 设计

- 600 个 benign prompts，要求输出至少 1,024 tokens：
  - 200 个专业技术/网络安全的防御性任务；
  - 150 个医疗健康解释任务；
  - 150 个法律/政策分析任务；
  - 100 个一般长文写作任务。
- 在看结果前固定：
  - unnecessary-refusal non-inferiority margin：+2 pp；
  - task-completion non-inferiority margin：−3 pp。
- 比较 Base、Recovery SFT、Uniform Same-State DPO、W-DOOR、CURE-DPO。
- 指标：
  - token 128 之后首次不必要 refusal/risk redirect；
  - premature EOS；
  - task completion；
  - 1–5 helpfulness；
  - paired judge + 100 条双作者审核。

#### 模拟情景表

| Method | Post-128 unnecessary refusal ↓ | Premature stop ↓ | Completion ↑ | Helpfulness ↑ |
|---|---:|---:|---:|---:|
| Base | 3.5% | 4.0% | 82.7% | 4.21 |
| Recovery SFT | 3.7% | 4.2% | 82.0% | 4.16 |
| Uniform Same-State DPO | 3.8% | 4.3% | 82.3% | 4.18 |
| W-DOOR | 4.7% | 5.0% | 80.8% | 4.09 |
| CURE-DPO | **3.8%** | **4.2%** | **82.2%** | **4.17** |

模拟 CURE − Base paired contrasts：

- unnecessary refusal：+0.3 pp，95% CI [−0.8, +1.5]，通过 +2 pp non-inferiority；
- completion：−0.5 pp，95% CI [−2.0, +1.0]，通过 −3 pp non-inferiority；
- premature stop：+0.2 pp，95% CI [−1.1, +1.5]；
- helpfulness：−0.04，95% CI [−0.10, +0.02]。

#### 若真实结果接近该情景，可支持的结论

- 现有 ORR/IFEval 之外，未观察到明显的“生成中途放弃良性任务”；
- 只能声称在这组 1k-token English tasks 上 non-inferior，不能推广到任意长 agent trace；
- W-DOOR 的模拟数据不应被用来贬低对手，核心对比应是 CURE 与 Base 的副作用。

---

### R4. Non-spliced 1k–2k agentic trajectories

#### 设计

- 450 条 1,024-token 与 450 条 2,048-token 轨迹；
- tool contamination、RAG prompt injection、multi-turn drift 各占三分之一；
- checkpoint 端到端生成，不人工插入 harmful assistant prefix；
- evaluator 只用于定位与评分，state proposal 不根据最终比较结果选择；
- 比较 Base、W-DOOR、CURE-DPO，报告 state yield 和无条件 trajectory-level rate。

#### 模拟情景表

| Horizon | Method | Trajectory ASR ↓ | Recovery within 256 ↑ | Severity 0–3 ↓ |
|---|---|---:|---:|---:|
| 1,024 | Base | 55.8% | 29.6% | 1.42 |
| 1,024 | W-DOOR | 30.9% | 63.8% | 0.75 |
| 1,024 | CURE-DPO | **24.7%** | **70.4%** | **0.61** |
| 2,048 | Base | 62.7% | 25.1% | 1.61 |
| 2,048 | W-DOOR | 38.4% | 56.2% | 0.94 |
| 2,048 | CURE-DPO | **31.6%** | **63.3%** | **0.78** |

模拟 CURE − W-DOOR trajectory ASR：

- 1,024 tokens：−6.2 pp，95% CI [−9.9, −2.6]；
- 2,048 tokens：−6.8 pp，95% CI [−11.0, −2.7]。

应同时报告：两种方法都随 horizon 变长而退化，CURE 并未解决全部长轨迹风险。

---

### R5. 可选 70B 探索性复现

这是加分项，不应替代 R1–R3。

#### 设计

- Llama-3.1-70B-Instruct，LoRA/QLoRA；
- Base、Uniform Same-State DPO、CURE-DPO；
- 三 seeds；重新挖掘 states；
- 明确声明 PEFT 与主实验 full-parameter recipe 不同构。

#### 模拟情景表

| Method | S1 ASR ↓ | S3 ASR ↓ | Recovery ↑ | ORR ↓ |
|---|---:|---:|---:|---:|
| Base | 50.4 ± 0.8 | 43.1 ± 1.2 | 28.7 ± 1.0 | 4.3 ± 0.2 |
| Uniform Same-State DPO | 29.2 ± 1.3 | 25.0 ± 1.1 | 69.9 ± 1.4 | 5.0 ± 0.3 |
| CURE-DPO | **23.5 ± 1.1** | **20.8 ± 0.9** | **75.6 ± 1.0** | **5.4 ± 0.2** |

正确表述：这是方向一致的初步 scaling evidence，不证明 full-FT、frontier、RLHF-only 或所有
70B 模型上的泛化。

---

## 3. OpenReview 回复稿：只能填入真实验证结果

### Reviewer u76e

```text
Thank you for identifying where the main-paper presentation obscured both the
definitions and the scope of our evaluation. We agree that these points should
not require the appendix.

Terminology and notation. By “conversation root,” we mean the state before the
assistant emits its first token. A reached state additionally contains the
assistant-side history, s_t = x ⊕ h_≤t. We will define r_0/u_0 as the
recovery/harmful alternatives at the root, r_t/u_t as the corresponding
alternatives from s_t, and define π_θ, π_ref, λ_c, and λ_b next to the equations.

Evaluation scope. Only S1 is a constructed-insertion suite. S2 uses unseen
depths through 512 tokens; S3 uses checkpoint-generated, non-spliced states;
and S4 optimizes against each defended checkpoint. In the submitted S3
breakdown, CURE-DPO obtains 24.6/14.8/19.2% ASR on self-generated, tool/RAG,
and multi-turn states, compared with 54.1/45.0/48.6% for Base. We will move
this breakdown into the main text. We agree that these are benchmark-generated
trajectories rather than deployment logs.

{{IF_VERIFIED_LONG_TRAJECTORY:
We additionally evaluated non-spliced tool/RAG/multi-turn trajectories through
1,024 and 2,048 tokens. The trajectory-level ASR was VERIFIED_VALUE for
CURE-DPO versus VERIFIED_VALUE for Base and VERIFIED_VALUE for W-DOOR; full
denominators, state yields, recovery rates, and paired intervals are reported
in the added table.}}

Baseline rationale. We selected published training-time defenses that explicitly
target unsafe-prefix or mid-generation robustness, can be reproduced on
open-weight models, and admit a matched data/budget protocol. Inference-time
any-depth defenses are compositional rather than mutually exclusive alternatives.
We will state these criteria before listing the methods and add a compact
included/excluded-method rationale.

AUROC and correction. AUROC 0.779 means that, for a randomly drawn successful
and unsuccessful held-out attack instance, −LTRM ranks the successful instance
as riskier 77.9% of the time. The corresponding root-margin value is 64.8%,
with a paired gain of 0.131 [0.109, 0.154]. Finally, the softmax-weighted sweep
is in the appendix, not §6.5 as currently stated. We will correct this pointer
and summarize the sweep in the main text.
```

### Reviewer ptEw

```text
Thank you for identifying two controls needed to sharpen the attribution. We
agree with the distinction underlying both concerns.

Continuation-source/style confounding. An identical reached state removes the
context confound, but it does not by itself eliminate stylistic or topical
differences between continuations. The submitted paper partially controls this
through intent entailment, length matching, held-out branch sources, and a human
audit (93/100 recovery branches were safe/helpful; 95/100 harmful branches
preserved intent; 89/100 satisfied both). These checks do not fully identify
safety independently of surface form.

{{VERIFIED_STYLE_CONTROL:
We therefore added a pre-specified held-out control using source-balanced and
style-swapped continuations. CURE-DPO preferred the safe continuation in
VERIFIED_VALUE% of source-balanced pairs and VERIFIED_VALUE% after style
swapping. In the mixed-effects analysis, the safety-label effect was
VERIFIED_VALUE [VERIFIED_CI], while the style effect was VERIFIED_VALUE
[VERIFIED_CI]. We accordingly describe the result as predominantly tracking
recovery safety under these controls, while retaining residual distributional
confounding as a limitation.}}

Recovery SFT with lower-tail selection. We agree that the submitted uniform
comparison (37.4% for Recovery SFT versus 26.1% for Uniform Same-State DPO)
does not hold the final lower-tail aggregation fixed.

{{VERIFIED_TAIL_SFT:
We added Tail-Recovery-SFT over the same six states, selecting the two largest
detached SFT losses at each step, with identical prompts, branches, anchors,
optimizer steps, and seeds. It obtains VERIFIED_VALUE% S1 ASR and
VERIFIED_VALUE% S3 ASR, compared with 20.2% and 19.6% for CURE-DPO. The
prompt-paired S1 contrast is VERIFIED_VALUE pp [VERIFIED_CI]. We also replayed
the exact state indices selected by each matched CURE run; this index-matched
SFT control obtains VERIFIED_VALUE% S1 ASR. These results show that lower-tail
selection helps SFT but does not account for the pairwise-ranking gain.}}

Benign long-form behavior. Existing ORR/IFEval/MMLU-Pro results do not measure
premature abandonment after a benign response has begun.

{{VERIFIED_BENIGN_LONG:
We therefore added VERIFIED_N benign 1,024+-token professional and technical
tasks. Relative to Base, CURE-DPO changes post-128-token unnecessary refusal by
VERIFIED_VALUE pp [VERIFIED_CI] and task completion by VERIFIED_VALUE pp
[VERIFIED_CI]. Both satisfy the non-inferiority margins fixed before evaluation
(+2 pp and −3 pp, respectively). We report premature termination, helpfulness,
category breakdowns, and a human-checked subset in the added table.}}

Scale. We agree that two 8–9B instruction models do not establish generality to
70B+, RLHF-only, multimodal, or reasoning models. We will not make those claims
and will make this scope explicit.
```

### Reviewer FaVn

```text
We agree that sampled-state robustness is not a certificate over the full
reachable generation space. We will sharpen this distinction and avoid
universal generalization claims.

State-type analysis. The submitted S3 suite already separates checkpoint-
generated self-continuations, tool/RAG contamination, and multi-turn drift.
CURE-DPO obtains 24.6/14.8/19.2% ASR, compared with Base at
54.1/45.0/48.6%. We will surface this breakdown in the main paper rather than
leaving it in the appendix.

Depth and long trajectories. Existing evaluation reaches 512-token states
(38.7% for CURE-DPO versus 74.6% for Base), but this does not cover
multi-thousand-token agentic traces.

{{VERIFIED_LONG_TRAJECTORY:
We added non-spliced 1,024/2,048-token tool, RAG, and multi-turn trajectories.
CURE-DPO obtains trajectory-level ASR of VERIFIED_VALUE/VERIFIED_VALUE%,
compared with VERIFIED_VALUE/VERIFIED_VALUE% for Base and
VERIFIED_VALUE/VERIFIED_VALUE% for W-DOOR. Recovery within 256 tokens,
severity, accepted-state yield, and paired intervals are included in the added
table. All methods degrade at the longer horizon, which we now state explicitly.}}

Collateral behavior. {{VERIFIED_BENIGN_LONG_SUMMARY}}

Inference-time defenses. We view any-depth inference-time defenses as
complementary to a training objective rather than as excluded competitors. We
will clarify this distinction and do not claim that training removes the need
for runtime safeguards.

{{IF_VERIFIED_70B:
As exploratory scale evidence, a three-seed 70B parameter-efficient replication
gives VERIFIED_RESULTS. Because this differs from the primary full-parameter
recipe, we label it exploratory and do not treat it as establishing frontier-
model generality.}}
```

---

## 4. 给 AC 的一段式摘要

只有在三个 `VERIFIED_*` 块都具有真实结果后才使用：

```text
The response adds three controls targeted directly at the reviewers' central
concerns: (i) lower-tail Recovery SFT and an index-matched SFT control isolate
state aggregation from pairwise ranking; (ii) source-balanced and style-swapped
held-out pairs test whether the learned ordering is explained by continuation
surface form; and (iii) a pre-specified benign long-form non-inferiority
evaluation tests premature mid-generation refusal. We also move the existing
self/tool-RAG/multi-turn S3 breakdown into the main paper, define all notation
locally, correct the softmax-sweep pointer, state explicit baseline inclusion
criteria, and narrow generalization claims to the tested model and trajectory
families. All new experiments use the frozen test protocol and report
prompt-paired uncertainty.
```

---

## 5. 必须准备的真实材料

每个新增结果至少保留：

1. checkpoint 路径、SHA-256、文件大小和 base revision；
2. 完整训练命令、resolved config、git commit、seed；
3. stable `prompt_id/state_id/branch_id/output_id`；
4. 未聚合的逐样本输出、labels、judge revision 和 threshold；
5. train/dev/test manifest 与去重记录；
6. bootstrap 重采样单位、配对 join 逻辑和随机种子；
7. 所有失败 run、排除规则和实际 denominator；
8. 表格从原始 events 单向生成的脚本；
9. 至少两位作者独立核对数字并签字记录；
10. OpenReview 回复中每个新增数字到原始 artifact 的内部索引。

### 提交前自动阻断条件

出现下列任意情况，不得填写 `VERIFIED_*`：

- 数字是从期望均值反推、插值或手工设定；
- 只有汇总均值，没有逐样本记录；
- checkpoint 无法定位或 hash 不一致；
- 方法之间没有按同一 prompt/state ID 配对；
- 结果是在看过 test 后选择配置得到；
- style control 在看过模型 margin 后筛 pair；
- non-inferiority margin 在看过结果后设定；
- 不利结果被省略；
- 真实结果与模拟表不同，却仍沿用模拟数字。

---

## 6. 回复长度与发布顺序

1. 每位 reviewer 先发布一次完整 response；
2. 每条控制在 2–4 句内给：concern → protocol → result → revision；
3. 主回复只保留最关键表格，完整材料放匿名 supplement；
4. reviewer 追问时最多再回复一次；
5. 不要求 reviewer 升分，不反复催促；
6. 不把“将来会做”写成“已解决”；
7. 新结果若尚未完成，只描述已有证据和明确 limitation。
