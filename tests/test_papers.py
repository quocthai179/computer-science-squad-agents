import gzip
import io
import json
import tarfile

from conftest import run_script
from paper_fetch import bibtex, parse_arxiv_atom, store_arxiv_source

ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <published>2017-06-12T17:57:34Z</published>
    <title>Attention Is All
      You Need</title>
    <summary>  The dominant sequence transduction models ... </summary>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <arxiv:primary_category term="cs.CL"/>
  </entry>
</feed>"""

EMPTY_ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>"""


def test_parse_arxiv_atom():
    m = parse_arxiv_atom(ATOM)
    assert m["arxiv"] == "1706.03762" and m["title"] == "Attention Is All You Need"
    assert m["authors"] == ["Ashish Vaswani", "Noam Shazeer"] and m["year"] == 2017
    assert m["category"] == "cs.CL" and m["venue"] == "arXiv"
    assert parse_arxiv_atom(EMPTY_ATOM) is None
    bib = bibtex("1706.03762", m)
    assert bib.startswith("@article{1706.03762,") and "eprint = {1706.03762}" in bib


def _tar(files):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_store_source_flattens_inputs_and_blocks_traversal(tmp_path):
    data = _tar({
        "main.tex": b"\\documentclass{article}\\begin{document}\\input{sections/intro}\\end{document}",
        "sections/intro.tex": b"Intro text here.",
        "../evil.tex": b"pwned",
    })
    assert store_arxiv_source(data, tmp_path) == "paper.tex"
    text = (tmp_path / "paper.tex").read_text()
    assert "Intro text here." in text and "\\input" not in text
    assert not (tmp_path.parent / "evil.tex").exists()


def test_store_source_single_gzipped_tex_and_pdf(tmp_path):
    a = tmp_path / "a"
    a.mkdir()
    assert store_arxiv_source(gzip.compress(b"\\documentclass{article} hi"), a) == "paper.tex"
    b = tmp_path / "b"
    b.mkdir()
    assert store_arxiv_source(gzip.compress(b"%PDF-1.5 fake"), b) in ("paper.pdf", "paper.txt")
    assert (b / "paper.pdf").exists()


def test_fetch_local_file(project):
    src = project / "My Paper.md"
    src.write_text("# A paper\ntext", encoding="utf-8")
    r = run_script("paper_fetch.py", str(src), "--tags", "course", cwd=project, check=True)
    assert r.stdout.startswith("ok  my-paper")
    rows = [json.loads(l) for l in (project / "research/papers/index.jsonl").read_text().splitlines()]
    assert rows[0]["id"] == "my-paper" and rows[0]["fulltext"] == "papers/raw/my-paper/paper.md"
    assert rows[0]["tags"] == ["course"]
    assert "@misc{my-paper," in (project / "research/papers/refs.bib").read_text()
    # second fetch updates instead of duplicating
    run_script("paper_fetch.py", str(src), "--tags", "x", cwd=project, check=True)
    rows = [json.loads(l) for l in (project / "research/papers/index.jsonl").read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["tags"] == ["course", "x"]
    assert (project / "research/papers/refs.bib").read_text().count("@misc{my-paper,") == 1


def test_fetch_rejects_garbage(project):
    r = run_script("paper_fetch.py", "no-such-thing", cwd=project)
    assert r.returncode == 1 and "not an arXiv id" in r.stderr


def test_index_merge_dedups(project, research):
    a = project / "scout-a.jsonl"
    b = project / "scout-b.jsonl"
    a.write_text("\n".join(json.dumps(x) for x in [
        {"title": "Attention Is All You Need", "url": "https://arxiv.org/abs/1706.03762v5", "year": 2017,
         "angle": "foundations", "relevance": 2, "why": "the transformer"},
        {"title": "Some Blog-Only Method", "authors": ["Jane Doe"], "year": 2025, "angle": "foundations",
         "relevance": 1},
    ]) + "\n")
    b.write_text("\n".join(json.dumps(x) for x in [
        {"title": "Attention is all you need.", "arxiv": "1706.03762", "angle": "methods", "relevance": 3},
        {"title": "Some blog-only method", "angle": "methods", "relevance": 0},
        {"no": "title"},
    ]) + "\n")
    r = run_script("paper_index.py", "merge", a, b, "--tag", "survey:transformers", cwd=project, check=True)
    assert "+2 new, 2 merged" in r.stdout
    rows = {x["id"]: x for x in map(json.loads, (research / "papers/index.jsonl").read_text().splitlines())}
    assert set(rows) == {"1706.03762", "doe-2025-some-blog-only-method"}
    t = rows["1706.03762"]
    assert t["relevance"] == 3 and t["pass"] == 1
    assert {"angle:foundations", "angle:methods", "survey:transformers"} <= set(t["tags"])
    r = run_script("paper_index.py", "set", "1706.03762", "pass=2", "tags=+read,-angle:methods", cwd=project, check=True)
    row = json.loads(r.stdout)
    assert row["pass"] == 2 and "read" in row["tags"] and "angle:methods" not in row["tags"]
    r = run_script("paper_index.py", "list", "--min-relevance", "2", cwd=project, check=True)
    assert "1706.03762" in r.stdout and "doe-2025" not in r.stdout
