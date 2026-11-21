"""The CV PDF exists, is one page, and carries no phone number. Standard library only."""
import re
import shutil
import subprocess
import unittest

from test_site import ROOT

PDF = ROOT / "assets" / "Archit_Rishabh_CV.pdf"


class CvPdf(unittest.TestCase):
    def test_file_is_a_real_pdf(self):
        data = PDF.read_bytes()
        self.assertTrue(data.startswith(b"%PDF-"))
        self.assertGreater(len(data), 5000)

    @unittest.skipUnless(shutil.which("pdftotext") and shutil.which("pdfinfo"), "poppler tools are not installed")
    def test_one_page_with_the_cv_and_no_phone_number(self):
        text = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True).stdout
        for needle in ("Archit Rishabh", "Windstream Technologies", "NexTurn Limited", "OOH Advertising", "archit.rishabh25@gmail.com"):
            self.assertIn(needle, text, needle)
        self.assertNotIn("+91", text)
        for m in re.finditer(r"\+?\(?\d[ \t().\-]{0,3}[\d \t().\-]{6,}\d", text):
            self.assertLess(sum(c.isdigit() for c in m.group()), 10, m.group())
        info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        self.assertRegex(info, r"Pages:\s+1\b")

    def test_the_pdf_is_the_owners_own_cv_not_rebuilt_from_the_page(self):
        # The supplied PDF is the source; the page text in index.html mirrors it.
        self.assertFalse((ROOT / "scripts" / "make_cv_pdf.js").exists())
        data = PDF.read_bytes()
        self.assertNotIn(b"8188812222", data)
        text = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True).stdout if shutil.which("pdftotext") else ""
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        if text:
            for needle in ("GTM Lead Intelligence Platform", "Invoice Exception Triage", "Call QA for Voice Agents", "ERA5 Weather Data"):
                self.assertIn(needle, text, needle)
                self.assertIn(needle, html, needle)


if __name__ == "__main__":
    unittest.main()
