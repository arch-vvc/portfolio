"""Static checks for the desktop home page (index.html). Standard library only."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from test_site import ROOT, check_html

FOLDERS = [
    ("tender-tracker", "Tender Tracker"),
    ("call-qa", "Call QA"),
    ("exception-triage", "Exception Triage"),
    ("gtm-agent", "gtm_agent"),
    ("capstone", "Immunological Supply Chain"),
    ("windstream", "Windstream"),
    ("nexturn", "NexTurn"),
    ("ooh", "OOH Advertising"),
    ("drishtikon", "Drishtikon '26"),
    ("e-cell", "E-Cell"),
    ("cricket", "Cricket"),
]

DOCK = ["Finder", "Launchpad", "Safari", "Messages", "FaceTime", "Photos", "Notes", "Music",
        "Siri", "System Settings", "Brave", "WhatsApp", "ChatGPT", "Claude", "Preview", "Trash"]


class Collect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buttons = []   # attrs dicts
        self.stack = []
        self.reminders = []
        self._in_reminder = False
        self._reminder_text = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "button":
            self.buttons.append(a)
        if tag == "li" and "data-reminder" in a:
            self._in_reminder = True
            self._reminder_text = ""

    def handle_endtag(self, tag):
        if tag == "li" and self._in_reminder:
            self._in_reminder = False
            self.reminders.append(self._reminder_text.strip())

    def handle_data(self, data):
        if self._in_reminder:
            self._reminder_text += data


class Desktop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.parsed = Collect()
        cls.parsed.feed(cls.html)
        cls.css = (ROOT / "desktop.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "desktop.js").read_text(encoding="utf-8")

    def test_page_passes_the_shared_checks(self):
        self.assertEqual(check_html(self.html, ROOT), [])

    def test_one_stylesheet_and_it_is_desktop_css(self):
        self.assertEqual(re.findall(r'rel="stylesheet" href="([^"]+)"', self.html), ["desktop.css"])

    def test_eleven_folders_in_cv_order(self):
        folders = [b for b in self.parsed.buttons if "data-folder" in b]
        self.assertEqual([(b["data-folder"], b["data-name"]) for b in folders], FOLDERS)
        for b in folders:
            self.assertTrue(b.get("aria-label"), b)

    def test_dock_has_every_icon_in_order(self):
        dock = [b["aria-label"] for b in self.parsed.buttons if "data-dock" in b]
        self.assertEqual(dock, DOCK)

    def test_dock_icon_files_exist(self):
        for name in DOCK:
            if name == "Trash":
                continue
            slug = name.lower().replace(" ", "")
            if name == "System Settings":
                slug = "settings"
            self.assertTrue((ROOT / "assets" / "icons" / f"{slug}.png").is_file(), slug)

    def test_three_reminders_and_the_first_asks_for_a_job(self):
        r = self.parsed.reminders
        self.assertEqual(len(r), 3, r)
        self.assertIn("Give Archit a job", r[0])
        self.assertIn("folders for demos", r[1])

    def test_window_buttons_are_labelled_and_wired(self):
        actions = {b["data-action"]: b.get("aria-label") for b in self.parsed.buttons
                   if "data-action" in b}
        self.assertEqual(actions, {"close": "Close", "minimise": "Minimise",
                                   "fullscreen": "Full screen"})
        for action in ("close", "minimise", "fullscreen"):
            self.assertIn(action, self.js, action)

    def test_cv_window_content(self):
        for t in ("Archit_Rishabh_CV.pdf", "Windstream Technologies", "NexTurn Limited",
                  "OOH Advertising", "$150M", "93%", "8 figure contract", "100+",
                  "71% of 76", "Drishtikon", "PESU Entrepreneurship Cell", "Cottonian Shield"):
            self.assertIn(t, self.html, t)

    def test_cv_has_no_phone_number_and_no_unsupported_claims(self):
        self.assertNotIn("8188812222", self.html.replace(" ", ""))
        self.assertNotIn("+91", self.html)
        low = self.html.lower()
        for bad in ("airflow", "receipts", "under consideration", "placeholder", "todo", "lorem"):
            self.assertNotIn(bad, low, bad)

    def test_exactly_one_h1_and_a_plain_version_link(self):
        self.assertEqual(len(re.findall(r"<h1[\s>]", self.html)), 1)
        self.assertIn('href="plain.html"', self.html)

    def test_small_screens_get_the_plain_version(self):
        self.assertRegex(self.css, r"@media\s*\(max-width:\s*\d+px\)")
        self.assertIn("small-screen", self.html)

    def test_wallpaper_is_one_swappable_file(self):
        self.assertRegex(self.css, r"url\(['\"]?assets/wallpaper\.\w+['\"]?\)")
        self.assertTrue(list((ROOT / "assets").glob("wallpaper.*")))

    def test_script_works_from_disk(self):
        for banned in ("fetch(", "import ", "export ", "XMLHttpRequest", "http://", "https://"):
            self.assertNotIn(banned, self.js, banned)

    def test_no_external_urls_in_css(self):
        self.assertNotRegex(self.css, r"https?://")
        self.assertNotIn("@font-face", self.css)

    def test_script_is_loaded_at_the_end_of_body(self):
        self.assertLess(self.html.index("<main"), self.html.index("desktop.js"))
        self.assertNotIn('type="module"', self.html)


if __name__ == "__main__":
    unittest.main()
