## Challenge Summary

**Overall risk assessment**: HIGH

The installation script is well-designed and functions correctly when run locally within the repository. However, the remote download fallback mechanism (designed to support installation via stdin from outside the repository) fails due to the remote repository URL returning a `404 Not Found` error.

## Challenges

### [High] Challenge 1: Failed Stdin Installation via Remote Fallback

- **Assumption challenged**: The script assumes that the repository `global-unch/gunch-skill` and the target file `SKILL.md` are publicly hosted on GitHub at `https://raw.githubusercontent.com/global-unch/gunch-skill/main/SKILL.md` and accessible without authentication.
- **Attack scenario**: A user attempts to install the skill via stdin (`cat install.py | python3`) from outside the cloned repository directory (e.g., from `/tmp` or another folder).
- **Blast radius**: The installation fails completely. The script prints a download failure error and exits with code 1 without setting up any of the 6 target environments.
- **Mitigation**: Update the URL to target the correct public repository/branch name, or ensure that the repository/branch is public and contains the `SKILL.md` file before releasing the script.

### [Medium] Challenge 2: Fragile YAML Injector in `install_hermes`

- **Assumption challenged**: The custom regex-based parser assumes `skills:` or `external_dirs:` is not defined inline as `skills: []` or commented out.
- **Attack scenario**: A user has a `~/.hermes/config.yaml` file with `skills: []` or comment lines imitating the structure.
- **Blast radius**: If the config has `skills: []`, the script appends indented lines under it, creating invalid YAML formatting that corrupts the configuration file.
- **Mitigation**: Use a python YAML library or perform safer string matching to ensure inline list configurations are fully handled/replaced.

## Stress Test Results

- **Scenario 1**: Run `python3 install.py` from repository root directory.
  - *Expected behavior*: Correctly parses local `SKILL.md` and sets up all 6 environments.
  - *Actual behavior*: Successfully parsed and installed Gunch in all 6 target environments.
  - *Status*: PASS
- **Scenario 2**: Run `cat install.py | python3` from directory with `SKILL.md` (local fallback).
  - *Expected behavior*: Resolves local file and completes installation.
  - *Actual behavior*: Successfully installed.
  - *Status*: PASS
- **Scenario 3**: Run `cat install.py | python3` from `/tmp` (remote fallback).
  - *Expected behavior*: Downloads `SKILL.md` from the remote repository and installs it.
  - *Actual behavior*: Failed with `HTTP Error 404: Not Found` from github.
  - *Status*: FAIL

## Unchallenged Areas

- **Other CLIs loading behavior** — We verified `hermes skills list` loads Gunch successfully. We did not run full Claude Code / Opencode / Codex / OpenClaw CLI commands to verify they actively parse the configured files, as these tools are not fully active or interactive in our zsh shell context.
