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


class HomePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_project_titles(self):
        for t in ("Call QA for voice agents", "Exception triage for accounts payable",
                  "gtm_agent", "Tender tracker"):
            self.assertIn(t, self.html, t)

    def test_employers(self):
        for t in ("NexTurn", "Windstream Technologies", "out of home advertising firm",
                  "Centre for Innovation and Entrepreneurship"):
            self.assertIn(t, self.html, t)

    def test_capstone_and_education(self):
        self.assertIn("Immunological Supply Chain", self.html)
        for t in ("PES University", "Delhi Public School South", "Bishop Cotton"):
            self.assertIn(t, self.html, t)

    def test_contact_links(self):
        self.assertIn('href="mailto:archit.rishabh25@gmail.com"', self.html)
        self.assertIn('href="https://www.linkedin.com/in/archit-rishabh"', self.html)
        self.assertIn('href="https://github.com/arch-vvc"', self.html)

    def test_no_dropped_figure(self):
        self.assertNotIn("93%", self.html)

    def test_sections_in_order(self):
        heads = re.findall(r"<h2[^>]*>(.*?)</h2>", self.html)
        self.assertEqual(heads, ["Projects", "Experience", "Research", "Education",
                                 "Leadership and activities"])

    def test_semantic_elements(self):
        for tag in ("<header", "<main", "<footer", "<section", "<ul"):
            self.assertIn(tag, self.html, tag)

    def test_project_links(self):
        for page in ("call-qa", "exception-triage", "gtm-agent", "tender-tracker"):
            self.assertIn(f'href="projects/{page}.html"', self.html, page)
        for repo in ("voice-agent-call-qa", "invoice-exception-triage", "gtm_agent"):
            self.assertIn(f"https://github.com/arch-vvc/{repo}", self.html, repo)
        self.assertNotIn("arch-vvc/tender-tracker", self.html)

    def test_demo_and_cv_slots(self):
        for slot in ("callqa", "triage", "gtm", "tender"):
            self.assertIn(f'data-demo="{slot}"', self.html, slot)
        self.assertIn("data-cv", self.html)


PROJECT_PAGES = ("call-qa", "exception-triage", "gtm-agent", "tender-tracker")


class ProjectPages(unittest.TestCase):
    def page(self, name):
        return (ROOT / "projects" / f"{name}.html").read_text(encoding="utf-8")

    def test_pages_exist(self):
        for n in PROJECT_PAGES:
            self.assertTrue((ROOT / "projects" / f"{n}.html").is_file(), n)

    def test_common_headings(self):
        for n in PROJECT_PAGES:
            heads = re.findall(r"<h2[^>]*>(.*?)</h2>", self.page(n))
            for h in ("The problem", "What it does", "Proof", "Limits"):
                self.assertIn(h, heads, (n, h))

    def test_tender_case_study(self):
        html = self.page("tender-tracker")
        heads = re.findall(r"<h2[^>]*>(.*?)</h2>", html)
        self.assertIn("What went wrong", heads)
        self.assertIn("Rules it keeps", heads)
        self.assertNotIn("github.com/arch-vvc/tender-tracker", html)
        self.assertIn("private", html)

    def test_back_home_link(self):
        for n in PROJECT_PAGES:
            self.assertIn('href="../index.html"', self.page(n), n)

    def test_repo_links(self):
        self.assertIn("github.com/arch-vvc/voice-agent-call-qa", self.page("call-qa"))
        self.assertIn("github.com/arch-vvc/invoice-exception-triage", self.page("exception-triage"))
        self.assertIn("github.com/arch-vvc/gtm_agent", self.page("gtm-agent"))

    def test_no_unfinished_words(self):
        for n in PROJECT_PAGES + ("../index",):
            low = self.page(n).lower()
            for bad in ("placeholder", "todo", "lorem"):
                self.assertNotIn(bad, low, (n, bad))

    def test_numbers_from_facts(self):
        self.assertIn("70% to 95%", self.page("call-qa"))
        self.assertIn("16 of 16", self.page("exception-triage"))
        self.assertIn("570", self.page("gtm-agent"))
        t = self.page("tender-tracker")
        for x in ("33 portals", "3,900", "57", "366", "8 of 10", "2 of 10"):
            self.assertIn(x, t, x)

    def test_config_slots(self):
        slots = {"call-qa": "callqa", "exception-triage": "triage",
                 "gtm-agent": "gtm", "tender-tracker": "tender"}
        for n, slot in slots.items():
            self.assertIn(f'data-demo="{slot}"', self.page(n), n)
        self.assertIn('data-text="callqaResult"', self.page("call-qa"))

    def test_script_and_css_paths(self):
        for n in PROJECT_PAGES:
            h = self.page(n)
            self.assertIn('href="../styles.css"', h)
            self.assertLess(h.index("../site.config.js"), h.index("../script.js"))


def _luminance(hexcol):
    h = hexcol.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    chans = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        chans.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]


def contrast(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def theme_vars(css):
    """Return (light, dark) dicts of custom properties."""
    root = re.search(r":root\s*\{([^}]*)\}", css).group(1)
    dark_block = re.search(
        r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}", css).group(1)
    pick = lambda blk: dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", blk))
    light = pick(root)
    dark = dict(light)
    dark.update(pick(dark_block))
    return light, dark


class Design(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / "styles.css").read_text(encoding="utf-8")

    def test_contrast_both_themes(self):
        light, dark = theme_vars(self.css)
        for name, t in (("light", light), ("dark", dark)):
            self.assertGreaterEqual(contrast(t["--fg"], t["--bg"]), 7, (name, "body"))
            self.assertGreaterEqual(contrast(t["--accent"], t["--bg"]), 4.5, (name, "accent"))
            self.assertGreaterEqual(contrast(t["--muted"], t["--bg"]), 4.5, (name, "muted"))

    def test_media_rules(self):
        self.assertRegex(self.css, r"@media\s*\(max-width:\s*600px\)")
        self.assertRegex(self.css, r"@media\s*\(prefers-color-scheme:\s*dark\)")
        self.assertRegex(self.css, r"@media\s+print")

    def test_print_shows_link_urls(self):
        self.assertIn("attr(href)", self.css)

    def test_no_wide_fixed_widths(self):
        for m in re.finditer(r"(?<![-\w])(?:min-|max-)?width:\s*(\d+)px", self.css):
            if "@media" in self.css[max(0, m.start() - 40):m.start()]:
                continue
            self.assertLessEqual(int(m.group(1)), 600, m.group(0))
        self.assertNotRegex(self.css, r"(?<![-\w])width:\s*\d{4,}px")

    def test_stylesheet_length(self):
        self.assertLess(len(self.css.splitlines()), 300)

    def test_focus_styles_and_no_animation(self):
        self.assertIn(":focus-visible", self.css)
        self.assertNotIn("@keyframes", self.css)
        self.assertNotIn("animation", self.css)

    def test_system_fonts_only(self):
        self.assertIn("system-ui", self.css)
        self.assertNotIn("@font-face", self.css)
        self.assertNotIn("url(", self.css)

    def test_one_stylesheet_everywhere(self):
        for f in site_pages():
            html = f.read_text(encoding="utf-8")
            self.assertEqual(len(re.findall(r'rel="stylesheet"', html)), 1, f.name)

    def test_no_horizontal_scroll_guard(self):
        self.assertRegex(self.css, r"overflow-wrap:\s*(anywhere|break-word)")


if __name__ == "__main__":
    unittest.main()
