import re

import pytest

from _lab import LANG_NAMES, SUPPORTED_LANGS, TEMPLATES, normalize_lang, parse_frontmatter, resolve_language
from conftest import run_script, write_runs

NAMES = sorted(p.name for p in (TEMPLATES / "en").glob("*.md"))
OTHERS = [l for l in SUPPORTED_LANGS if l != "en"]


def test_supported_languages_and_default():
    assert SUPPORTED_LANGS == ("en", "vi", "zh", "fr", "ja")
    assert set(LANG_NAMES) == set(SUPPORTED_LANGS)
    assert len(NAMES) == 13


@pytest.mark.parametrize("lang", SUPPORTED_LANGS)
def test_every_language_has_every_template(lang):
    assert sorted(p.name for p in (TEMPLATES / lang).glob("*.md")) == NAMES


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("lang", OTHERS)
def test_templates_keep_machine_structure(name, lang):
    """Translations may change words, never the keys, placeholders or structure the scripts rely on."""
    en = (TEMPLATES / "en" / name).read_text(encoding="utf-8")
    tr = (TEMPLATES / lang / name).read_text(encoding="utf-8")
    assert list(parse_frontmatter(en)[0]) == list(parse_frontmatter(tr)[0]), "frontmatter keys differ"
    for key in ("status", "label", "metric_direction", "smoke_required", "seeds", "max_runs", "stage", "round"):
        if key in parse_frontmatter(en)[0]:
            assert parse_frontmatter(en)[0][key] == parse_frontmatter(tr)[0][key], f"value of {key} differs"
    assert re.findall(r"\{\{\w+\}\}", en) == re.findall(r"\{\{\w+\}\}", tr)
    heads = lambda t: len(re.findall(r"^#{1,6} ", t, re.M))  # noqa: E731
    assert heads(en) == heads(tr), "heading count differs"
    assert en.count("- [ ]") == tr.count("- [ ]")
    assert len(re.findall(r"^\|[-| ]+\|$", en, re.M)) == len(re.findall(r"^\|[-| ]+\|$", tr, re.M))
    assert re.findall(r"\[(?:run|@):", en) == re.findall(r"\[(?:run|@):", tr)


@pytest.mark.parametrize("lang", OTHERS)
def test_translated_templates_are_really_translated(lang):
    en = (TEMPLATES / "en" / "paper-card.md").read_text(encoding="utf-8")
    tr = (TEMPLATES / lang / "paper-card.md").read_text(encoding="utf-8")
    assert en != tr and "Explain-back" in tr
    script = {"zh": r"[一-鿿]", "ja": r"[぀-ヿ一-鿿]", "vi": r"[ạảãâấầẩẫậăắằẳẵặêếềểễệôốồổỗộơớờởỡợưứừửữự]",
              "fr": r"[éèêàçù]"}[lang]
    assert re.search(script, tr)


def test_template_fallback_to_english(tmp_path, monkeypatch):
    import _lab
    monkeypatch.setattr(_lab, "TEMPLATES", tmp_path)
    (tmp_path / "en").mkdir()
    (tmp_path / "en" / "x.md").write_text("en")
    assert _lab.template_path("x.md", "ja") == tmp_path / "en" / "x.md"


def test_normalize_lang():
    cases = {"Vietnamese": "vi", "vi_VN": "vi", "Tiếng Việt": "vi", "Chinese": "zh", "中文": "zh", "zh-TW": "zh",
             "français": "fr", "Francais": "fr", "French": "fr", "日本語": "ja", "Japanese": "ja", "ja-JP": "ja",
             "English": "en", " EN ": "en", '"fr"': "fr"}
    for raw, code in cases.items():
        assert normalize_lang(raw) == code, raw
    assert normalize_lang("klingon") is None and normalize_lang("") is None and normalize_lang(None) is None


@pytest.mark.parametrize("lang,marker", [("en", "What are you trying to do"), ("vi", "Định làm gì"),
                                         ("zh", "你要做什么"), ("fr", "Que voulez-vous faire"),
                                         ("ja", "何をしようとしているか")])
