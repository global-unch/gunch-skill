## Challenge Summary

**Overall risk assessment**: MEDIUM

## Challenges

### [High] Challenge 1: YAML parsing failure with trailing spaces on frontmatter delimiter line

- **Assumption challenged**: The script assumes that the YAML frontmatter section always starts exactly with `---` followed immediately by a newline (`---\n` or `---\r\n`).
- **Attack scenario**: A skill file containing a trailing space on the first line (e.g. `--- ` instead of `---`) will fail the opening check `content.startswith("---\n")`. This causes the parser to treat the entire frontmatter as the markdown body and set the name to the default `"gunch"` with an empty description.
- **Blast radius**: Broken metadata in the installed command files (e.g., Codex TOML command description is empty, and the frontmatter block leaks into the Codex command body).
- **Mitigation**: Strip whitespace from the first line or use a regular expression check matching `^---\s*$` to identify the frontmatter start, rather than a strict prefix match.

### [High] Challenge 2: Broken Codex TOML structure when skill body contains Python docstrings or triple double-quotes (`"""`)

- **Assumption challenged**: The script assumes the skill markdown body never contains triple double-quotes (`"""`).
- **Attack scenario**: If the Markdown body contains a code snippet with Python triple double-quotes, the generated `~/.codex/commands/gunch.toml` will contain unescaped nested triple double-quotes. This invalidates the TOML syntax, causing the Codex command loader to crash.
- **Blast radius**: Codex environment command parsing failure, preventing Gunch command execution.
- **Mitigation**: Escape triple double-quotes `"""` in the body or use alternative TOML multi-line string delimiters.

### [Medium] Challenge 3: Invalid YAML generation in Hermes config when `external_dirs` is defined as an inline flow sequence

- **Assumption challenged**: The script assumes `external_dirs:` in `~/.hermes/config.yaml` is either absent, defined using standard YAML block format, or is exactly an empty list `[]`.
- **Attack scenario**: If the user's `config.yaml` contains `external_dirs: [/some/path]` (flow style array), the script does not match `[]`, so it does not replace it. It then appends `    - ~/.agents/skills` below it at a block level. This creates a syntactically invalid hybrid flow/block sequence.
- **Blast radius**: Broken Hermes configuration file, preventing Hermes from launching or parsing its config.
- **Mitigation**: Parse `config.yaml` using a proper YAML parser or check if the line contains a flow-style array matching `\[.*\]` and append/convert accordingly.

## Stress Test Results

- Trailing spaces on frontmatter start delimiter (`--- `) → Parse name and description successfully → Parsed name defaults to 'gunch', description is empty → FAIL
- Skill body containing triple double-quotes (`"""`) → Generate valid Codex TOML command → TOML generated is syntactically invalid → FAIL
- Hermes config contains `external_dirs: [/some/path]` → Add target directory without breaking YAML formatting → Appends block sequence item to flow list, breaking YAML → FAIL
- Missing `skills:` section in Hermes config → Automatically insert `skills:` and `external_dirs:` block → Successfully appends new configuration blocks → PASS
- Indented `skills:` inside text block string in Hermes config → Ignore indented occurrence and append top-level skills block → Correctly appends top-level section without modifying block string → PASS

## Unchallenged Areas

- Global skill copy permission issues — reason not challenged: standard out-of-scope system permission restrictions.
