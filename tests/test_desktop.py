"""Static checks for the desktop home page (index.html). Standard library only."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from test_site import ROOT, check_html

FOLDERS = [
    ("windstream", "Windstream"),
    ("nexturn", "NexTurn"),
    ("ooh", "OOH Advertising"),
    ("capstone", "Immunological Supply Chain"),
    ("tender-tracker", "Tender Tracker"),
    ("call-qa", "Call QA"),
    ("exception-triage", "Exception Triage"),
    ("gtm-agent", "gtm_agent"),
    ("drishtikon", "Drishtikon '26"),
    ("e-cell", "E-Cell"),
    ("cricket", "Cricket"),
]

DOCK = ["Safari", "Mail", "Messages", "Photos", "Music", "Claude", "Trash"]

REPOS = ["voice-agent-call-qa", "invoice-exception-triage", "gtm_agent",
         "immunological_supply_chain_management"]


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
        cls.apps = (ROOT / "apps.js").read_text(encoding="utf-8")

    def test_page_passes_the_shared_checks(self):
        self.assertEqual(check_html(self.html, ROOT), [])

    def test_one_stylesheet_and_it_is_desktop_css(self):
        self.assertEqual([h.split("?")[0] for h in re.findall(r'rel="stylesheet" href="([^"]+)"', self.html)], ["desktop.css"])

    def test_eleven_folders_internships_first_then_groups_of_three(self):
        folders = [b for b in self.parsed.buttons if "data-folder" in b]
        self.assertEqual([(b["data-folder"], b["data-name"]) for b in folders], FOLDERS)
        for b in folders:
            self.assertTrue(b.get("aria-label"), b)

    def test_dock_has_every_icon_in_order(self):
        dock = [b["aria-label"] for b in self.parsed.buttons if "data-dock" in b]
        self.assertEqual(dock, DOCK)

    def test_dock_icon_files_exist(self):
        for name in DOCK:
            slug = name.lower().replace(" ", "")
            self.assertTrue((ROOT / "assets" / "icons" / f"{slug}.png").is_file(), slug)

    def test_three_reminders_in_the_authors_words(self):
        self.assertEqual(self.parsed.reminders, [
            "ask about capstone", "hire archit", "check out folders for demos and info"])

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

    def test_small_screens_get_the_phone_layout_and_keep_the_plain_link(self):
        self.assertRegex(self.css, r"@media\s*\(max-width:\s*\d+px\)")
        self.assertIn('class="phone"', self.html)
        self.assertIn('href="plain.html"', self.html)

    def test_wallpaper_is_one_swappable_file(self):
        self.assertRegex(self.css, r"url\(['\"]?assets/wallpaper\.\w+['\"]?\)")
        self.assertTrue(list((ROOT / "assets").glob("wallpaper.*")))

    def test_script_works_from_disk(self):
        for banned in ("fetch(", "import ", "export ", "XMLHttpRequest", "http://"):
            self.assertNotIn(banned, self.js, banned)
        # Only plain links to the author's own GitHub may appear; nothing is loaded remotely.
        for url in re.findall(r"https://[^\"'\s]+", self.js):
            self.assertTrue(url.startswith("https://github.com/arch-vvc/"), url)

    def test_folder_and_file_icons_are_the_real_ones(self):
        for name in ("folder.png", "cvfile.png"):
            self.assertTrue((ROOT / "assets" / "icons" / name).is_file(), name)
        laptop = self.html[self.html.index('id="desktop"'):]
        self.assertEqual(laptop.count('src="assets/icons/folder.png"'), 11)

    def test_every_folder_has_a_finder_window_definition(self):
        keys = re.findall(r'"([a-z\-]+)":\s*\{\s*title:', self.js)
        self.assertEqual(sorted(keys), sorted([k for k, _ in FOLDERS] + ["trash"]))

    def test_project_folders_offer_a_demo_and_the_repos_open_on_github(self):
        heads = list(re.finditer(r'"([a-z\-]+)":\s*\{\s*title:', self.js))
        blocks = {}
        for i, m in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(self.js)
            blocks[m.group(1)] = self.js[m.start():end]
        for key in ("tender-tracker", "call-qa", "exception-triage", "gtm-agent", "capstone"):
            self.assertIn('demo: "', blocks[key], key)
        self.assertIn("Demo.mov", self.js)
        for repo in REPOS:
            self.assertIn('repo: "' + repo + '"', self.js, repo)
        self.assertNotIn("arch-vvc/tender-tracker", self.js)
        self.assertIn('REPO = "https://github.com/arch-vvc/"', self.js)

    def test_finder_window_has_the_sidebar_from_the_reference(self):
        for label in ("Recents", "Shared", "Favorites", "Downloads", "Applications", "Desktop",
                      "Documents", "Locations", "iCloud Drive", "archit"):
            self.assertIn(label, self.js, label)
        for col in ("Name", "Date Modified", "Size"):
            self.assertIn(col, self.js, col)

    def test_demo_buttons_read_the_config(self):
        self.assertIn("SITE_CONFIG", self.js)
        self.assertLess(self.html.index("site.config.js"), self.html.index("desktop.js"))

    def test_no_external_urls_in_css(self):
        self.assertNotRegex(self.css, r"https?://")
        self.assertNotIn("@font-face", self.css)

    def test_script_is_loaded_at_the_end_of_body(self):
        self.assertLess(self.html.index("<main"), self.html.index("desktop.js"))
        self.assertNotIn('type="module"', self.html)

    # ----- the four app windows -----
    def test_apps_script_loads_between_config_and_desktop(self):
        i = [self.html.index(s) for s in ("site.config.js", "apps.js", "desktop.js")]
        self.assertEqual(i, sorted(i))

    def test_apps_script_works_from_disk(self):
        for banned in ("fetch(", "import ", "export ", "XMLHttpRequest", "http://"):
            self.assertNotIn(banned, self.apps, banned)
        for url in re.findall(r"https://[^\"'\s]+", self.apps):
            self.assertTrue(url.startswith(("https://github.com/arch-vvc", "https://www.linkedin.com/in/archit-rishabh", "https://mail.google.com/mail/?view=cm")), url)

    def test_dock_apps_are_wired(self):
        for label in ("Safari", "Mail", "Messages", "Photos", "Music"):
            self.assertRegex(self.js + self.apps, r'"%s"' % label)

    def test_messages_threads(self):
        for name in ("Archit Rishabh", "Areas I want to work in", "Work I've done before"):
            self.assertIn(name, self.apps, name)
        self.assertIn("mailto:archit.rishabh25@gmail.com", self.apps)
        self.assertIn("Search", self.apps)
        self.assertIn("iMessage", self.apps)

    def test_mail_draft_and_send_paths(self):
        self.assertIn("Cool website, let's schedule a call", self.apps)
        self.assertIn('TO = "archit.rishabh25@gmail.com"', self.apps)
        self.assertIn("mail.google.com/mail/?view=cm", self.apps)
        self.assertIn("encodeURIComponent", self.apps)
        self.assertIn("mailto:", self.apps)
        self.assertIn('id="ml-subject"', self.apps)
        self.assertIn("<textarea", self.apps)

    def test_music_is_all_drake_with_real_covers(self):
        covers = re.findall(r'assets/music/[\w.]+', self.apps)
        self.assertGreaterEqual(len(set(covers)), 8)
        for c in covers:
            self.assertTrue((ROOT / c).is_file(), c)
        self.assertNotIn("Song title", self.apps)
        self.assertNotIn("Album title", self.apps)
        self.assertGreaterEqual(self.apps.count("Drake"), 3)

    def test_the_firm_is_named_ooh_advertising_everywhere(self):
        for f in ROOT.rglob("*"):
            if f.suffix in (".html", ".js") and ".git" not in f.parts and "tests" not in f.parts:
                self.assertNotIn("out of home advertising firm", f.read_text(encoding="utf-8"), f.name)

    def test_folders_and_files_open_on_double_click(self):
        self.assertIn('addEventListener("dblclick"', self.js)
        # a single click on a desktop icon only selects unless it came from the keyboard
        self.assertIn("e.detail === 0", self.js)
        self.assertNotIn('icon.addEventListener("click", function () { openWin(cvWin); });', self.js)

    def test_desktop_icons_sit_in_rows_of_three(self):
        # the three internships open the grid, and the CV file closes the third row
        order = re.findall(r'data-(?:folder|file)="([a-z\-]+)"', self.html)
        self.assertEqual(order[:3], ["windstream", "nexturn", "ooh"])
        self.assertEqual(order[3:6], ["capstone", "tender-tracker", "call-qa"])
        self.assertEqual(order[8], "cv")
        self.assertRegex(self.css, r"\.icons\s*\{[^}]*grid-template-columns:\s*repeat\(3")

    def test_trash_opens_a_window_with_the_message(self):
        self.assertIn("Nothing to say here, everything I make is sexy", self.js)
        self.assertRegex(self.js, r'"trash":\s*\{\s*title: "Trash"')
        self.assertIn('=== "Trash"', self.js)

    def test_windows_emerge_from_what_opened_them(self):
        self.assertIn("--ox", self.css)
        self.assertIn("--oy", self.css)
        self.assertIn("is-opening", self.css)
        self.assertIn("no-anim", self.css)
        self.assertIn("function emerge(", self.js)
        self.assertIn("getBoundingClientRect", self.js)

    def test_scripts_and_styles_carry_a_version_so_phones_never_keep_old_ones(self):
        refs = re.findall(r'(?:href|src)="((?:desktop\.css|site\.config\.js|apps\.js|desktop\.js|phone\.js)[^"]*)"', self.html)
        self.assertEqual(len(refs), 5, refs)
        for r in refs:
            self.assertRegex(r, r"\?v=\w+$", r)
        self.assertEqual(len({r.split("?v=")[1] for r in refs}), 1, refs)

    def test_cv_pdf_is_offered_on_the_laptop_the_phone_and_the_plain_page(self):
        self.assertIn('href="assets/Archit_Rishabh_CV.pdf" download', self.html)
        self.assertIn('Download the CV as a PDF', self.html)
        phone = (ROOT / "phone.js").read_text(encoding="utf-8")
        self.assertIn("Download PDF", phone)
        self.assertIn('cvPath: "assets/Archit_Rishabh_CV.pdf"', (ROOT / "site.config.js").read_text(encoding="utf-8"))

    def test_last_played_is_headlines_by_drake_on_the_take_care_cover(self):
        self.assertIn('title: "Headlines", artist: "Drake", cover: ALBUMS[0], album: ALBUM_TITLES[0]', self.apps)
        self.assertEqual(self.apps.count("esc(LAST_PLAYED.title)"), 2)   # the Last Played row and the player bar
        self.assertIn('art(ALBUMS, 0, LAST_PLAYED.album)', self.apps)

    def test_music_window_shape(self):
        for t in ("Home", "Recently Played", "Library", "Playlists", "Albums", "Songs"):
            self.assertIn(t, self.apps, t)

    def test_safari_tabs_and_what_they_do(self):
        for tab in ("GitHub", "Krillion", "LinkedIn", "Twitter", "YouTube"):
            self.assertIn('"%s"' % tab, self.apps, tab)
        self.assertIn("https://github.com/arch-vvc", self.apps)
        self.assertIn("https://www.linkedin.com/in/archit-rishabh", self.apps)
        for key in ("krillionImage", "twitter", "youtube"):
            self.assertIn("cfg." + key, self.apps, key)

    def test_ecell_folder_opens_the_case_board_page(self):
        self.assertIn('name: "Case board.html", href: "projects/e-cell.html"', (ROOT / "desktop.js").read_text(encoding="utf-8"))
        page = (ROOT / "projects" / "e-cell.html").read_text(encoding="utf-8")
        self.assertEqual(page.count("<li>"), 20)          # the 20 cases on the board
        for tier in ("Tier 4, 100 points", "Tier 3, 200 points", "Tier 2, 300 points", "Tier 1, 400 points"):
            self.assertIn(tier, page, tier)
        for precedent in ("Yahoo", "Steve Jobs", "Black Friday"):
            self.assertIn(precedent, page, precedent)

    def test_photos_is_a_stub_until_photos_arrive(self):
        self.assertIn("Photos", self.apps)
        self.assertIn("photos", self.apps)

    def test_no_private_screenshot_content_was_copied(self):
        low = (self.apps + self.html).lower()
        for private in ("naisha", "baxani", "peda", "charleia", "+1 (", "95292", "farmvilla"):
            self.assertNotIn(private, low, private)


if __name__ == "__main__":
    unittest.main()
