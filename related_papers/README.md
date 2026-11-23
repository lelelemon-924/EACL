# CURE-DPO 相关论文合集

路径：`/Users/zhaoyuesen/Desktop/EACL/related_papers`

来源：
1. `paper.tex` / `custom.bib` 已引用文献
2. `写作指导.md` 第 12 节规划的约 40 篇参考文献
3. 正文外部基线（Backtracking、Circuit Breakers）及近邻安全/越狱工作

## 统计
- PDF：45 篇
- 附加：Qwen3.5-9B model card（`33b_qwen35_9b_model_card.md`）

## 分类索引

### A. 偏好优化 / Alignment
`01` InstructGPT · `02` Constitutional AI · `03` DPO · `04` SimPO · `05` TDPO · `06` TIS-DPO · `07` MMPO · `08` Safe-RLHF · `09` BeaverTails · `10` CVaR (Rockafellar & Uryasev)

### B. Safety depth / Recovery（最近邻）
`11` Shallow Safety (Qi) · `12` DOOR · `13` PRESTO/RAP · `14` Any-Depth · `15` Safety Depth · `16` DeepRefusal · `17` Autoregressive Consistency / worst-insertion · `18` Inference-Time Vulnerability · `41` Backtracking · `42` Circuit Breakers

### C. Jailbreak / Red-teaming / 评测
`19` Jailbreaks as Inference-Time Alignment · `19b` LIAR arXiv · `20` Safety Knowledge Neurons · `21` GCG · `22` Gradient Red Teaming · `23` Ganguli Red Teaming · `24` Jailbroken · `25` PAIR · `26` JailbreakBench · `27` HarmBench · `28` StrongREJECT · `29` XSTest · `30` OR-Bench · `43` Adaptive Attacks · `44` AutoDAN

### D. 模型 / 适配 / 评测效用 / 统计挖掘
`31` IFEval · `32` MMLU-Pro · `33` Qwen3 Tech Report · `33b` Qwen3.5-9B card · `34` Llama 3 · `35` LoRA · `36` Bootstrap 章节笔记（Wasserman，替代 Efron 1993 原书） · `37` Holm 1979 · `38b` Cohen kappa 课程笔记（原刊 PDF 付费墙未拿到） · `39` Successive Halving · `40` LUCB / PAC subset selection

## 未拿到原版的条目
| 目标 | 状态 | 替代 / DOI |
|---|---|---|
| Efron & Tibshirani (1993) *An Introduction to the Bootstrap* | 原书无开放 PDF | 已用 `36_wasserman_bootstrap_chapter.pdf`；DOI 相关：Efron 1979 AoS `10.1214/aos/1176344552` |
| Cohen (1960) kappa 原刊 | Sage 付费墙 | 已用 `38b_cohen_kappa_course_notes.pdf`；DOI `10.1177/001316446002000104` |
| Qwen3.5 独立 tech report | 暂无 arXiv | 已用 Qwen3 report + HF model card |

## 文件列表
- `01_ouyang2022_instructgpt.pdf` (1755 KB)
- `02_bai2022_constitutional_ai.pdf` (2039 KB)
- `03_rafailov2023_dpo.pdf` (1269 KB)
- `04_meng2024_simpo.pdf` (1285 KB)
- `05_zeng2024_tdpo.pdf` (884 KB)
- `06_liu2025_tis_dpo.pdf` (987 KB)
- `07_najafi2026_mmpo.pdf` (1483 KB)
- `08_dai2023_safe_rlhf.pdf` (1057 KB)
- `09_ji2023_beavertails.pdf` (1830 KB)
- `10_rockafellar2000_cvar.pdf` (195 KB)
- `11_qi2025_shallow_safety.pdf` (868 KB)
- `12_zhao2025_door.pdf` (1150 KB)
- `13_vega2025_presto.pdf` (1009 KB)
- `14_zhang2025_any_depth.pdf` (7997 KB)
- `15_kao2025_safety_depth.pdf` (3312 KB)
- `16_xie2025_deeprefusal.pdf` (1099 KB)
- `17_lyu2026_autoregressive_consistency.pdf` (1718 KB)
- `18_park2026_inference_time_vulnerability.pdf` (3143 KB)
- `19_beetham2026_jailbreaks_inference_alignment.pdf` (676 KB)
- `19b_beetham2024_liar_arxiv.pdf` (680 KB)
- `20_zhao2026_safety_knowledge_neurons.pdf` (2214 KB)
- `21_zou2023_gcg.pdf` (4547 KB)
- `22_wichers2024_gradient_red_teaming.pdf` (397 KB)
- `23_ganguli2022_red_teaming.pdf` (3015 KB)
- `24_wei2023_jailbroken.pdf` (443 KB)
- `25_chao2023_pair.pdf` (5228 KB)
- `26_chao2024_jailbreakbench.pdf` (626 KB)
- `27_mazeika2024_harmbench.pdf` (3158 KB)
- `28_souly2024_strongreject.pdf` (586 KB)
- `29_rottger2024_xstest.pdf` (424 KB)
- `30_cui2025_orbench.pdf` (1050 KB)
- `31_zhou2023_ifeval.pdf` (453 KB)
- `32_wang2024_mmlu_pro.pdf` (937 KB)
- `33_qwen2025_qwen3_tech_report.pdf` (761 KB)
- `34_dubey2024_llama3.pdf` (9603 KB)
- `35_hu2022_lora.pdf` (1572 KB)
- `36_wasserman_bootstrap_chapter.pdf` (557 KB)
- `37_holm1979_multiple_test.pdf` (1035 KB)
- `38b_cohen_kappa_course_notes.pdf` (31 KB)
- `39_jamieson2016_successive_halving.pdf` (746 KB)
- `40_kalyanakrishnan2012_lucb.pdf` (227 KB)
- `41_zhang2025_backtracking.pdf` (582 KB)
- `42_zou2024_circuit_breakers.pdf` (899 KB)
- `43_andriushchenko2024_adaptive_attacks.pdf` (1825 KB)
- `44_liu2023_autodan.pdf` (597 KB)

按主题浏览：`by_topic/`（硬链接，不占额外空间）。
未拿到原版：见 `MISSING.md`。

详见 `download_log.json`。
