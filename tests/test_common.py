from _lab import is_blank, parse_arxiv_id, parse_frontmatter, set_frontmatter_field, slugify


def test_frontmatter_types_comments_and_lists():
    meta, body = parse_frontmatter(
        "---\n"
        "a: 3\n"
        "b: 2.5\n"
        "c: [x, 'y z', 4]\n"
        "d: approved   # trailing comment\n"
        "e: \"keep # this\"\n"
        "f:\n"
        "  - one\n"
        "  - two\n"
        "g: true\n"
        "h:\n"
        "---\nbody text\n")
    assert meta == {"a": 3, "b": 2.5, "c": ["x", "y z", 4], "d": "approved", "e": "keep # this",
                    "f": ["one", "two"], "g": True, "h": ""}
    assert body == "body text\n"


def test_no_frontmatter():
    assert parse_frontmatter("# title\n") == ({}, "# title\n")


def test_is_blank():
    assert is_blank(None) and is_blank("") and is_blank([]) and is_blank("<kết quả cụ thể>")
    assert is_blank("TODO") and is_blank("...")
    assert not is_blank("B beats A") and not is_blank(0) and not is_blank(["x"])


def test_set_frontmatter_field(tmp_path):
    p = tmp_path / "PLAN.md"
    p.write_text("---\nstatus: draft\nx: 1\n---\nbody\n", encoding="utf-8")
    set_frontmatter_field(p, "status", "approved")
    set_frontmatter_field(p, "approved_at", "2026-10-07")
    meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
    assert meta["status"] == "approved" and meta["approved_at"] == "2026-10-07" and meta["x"] == 1
    assert body == "body\n"


def test_parse_arxiv_id():
    assert parse_arxiv_id("2401.12345") == "2401.12345"
    assert parse_arxiv_id("arXiv:2401.12345v3") == "2401.12345"
    assert parse_arxiv_id("https://arxiv.org/abs/2401.12345v2") == "2401.12345"
    assert parse_arxiv_id("https://arxiv.org/pdf/2401.12345.pdf") == "2401.12345"
    assert parse_arxiv_id("hep-th/9901001") == "hep-th/9901001"
    assert parse_arxiv_id("https://example.com/paper") is None
    assert parse_arxiv_id("not an id") is None


def test_slugify():
    assert slugify("Attention Is All You Need!") == "attention-is-all-you-need"
    assert slugify("???") == "item"


def test_frontmatter_comment_after_list_or_quote():
    meta, _ = parse_frontmatter("---\nprotected_files: [eval.py, \"a b.py\"]   # eval + data\nseeds: []    # none yet\n"
                                "t: \"x # y\"   # note\nu: plain   # note\n---\n")
    assert meta == {"protected_files": ["eval.py", "a b.py"], "seeds": [], "t": "x # y", "u": "plain"}
