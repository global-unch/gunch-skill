#!/usr/bin/env python3
import os
import sys
import json
import shutil
import re

HOME = os.path.expanduser("~")
SKILL_SOURCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "SKILL.md"))

def log_success(msg):
    print(f"[\033[92mSUCCESS\033[0m] {msg}")

def log_info(msg):
    print(f"[\033[94mINFO\033[0m] {msg}")

def log_warn(msg):
    print(f"[\033[93mWARN\033[0m] {msg}")

def parse_skill_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple markdown frontmatter parser
    if not (content.startswith("---\n") or content.startswith("---\r\n")):
        return {"name": "gunch", "description": "", "body": content}
        
    parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm_content = parts[1].strip()
        body = parts[2].strip()
        
        fm = {}
        for line in fm_content.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip().strip("'\"")
        return {"name": fm.get("name", "gunch"), "description": fm.get("description", ""), "body": body, "raw_fm": fm_content}
        
    return {"name": "gunch", "description": "", "body": content}

def install_global_agents():
    # 1. Base ~/.agents/skills/gunch
    agents_dir = os.path.join(HOME, ".agents", "skills", "gunch")
    os.makedirs(agents_dir, exist_ok=True)
    target_path = os.path.join(agents_dir, "SKILL.md")
    shutil.copy(SKILL_SOURCE, target_path)
    log_success(f"Installed global skill to {target_path}")

    # Update ~/.agents/.skill-lock.json
    lock_path = os.path.join(HOME, ".agents", ".skill-lock.json")
    lock_data = {"version": 3, "skills": {}, "dismissed": {"findSkillsPrompt": True}}
    if os.path.exists(lock_path):
        try:
            with open(lock_path, "r") as f:
                lock_data = json.load(f)
        except Exception:
            pass

    lock_data["skills"]["gunch"] = {
        "source": "global-unch/gunch-skill",
        "sourceType": "github",
        "sourceUrl": "https://github.com/global-unch/gunch-skill.git",
        "skillPath": "skills/gunch/SKILL.md",
        "installedAt": "2026-06-28T09:30:00.000Z",
        "updatedAt": "2026-06-28T09:30:00.000Z"
    }

    with open(lock_path, "w") as f:
        json.dump(lock_data, f, indent=2)
    log_success(f"Registered Gunch in {lock_path}")

def install_claude():
    # 2. Claude Code ~/.claude/skills/gunch
    claude_skills_dir = os.path.join(HOME, ".claude", "skills")
    os.makedirs(claude_skills_dir, exist_ok=True)
    symlink_path = os.path.join(claude_skills_dir, "gunch")
    
    if os.path.exists(symlink_path) or os.path.islink(symlink_path):
        if os.path.islink(symlink_path):
            os.unlink(symlink_path)
        else:
            shutil.rmtree(symlink_path)
            
    os.symlink(os.path.join(HOME, ".agents", "skills", "gunch"), symlink_path)
    log_success(f"Created Claude Code symlink at {symlink_path}")

def install_codex(parsed):
    # 3. Codex ~/.codex/commands/gunch.toml
    codex_dir = os.path.join(HOME, ".codex", "commands")
    os.makedirs(codex_dir, exist_ok=True)
    toml_path = os.path.join(codex_dir, "gunch.toml")
    
    # Build TOML content
    desc = parsed["description"].replace("\n", " ").strip()
    toml_content = f'description = "{desc}"\nprompt = """\n{parsed["body"]}\n"""\n'
    
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(toml_content)
    log_success(f"Created Codex TOML command at {toml_path}")

