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
        html = (ROOT / "plain.html").read_text(encoding="utf-8")
        self.assertLess(html.index("site.config.js"), html.index("script.js"))
        self.assertNotIn("type=\"module\"", html)

    def test_script_renders_demo_only_when_url_set(self):
        js = (ROOT / "script.js").read_text(encoding="utf-8")
        # An empty URL must return before any element is created.
        self.assertRegex(js, r"if\s*\(\s*!url\s*\)\s*return")


class HomePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "plain.html").read_text(encoding="utf-8")

    def test_project_titles(self):
        for t in ("Call QA for voice agents", "Exception triage for accounts payable",
                  "gtm_agent", "Tender tracker"):
            self.assertIn(t, self.html, t)

    def test_employers(self):
        for t in ("NexTurn", "Windstream Technologies", "OOH Advertising",
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

    def test_headline_figures(self):
        for t in ("93%", "$150M", "8 figure contract", "100+ renewable", "750+", "paper submitted"):
            self.assertIn(t, self.html, t)

    def test_no_hedging_or_disclosure_copy(self):
        low = self.html.lower()
        for bad in ("what i learned", "learned:", "ai wrote", "written by ai", "synthetic",
                    "no audio yet", "airflow", "34 renewable"):
            self.assertNotIn(bad, low, bad)

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
            for h in ("The problem", "What it does", "Proof", "Scope"):
                self.assertIn(h, heads, (n, h))

    def test_tender_case_study(self):
        html = self.page("tender-tracker")
        heads = re.findall(r"<h2[^>]*>(.*?)</h2>", html)
        self.assertNotIn("What went wrong", heads)
        self.assertIn("Rules it keeps", heads)
        self.assertIn("8 figure contract", html)
        self.assertNotIn("github.com/arch-vvc/tender-tracker", html)
        self.assertIn("private", html)

    def test_back_home_link(self):
        for n in PROJECT_PAGES:
            self.assertIn('href="../plain.html"', self.page(n), n)

    def test_repo_links(self):
        self.assertIn("github.com/arch-vvc/voice-agent-call-qa", self.page("call-qa"))
        self.assertIn("github.com/arch-vvc/invoice-exception-triage", self.page("exception-triage"))
        self.assertIn("github.com/arch-vvc/gtm_agent", self.page("gtm-agent"))

    def test_no_unfinished_words(self):
        for n in PROJECT_PAGES + ("../plain", "../index"):
            low = self.page(n).lower()
            for bad in ("placeholder", "todo", "lorem"):
                self.assertNotIn(bad, low, (n, bad))

    def test_numbers_from_facts(self):
        for x in ("0 of 5", "4 of 5", "428"):
            self.assertIn(x, self.page("call-qa"), x)
        for x in ("16 of 16", "505"):
            self.assertIn(x, self.page("exception-triage"), x)
        self.assertIn("632", self.page("gtm-agent"))
        t = self.page("tender-tracker")
        for x in ("33 portals", "3,900", "57", "366"):
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


class Sharing(unittest.TestCase):
    def meta(self, f):
        p = PageParser()
        p.feed(f.read_text(encoding="utf-8"))
        d = {}
        for m in p.metas:
            key = m.get("name") or m.get("property")
            if key:
                d[key] = m.get("content") or ""
        return p, d

    def test_pages_include_404(self):
        self.assertIn("404.html", [f.name for f in site_pages()])

    def test_distinct_title_and_description(self):
        titles, descs = [], []
        for f in site_pages():
            p, d = self.meta(f)
            titles.append(p.title.strip())
            descs.append(d["description"].strip())
        self.assertEqual(len(set(titles)), len(titles), titles)
        self.assertEqual(len(set(descs)), len(descs), descs)

    def test_open_graph_tags(self):
        for f in site_pages():
            p, d = self.meta(f)
            self.assertTrue(d.get("og:title", "").strip(), f.name)
            self.assertTrue(d.get("og:description", "").strip(), f.name)
            self.assertEqual(d["og:title"], p.title.strip(), f.name)

    def test_inline_svg_favicon(self):
        for f in site_pages():
            html = f.read_text(encoding="utf-8")
            self.assertRegex(html, r'<link rel="icon" href="data:image/svg\+xml', f.name)

    def test_404_links_home(self):
        html = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertRegex(html, r'href="index\.html"')

    def test_no_tracking(self):
        for f in site_pages():
            low = f.read_text(encoding="utf-8").lower()
            for bad in ("analytics", "gtag", "pixel", "googletagmanager"):
                self.assertNotIn(bad, low, (f.name, bad))

    def test_readme(self):
        r = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("site.config.js", r)
        self.assertIn("python3 -m unittest discover -s tests -q", r)
        for part in ("What this is", "Edit site.config.js", "Run the checks", "Publish"):
            self.assertIn(part, r, part)
        self.assertIn("GitHub Pages", r)
        self.assertNotRegex(r, r"\u2014|\u2013")


class Accessibility(unittest.TestCase):
    """S2: checks that were missing. Already covered elsewhere: title, description,
    viewport, exactly one h1 and alt text (all in check_html)."""

    BAD_LINK_TEXT = {"click here", "here", "link", "read more", "more"}

    @staticmethod
    def headings(html):
        return [int(n) for n in re.findall(r"<h([1-6])[\s>]", html)]

    @staticmethod
    def link_texts(html):
        return [re.sub(r"<[^>]+>", "", t).strip().lower()
                for t in re.findall(r"<a\b[^>]*>(.*?)</a>", html, flags=re.S)]

    def test_lang_on_html(self):
        for f in site_pages():
            self.assertRegex(f.read_text(encoding="utf-8"),
                             r"<html[^>]*\blang=\"[a-zA-Z-]{2,}\"", f.name)

    def test_heading_order_has_no_gaps(self):
        for f in site_pages():
            levels = self.headings(f.read_text(encoding="utf-8"))
            self.assertEqual(levels[0], 1, f.name)
            for prev, cur in zip(levels, levels[1:]):
                self.assertLessEqual(cur, prev + 1, (f.name, levels))

    def test_heading_checker_catches_a_gap(self):
        levels = self.headings("<h1>a</h1><h3>b</h3>")
        self.assertTrue(any(c > p + 1 for p, c in zip(levels, levels[1:])))

    def test_links_have_descriptive_text(self):
        for f in site_pages():
            for t in self.link_texts(f.read_text(encoding="utf-8")):
                self.assertNotIn(t, self.BAD_LINK_TEXT, (f.name, t))

    def test_link_text_checker_catches_click_here(self):
        self.assertIn("click here", self.link_texts('<a href="x">Click here</a>'))

    def test_every_link_has_some_text(self):
        for f in site_pages():
            html = f.read_text(encoding="utf-8")
            for m in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html, flags=re.S):
                text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                if not text:
                    # empty anchors are only allowed as script filled slots
                    self.assertIn("data-", m.group(1), (f.name, m.group(0)))

    def test_404_does_not_need_a_deep_path(self):
        """GitHub Pages serves 404.html at any depth, so relative links would break."""
        html = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertIn("<style", html, "404 needs inline styles so it looks right at any depth")


