# Research Squad (`lab`)

[English](README.md) · **Tiếng Việt** · [中文](README.zh.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Plugin Claude Code cho nghiên cứu AI/ML: một **Lead** (main session chạy theo các skill `/lab:*`) điều phối **7 subagent** và dùng thư mục `research/` trong repo làm sổ lab chung. Agent lo thông lượng (đọc, chạy, kiểm, viết nháp); bạn giữ taste và quyền quyết định ở năm gate G1–G5.

Ba thứ plugin thêm vào so với một lần "deep research" thông thường:

1. **Run ledger** và luật "mọi con số truy được về một lần chạy", thực thi bằng script và hook chứ không bằng prompt.
2. **`skeptic`**, người phản biện độc lập: chỉ nhận đường dẫn artifact, không nhận lập luận của tác giả.
3. **Vòng rút kinh nghiệm** có đo calibration giữa dự đoán và kết quả, giữa ước lượng thời gian và thời gian thực.

Plugin hỗ trợ **năm ngôn ngữ**: English (mặc định), Tiếng Việt, 中文, Français, 日本語. Xem [Ngôn ngữ](#ngôn-ngữ).

## Cài đặt

Yêu cầu: Claude Code (v2.1.271 trở lên cho bộ chọn ngôn ngữ; eval cần v2.1.269+), `python3` ≥ 3.10 trên `PATH`. Script chỉ dùng thư viện chuẩn; `pdftotext` (poppler) là tuỳ chọn để có bản text của PDF.

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

## Ngôn ngữ

| Mã | Ngôn ngữ | Ghi chú |
|---|---|---|
| `en` | English | mặc định |
| `vi` | Tiếng Việt | giữ thuật ngữ tiếng Anh |
| `zh` | 中文 | chữ giản thể |
| `fr` | Français | văn phong trang trọng (vous) |
| `ja` | 日本語 | thể lịch sự (です・ます) |

**Cái gì đổi theo ngôn ngữ:** mọi thứ ghi vào `research/` (ghi chú, card, plan, review, báo cáo), các template khởi đầu (`templates/<lang>/`), và câu trả lời của agent cho bạn. **Cái gì không bao giờ đổi:** khoá frontmatter và giá trị cố định của chúng (`status: approved`, `verdict: reject`), tên trường JSONL, tên file, id, và các neo `[@paper-id, loc]` / `[run:id]`, nên script chạy được ở mọi ngôn ngữ. Chỉ dẫn, playbook và output của script bằng tiếng Anh; Lead chuyển lại cho bạn bằng ngôn ngữ của bạn.

**Chọn ngôn ngữ**, khớp đầu tiên thắng:

1. `language:` trong `research/PROJECT.md`. `/lab:setup` ghi giá trị này theo ngôn ngữ bạn đang viết. Đổi sau bằng `python3 <plugin>/scripts/lang.py set fr`.
2. Tuỳ chọn của plugin (mặc định cá nhân cho dự án mới):
   ```bash
   claude plugin configure lab@computer-science-squad-agents --values-stdin <<< '{"language":"vi"}'
   ```
   hoặc `/plugin configure lab@computer-science-squad-agents` trong Claude Code. Khi chưa lưu giá trị, tuỳ chọn là "chưa đặt" và áp dụng tiếng Anh.
3. English.

Câu trả lời trong chat theo ngôn ngữ bạn gõ, bất kể ngôn ngữ của dự án. Yêu cầu tự nhiên bằng cả năm ngôn ngữ đều kích hoạt đúng skill ("khảo sát…", "文献综述…", "revue de littérature…", "文献調査…").

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
├── PROJECT.md          # brief Heilmeier, stage, compute profile, ngôn ngữ
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
| Không sửa eval, metric, test data khi đang chạy | hook chặn `protected_files` của plan `approved`/`running` |
| Số liệu trong văn bản phải có trong bảng, ledger hoặc card | `lint_report.py` |
| Không placeholder trong bản cuối | `lint_report.py` |
| Không "novel", "đầu tiên", "SOTA" khi chưa kiểm `closest_prior_work` | `lint_report.py`, cả năm ngôn ngữ |
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
| `init_workspace.py` | tạo `research/` (idempotent, `--lang`), thêm khối luật vào `CLAUDE.md` |
| `lang.py` | xem hoặc đổi ngôn ngữ workspace |
| `paper_fetch.py` | arXiv id, URL hoặc file → metadata, LaTeX (đã flatten) hoặc PDF, `index.jsonl`, `refs.bib` |
| `paper_index.py` | gộp và khử trùng output của scout; liệt kê; sửa trường |
| `runwrap.py` | bọc lệnh train, giữ gate, ghi ledger |
| `ledger.py` | liệt kê run, sinh bảng markdown và hình SVG, xem ngân sách |
| `stats.py` | mean, std, t-CI 95%, so sánh ghép theo seed với bootstrap CI |
| `cite_check.py` | kiểm citation `[@id, vị trí]`, `\cite{}`, arXiv, DOI, `[run:id]` |
| `lint_report.py` | placeholder, con số không có nguồn, từ novelty chưa kiểm (en, vi, zh, fr, ja) |
| `calibration.py` | dự đoán và kết quả; ước lượng và thời gian thực; Brier score |
| `retro_digest.py` | tổng hợp tuần cho `/lab:retro` và trạng thái cho `/lab:next` |
| `notebook.py` | ghi thêm vào notebook |
| `guard_generated.py` | hook chặn sửa tay file sinh tự động và file được bảo vệ |

## Demo

Ảnh chụp từ các lần chạy thật trong Claude Code (phiên làm việc bằng tiếng Việt). Đầu vào là fixture của bộ eval, nên chạy lại được ([cách tái tạo](../docs/screenshots/capture/README.md)).

**`/lab:critique`: phản biện độc lập.** Lead chỉ đưa đường dẫn cho `lab:skeptic`, không đưa lập luận. Báo cáo thí nghiệm này được cài sẵn năm lỗi, và skeptic gọi đúng tên cả năm, kèm số dòng.

![lab:skeptic đang review FINDINGS.md](../docs/screenshots/critique-running.png)

![Verdict reject với năm lỗi chặn](../docs/screenshots/critique-verdict.png)

**`/lab:read-paper`: đọc sâu và explain-back.** `lab:reader` đọc full text rồi viết paper card. Lead trả về tóm tắt và ba câu hỏi để bạn tự kiểm tra mức hiểu. Paper ở đây là paper tổng hợp viết riêng cho eval; reader tự phát hiện bằng chứng yếu mà nó cài sẵn (tune không công bằng, báo best of 3 seeds).

![lab:reader chạy nền](../docs/screenshots/read-running.png)

![Paper card, tóm tắt và câu hỏi explain-back](../docs/screenshots/read-card.png)

**Guardrail bằng script, không bằng prompt.** `runwrap.py` từ chối chạy khi PLAN chưa được duyệt (G3) và khi chưa có smoke run; mọi run vào ledger kèm git SHA.

![runwrap từ chối, rồi smoke run và 6 run chính](../docs/screenshots/guardrails.png)

**Thống kê ghép theo seed.** Thí nghiệm đồ chơi (logistic regression trên dữ liệu tổng hợp): label smoothing không giúp gì, và `stats.py compare` nói thẳng điều đó vì CI 95% của hiệu chứa 0.

![stats.py compare: CI chứa 0](../docs/screenshots/stats.png)

## Kiểm thử

Unit test cho script (ở gốc repo):

```bash
pip install pytest
pytest tests
```

Test còn kiểm cả năm ngôn ngữ đều có đủ 13 template với cùng khoá frontmatter, số heading và checklist, và linter chạy đúng trên văn bản tiếng Anh, Việt, Trung, Pháp, Nhật.

Eval của plugin (`evals/`, 9 case). Mỗi run là một model call thật, tính vào usage của bạn. Các case dùng `scaffold.sh` để dựng fixture, nên cần `--scaffold`:

```bash
# lặp nhanh: một run, không nhánh baseline
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent --runs 1 --ablation none
# xác nhận: ba run, có nhánh không-plugin để thấy Δ
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent
```

| Case | Kiểm gì |
|---|---|
| `read-paper-card` | yêu cầu tiếng Anh → paper card đủ mục, trích dẫn có vị trí, explain-back |
| `critique-planted-bugs` | `skeptic` gọi đúng tên cả năm lỗi cài sẵn |
| `design-exp-plan` | `PLAN.md` đủ mục, dự đoán được ghi, plan không tự duyệt (G3) |
| `no-trigger-simple-question` | câu hỏi sự kiện đơn lẻ không gọi skill nào |
| `next-step-analyze` | `/lab:next` đề nghị phân tích các run đã xong |
| `setup-fr` | yêu cầu tiếng Pháp → workspace tiếng Pháp, `language: fr` |
| `read-paper-ja` | yêu cầu tiếng Nhật → card và câu trả lời bằng tiếng Nhật |
| `critique-zh` | yêu cầu tiếng Trung → trả lời tiếng Trung, nêu đủ năm lỗi |
| `read-paper-vi` | yêu cầu tiếng Việt → card và explain-back bằng tiếng Việt |

Survey cần web nên không tất định, không có eval case; đánh giá bằng golden task.

## Mặc định đã chọn

1. Bề mặt chính: Claude Code. Subagent và hook trong Claude app **chưa xác minh**.
2. Tên và prefix: `lab`.
3. Workspace: `research/` trong từng repo.
4. Ngôn ngữ artifact: mặc định English; hỗ trợ `vi`, `zh`, `fr`, `ja`; draft paper có thể khác ngôn ngữ dự án.
5. Compute profile: điền khi chạy `/lab:setup`; ngân sách trong `PLAN.md` lấy từ đó.
6. `skeptic` dùng `opus`; chưa dùng họ model khác làm reviewer.

## Giới hạn

- Chi phí token: một survey đầy đủ chạy 4–5 scout và 5–8 reader. Dùng `--quick` cho câu hỏi hẹp.
- `skeptic` cùng họ model với tác giả nên có thể chung điểm mù; bạn vẫn phải đọc bản cuối.
- `cite_check.py` và `paper_fetch.py` cần truy cập `export.arxiv.org`, `arxiv.org`, `doi.org`, `api.semanticscholar.org`.
- Hook gọi `python3`; trên Windows cần `python3` trên `PATH`.
- Chất lượng văn bản ở các ngôn ngữ ngoài tiếng Anh phụ thuộc vào model; cấu trúc, neo và con số không phụ thuộc ngôn ngữ và được script kiểm.
- Tăng tốc phần cơ học, không thay phần hiểu: vì vậy `/lab:read-paper` có explain-back và `/lab:write-up` kết thúc bằng G5.
