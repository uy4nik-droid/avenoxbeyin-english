#!/usr/bin/env python3
"""Regression contract for the public one-prompt installation entrypoint."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = (ROOT / "docs" / "beyin-v2.md").read_text(encoding="utf-8")
README = (ROOT / "docs" / "V2-README.md").read_text(encoding="utf-8")


def section(text: str, start: str, end: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at + len(start))
    return text[start_at:end_at]


class EntrypointRoutingTest(unittest.TestCase):
    def test_platform_gate_precedes_every_install_step(self) -> None:
        self.assertLess(
            ENTRYPOINT.index("## STEP -1: Platform gate"),
            ENTRYPOINT.index("## STEP 0: Is there an existing brain?"),
        )
        rules = section(ENTRYPOINT, "## Rules for you, Claude", "Placeholders you must resolve")
        self.assertIn("Route first, interview second, build third", rules)

    def test_native_windows_hands_off_before_any_posix_path(self) -> None:
        route = section(
            ENTRYPOINT,
            "### Native Windows: hand off and stop this file",
            "### WSL: stay entirely inside the Linux lane",
        )
        self.assertIn("SETUP-WINDOWS.md", route)
        self.assertIn("upgrade.sh", route)
        self.assertIn("Do **not** execute STEP 0", route)
        self.assertIn("[guid]::NewGuid()", route)
        self.assertIn("Stop reading this\nfile now", route)

    def test_wsl_is_one_posix_runtime_not_a_mixed_windows_install(self) -> None:
        route = section(
            ENTRYPOINT,
            "### WSL: stay entirely inside the Linux lane",
            "### macOS or Linux: keep the existing POSIX lane",
        )
        self.assertIn("SETUP.md", route)
        self.assertIn("same WSL distro", route)
        self.assertIn("not under `/mnt/c`", route)
        self.assertIn("not claimed as\nverified", route)

    def test_existing_macos_fast_path_remains_intact(self) -> None:
        self.assertIn(
            "git clone https://github.com/uy4nik-droid/avenoxbeyin-english.git /tmp/avenoxbeyin && cd /tmp/avenoxbeyin",
            ENTRYPOINT,
        )
        self.assertIn("Then read and follow `SETUP.md` in that repo", ENTRYPOINT)
        self.assertIn("macOS remains the fully tested POSIX path", ENTRYPOINT)

    def test_readme_exposes_the_same_three_way_contract(self) -> None:
        self.assertIn("This one-line entry first tells platforms apart", README)
        self.assertIn("Or on macOS, Linux or WSL, clone the repo directly", README)
        self.assertIn("native\nWindows moves to `SETUP-WINDOWS.md`", README)
        self.assertIn("WSL uses the POSIX path that stays entirely\ninside the same Linux distribution", README)
        self.assertIn("On native Windows", README)


if __name__ == "__main__":
    unittest.main(verbosity=2)
