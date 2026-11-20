"""Static checks for the phone layout inside index.html. Standard library only."""
import re
import unittest

from test_site import ROOT, check_html

HOME_FOLDERS = ["windstream", "nexturn", "ooh"]
PROJECT_FOLDERS = ["capstone", "tender-tracker", "call-qa", "exception-triage", "gtm-agent",
                   "drishtikon", "e-cell", "cricket"]
LETTERS = {"windstream": "W", "nexturn": "N", "ooh": "O", "capstone": "I", "tender-tracker": "T",
           "call-qa": "C", "exception-triage": "E", "gtm-agent": "G", "drishtikon": "D",
           "e-cell": "E", "cricket": "C"}
DOCK = ["Phone", "Music", "Messages", "Safari"]
ALBUMS = ["Take Care", "Habibti", "Views", "Nothing Was The Same"]


class Phone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "desktop.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "phone.js").read_text(encoding="utf-8")
        cls.desktop_js = (ROOT / "desktop.js").read_text(encoding="utf-8")
        cls.apps_js = (ROOT / "apps.js").read_text(encoding="utf-8")
        start = cls.html.index('class="phone"')
        cls.phone = cls.html[start:cls.html.index('id="desktop"')]
        cls.home = cls.phone[cls.phone.index('data-page="0"'):cls.phone.index('data-page="1"')]
        cls.projects = cls.phone[cls.phone.index('data-page="1"'):cls.phone.index('id="p-dots"')]

    # ----- structure -----
    def test_page_still_passes_the_shared_checks(self):
        self.assertEqual(check_html(self.html, ROOT), [])

    def test_phone_shell_and_status_bar(self):
        for needle in ('class="phone"', 'class="phone-screen"', 'id="p-clock"', 'id="p-pager"'):
            self.assertIn(needle, self.html, needle)

    def test_home_is_first_and_projects_is_one_swipe_to_the_left(self):
        self.assertLess(self.phone.index('data-page="0"'), self.phone.index('data-page="1"'))
        self.assertIn('aria-label="Home"', self.home)
        self.assertIn('aria-label="Projects"', self.projects)
        self.assertRegex(self.js, r"var page = 0\b")

    def test_home_page_is_the_widget_three_internships_and_the_cv(self):
        for key in HOME_FOLDERS:
            self.assertIn('data-pfolder="%s"' % key, self.home, key)
        self.assertIn('data-pfile="cv"', self.home)
        self.assertEqual(len(re.findall(r"data-preminder", self.home)), 3)
        for text in ("ask about capstone", "hire archit", "check out folders for demos and info"):
            self.assertIn(text, self.home, text)

    def test_projects_page_holds_five_projects_and_three_activities(self):
        for key in PROJECT_FOLDERS:
            self.assertIn('data-pfolder="%s"' % key, self.projects, key)
        self.assertEqual(len(re.findall(r"data-pfolder=", self.projects)), 8)

    def test_hint_and_page_dots(self):
        self.assertIn("swipe left to see projects", self.phone)
        self.assertEqual(len(re.findall(r"data-pdot=", self.phone)), 2)
        self.assertRegex(self.phone, r'data-pdot="0"[^>]*aria-current="true"')

    def test_dock_is_the_four_icons_of_an_iphone(self):
        labels = re.findall(r'data-pdock[^>]*aria-label="([^"]+)"', self.phone)
        self.assertEqual(labels, DOCK)
        for name in DOCK:
            self.assertTrue((ROOT / "assets" / "icons" / ("ios-" + name.lower() + ".png")).is_file(), name)
        self.assertNotIn("Trash", self.phone)
        self.assertNotIn("p-dock-sep", self.phone)

    def test_folder_icons_are_stylised_first_letters(self):
        self.assertEqual(self.phone.count('class="p-tile letter"'), 11)
        for key, letter in LETTERS.items():
            pat = r'data-pfolder="%s".*?class="p-tile letter"[^>]*>%s</span>' % (re.escape(key), letter)
            self.assertRegex(self.phone, re.compile(pat, re.S), key)
        self.assertNotIn("folder.png", self.phone)
        self.assertIn('src="assets/icons/cvfile.png"', self.home)

    def test_internships_name_their_roles_on_home(self):
        self.assertIn("Founder's Office intern", self.home)
        self.assertIn("Data and AI strategy intern", self.home)

    def test_no_plain_version_link_on_the_phone(self):
        self.assertNotIn("p-plain", self.phone)
        self.assertNotIn('href="plain.html"', self.phone)

    def test_no_duplicate_ids(self):
        ids = re.findall(r'\bid="([^"]+)"', self.html)
        self.assertEqual(len(ids), len(set(ids)), [i for i in ids if ids.count(i) > 1])

    def test_home_says_who_this_is(self):
        self.assertIn(">Archit Rishabh<", self.home)
        self.assertIn("Applied AI for messy business operations", self.home)

    # ----- styles -----
    def test_black_wallpaper(self):
        self.assertRegex(self.css, r"\.phone\s*\{[^}]*background:\s*#000")

    def test_frame_is_inset_from_the_real_screen_edges(self):
        block = re.search(r"\.phone-screen\s*\{([^}]*)\}", self.css).group(1)
        for side in ("left", "right", "top", "bottom"):
            m = re.search(side + r":\s*[^;]*?(\d+)px", block)
            self.assertIsNotNone(m, side)
            self.assertGreaterEqual(int(m.group(1)), 10, side)
        self.assertIn("env(safe-area-inset-bottom", block)
        self.assertIn("env(safe-area-inset-top", block)

    def test_touch_actions_protect_the_gestures(self):
        self.assertRegex(self.css, r"\.p-pager\s*\{[^}]*touch-action:\s*pan-y")
        self.assertRegex(self.css, r"\.p-home-bar\s*\{[^}]*touch-action:\s*none")
        self.assertRegex(self.css, r"\.p-sheet\s*\{[^}]*touch-action:\s*pan-y")
        self.assertRegex(self.css, r"\.p-body\s*\{[^}]*touch-action:\s*pan-y")
        self.assertIn("overscroll-behavior", self.css)
        bar = re.search(r"\.p-home-bar\s*\{([^}]*)\}", self.css).group(1)
        self.assertGreaterEqual(int(re.search(r"height:\s*(\d+)px", bar).group(1)), 48)

    def test_phone_replaces_the_laptop_on_narrow_screens(self):
        m = re.search(r"@media\s*\(max-width:\s*899px\)\s*\{(.*?)\n\}", self.css, re.S)
        self.assertIsNotNone(m)
        self.assertRegex(m.group(1), r"\.desktop\s*\{[^}]*display:\s*none")
        self.assertRegex(m.group(1), r"\.phone\s*\{[^}]*display:\s*block")
        self.assertRegex(self.css, r"\.phone\s*\{[^}]*display:\s*none")

    def test_reduced_motion_is_respected(self):
        self.assertIn("prefers-reduced-motion", self.css)

    def test_tap_targets_are_comfortable(self):
        dot = re.search(r"\.p-dot\s*\{([^}]*)\}", self.css).group(1)
        self.assertGreaterEqual(int(re.search(r"width:\s*(\d+)px", dot).group(1)), 36)
        self.assertGreaterEqual(int(re.search(r"height:\s*(\d+)px", dot).group(1)), 28)

    # ----- behaviour -----
    def test_scripts_load_in_order(self):
        order = [self.html.index(s) for s in ("site.config.js", "apps.js", "desktop.js", "phone.js")]
        self.assertEqual(order, sorted(order))

    def test_phone_script_works_from_disk(self):
        for banned in ("fetch(", "import ", "export ", "XMLHttpRequest", "http://"):
            self.assertNotIn(banned, self.js, banned)
        for url in re.findall(r"https://[^\"'\s]+", self.js):
            self.assertTrue(url.startswith(("https://github.com/arch-vvc", "https://www.linkedin.com/in/archit-rishabh")), url)

    def test_data_is_shared_with_the_laptop_code(self):
        self.assertIn("window.DESKTOP_DATA", self.desktop_js)
        self.assertIn("window.DESKTOP_SHARED", self.apps_js)
        self.assertIn("DESKTOP_DATA", self.js)
        self.assertIn("DESKTOP_SHARED", self.js)

    def test_iphone_gestures_are_implemented(self):
        for needle in ("pointerdown", "pointermove", "pointerup", "pointercancel", "setPointerCapture",
                       "rubber", "p-home-bar", "Escape", "ArrowLeft", "ArrowRight"):
            self.assertIn(needle, self.js, needle)

    def test_sheets_for_every_dock_app_and_folder(self):
        for name in DOCK:
            self.assertIn('"%s"' % name, self.js, name)
        for fn in ("folderSheet", "cvSheet", "mailSheet", "phoneSheet", "messagesSheet", "safariSheet", "musicSheet"):
            self.assertIn(fn, self.js, fn)
        self.assertNotIn("photosSheet", self.js)

    def test_phone_app_offers_the_drafted_email_and_no_number_by_default(self):
        self.assertIn("Email Archit", self.js)
        self.assertIn("cfg.phone", self.js)
        self.assertRegex((ROOT / "site.config.js").read_text(encoding="utf-8"), r'phone:\s*""')

    def test_close_returns_to_the_icon(self):
        self.assertIn("getBoundingClientRect", self.js)
        self.assertIn("p-sheet", self.css)

    def test_the_page_that_is_off_screen_cannot_take_focus(self):
        self.assertIn('setAttribute("inert", "")', self.js)
        self.assertRegex(self.js, r"pages\[pg\]\.removeAttribute\(\"inert\"\)")

    def test_visitors_without_javascript_are_sent_to_the_plain_version(self):
        self.assertRegex(self.html, r'<noscript><meta http-equiv="refresh" content="0; url=plain\.html"></noscript>')

    def test_project_pages_lead_back_to_the_portfolio_and_the_plain_version(self):
        for f in (ROOT / "projects").glob("*.html"):
            t = f.read_text(encoding="utf-8")
            self.assertIn('href="../index.html"', t, f.name)
            self.assertIn('href="../plain.html"', t, f.name)

    def test_no_stub_text_on_first_open(self):
        self.assertIn('rows[r].kind === "mov" && !rows[r].href', self.js)
        self.assertNotIn("goes here", self.js)
        self.assertNotIn("is coming soon", self.js)

    # ----- the music names the owner asked for -----
    def test_phone_last_played_matches_the_laptop(self):
        self.assertIn("shared.lastPlayed", self.js)
        self.assertIn('"Last Played"'.replace('"', ''), self.js)
        self.assertNotIn("<span>Drake<br>Drake</span>", self.js)

    def test_recently_played_shows_the_album_names_not_drake(self):
        for title in ALBUMS:
            self.assertIn('"%s"' % title, self.apps_js, title)
        self.assertIn("albumTitles", self.apps_js)
        self.assertIn("shared.albumTitles", self.js)
        self.assertRegex(self.apps_js, r"tiles\(ALBUMS, 4, \"small\", ALBUM_TITLES\)")


if __name__ == "__main__":
    unittest.main()
