import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import tempfile
import json
import shutil

# Add parent path to path if needed, but it's in the same directory
import install

class TestInstall(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_home = install.HOME
        install.HOME = self.temp_dir

    def tearDown(self):
        install.HOME = self.old_home
        shutil.rmtree(self.temp_dir)

    def test_parse_skill_md_folded_block(self):
        """Test that parse_skill_md correctly parses folded block in YAML frontmatter."""
        skill_content = """---
name: test-skill
description: >
  Line one of description.
  Line two of description.
version: 2.0.0
---
Body of the skill.
"""
        with patch("builtins.open", mock_open(read_data=skill_content)):
            parsed = install.parse_skill_md("SKILL.md")
            self.assertEqual(parsed["name"], "test-skill")
            self.assertEqual(
                parsed["description"],
                "Line one of description. Line two of description."
            )
            self.assertEqual(parsed["body"], "Body of the skill.")

    def test_parse_skill_md_literal_block(self):
        """Test that parse_skill_md correctly parses literal block in YAML frontmatter."""
        skill_content = """---
name: test-skill
description: |
  Line one of description.
  Line two of description.
version: 2.0.0
---
Body of the skill.
"""
        with patch("builtins.open", mock_open(read_data=skill_content)):
            parsed = install.parse_skill_md("SKILL.md")
            self.assertEqual(
                parsed["description"],
                "Line one of description.\nLine two of description."
            )

    def test_skill_lock_json_missing_skills_key(self):
        """Test that install_global_agents correctly handles missing 'skills' key in .skill-lock.json."""
        lock_path = os.path.join(install.HOME, ".agents", ".skill-lock.json")
        
        # Setup a lock file with missing skills key
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        with open(lock_path, "w", encoding="utf-8") as f:
            json.dump({"version": 3}, f)
        
        # Run install_global_agents (mocking SKILL_SOURCE copy to avoid copying)
        with patch("shutil.copy"):
            install.install_global_agents()
            
        # Verify lock file has 'skills' and the 'gunch' key
        with open(lock_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("skills", data)
        self.assertIn("gunch", data["skills"])

    def test_install_hermes_brittle_yaml_parser(self):
        """Test that install_hermes updates config.yaml robustly even with blank lines and comments."""
        config_path = os.path.join(install.HOME, ".hermes", "config.yaml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Case 1: skills section with comments and blank lines, but no external_dirs
        test_yaml = """model:
  default: gemini
skills:
  # some comments
  
  template_vars: true
curator:
  enabled: true
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(test_yaml)
            
        install.install_hermes()
        
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("external_dirs:", content)
        self.assertIn("- " + os.path.join(install.HOME, ".agents", "skills"), content)
        # Ensure no duplication of skills
        self.assertEqual(content.count("skills:"), 1)
        self.assertEqual(content.count("external_dirs:"), 1)

        # Case 2: skills section with existing external_dirs empty []
        test_yaml_2 = """skills:
  # comment
  external_dirs: []
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(test_yaml_2)
            
        install.install_hermes()
        
        with open(config_path, "r", encoding="utf-8") as f:
            content_2 = f.read()
        self.assertIn("external_dirs: [" + os.path.join(install.HOME, ".agents", "skills") + "]", content_2)

    @patch("urllib.request.urlopen")
    @patch("os.path.exists")
    def test_resolve_skill_source_fallback(self, mock_exists, mock_urlopen):
        """Test that resolve_skill_source fetches from GitHub when local SKILL.md is not found."""
        # 1. First scenario: script relative path and cwd don't exist
        mock_exists.return_value = False
        
        # Mock urlopen context manager
        mock_response = MagicMock()
        mock_response.read.return_value = b"Remote body"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Patch __file__ inside install to look like stdin
        with patch.dict(install.__dict__, {"__file__": "<stdin>"}):
            with patch("tempfile.gettempdir", return_value="/tmp"):
                # We mock opening the downloaded file for write
                m_open = mock_open()
                with patch("builtins.open", m_open):
                    path = install.resolve_skill_source()
                    self.assertEqual(path, "/tmp/gunch_skill_temp.md")
                    m_open.assert_called_once_with("/tmp/gunch_skill_temp.md", "wb")
                    m_open().write.assert_called_once_with(b"Remote body")

    def test_install_hermes_indented_skills(self):
        """Test that install_hermes does not treat indented 'skills:' as the top-level section."""
        config_path = os.path.join(install.HOME, ".hermes", "config.yaml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # The word 'skills:' is indented inside description.
        test_yaml = """model:
  description: |
    This model has skills:
    - coding
curator:
  enabled: true
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(test_yaml)
            
        install.install_hermes()
        
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Verify the top-level 'skills:' was appended at the end and the
        # indented one is left untouched
        expected_skills = (
            "\nskills:\n  external_dirs:\n    - "
            + os.path.join(install.HOME, ".agents", "skills")
        )
        self.assertIn(expected_skills, content)
        self.assertEqual(content.count("  description: |"), 1)
        self.assertEqual(content.count("    This model has skills:"), 1)

    @patch("os.path.exists")
    def test_resolve_skill_source_developer_fallback(self, mock_exists):
        """Test that resolve_skill_source falls back to absolute
        developer paths when local SKILL.md is missing.
        """
        def side_effect(path):
            # Return True only for the developer fallback path
            fallback = "/Users/uchebnick/projects/gunch/skills/gunch/SKILL.md"
            return path == fallback

        mock_exists.side_effect = side_effect

        # Patch __file__ inside install to look like stdin
        with patch.dict(install.__dict__, {"__file__": "<stdin>"}):
            path = install.resolve_skill_source()
            expected = "/Users/uchebnick/projects/gunch/skills/gunch/SKILL.md"
            self.assertEqual(path, expected)

    def test_parse_skill_md_with_horizontal_rule(self):
        """Test that parse_skill_md with horizontal rule inside
        the Markdown body does not split content incorrectly.
        """
        skill_content = """---
name: test-skill
description: "A description"
---
Body of the skill before HR.
---
Body of the skill after HR.
"""
        with patch("builtins.open", mock_open(read_data=skill_content)):
            parsed = install.parse_skill_md("SKILL.md")
            self.assertEqual(parsed["name"], "test-skill")
            self.assertEqual(parsed["description"], "A description")
            expected_body = (
                "Body of the skill before HR.\n"
                "---\n"
                "Body of the skill after HR."
            )
            self.assertIn(expected_body, parsed["body"])

    def test_install_codex_toml_escaping(self):
        """Test that install_codex escapes double quotes in description."""
        parsed = {
            "name": "gunch",
            "description": 'This is a description with "quotes".',
            "body": "Body here."
        }

        codex_toml_path = os.path.join(install.HOME, ".codex", "commands", "gunch.toml")
        os.makedirs(os.path.dirname(codex_toml_path), exist_ok=True)
        install.install_codex(parsed)

        with open(codex_toml_path, "r", encoding="utf-8") as f:
            content = f.read()

        expected_desc = (
            'description = "This is a description with \\"quotes\\"."'
        )
        self.assertIn(expected_desc, content)


    @patch("urllib.request.urlopen")
    @patch("os.path.exists")
    @patch("install.log_warn")
    def test_resolve_skill_source_http_failure_fallback(self, mock_log_warn, mock_exists, mock_urlopen):
        """Test that resolve_skill_source falls back to embedded SKILL.md when URL fetch fails."""
        # Force all local checks to fail so it goes to HTTP fetch
        mock_exists.return_value = False
        
        # Force urllib.request.urlopen to raise an Exception
        mock_urlopen.side_effect = Exception("Network unreachable")
        
        # Patch __file__ inside install to look like stdin
        with patch.dict(install.__dict__, {"__file__": "<stdin>"}):
            with patch("tempfile.gettempdir", return_value="/tmp"):
                # We mock opening the downloaded file for write/read
                m_open = mock_open()
                with patch("builtins.open", m_open):
                    path = install.resolve_skill_source()
                    self.assertEqual(path, "/tmp/gunch_skill_temp.md")
                    
                    # Verify mock_log_warn was called
                    mock_log_warn.assert_called_once()
                    
                    # Verify it wrote the fallback content
                    write_calls = m_open().write.call_args_list
                    self.assertTrue(len(write_calls) > 0)
                    written_content = write_calls[0][0][0]
                    self.assertIn("GUNCH KNOWLEDGE BASE SKILL", written_content)
                    self.assertIn("name: gunch", written_content)

    def test_install_claude_cleanup_modes(self):
        """Test that install_claude cleans up existing directories, files, or symlinks correctly."""
        claude_skills_dir = os.path.join(install.HOME, ".claude", "skills")
        symlink_path = os.path.join(claude_skills_dir, "gunch")
        global_skill_dir = os.path.join(install.HOME, ".agents", "skills", "gunch")
        os.makedirs(global_skill_dir, exist_ok=True)
        
        # Case 1: Existing path is a regular directory
        os.makedirs(symlink_path, exist_ok=True)
        with open(os.path.join(symlink_path, "dummy.txt"), "w", encoding="utf-8") as f:
            f.write("dummy")
        install.install_claude()
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), global_skill_dir)
        
        # Case 2: Existing path is a regular file
        os.unlink(symlink_path)
        with open(symlink_path, "w", encoding="utf-8") as f:
            f.write("regular file")
        install.install_claude()
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), global_skill_dir)
        
        # Case 3: Existing path is a symlink (even broken)
        os.unlink(symlink_path)
        os.symlink("/nonexistent/path", symlink_path)
        install.install_claude()
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), global_skill_dir)

    def test_install_opencode_cleanup_modes(self):
        """Test that install_opencode cleans up existing directories, files, or symlinks correctly."""
        opencode_skills_dir = os.path.join(install.HOME, ".config", "opencode", "skills")
        symlink_path = os.path.join(opencode_skills_dir, "gunch")
        global_skill_dir = os.path.join(install.HOME, ".agents", "skills", "gunch")
        os.makedirs(global_skill_dir, exist_ok=True)
        
        # Case 1: Existing path is a regular directory
        os.makedirs(symlink_path, exist_ok=True)
        with open(os.path.join(symlink_path, "dummy.txt"), "w", encoding="utf-8") as f:
            f.write("dummy")
        install.install_opencode()
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), global_skill_dir)
        
        # Case 2: Existing path is a regular file
        os.unlink(symlink_path)
        with open(symlink_path, "w", encoding="utf-8") as f:
            f.write("regular file")
        install.install_opencode()
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), global_skill_dir)
        
        # Case 3: Existing path is a symlink (even broken)
        os.unlink(symlink_path)
        os.symlink("/nonexistent/path", symlink_path)
        install.install_opencode()
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), global_skill_dir)

    def test_install_hermes_flow_style_empty(self):
        """Test that install_hermes updates config.yaml when
        external_dirs is empty flow style (e.g. external_dirs: []).
        """
        config_path = os.path.join(install.HOME, ".hermes", "config.yaml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        test_yaml = """skills:
  external_dirs: []
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(test_yaml)

        install.install_hermes()

        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        expected_dir = os.path.join(install.HOME, ".agents", "skills")
        expected_val = f"  external_dirs: [{expected_dir}]\n"
        self.assertIn(expected_val, content)

    def test_install_hermes_flow_style_pre_populated(self):
        """Test that install_hermes updates config.yaml when
        external_dirs is pre-populated flow style.
        """
        config_path = os.path.join(install.HOME, ".hermes", "config.yaml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        test_yaml = """skills:
  external_dirs: [/some/path]
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(test_yaml)

        install.install_hermes()

        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        expected_dir = os.path.join(install.HOME, ".agents", "skills")
        expected_val = f"  external_dirs: [/some/path, {expected_dir}]\n"
        self.assertIn(expected_val, content)

    def test_install_codex_triple_quote_escaping(self):
        """Test that install_codex escapes triple-quotes in the body
        to avoid Codex command TOML syntax break.
        """
        parsed = {
            "name": "gunch",
            "description": "A skill that has triple quotes.",
            "body": (
                'This is a body containing triple quotes: """ '
                'and another pair of """'
            )
        }

        codex_toml_path = os.path.join(
            install.HOME, ".codex", "commands", "gunch.toml"
        )
        os.makedirs(os.path.dirname(codex_toml_path), exist_ok=True)
        install.install_codex(parsed)

        with open(codex_toml_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify the prompt block has escaped triple quotes
        expected_body = (
            'This is a body containing triple quotes: \\"\\"\\" '
            'and another pair of \\"\\"\\"'
        )
        self.assertIn(expected_body, content)


if __name__ == "__main__":
    unittest.main()
