"""Static checks for the phone layout inside index.html. Standard library only."""
import re
import unittest

from test_site import ROOT, check_html

HOME_FOLDERS = ["windstream", "nexturn", "ooh"]
PROJECT_FOLDERS = ["capstone", "tender-tracker", "call-qa", "exception-triage", "gtm-agent",
                   "drishtikon", "e-cell", "cricket"]
DOCK = ["Safari", "Mail", "Messages", "Photos", "Music", "Claude", "Trash"]


class Phone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "desktop.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "phone.js").read_text(encoding="utf-8")
        cls.desktop_js = (ROOT / "desktop.js").read_text(encoding="utf-8")
        cls.apps_js = (ROOT / "apps.js").read_text(encoding="utf-8")

    # ----- structure -----
    def test_page_still_passes_the_shared_checks(self):
        self.assertEqual(check_html(self.html, ROOT), [])

    def test_phone_shell_and_status_bar(self):
        for needle in ('class="phone"', 'class="phone-screen"', 'id="p-clock"', 'id="p-pager"'):
            self.assertIn(needle, self.html, needle)

    def test_projects_page_sits_left_of_home_so_swiping_right_reveals_it(self):
        self.assertLess(self.html.index('data-page="0"'), self.html.index('data-page="1"'))
        self.assertRegex(self.js, r"var page = 1\b")
        first = self.html[self.html.index('data-page="0"'):self.html.index('data-page="1"')]
        for key in PROJECT_FOLDERS:
            self.assertIn('data-pfolder="%s"' % key, first, key)

    def test_home_page_is_the_widget_three_internships_and_the_cv(self):
        home = self.html[self.html.index('data-page="1"'):self.html.index('id="p-dots"')]
        for key in HOME_FOLDERS:
            self.assertIn('data-pfolder="%s"' % key, home, key)
        self.assertIn('data-pfile="cv"', home)
        self.assertEqual(len(re.findall(r"data-preminder", home)), 3)
        for text in ("ask about capstone", "hire archit", "check out folders for demos and info"):
            self.assertIn(text, home, text)

    def test_projects_page_holds_five_projects_and_three_activities(self):
        first = self.html[self.html.index('data-page="0"'):self.html.index('data-page="1"')]
        self.assertEqual(len(re.findall(r"data-pfolder=", first)), 8)

    def test_hint_and_page_dots(self):
        self.assertIn("swipe right to see projects", self.html)
        self.assertEqual(len(re.findall(r"data-pdot=", self.html)), 2)

    def test_dock_is_unchanged_from_the_laptop(self):
        labels = re.findall(r'data-pdock[^>]*aria-label="([^"]+)"', self.html)
        self.assertEqual(labels, DOCK)
        for name in DOCK[:-1]:
            self.assertTrue((ROOT / "assets" / "icons" / (name.lower() + ".png")).is_file(), name)

    def test_phone_icons_use_the_real_folder_and_cv_images(self):
        phone = self.html[self.html.index('class="phone"'):]
        self.assertGreaterEqual(phone.count('src="assets/icons/folder.png"'), 10)
        self.assertIn('src="assets/icons/cvfile.png"', phone)

    def test_no_second_cv_or_duplicate_ids(self):
        ids = re.findall(r'\bid="([^"]+)"', self.html)
        self.assertEqual(len(ids), len(set(ids)), [i for i in ids if ids.count(i) > 1])

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
        self.assertIn("overscroll-behavior", self.css)

    def test_phone_replaces_the_laptop_on_narrow_screens(self):
        m = re.search(r"@media\s*\(max-width:\s*899px\)\s*\{(.*?)\n\}", self.css, re.S)
        self.assertIsNotNone(m)
        self.assertRegex(m.group(1), r"\.desktop\s*\{[^}]*display:\s*none")
        self.assertRegex(m.group(1), r"\.phone\s*\{[^}]*display:\s*block")
        self.assertRegex(self.css, r"\.phone\s*\{[^}]*display:\s*none")

    def test_reduced_motion_is_respected(self):
        self.assertIn("prefers-reduced-motion", self.css)

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
        for needle in ("pointerdown", "pointermove", "pointerup", "setPointerCapture",
                       "rubber", "p-home-bar", "Escape", "ArrowLeft", "ArrowRight"):
            self.assertIn(needle, self.js, needle)

    def test_sheets_for_every_dock_app_and_folder(self):
        for name in ("Mail", "Messages", "Safari", "Music", "Photos", "Trash", "Claude"):
            self.assertIn('"%s"' % name, self.js, name)
        self.assertIn("folderSheet", self.js)
        self.assertIn("cvSheet", self.js)

    def test_close_returns_to_the_icon(self):
        self.assertIn("getBoundingClientRect", self.js)
        self.assertIn("p-sheet", self.css)


    # ----- fixes from the first council round -----
    def test_visitors_without_javascript_are_sent_to_the_plain_version(self):
        self.assertRegex(self.html, r'<noscript><meta http-equiv="refresh" content="0; url=plain\.html"></noscript>')

    def test_plain_version_is_reachable_on_the_phone_without_a_keyboard(self):
        home = self.html[self.html.index('data-page="1"'):self.html.index('id="p-dots"')]
        self.assertIn('class="p-plain" href="plain.html"', home)

    def test_home_says_who_this_is(self):
        home = self.html[self.html.index('data-page="1"'):self.html.index('id="p-dots"')]
        self.assertIn(">Archit Rishabh<", home)
        self.assertIn("Applied AI for messy business operations", home)

    def test_project_pages_lead_back_to_the_portfolio_and_the_plain_version(self):
        for f in (ROOT / "projects").glob("*.html"):
            t = f.read_text(encoding="utf-8")
            self.assertIn('href="../index.html"', t, f.name)
            self.assertIn('href="../plain.html"', t, f.name)

    def test_the_page_that_is_off_screen_cannot_take_focus(self):
        self.assertIn('setAttribute("inert", "")', self.js)
        self.assertRegex(self.js, r"pages\[pg\]\.removeAttribute\(\"inert\"\)")

    def test_edge_swipe_and_home_bar_get_their_horizontal_and_vertical_moves(self):
        self.assertRegex(self.css, r"\.p-sheet\s*\{[^}]*touch-action:\s*pan-y")
        self.assertRegex(self.css, r"\.p-body\s*\{[^}]*touch-action:\s*pan-y")
        bar = re.search(r"\.p-home-bar\s*\{([^}]*)\}", self.css).group(1)
        self.assertGreaterEqual(int(re.search(r"height:\s*(\d+)px", bar).group(1)), 48)

    def test_no_stub_text_on_first_open(self):
        # no Demo row without a video, no Safari tab without content, Claude answers with a shake
        self.assertIn('rows[r].kind === "mov" && !rows[r].href', self.js)
        self.assertNotIn("goes here", self.js)
        self.assertNotIn("is coming soon", self.js)
        self.assertIn("shake", self.js)

    def test_dock_separator_matches_the_laptop(self):
        self.assertIn('class="p-dock-sep"', self.html)

    def test_tap_targets_are_comfortable(self):
        dot = re.search(r"\.p-dot\s*\{([^}]*)\}", self.css).group(1)
        self.assertGreaterEqual(int(re.search(r"width:\s*(\d+)px", dot).group(1)), 36)
        self.assertGreaterEqual(int(re.search(r"height:\s*(\d+)px", dot).group(1)), 28)


if __name__ == "__main__":
    unittest.main()
