# Gunch Skill Installer

Интеграция базы знаний **Gunch** в ваши любимые агентные IDE и CLI-среды. 

Этот репозиторий позволяет установить Gunch Skill во все поддерживаемые агентные платформы за **одну команду** или вручную по таблице путей.

---

## 🚀 Быстрая установка (в одну команду)

Запустите установщик напрямую из репозитория:

```bash
curl -sSL https://raw.githubusercontent.com/global-unch/gunch-skill/main/install.py | python3
```

Скрипт автоматически обнаружит установленные среды и разложит скилл `gunch` по нужным путям, включая настройку внешних директорий и генерацию TOML-команд.

---

## 📋 Таблица ручной установки

Если вы предпочитаете ручную установку, скопируйте `SKILL.md` (или сгенерируйте TOML для Codex) по следующим путям:

| Агентная IDE / CLI | Локальный путь для установки | Формат файла | Примечание |
| :--- | :--- | :--- | :--- |
| **Antigravity** | `~/.agents/skills/gunch/SKILL.md` | Markdown | Ссылка/копия `SKILL.md` |
| **Claude Code** | `~/.claude/skills/gunch/SKILL.md` | Markdown | Симлинк на глобальную папку |
| **Codex** | `~/.codex/commands/gunch.toml` | TOML | Поля `description` и `prompt` |
| **Hermes Agent** | `~/.hermes/skills/gunch/SKILL.md` | Markdown | И добавление пути в `external_dirs` в `config.yaml` |
| **Opencode** | `~/.config/opencode/skills/gunch/SKILL.md` | Markdown | Симлинк на глобальную папку |
| **OpenClaw** | `~/.openclaw/workspace/skills/gunch/SKILL.md` | Markdown | Требует `version` и `always: true` в frontmatter |

---

## 🔍 Локальная верификация

Убедитесь, что все CLI-инструменты корректно видят установленный скилл:

### 1. Antigravity / Claude Code / Opencode / OpenClaw
Скилл загружается автоматически при запуске агента. Вы можете проверить наличие файлов:
```bash
ls -l ~/.agents/skills/gunch/SKILL.md
ls -l ~/.claude/skills/gunch/SKILL.md
ls -l ~/.config/opencode/skills/gunch/SKILL.md
ls -l ~/.openclaw/workspace/skills/gunch/SKILL.md
```

### 2. Codex
Проверьте, что сгенерированный TOML-файл содержит описание скилла:
```bash
head -n 5 ~/.codex/commands/gunch.toml
```

### 3. Hermes Agent
Запустите тестовый запрос с флагом предзагрузки скилла `-s gunch`:
```bash
hermes -s gunch chat -q "Проверь загрузку скилла gunch" --yolo
```
В выводе вы должны увидеть успешную инициализацию скилла:
`📚 skill     gunch  0.0s`
