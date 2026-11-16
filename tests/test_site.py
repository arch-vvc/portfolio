"""Static checks for the portfolio site. Standard library only."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "reports", "tasks", "docs", "scripts", ".claude", "tests"}
PHONE_RE = re.compile(r"\+?\(?\d[\d\s().\-]{7,}\d")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.skip_text = 0
        self.metas = []
        self.links = []   # (tag, attr, value, attrs dict)
        self.imgs = []
        self.h1 = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag in ("script", "style"):
            self.skip_text += 1
        if tag == "meta":
            self.metas.append(a)
        if tag == "h1":
            self.h1 += 1
        if tag == "img":
            self.imgs.append(a)
        for attr in ("href", "src"):
            if attr in a and a[attr] is not None:
                self.links.append((tag, attr, a[attr], a))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in ("script", "style"):
            self.skip_text -= 1

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if not self.skip_text:
            self.text.append(data)


def is_external(value):
    v = value.strip().lower()
    return v.startswith(("http://", "https://", "//"))


def check_html(html, page_dir=ROOT, root=ROOT):
    """Return a list of problems found in one HTML string."""
    p = PageParser()
    p.feed(html)
    errors = []
    if not p.title.strip():
        errors.append("missing <title>")
    names = {(m.get("name") or "").lower(): (m.get("content") or "") for m in p.metas}
    if not names.get("description", "").strip():
        errors.append("missing meta description")
    if "viewport" not in names:
        errors.append("missing viewport meta")
    if p.h1 != 1:
        errors.append(f"expected exactly one h1, found {p.h1}")
    for img in p.imgs:
        if not (img.get("alt") or "").strip():
            errors.append(f"img without alt text: {img.get('src')}")
    for tag, attr, value, a in p.links:
        v = value.strip()
        # Things that must be local: scripts, stylesheets and other link tags, images.
        must_be_local = tag in ("script", "img", "link", "source", "iframe", "video", "audio")
        if is_external(v):
            if must_be_local:
                errors.append(f"external resource <{tag} {attr}={v}>")
            continue
        if v.startswith(("mailto:", "tel:", "#", "data:", "javascript:")) or not v:
            continue
        if v.startswith("/"):
            errors.append(f"root absolute path breaks on disk: {v}")
            continue
        path = unquote(urlparse(v).path)
        target = (page_dir / path).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            errors.append(f"local file not found: {v}")
        else:
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"link leaves the repo: {v}")
    text = " ".join(p.text)
    for m in PHONE_RE.finditer(text):
        if sum(ch.isdigit() for ch in m.group()) >= 10:
            errors.append(f"phone number pattern: {m.group().strip()}")
    return errors


def site_pages():
    pages = []
    for f in sorted(ROOT.rglob("*.html")):
        if SKIP_DIRS & set(f.relative_to(ROOT).parts[:-1]):
            continue
        pages.append(f)
    return pages


GOOD = (
    "<!doctype html><html lang='en'><head><title>T</title>"
    "<meta name='description' content='d'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "</head><body><h1>Hi</h1>%s</body></html>"
)


class CheckerCatchesProblems(unittest.TestCase):
    def test_good_page_passes(self):
        self.assertEqual(check_html(GOOD % "<p>Hello</p>"), [])

    def test_missing_local_file_is_caught(self):
        errs = check_html(GOOD % "<a href='nope/missing.html'>x</a>")
        self.assertTrue(any("not found" in e for e in errs), errs)

    def test_external_script_is_caught(self):
        errs = check_html(GOOD % "<script src='https://cdn.example.com/x.js'></script>")
        self.assertTrue(any("external resource" in e for e in errs), errs)

    def test_external_stylesheet_and_image_are_caught(self):
        errs = check_html(
            GOOD % "<link rel='stylesheet' href='//fonts.example.com/f.css'>"
            "<img src='https://x.example.com/a.png' alt='a'>"
        )
        self.assertEqual(len([e for e in errs if "external resource" in e]), 2, errs)

    def test_missing_alt_is_caught(self):
        errs = check_html(GOOD % "<img src='styles.css'>")
        self.assertTrue(any("alt" in e for e in errs), errs)

    def test_phone_number_is_caught(self):
        for number in ("+91 98765 43210", "098-7654-3210", "(080) 2345 6789"):
            errs = check_html(GOOD % f"<p>Call {number}</p>")
            self.assertTrue(any("phone" in e for e in errs), (number, errs))

    def test_years_and_figures_are_not_phone_numbers(self):
        html = GOOD % "<p>2023 to 2027, 96.67%, about 3,900 tenders, 366 tests</p>"
        self.assertEqual(check_html(html), [])

    def test_missing_head_parts_are_caught(self):
        errs = check_html("<html><body><p>x</p></body></html>")
        for needle in ("title", "description", "viewport", "h1"):
            self.assertTrue(any(needle in e for e in errs), (needle, errs))

    def test_two_h1_is_caught(self):
        errs = check_html(GOOD % "<h1>Again</h1>")
        self.assertTrue(any("h1" in e for e in errs), errs)

    def test_external_links_are_allowed(self):
        self.assertEqual(check_html(GOOD % "<a href='https://github.com/arch-vvc'>g</a>"), [])


class RealPages(unittest.TestCase):
    def test_pages_exist(self):
        self.assertTrue((ROOT / "index.html").is_file())

    def test_every_real_page_passes(self):
        pages = site_pages()
        self.assertTrue(pages, "no html pages found")
        for f in pages:
            with self.subTest(page=str(f.relative_to(ROOT))):
                errs = check_html(f.read_text(encoding="utf-8"), f.parent)
                self.assertEqual(errs, [])


class SkeletonFiles(unittest.TestCase):
    def test_required_files(self):
        for name in ("index.html", "styles.css", "script.js", "site.config.js", ".nojekyll"):
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertTrue((ROOT / "assets").is_dir())

    def test_config_keys_are_present_and_empty(self):
        cfg = (ROOT / "site.config.js").read_text(encoding="utf-8")
        self.assertIn("SITE_CONFIG", cfg)
        for key in ("callqa", "triage", "gtm", "tender", "callqaResult",
                    "capstoneResult", "cvPath", "windstreamPhotos"):
            self.assertRegex(cfg, rf"\b{key}\s*:", key)
        self.assertNotRegex(cfg, r"https?://", "config must ship with empty values")
        self.assertRegex(cfg, r"windstreamPhotos\s*:\s*\[\s*\]")

    def test_script_works_from_disk(self):
        js = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn("SITE_CONFIG", js)
        for banned in ("fetch(", "import ", "export ", "XMLHttpRequest", "http://", "https://"):
            self.assertNotIn(banned, js, banned)

    def test_index_loads_config_before_script(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index("site.config.js"), html.index("script.js"))
        self.assertNotIn("type=\"module\"", html)

    def test_script_renders_demo_only_when_url_set(self):
        js = (ROOT / "script.js").read_text(encoding="utf-8")
        # An empty URL must return before any element is created.
        self.assertRegex(js, r"if\s*\(\s*!url\s*\)\s*return")


if __name__ == "__main__":
    unittest.main()
