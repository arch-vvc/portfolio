"""Runs the real browser gesture check when Node and Playwright are installed, otherwise skips."""
import shutil
import subprocess
import unittest

from test_site import ROOT


def playwright_available():
    node = shutil.which("node")
    if not node:
        return False
    probe = subprocess.run([node, "-e", "require('playwright')"], capture_output=True, text=True)
    return probe.returncode == 0


@unittest.skipUnless(playwright_available(), "Node with Playwright is not installed")
class PhoneGestures(unittest.TestCase):
    def test_gestures_in_an_emulated_iphone(self):
        run = subprocess.run(["node", str(ROOT / "tests" / "phone_gestures.js")],
                             capture_output=True, text=True, timeout=240)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("PHONE GESTURES OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