class TodoConfig(unittest.TestCase):
    def run_script(self, text):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "c.js"
            cfg.write_text(text, encoding="utf-8")
            return subprocess.run(["python3", str(ROOT / "scripts" / "todo_config.py"), str(cfg)],
                                  capture_output=True, text=True)

    def test_lists_only_empty_values_and_exits_zero(self):
        r = self.run_script('var C = {\n  a: "",\n  cvPath: "x.pdf",\n  windstreamPhotos: [],\n  degreeTitle: "" // note\n};')
        self.assertEqual(r.returncode, 0)
        self.assertIn("- [ ] a:", r.stdout)
        self.assertIn("- [ ] windstreamPhotos:", r.stdout)
        self.assertIn("- [ ] degreeTitle:", r.stdout)
        self.assertNotIn("cvPath", r.stdout)

    def test_all_filled_says_nothing_to_do(self):
        r = self.run_script('var C = {\n  a: "x"\n};')
        self.assertEqual(r.returncode, 0)
        self.assertIn("Nothing to fill in", r.stdout)

    def test_real_config_lists_the_empty_items(self):
        import subprocess
        r = subprocess.run(["python3", str(ROOT / "scripts" / "todo_config.py")],
                           capture_output=True, text=True)
        self.assertEqual(r.stdout.count("- [ ]"), 11)

    def test_gitignore_covers_junk(self):
        g = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".DS_Store", g)
        self.assertIn("__pycache__", g)


if __name__ == "__main__":
    unittest.main()
