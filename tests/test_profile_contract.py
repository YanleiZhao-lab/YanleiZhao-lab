from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

import yaml


ROOT = Path(__file__).resolve().parents[1]


class ProfileContractTest(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "README.md",
            "assets/terminal-hero.svg",
            "assets/divider.svg",
            "profile-summary-card-output/transparent/0-profile-details.svg",
            "profile-summary-card-output/transparent/1-repos-per-language.svg",
            "profile-summary-card-output/transparent/3-stats.svg",
            "profile-3d-contrib/profile-night-rainbow.svg",
            ".github/scripts/update-activity.mjs",
            ".github/scripts/generate-profile-visuals.mjs",
            ".github/workflows/achievements.yml",
            ".github/workflows/breakout.yml",
            ".github/workflows/contribution-3d.yml",
            ".github/workflows/recent-activity.yml",
        ]
        for relative_path in required:
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())

    def test_readme_has_complete_portal_structure(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        required_text = (
            "Hi there, I'm YanleiZhao",
            "GitHub Radar",
            "Contribution Breakout",
            "Project Map",
            "Tech Stack",
            "GitHub Statistics",
            "3D Contributions",
            "<!--RECENT_ACTIVITY:start-->",
            "<!--RECENT_ACTIVITY:end-->",
            "<!-- my-badges start -->",
            "<!-- my-badges end -->",
        )
        positions = []
        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, readme)
                positions.append(readme.index(text))
        self.assertLess(readme.index("GitHub Radar"), readme.index("Contribution Breakout"))
        self.assertLess(readme.index("Project Map"), readme.index("Tech Stack"))
        self.assertLess(readme.index("Tech Stack"), readme.index("GitHub Statistics"))
        self.assertLess(readme.index("GitHub Statistics"), readme.index("3D Contributions"))

    def test_original_projects_are_linked(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        projects = (
            "NVH_Analysis",
            "IELTS-Typing_Pro",
            "wechat-codex-autowrite",
            "xiaohuajia",
            "ai-new-hub",
        )
        self.assertNotIn("Fork / Upstream", readme)
        for project in projects:
            with self.subTest(project=project):
                self.assertIn(f"https://github.com/YanleiZhao-lab/{project}", readme)

    def test_svg_assets_are_valid_and_accessible(self):
        for relative_path in (
            "assets/terminal-hero.svg",
            "assets/divider.svg",
            "profile-summary-card-output/transparent/0-profile-details.svg",
            "profile-summary-card-output/transparent/1-repos-per-language.svg",
            "profile-summary-card-output/transparent/3-stats.svg",
            "profile-3d-contrib/profile-night-rainbow.svg",
        ):
            with self.subTest(path=relative_path):
                root = ET.parse(ROOT / relative_path).getroot()
                namespace = {"svg": "http://www.w3.org/2000/svg"}
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertIsNotNone(root.find("svg:title", namespace))
                self.assertIsNotNone(root.find("svg:desc", namespace))

    def test_workflows_have_safe_triggers_and_permissions(self):
        workflows = sorted((ROOT / ".github/workflows").glob("*.yml"))
        self.assertEqual(len(workflows), 4)
        for workflow in workflows:
            with self.subTest(workflow=workflow.name):
                data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
                triggers = data.get("on", data.get(True, {}))
                self.assertIn("schedule", triggers)
                self.assertIn("workflow_dispatch", triggers)
                self.assertEqual(data.get("permissions", {}).get("contents"), "write")

    def test_actions_are_pinned_and_tokens_are_builtin(self):
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / ".github/workflows").glob("*.yml"))
        )
        self.assertNotRegex(workflow_text, r"uses:\s+[^\s]+@(main|master|v\d+)\s*$")
        self.assertIn("cyprieng/github-breakout@60c43dca3a1361fbc9fb9bb533b5193296345c4f", workflow_text)
        self.assertIn("node .github/scripts/generate-profile-visuals.mjs", workflow_text)
        self.assertNotIn("PAT", workflow_text)
        self.assertNotIn("PERSONAL_TOKEN", workflow_text)
        self.assertIn("secrets.GITHUB_TOKEN", workflow_text)

    def test_repository_has_no_embedded_pat(self):
        token_pattern = re.compile(r"(?:ghp|github_pat)_[A-Za-z0-9_]{12,}")
        scanned = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "docs" in path.parts or "tests" in path.parts:
                continue
            if path.suffix.lower() not in {".md", ".yml", ".yaml", ".mjs", ".svg", ".py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            scanned.append(path)
            self.assertIsNone(token_pattern.search(text), path)
        self.assertTrue(scanned)


if __name__ == "__main__":
    unittest.main()
