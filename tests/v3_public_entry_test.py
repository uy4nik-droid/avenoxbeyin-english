"""Public one-message entrypoint stays deterministic and novice-safe."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicEntryTest(unittest.TestCase):
    def test_entrypoint_routes_agent_to_verified_release_and_preserves_notes(self):
        text = (ROOT / 'beyin.md').read_text(encoding='utf-8')
        required = (
            'releases/latest', '.zip.sha256', 'install_v3.py --vault',
            'beyin.py doctor --human', 'beyin.py preferences --human',
            'https://avenox.lol/ikincibeyin', 'Do not delete, move, rename or overwrite user notes',
            '.agents/skills/beyin/SKILL.md',
        )
        for phrase in required:
            self.assertIn(phrase, text)
        self.assertNotIn('Mem0 is required', text)
        self.assertNotIn('git reset --hard', text)

    def test_entrypoint_requires_fresh_session_before_memory_success_claim(self):
        text = (ROOT / 'beyin.md').read_text(encoding='utf-8')
        self.assertIn('ask the user to open a new session', text)
        self.assertIn('Do not say "memory across sessions is verified"', text)


if __name__ == '__main__':
    unittest.main()