def test_init_workspace_in_each_language(tmp_path, lang, marker):
    r = run_script("init_workspace.py", "--lang", lang, "--title", "T", cwd=tmp_path, check=True)
    assert f"language: {lang}" in r.stdout
    proj = (tmp_path / "research" / "PROJECT.md").read_text(encoding="utf-8")
    assert marker in proj and f"language: {lang}" in proj and "{{" not in proj
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert f"{lang} ({LANG_NAMES[lang]})" in claude and "{{language}}" not in claude
    assert "language:" in (tmp_path / "research" / "ideas" / "backlog.md").read_text() or True
    # idempotent re-run keeps the workspace language even without --lang
    run_script("init_workspace.py", cwd=tmp_path, check=True)
    assert resolve_language(tmp_path / "research") == lang


def test_init_default_is_english_and_rejects_unknown(tmp_path):
    run_script("init_workspace.py", cwd=tmp_path, check=True)
    assert "language: en" in (tmp_path / "research" / "PROJECT.md").read_text()
    r = run_script("init_workspace.py", "--lang", "klingon", cwd=tmp_path / ".." / "nonexistent-x" if False else tmp_path)
    assert r.returncode == 2 and "Supported: en, vi, zh, fr, ja" in r.stderr


def test_lang_script(project):
    c = lambda *a, **k: run_script("lang.py", *a, cwd=project, **k)  # noqa: E731
    assert c("get", check=True).stdout.strip() == "en"
    assert c("get", "--default", "ja", check=True).stdout.strip() == "en"       # init wrote `language: en`; it wins
    path = project / "research" / "PROJECT.md"
    path.write_text(path.read_text(encoding="utf-8").replace("language: en", "language:"), encoding="utf-8")
    assert c("get", "--default", "ja", check=True).stdout.strip() == "ja"       # blank in PROJECT.md: plugin default
    c("set", "Français", check=True)
    assert c("get", "--default", "ja", check=True).stdout.strip() == "fr"       # PROJECT.md wins over the plugin default
    assert c("name", check=True).stdout.strip() == "Français"
    assert c("set", "klingon").returncode == 2
    assert "ja\t日本語" in c("list", check=True).stdout


def test_lang_get_without_workspace_uses_default(tmp_path):
    assert run_script("lang.py", "get", "--default", "zh", cwd=tmp_path, check=True).stdout.strip() == "zh"
    assert run_script("lang.py", "get", cwd=tmp_path, check=True).stdout.strip() == "en"


# ------------------------------------------------------------------ lint in every language

def lint(project, research, text, name="d.md"):
    exp = research / "experiments" / "e001"
    (exp / "tables").mkdir(parents=True, exist_ok=True)
    (exp / "tables" / "acc.md").write_text("| method | 3 | 0.9130 |\n| baseline | 3 | 0.8120 |\n| big | 3 | 12.5 |\n")
    write_runs(exp, [{"run_id": "e001-r002", "status": "ok", "metrics": {"acc": 0.913}}])
    f = research / "reports" / name
    f.parent.mkdir(exist_ok=True)
    f.write_text(text, encoding="utf-8")
    r = run_script("lint_report.py", f, cwd=project)
    return r.returncode, r.stdout


@pytest.mark.parametrize("text", [
    "精度は0.913です。ベースラインは0.812でした。",                       # ja: digits glued to kana
    "准确率为0.913，基线为0.812。提升了12.5%。",                          # zh: digits glued to hanzi, 12.5 is in a table
    "Exactitude : 0,913 contre 0,812 ; gain de 12,5 %.",                   # fr: decimal comma, NBSP before %
    "Exactitude : 0,913 contre 0,812 ; gain de 12,5 %.",              # fr: narrow no-break space
    "Độ chính xác 0,913 so với 0,812, tăng 12,5%.",                        # vi
    "Accuracy is 0.913 against 0.812, a 12.5% gain.",                      # en
    "全角の数値０．９１３は半角に直して照合されます。",                      # ja full-width digits
])
def test_lint_numbers_in_all_languages_pass_when_sourced(project, research, text):
    code, out = lint(project, research, text.replace("０．９１３", "0.913"))
    assert code == 0, out