def install_hermes():
    # 4. Hermes ~/.hermes/config.yaml external dirs
    hermes_config = os.path.join(HOME, ".hermes", "config.yaml")
    if not os.path.exists(hermes_config):
        log_warn(f"Hermes config not found at {hermes_config}. Skipping Hermes configuration.")
        return
        
    with open(hermes_config, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    skills_section_found = False
    ext_dirs_found = False
    in_skills = False
    
    new_lines = []
    i = 0
    target_dir = os.path.join(HOME, ".agents", "skills")
    
    # Check if target_dir is already there
    config_str = "".join(lines)
    if target_dir in config_str:
        log_info("Hermes external_dirs already contains ~/.agents/skills")
        return

    # Lightweight YAML injection
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        if line.strip().startswith("skills:"):
            in_skills = True
            skills_section_found = True
        elif in_skills and line.strip().startswith("external_dirs:"):
            ext_dirs_found = True
            # Check if it has []
            if "[]" in line:
                # Replace with multiline
                new_lines[-1] = line.replace("[]", "")
            new_lines.append(f"    - {target_dir}\n")
            in_skills = False
        elif in_skills and (line.startswith(" ") or line.startswith("\t")):
            pass
        else:
            in_skills = False
            
        i += 1
        
    if not skills_section_found:
        new_lines.append("\nskills:\n  external_dirs:\n    - " + target_dir + "\n")
    elif not ext_dirs_found:
        # Find skills: and insert external_dirs
        for idx, line in enumerate(new_lines):
            if line.strip().startswith("skills:"):
                new_lines.insert(idx + 1, "  external_dirs:\n    - " + target_dir + "\n")
                break
                
    with open(hermes_config, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    log_success(f"Updated Hermes config.yaml to load global skills directory")

def install_opencode():
    # 5. Opencode ~/.config/opencode/skills/gunch
    opencode_skills_dir = os.path.join(HOME, ".config", "opencode", "skills")
    os.makedirs(opencode_skills_dir, exist_ok=True)
    symlink_path = os.path.join(opencode_skills_dir, "gunch")
    
    if os.path.exists(symlink_path) or os.path.islink(symlink_path):
        if os.path.islink(symlink_path):
            os.unlink(symlink_path)
        else:
            shutil.rmtree(symlink_path)
            
    os.symlink(os.path.join(HOME, ".agents", "skills", "gunch"), symlink_path)
    log_success(f"Created Opencode symlink at {symlink_path}")

def install_openclaw(parsed):
    # 6. OpenClaw ~/.openclaw/workspace/skills/gunch/SKILL.md
    openclaw_skills_dir = os.path.join(HOME, ".openclaw", "workspace", "skills", "gunch")
    os.makedirs(openclaw_skills_dir, exist_ok=True)
    target_path = os.path.join(openclaw_skills_dir, "SKILL.md")
    
    # Merge version and always properties in frontmatter
    raw_fm = parsed.get("raw_fm", "")
    body = parsed.get("body", "")
    
    new_fm = []
    name_found = False
    version_found = False
    always_found = False
    
    for line in raw_fm.split("\n"):
        if line.strip().startswith("name:"):
            name_found = True
        elif line.strip().startswith("version:"):
            version_found = True
        elif line.strip().startswith("always:"):
            always_found = True
        new_fm.append(line)
        
    if not name_found:
        new_fm.append("name: gunch")
    if not version_found:
        new_fm.append("version: 1.0.0")
    if not always_found:
        new_fm.append("always: true")
        
    merged_fm = "\n".join(new_fm)
    merged_content = f"---\n{merged_fm}\n---\n\n{body}\n"
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(merged_content)
    log_success(f"Installed OpenClaw skill to {target_path}")

def main():
    if not os.path.exists(SKILL_SOURCE):
        print(f"ERROR: SKILL.md not found at {SKILL_SOURCE}")
        sys.exit(1)
        
    log_info("Parsing SKILL.md...")
    parsed = parse_skill_md(SKILL_SOURCE)
    
    log_info("Installing Gunch Skill into agent IDEs...")
    
    try:
        install_global_agents()
        install_claude()
        install_codex(parsed)
        install_hermes()
        install_opencode()
        install_openclaw(parsed)
        print("\n\033[92m★ Gunch Skill successfully installed to all IDEs! ★\033[0m")
    except Exception as e:
        print(f"\n\033[91mERROR during installation: {e}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
