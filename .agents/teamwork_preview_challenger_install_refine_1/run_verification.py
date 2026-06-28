import os
import sys
import shutil
import tempfile
import subprocess
import json

WORKSPACE = "/Users/uchebnick/projects/gunch-skill"

def log_test(name, success, msg=""):
    status = "\033[92mPASS\033[0m" if success else "\033[91mFAIL\033[0m"
    print(f"[{status}] {name} {msg}")
    if not success:
        sys.exit(1)

def verify_target_environments():
    print("--- Task 1: Verifying 6 target environments ---")
    
    # Create isolated HOME directory
    verify_home = tempfile.mkdtemp(prefix="gunch_verify_home_")
    env = os.environ.copy()
    env["HOME"] = verify_home

    # 1. Run install.py without Hermes config pre-created
    log_warn_triggered = False
    try:
        proc = subprocess.run(
            [sys.executable, "install.py"],
            env=env,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True
        )
        output = proc.stdout + proc.stderr
        if "Skipping Hermes configuration" in output:
            log_warn_triggered = True
    except Exception as e:
        log_test("Install without Hermes config", False, f"failed: {e}")
    
    log_test("Install warning for missing Hermes config", log_warn_triggered, "Warning printed successfully.")

    # 2. Pre-create Hermes config
    hermes_dir = os.path.join(verify_home, ".hermes")
    os.makedirs(hermes_dir, exist_ok=True)
    hermes_config = os.path.join(hermes_dir, "config.yaml")
    initial_hermes_yaml = "model:\n  default: gemini\n"
    with open(hermes_config, "w") as f:
        f.write(initial_hermes_yaml)

    # 3. Run install.py again with Hermes config present
    try:
        proc = subprocess.run(
            [sys.executable, "install.py"],
            env=env,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True
        )
    except Exception as e:
        log_test("Install with Hermes config", False, f"failed: {e}")

    # Now verify all 6 targets
    # 1. Antigravity
    agents_dir = os.path.join(verify_home, ".agents", "skills", "gunch")
    skill_path = os.path.join(agents_dir, "SKILL.md")
    lock_path = os.path.join(verify_home, ".agents", ".skill-lock.json")
    
    log_test("Antigravity: SKILL.md exists", os.path.isfile(skill_path))
    
    # Read skill-lock.json
    lock_exists = os.path.isfile(lock_path)
    log_test("Antigravity: .skill-lock.json exists", lock_exists)
    if lock_exists:
        with open(lock_path, "r") as f:
            lock_data = json.load(f)
        log_test("Antigravity: .skill-lock.json Gunch registered", "gunch" in lock_data.get("skills", {}))

    # 2. Claude Code
    claude_symlink = os.path.join(verify_home, ".claude", "skills", "gunch")
    is_link = os.path.islink(claude_symlink)
    log_test("Claude Code: Symlink exists", is_link)
    if is_link:
        target = os.readlink(claude_symlink)
        expected_target = os.path.join(verify_home, ".agents", "skills", "gunch")
        log_test("Claude Code: Symlink points to correct destination", target == expected_target, f"(points to {target})")

    # 3. Codex
    codex_toml = os.path.join(verify_home, ".codex", "commands", "gunch.toml")
    log_test("Codex: TOML file exists", os.path.isfile(codex_toml))
    if os.path.isfile(codex_toml):
        with open(codex_toml, "r") as f:
            toml_content = f.read()
        log_test("Codex: TOML has prompt and description", "prompt =" in toml_content and "description =" in toml_content)

    # 4. Hermes Agent
    log_test("Hermes: Config file exists", os.path.isfile(hermes_config))
    if os.path.isfile(hermes_config):
        with open(hermes_config, "r") as f:
            hermes_content = f.read()
        expected_dir = os.path.join(verify_home, ".agents", "skills")
        log_test("Hermes: Config loaded global skills directory", expected_dir in hermes_content)

    # 5. Opencode
    opencode_symlink = os.path.join(verify_home, ".config", "opencode", "skills", "gunch")
    is_opencode_link = os.path.islink(opencode_symlink)
    log_test("Opencode: Symlink exists", is_opencode_link)
    if is_opencode_link:
        target = os.readlink(opencode_symlink)
        expected_target = os.path.join(verify_home, ".agents", "skills", "gunch")
        log_test("Opencode: Symlink points to correct destination", target == expected_target, f"(points to {target})")

    # 6. OpenClaw
    openclaw_skill = os.path.join(verify_home, ".openclaw", "workspace", "skills", "gunch", "SKILL.md")
    log_test("OpenClaw: SKILL.md exists", os.path.isfile(openclaw_skill))
    if os.path.isfile(openclaw_skill):
        with open(openclaw_skill, "r") as f:
            openclaw_content = f.read()
        log_test("OpenClaw: Frontmatter merged with version and always", 
                 "version: 1.0.0" in openclaw_content and "always: true" in openclaw_content)

    # Clean up temp home directory
    shutil.rmtree(verify_home)

def verify_stdin_fallback():
    print("\n--- Task 2: Verifying stdin fallback execution ---")
    
    # Create isolated HOME directory
    verify_home = tempfile.mkdtemp(prefix="gunch_verify_stdin_home_")
    env = os.environ.copy()
    env["HOME"] = verify_home

    # Run from a different directory (e.g. temporary directory) where SKILL.md is not present
    temp_run_dir = tempfile.mkdtemp()
    
    # Simulate cat install.py | python3
    with open(os.path.join(WORKSPACE, "install.py"), "r") as f:
        install_script_content = f.read()

    try:
        proc = subprocess.run(
            [sys.executable],
            input=install_script_content,
            env=env,
            cwd=temp_run_dir,
            capture_output=True,
            text=True,
            check=True
        )
        output = proc.stdout + proc.stderr
        
        # Verify it didn't print "Fetching from..." which indicates falling back to remote url
        log_test("Stdin: Did not attempt raw GitHub fetch", "Fetching from https://raw.githubusercontent.com" not in output, 
                 f"Output had: {output}")
        
        # Verify it successfully installed to the isolated home
        agents_dir = os.path.join(verify_home, ".agents", "skills", "gunch")
        skill_path = os.path.join(agents_dir, "SKILL.md")
        log_test("Stdin: SKILL.md successfully resolved and installed", os.path.isfile(skill_path))
        
    except Exception as e:
        log_test("Stdin execution fallback", False, f"failed: {e}")
    finally:
        shutil.rmtree(verify_home)
        shutil.rmtree(temp_run_dir)

def verify_stress_test():
    print("\n--- Task 3: Verifying stress_test.py ---")
    try:
        proc = subprocess.run(
            [sys.executable, "stress_test.py"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True
        )
        log_test("Stress tests passed", "OK" in proc.stderr or "OK" in proc.stdout, proc.stderr)
    except Exception as e:
        log_test("Stress tests run", False, f"failed: {e}")

if __name__ == "__main__":
    verify_target_environments()
    verify_stdin_fallback()
    verify_stress_test()
    print("\n\033[92m★ All installation script verifications passed successfully! ★\033[0m")
