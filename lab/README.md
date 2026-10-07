# Research Squad (`lab`)

Plugin Claude Code cho nghiên cứu AI/ML: một **Lead** (main session chạy theo skill `/lab:*`) điều phối **7 subagent**, dùng thư mục `research/` trong repo làm sổ lab chung. Agent lo thông lượng (đọc, chạy, kiểm, viết nháp); bạn giữ taste và quyền quyết định ở năm gate G1–G5.

Ba thứ plugin thêm vào so với một lần "deep research" thông thường:

1. **Run ledger** và luật "mọi con số truy được về một lần chạy", thực thi bằng script và hook chứ không bằng prompt.
2. **`skeptic`** phản biện bằng context độc lập: chỉ nhận đường dẫn artifact, không nhận lập luận của tác giả.
3. **Vòng rút kinh nghiệm** có đo calibration giữa dự đoán và kết quả, giữa ước lượng thời gian và thời gian thực.

Thiết kế đầy đủ và nguồn tham khảo: kế hoạch "Research Squad" bản 0.1 (2026-10-07).

## Cài đặt

Yêu cầu: Claude Code (eval cần v2.1.269 trở lên), `python3` ≥ 3.10 trên `PATH`. Script chỉ dùng thư viện chuẩn; `pdftotext` (poppler) là tuỳ chọn để có bản text của PDF.

Từ GitHub:

```text
/plugin marketplace add quocthai179/computer-science-squad-agents
/plugin install lab@computer-science-squad-agents
```

Phát triển tại máy:

```bash
claude --plugin-dir ./lab        # sửa file rồi /reload-plugins
claude plugin validate ./lab
```

## Lệnh

| Bạn cần | Lệnh | Sản phẩm |
|---|---|---|
| Khởi tạo đề tài (G1) | `/lab:setup [tên]` | `research/`, `PROJECT.md` theo Heilmeier |
| Nắm nhanh một chủ đề | `/lab:survey <chủ đề> [--quick]` | survey có nguồn, khoảng trống, điểm mâu thuẫn |
| Hiểu sâu một paper | `/lab:read-paper <arXiv id \| URL \| file> [--deep]` | paper card, explain-back |
| Phản biện một artifact | `/lab:critique <đường dẫn>` | review độc lập |
| Tìm ý tưởng (G2) | `/lab:ideate [trọng tâm]` | idea card đã qua novelty protocol |
| Thiết kế thí nghiệm (G3) | `/lab:design-exp <idea-id \| câu hỏi>` | `PLAN.md` |
| Chạy thí nghiệm | `/lab:run-exp <exp-id>` (chỉ khi bạn gõ) | run ledger |
| Phân tích | `/lab:analyze <exp-id>` | `FINDINGS.md`, bảng, hình |
| Viết báo cáo (G4, G5) | `/lab:write-up <loại> [slug]` | `claims.md` → `draft.md` → `final.md` |
| Review tuần | `/lab:retro [số ngày]` | retro, `LESSONS.md`, calibration |
| Việc tiếp theo | `/lab:next` | đúng một việc và lý do |

Skill nào cũng có đường lui: không gọi được subagent thì Lead tự làm tuần tự theo cùng playbook và nói rõ điều đó.

## Đội hình

| Agent | Vai | Tools | Model | Ghi vào |
|---|---|---|---|---|
| `scout` | trinh sát tài liệu, đọc lượt 1 | Read, Glob, Grep, WebSearch, WebFetch, Write | sonnet | `surveys/<slug>/scout-*.jsonl` |
| `reader` | đọc lượt 2 trên full text | Read, Glob, Grep, Write | sonnet | `papers/cards/` |
| `writer` | người viết duy nhất | Read, Glob, Grep, Write, Edit | inherit | `surveys/`, `reports/` |
| `skeptic` | phản biện độc lập | Read, Glob, Grep, WebSearch, WebFetch, Write | opus | `reviews/` |
| `experimenter` | kỹ sư thí nghiệm | Read, Glob, Grep, Edit, Write, Bash | sonnet | code, `experiments/<id>/` |
| `analyst` | phân tích kết quả | Read, Glob, Grep, Bash, Write | sonnet | `FINDINGS.md`, bảng, hình |
| `ideator` | sinh giả thuyết | Read, Glob, Grep, Write | opus | `ideas/cards/` |

Không agent nào có tool `Agent`, nên chuỗi gọi luôn phẳng. `scout` và `reader` đọc nội dung không tin cậy nên không có `Bash` hay `Edit`. `analyst` không có `Edit`, nên không sửa được code train. Mọi bàn giao đi qua file theo hợp đồng `TASK BRIEF` / `RECEIPT` (`playbooks/handoff.md`).

## Workspace

```text
research/
├── PROJECT.md          # brief Heilmeier, stage, compute profile
├── notebook/           # YYYY-MM-DD.md, chỉ ghi thêm (scripts/notebook.py)
├── decisions.md        # quyết định ở các gate
├── papers/             # index.jsonl, refs.bib, cards/, raw/ (gitignore)
├── surveys/<slug>/     # angles.md, scout-*.jsonl, evidence.jsonl, gaps.md, survey.md
├── ideas/              # backlog.md, cards/
├── experiments/<id>/   # PLAN.md, runs.jsonl, runs/ (gitignore), FINDINGS.md, tables/, figures/
├── reports/<slug>/     # claims.md, draft.md, final.md
├── reviews/
└── lessons/            # LESSONS.md (≤ 50 dòng), calibration.jsonl, squad-issues.md, retros/
```

`/lab:setup` thêm một khối luật chung vào `CLAUDE.md` của repo (giữa `<!-- lab:begin -->` và `<!-- lab:end -->`), vì subagent có nạp `CLAUDE.md`.

