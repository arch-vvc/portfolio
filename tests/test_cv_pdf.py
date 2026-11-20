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
        for m in re.finditer(r"\+?\(?\d[\d\s().\-]{7,}\d", text):
            self.assertLess(sum(c.isdigit() for c in m.group()), 10, m.group())
        info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        self.assertRegex(info, r"Pages:\s+1\b")

    def test_the_pdf_script_exists_so_it_can_be_rebuilt(self):
        self.assertTrue((ROOT / "scripts" / "make_cv_pdf.js").is_file())


if __name__ == "__main__":
    unittest.main()
