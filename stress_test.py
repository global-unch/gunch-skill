import unittest
from unittest.mock import patch
import os
import shutil
import tempfile
import sys

# Ensure workspace is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import install

class TestInstallStress(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_home = install.HOME
        install.HOME = self.temp_dir

    def tearDown(self):
        install.HOME = self.old_home
        shutil.rmtree(self.temp_dir)

    def test_hermes_skills_in_block_string(self):
        """Test that install_hermes is fooled by 'skills:' inside a block string."""
        hermes_dir = os.path.join(self.temp_dir, ".hermes")
        os.makedirs(hermes_dir, exist_ok=True)
        config_path = os.path.join(hermes_dir, "config.yaml")

        # config.yaml where skills: is part of a text description block
        adversarial_yaml = """model:
  default: gemini
description: |
  This is a description of my agent.
  skills:
  - math
  - coding
curator:
  enabled: true
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(adversarial_yaml)

        # Run installation
        install.install_hermes()

        with open(config_path, "r", encoding="utf-8") as f:
            result = f.read()

        # Let's see what happened to result.
        # It should NOT modify the block string description, but let's check if it did.
        print("--- Resulting config.yaml ---")
        print(result)
        print("----------------------------")
        
        # If it matched the 'skills:' in description, it would have inserted external_dirs inside description
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "external_dirs:" in line:
                # The parent line should be 'skills:' at the same indentation level
                # In this adversarial case, it probably inserted it at skills_indent+2 (which is 2+2=4 spaces)
                self.assertTrue(line.startswith("    -") or line.startswith("  external_dirs:"), 
                                "Should have inserted external_dirs correctly")

    def test_hermes_no_skills_section(self):
        """Test that install_hermes correctly appends skills section if missing."""
        hermes_dir = os.path.join(self.temp_dir, ".hermes")
        os.makedirs(hermes_dir, exist_ok=True)
        config_path = os.path.join(hermes_dir, "config.yaml")

        simple_yaml = """model:
  default: gemini
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(simple_yaml)

        install.install_hermes()

        with open(config_path, "r", encoding="utf-8") as f:
            result = f.read()

        self.assertIn("skills:", result)
        self.assertIn("external_dirs:", result)

if __name__ == "__main__":
    unittest.main()