## Guardrail và cách thực thi

| Luật | Thực thi bằng |
|---|---|
| Không chạy khi `PLAN.md` thiếu `prediction` hoặc `kill_criteria` | `runwrap.py` từ chối (exit 3) |
| Chỉ chạy plan đã duyệt (G3) | `runwrap.py` đòi `status: approved` hoặc `running` |
| Smoke trước mọi run thật | `runwrap.py` đòi một smoke run `ok` |
| Ngân sách run | `runwrap.py` so với `max_runs`; timeout theo `budget_minutes_per_run` |
| Sửa lỗi tối đa 3 lần | `runwrap.py` từ chối sau 3 run hỏng liên tiếp, trừ `--after-review` khi bạn cho phép |
| Không sửa tay ledger, `tables/`, `figures/` | hook `PreToolUse` (`scripts/guard_generated.py`) |
| Không sửa eval, metric, test data khi đang chạy | hook chặn `protected_files` của PLAN `approved`/`running` |
| Số liệu trong văn bản phải có trong bảng, ledger hoặc card | `lint_report.py` |
| Không placeholder trong bản cuối | `lint_report.py` |
| Không "novel", "đầu tiên", "SOTA" khi idea card thiếu `closest_prior_work` | `lint_report.py` |
| Citation phải resolve | `cite_check.py` (arXiv, doi.org, Semantic Scholar; `--offline` chỉ kiểm cục bộ) |
| Review tối đa 2 vòng, survey tối đa 1 vòng bổ sung, tối đa 5 scout | trong skill |

## Script train báo metric thế nào

Mọi run đi qua `runwrap.py`:

```bash
python3 <plugin>/scripts/runwrap.py --exp e001-ls --name baseline --tag baseline --seed 0 -- python train.py
```

Script train đọc seed từ `$LAB_SEED` và báo metric bằng một trong hai cách: in dòng `LAB_METRIC test_acc=0.8312`, hoặc ghi JSON vào `$LAB_METRICS_FILE`. Ledger ghi git SHA, cờ dirty, hash config, seed, thời gian, exit code và metric.

## Script

| Script | Việc |
|---|---|
| `init_workspace.py` | tạo `research/` (idempotent), thêm khối luật vào `CLAUDE.md` |
| `paper_fetch.py` | arXiv id, URL hoặc file → metadata, LaTeX (đã flatten) hoặc PDF, `index.jsonl`, `refs.bib` |
| `paper_index.py` | gộp và khử trùng output của scout; liệt kê; sửa trường |
| `runwrap.py` | bọc lệnh train, giữ gate, ghi ledger |
| `ledger.py` | liệt kê run, sinh bảng markdown và hình SVG, xem ngân sách |
| `stats.py` | mean, std, t-CI 95%, so sánh ghép theo seed với bootstrap CI |
| `cite_check.py` | kiểm citation `[@id, vị trí]`, `\cite{}`, arXiv, DOI, `[run:id]` |
| `lint_report.py` | placeholder, con số không có nguồn, từ novelty chưa kiểm |
| `calibration.py` | dự đoán và kết quả; ước lượng và thời gian thực; Brier score |
| `retro_digest.py` | tổng hợp tuần cho `/lab:retro` và trạng thái cho `/lab:next` |
| `notebook.py` | ghi thêm vào notebook |
| `guard_generated.py` | hook chặn sửa tay file sinh tự động và file được bảo vệ |

## Kiểm thử

Unit test cho script (ở gốc repo):

```bash
pip install pytest
pytest tests
```

Eval của plugin (`evals/`, 5 case: `read-paper-card`, `critique-planted-bugs`, `design-exp-plan`, `no-trigger-simple-question`, `next-step-analyze`). Mỗi run là một model call thật, tính vào usage của bạn. Các case dùng `scaffold.sh` để dựng fixture, nên cần `--scaffold`:

```bash
# lặp nhanh: một run, không baseline
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent --runs 1 --ablation none
# xác nhận: ba run, có nhánh không-plugin để thấy Δ
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent
```

`critique-planted-bugs` cài sẵn năm lỗi (leakage, thiếu baseline, một seed, cherry-pick, con số không có trong ledger) và kiểm `skeptic` gọi đúng tên từng lỗi. Survey cần web nên không có case tất định; đánh giá bằng golden task (xem kế hoạch, mục 8).

## Mặc định đã chọn

Theo mục 10 của kế hoạch, mỗi mục lấy mặc định; đổi mục nào thì sửa phần liên quan:

1. Bề mặt chính: Claude Code. Subagent và hook trong Claude app **chưa xác minh**.
2. Tên và prefix: `lab`.
3. Workspace: `research/` trong từng repo.
4. Ngôn ngữ artifact: tiếng Việt với thuật ngữ tiếng Anh (trường `language` trong `PROJECT.md`); draft paper bằng tiếng Anh.
5. Compute profile: điền khi chạy `/lab:setup`; ngân sách trong `PLAN.md` lấy từ đó.
6. `skeptic` dùng `opus`; chưa dùng model khác làm reviewer.

## Giới hạn

- Chi phí token: một survey đầy đủ chạy 4–5 scout và 5–8 reader. Dùng `--quick` cho câu hỏi hẹp.
- `skeptic` cùng họ model với tác giả nên có thể chung điểm mù; bạn vẫn phải đọc bản cuối.
- `cite_check.py` và `paper_fetch.py` cần truy cập `export.arxiv.org`, `arxiv.org`, `doi.org`, `api.semanticscholar.org`.
- Hook gọi `python3`; trên Windows cần `python3` trên `PATH`.
- Tăng tốc phần cơ học, không thay phần hiểu: explain-back ở `/lab:read-paper` và G5 tồn tại vì lý do đó.
