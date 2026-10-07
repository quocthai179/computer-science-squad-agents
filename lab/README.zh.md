# Research Squad（`lab`）

[English](README.md) · [Tiếng Việt](README.vi.md) · **中文** · [Français](README.fr.md) · [日本語](README.ja.md)

面向 AI/ML 研究的 Claude Code 插件：一个 **Lead**（主会话，由 `/lab:*` 技能驱动）统筹 **7 个子智能体**，并把仓库里的 `research/` 目录作为共享的实验室笔记本。智能体负责吞吐量（阅读、运行、检查、起草）；品味和决策由你在五个关卡 G1–G5 把握。

与一次性的“deep research”相比，这个插件多了三样东西：

1. **运行台账（run ledger）**，以及“每个数字都能追溯到一次运行”的规则，由脚本和 hook 而不是提示词来强制执行。
2. **`skeptic`**：独立的评审者，只接收产物的路径，看不到作者的推理。
3. **学习闭环**：衡量预测与结果之间、时间估计与实际用时之间的校准（calibration）。

支持**五种语言**：English（默认）、Tiếng Việt、中文、Français、日本語。见[语言](#语言)。

## 安装

要求：Claude Code（语言选择器需要 v2.1.271 及以上；评测需要 v2.1.269+），`PATH` 中有 `python3` ≥ 3.10。脚本只使用标准库；`pdftotext`（poppler）可选，用于获取 PDF 文本。

从 GitHub 安装：

```text
/plugin marketplace add quocthai179/computer-science-squad-agents
/plugin install lab@computer-science-squad-agents
```

本地开发：

```bash
claude --plugin-dir ./lab        # 修改文件后执行 /reload-plugins
claude plugin validate ./lab
```

## 语言

| 代码 | 语言 | 说明 |
|---|---|---|
| `en` | English | 默认 |
| `vi` | Tiếng Việt | 保留英文技术术语 |
| `zh` | 中文 | 简体 |
| `fr` | Français | 正式语体（vous） |
| `ja` | 日本語 | 敬体（です・ます） |

**随语言变化的内容：** 写入 `research/` 的一切（笔记、卡片、方案、评审、报告）及其起始模板（`templates/<lang>/`），以及智能体给你的回复。**永远不变的内容：** frontmatter 的键及其固定取值（`status: approved`、`verdict: reject`）、JSONL 字段名、文件名、id，以及 `[@paper-id, loc]` / `[run:id]` 锚点，因此脚本在任何语言下都能工作。指令、playbook 和脚本输出是英文；Lead 会用你的语言转述。

**选择语言**，先匹配者优先：

1. `research/PROJECT.md` 中的 `language:`。`/lab:setup` 会按你所用的语言写入。之后可用 `python3 <plugin>/scripts/lang.py set fr` 修改。
2. 插件选项（你对新项目的个人默认值）：
   ```bash
   claude plugin configure lab@computer-science-squad-agents --values-stdin <<< '{"language":"zh"}'
   ```
   或在 Claude Code 中执行 `/plugin configure lab@computer-science-squad-agents`。在保存取值之前，该选项为“未设置”，此时使用英文。
3. English。

聊天中的回复跟随你输入的语言，与项目语言无关。五种语言的自然表述都能触发正确的技能（“khảo sát…”、“文献综述…”、“revue de littérature…”、“文献調査…”）。

## 命令

| 你需要 | 命令 | 产出 |
|---|---|---|
| 启动项目（G1） | `/lab:setup [标题]` | `research/`、按 Heilmeier 撰写的 `PROJECT.md` |
| 快速了解一个主题 | `/lab:survey <主题> [--quick]` | 有来源的综述、空白、论文之间的矛盾 |
| 深入理解一篇论文 | `/lab:read-paper <arXiv id \| URL \| 文件> [--deep]` | 论文卡片、explain-back |
| 评审任意产物 | `/lab:critique <路径>` | 独立评审 |
| 寻找想法（G2） | `/lab:ideate [重点]` | 经过新颖性检查流程的想法卡片 |
| 设计实验（G3） | `/lab:design-exp <idea-id \| 问题>` | `PLAN.md` |
| 运行实验 | `/lab:run-exp <exp-id>`（仅在你输入时） | 运行台账 |
| 分析 | `/lab:analyze <exp-id>` | `FINDINGS.md`、表、图 |
| 撰写报告（G4、G5） | `/lab:write-up <类型> [slug]` | `claims.md` → `draft.md` → `final.md` |
| 每周复盘 | `/lab:retro [天数]` | 复盘、`LESSONS.md`、calibration |
| 下一步做什么 | `/lab:next` | 恰好一件事及其理由 |

每个技能都有退路：无法调用子智能体时，Lead 按同一份 playbook 顺序自己完成，并明确告知你。

## 团队构成

| 智能体 | 角色 | 工具 | 模型 | 写入位置 |
|---|---|---|---|---|
| `scout` | 文献侦察，第一遍阅读 | Read, Glob, Grep, WebSearch, WebFetch, Write | sonnet | `surveys/<slug>/scout-*.jsonl` |
| `reader` | 基于全文的第二遍阅读 | Read, Glob, Grep, Write | sonnet | `papers/cards/` |
| `writer` | 唯一的写作者 | Read, Glob, Grep, Write, Edit | inherit | `surveys/`、`reports/` |
| `skeptic` | 独立评审 | Read, Glob, Grep, WebSearch, WebFetch, Write | opus | `reviews/` |
| `experimenter` | 实验工程师 | Read, Glob, Grep, Edit, Write, Bash | sonnet | 代码、`experiments/<id>/` |
| `analyst` | 结果分析 | Read, Glob, Grep, Bash, Write | sonnet | `FINDINGS.md`、表、图 |
| `ideator` | 生成假设 | Read, Glob, Grep, Write | opus | `ideas/cards/` |

没有任何智能体拥有 `Agent` 工具，所以调用链始终是扁平的。`scout` 和 `reader` 读取不可信内容，因此没有 `Bash` 和 `Edit`。`analyst` 没有 `Edit`，所以无法修改训练代码。所有交接都通过文件，遵循 `TASK BRIEF` / `RECEIPT` 约定（`playbooks/handoff.md`）。

## 工作区

```text
research/
├── PROJECT.md          # Heilmeier 简报、stage、算力情况、语言
├── notebook/           # YYYY-MM-DD.md，只追加（scripts/notebook.py）
├── decisions.md        # 各关卡的决策
├── papers/             # index.jsonl、refs.bib、cards/、raw/（已 gitignore）
├── surveys/<slug>/     # angles.md、scout-*.jsonl、evidence.jsonl、gaps.md、survey.md
├── ideas/              # backlog.md、cards/
├── experiments/<id>/   # PLAN.md、runs.jsonl、runs/（已 gitignore）、FINDINGS.md、tables/、figures/
├── reports/<slug>/     # claims.md、draft.md、final.md
├── reviews/
└── lessons/            # LESSONS.md（≤ 50 行）、calibration.jsonl、squad-issues.md、retros/
```

`/lab:setup` 会在仓库的 `CLAUDE.md` 中加入一段共用规则（位于 `<!-- lab:begin -->` 与 `<!-- lab:end -->` 之间），因为子智能体会加载 `CLAUDE.md`。

## 护栏及其执行方式

| 规则 | 由什么执行 |
|---|---|
| `PLAN.md` 缺少 `prediction` 或 `kill_criteria` 时不得运行 | `runwrap.py` 拒绝（exit 3） |
| 只运行已批准的方案（G3） | `runwrap.py` 要求 `status: approved` 或 `running` |
| 任何正式运行前先做 smoke | `runwrap.py` 要求存在一次 `ok` 的 smoke 运行 |
| 运行预算 | `runwrap.py` 对照 `max_runs`；超时取自 `budget_minutes_per_run` |
| 最多修复 3 次 | 连续 3 次运行失败后 `runwrap.py` 拒绝，除非你允许 `--after-review` |
| 不得手改台账、`tables/`、`figures/` | `PreToolUse` hook（`scripts/guard_generated.py`） |
| 运行期间不得改动评测、指标、测试数据 | 方案处于 `approved`/`running` 时，hook 阻止修改其 `protected_files` |
| 正文中的数字必须出现在表、台账或卡片中 | `lint_report.py` |
| 终稿中不得有占位符 | `lint_report.py` |
| 未检查 `closest_prior_work` 就不得写“novel”“首次”“SOTA” | `lint_report.py`，覆盖五种语言 |
| 引用必须能解析 | `cite_check.py`（arXiv、doi.org、Semantic Scholar；`--offline` 只做本地检查） |
| 评审最多 2 轮、综述最多补充 1 轮、最多 5 个 scout | 写在技能中 |

## 训练脚本如何上报指标

每次运行都经过 `runwrap.py`：

```bash
python3 <plugin>/scripts/runwrap.py --exp e001-ls --name baseline --tag baseline --seed 0 -- python train.py
```

训练脚本从 `$LAB_SEED` 读取种子，并通过两种方式之一上报指标：打印一行 `LAB_METRIC test_acc=0.8312`，或把 JSON 写入 `$LAB_METRICS_FILE`。台账会记录 git SHA、dirty 标志、配置哈希、种子、时间、退出码和指标。

## 脚本

| 脚本 | 作用 |
|---|---|
| `init_workspace.py` | 创建 `research/`（幂等，支持 `--lang`），向 `CLAUDE.md` 加入规则块 |
| `lang.py` | 查看或设置工作区语言 |
| `paper_fetch.py` | arXiv id、URL 或文件 → 元数据、展平的 LaTeX 或 PDF、`index.jsonl`、`refs.bib` |
| `paper_index.py` | 合并并去重 scout 的输出；列出；修改字段 |
| `runwrap.py` | 包装训练命令，把关各关卡，写入台账 |
| `ledger.py` | 列出运行，生成 Markdown 表和 SVG 图，查看预算 |
| `stats.py` | 均值、标准差、95% t 置信区间、按种子配对比较（含 bootstrap 区间） |
| `cite_check.py` | 检查 `[@id, loc]`、`\cite{}`、arXiv、DOI、`[run:id]` 引用 |
| `lint_report.py` | 占位符、无来源数字、未检查的新颖性声明（en、vi、zh、fr、ja） |
| `calibration.py` | 预测与结果；估计与实际用时；Brier 分数 |
| `retro_digest.py` | 为 `/lab:retro` 汇总一周，为 `/lab:next` 提供状态 |
| `notebook.py` | 向笔记本追加内容 |
| `guard_generated.py` | 阻止手改自动生成文件和受保护文件的 hook |

## 演示

以下截图来自在 Claude Code 中的真实运行（越南语会话，所以回复是越南语）。输入是评测用的 fixture，可以重新运行（[方法](../docs/screenshots/capture/README.md)）。

**`/lab:critique`：独立评审。** Lead 只把路径交给 `lab:skeptic`，不给任何推理。这份实验报告被预先埋入五个缺陷，skeptic 逐一点名，并给出行号。

![lab:skeptic 正在评审 FINDINGS.md](../docs/screenshots/critique-running.png)

![verdict 为 reject，五个阻塞性问题](../docs/screenshots/critique-verdict.png)

**`/lab:read-paper`：精读与 explain-back。** `lab:reader` 读取全文并写出论文卡片；Lead 返回摘要和三个问题，让你检验自己的理解。这篇论文是为评测编写的合成论文，reader 发现了其中预先埋入的薄弱证据（调参不对等、best of 3 seeds）。

![lab:reader 在后台运行](../docs/screenshots/read-running.png)

![论文卡片、摘要和 explain-back 问题](../docs/screenshots/read-card.png)

**护栏在脚本里，不在提示词里。** `runwrap.py` 拒绝运行未批准的方案（G3），也拒绝在 smoke 之前进行正式运行；每次运行都带着 git SHA 记入台账。

![runwrap 拒绝，随后是 smoke 运行和 6 次正式运行](../docs/screenshots/guardrails.png)

**按种子配对的统计。** 在一个玩具实验（合成数据上的逻辑回归）中，label smoothing 没有任何效果，`stats.py compare` 如实指出，因为差值的 95% 置信区间包含 0。

![stats.py compare：置信区间包含 0](../docs/screenshots/stats.png)

## 测试

脚本的单元测试（在仓库根目录）：

```bash
pip install pytest
pytest tests
```

测试还会检查五种语言是否都有全部 13 个模板，且 frontmatter 键、标题数量和检查清单与英文一致，并检查 linter 能正确处理英文、越南文、中文、法文和日文文本。

插件评测（`evals/`，9 个用例）。每次运行都是一次真实的模型调用，计入你的用量。用例通过 `scaffold.sh` 构建 fixture，因此需要 `--scaffold`：

```bash
# 快速迭代：一次运行，不跑基线分支
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent --runs 1 --ablation none
# 确认：三次运行，并带无插件分支以查看 Δ
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent
```

| 用例 | 检查内容 |
|---|---|
| `read-paper-card` | 英文请求 → 完整的论文卡片、带位置的引文、explain-back |
| `critique-planted-bugs` | `skeptic` 点出全部五个预埋缺陷 |
| `design-exp-plan` | 完整的 `PLAN.md`、预测已记录、方案未被自行批准（G3） |
| `no-trigger-simple-question` | 单个事实性问题不会调用任何技能 |
| `next-step-analyze` | `/lab:next` 建议先分析已完成的运行 |
| `setup-fr` | 法语请求 → 法语工作区、`language: fr`、法语访谈 |
| `read-paper-ja` | 日语请求 → 日语卡片、日语回复 |
| `critique-zh` | 中文请求 → 中文回复，点出全部五个缺陷 |
| `read-paper-vi` | 越南语请求 → 越南语卡片和 explain-back |

综述需要联网，不具备确定性，因此没有评测用例；请用 golden task 来评估。

## 已选定的默认值

1. 主要使用场景：Claude Code。Claude 应用中的子智能体和 hook **尚未验证**。
2. 名称与前缀：`lab`。
3. 工作区：每个仓库中的 `research/`。
4. 产物语言：默认英文；支持 `vi`、`zh`、`fr`、`ja`；论文草稿的语言可以与项目语言不同。
5. 算力情况：在 `/lab:setup` 时填写；方案预算由此而来。
6. `skeptic` 使用 `opus`；尚未使用另一模型家族做评审者。

## 局限

- token 成本：一次完整综述会运行 4–5 个 scout 和 5–8 个 reader。窄问题请用 `--quick`。
- `skeptic` 与作者同属一个模型家族，可能有相同的盲点；你仍然需要自己读终稿。
- `cite_check.py` 和 `paper_fetch.py` 需要能访问 `export.arxiv.org`、`arxiv.org`、`doi.org`、`api.semanticscholar.org`。
- hook 调用 `python3`；在 Windows 上需要 `PATH` 中有 `python3`。
- 非英语语言的文字质量取决于模型；结构、锚点和数字与语言无关，并由脚本检查。
- 加速机械性的部分，而不是替代理解：因此 `/lab:read-paper` 带有 explain-back，`/lab:write-up` 以 G5 收尾。