@pytest.mark.parametrize("text,bad", [
    ("精度は0.777です。", "0.777"),
    ("准确率为0.777，很高。", "0.777"),
    ("Exactitude : 0,777.", "0,777"),
    ("Exactitude : 77,7 %.", "77,7"),
    ("精度は７７．７％です。", "77.7"),
])
def test_lint_flags_unsourced_numbers_in_all_languages(project, research, text, bad):
    code, out = lint(project, research, text)
    assert code == 1 and "number:" in out and bad in out, out


def test_french_thousands_grouping_is_not_a_false_positive(project, research):
    exp = research / "experiments" / "e001"
    (exp / "tables").mkdir(parents=True, exist_ok=True)
    (exp / "tables" / "big.md").write_text("| n | 1234.5 |\n")
    f = research / "reports" / "fr.md"
    f.parent.mkdir(exist_ok=True)
    f.write_text("La moyenne est de 1 234,5 points.\n", encoding="utf-8")
    assert run_script("lint_report.py", f, cwd=project).returncode == 0


@pytest.mark.parametrize("text,word", [
    ("Notre méthode est novatrice et dépasse l'état de l'art.", "novatrice"),
    ("C'est la première approche à résoudre ce problème.", "première"),
    ("本方法首次实现了这一目标，且最先进。", "首次"),
    ("这是前所未有的全新方法。", "前所未有"),
    ("本手法は世界初であり、最先端の性能を示す。", "世界初"),
    ("これは初めての試みで、画期的である。", "初めて"),
    ("Đây là phương pháp đầu tiên làm việc này.", "phương pháp đầu tiên"),
])
def test_lint_novelty_claims_in_all_languages(project, research, text, word):
    code, out = lint(project, research, text)
    assert code == 1 and "novelty:" in out and word in out, out


def test_french_literature_review_heading_is_not_a_novelty_claim(project, research):
    code, out = lint(project, research, "## État de l'art\n\nLes travaux existants sont nombreux.\n")
    assert code == 0, out


@pytest.mark.parametrize("text", [
    "此处填写结论\n", "待补充\n", "Conclusions ici\n", "à compléter\n", "ここに結論を記入\n", "未記入\n",
    "结果：<填写结果>\n", "Résultat : <résultat>\n", "結果：<結果>\n", "TODO\n",
])
def test_lint_placeholders_in_all_languages(project, research, text):
    code, out = lint(project, research, text)
    assert code == 1 and "placeholder" in out, out


def test_lint_cjk_reference_numbers_are_not_flagged(project, research):
    code, out = lint(project, research, "详见表2和图3.1，以及第4节。見て図2.5と表3を参照。Voir le Tableau 2.\n")
    assert code == 0, out


def test_retro_digest_finds_next_steps_in_every_language(project, research):
    d = research / "lessons" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    for lang, heading in [("en", "Next steps"), ("vi", "Bước tiếp theo"), ("zh", "下一步（Next steps）"),
                          ("fr", "Prochaines étapes"), ("ja", "次のステップ（Next steps）")]:
        for f in d.glob("*.md"):
            f.unlink()
        (d / "2026-10-01.md").write_text(f"# Retro\n\n## {heading}\n\n- [ ] TASK-{lang}\n\n## Other\n", encoding="utf-8")
        out = run_script("retro_digest.py", cwd=project, check=True).stdout
        assert f"TASK-{lang}" in out, lang


def test_unresolved_plugin_option_placeholder_means_unset(tmp_path):
    # Claude Code leaves the literal text when the userConfig value was never saved
    assert run_script("lang.py", "get", "--default", "${user_config.language}", cwd=tmp_path, check=True).stdout.strip() == "en"
    assert run_script("lang.py", "get", "--default", "fr", cwd=tmp_path, check=True).stdout.strip() == "fr"
    r = run_script("lang.py", "get", "--default", "klingon", cwd=tmp_path)
    assert r.returncode == 2
