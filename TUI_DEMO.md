# Simple TUI Interface

A minimal, centered dialog-style interface for Claude Code backup.

## UI Layout

```
┌─────────────────────────────────────────┐
│    Claude Code Backup Tool             │
├─────────────────────────────────────────┤
│                                         │
│        🔧 Backup Options               │
│                                         │
│         MBP16M426LZ / nocoo             │
│                                         │
│   ☐ Sanitize secrets                   │
│                                         │
│   ☐ Include history                    │
│                                         │
│   ┌─────────────────────────┐           │
│   │  💾 Backup              │           │
│   ├─────────────────────────┤           │
│   │  ❌ Quit                │           │
│   └─────────────────────────┘           │
│                                         │
│   ✅ Saved: ccbackup_*.zip (45KB)       │
│                                         │
└─────────────────────────────────────────┘

Keyboard: b=Backup  d=Dark  q=Quit
```

## Features

- 🎯 **Centered window** - Easy to focus on
- ⚙️ **Two simple options**:
  - Sanitize secrets (replace with placeholders)
  - Include history (larger backup with session data)
- 🔲 **Toggle switches** - Just click or use keyboard
- 💾 **Action buttons** - Backup and Quit
- 📊 **Status display** - Shows progress or result
- 🌙 **Dark mode** - Press 'd' to toggle

## Usage

```bash
# Start the TUI
python3 ccbackup_tui.py

# Or with pipe
python3 ccbackup_tui.py 2>/dev/null
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `b` | Start backup |
| `d` | Toggle dark mode |
| `q` | Quit app |
| `Tab` | Navigate between options |
| `Space` | Toggle switch / Press button |
| `Enter` | Press focused button |

## What Each Option Does

### Sanitize Secrets
- **Off** (default): Full backup with all settings
- **On**: Replaces API tokens with `<YOUR_KEY>` placeholders
- **Use case**: Safe to share or back up to cloud

### Include History
- **Off** (default): ~20 KB backup (fast)
- **On**: ~30 MB backup (includes session history)
- **Use case**: Complete migration between machines

## Output

After clicking "Backup":

✅ **Success:**
```
✅ Saved: ccbackup_MBP16_nocoo_20260106_073855.zip (45KB)
```

❌ **Error:**
```
❌ Failed: Cannot create backup directory
```

⏳ **In Progress:**
```
⏳ Backing up...
```

## Backup Location

All backups go to: `./backups/`

Example:
```
backups/
└── ccbackup_MBP16M426LZ_nocoo_20260106_073855.zip
```

## File Format

Inside the ZIP file:
```
ccbackup_*.zip
├── manifest.json          # Metadata
├── CLAUDE.md             # Global prompts
├── settings.json         # User config (with or without secrets)
├── skills/               # Custom skills
│   ├── task-notifier/
│   └── planning-with-files/
├── plugins/
│   ├── installed_plugins.json
│   └── known_marketplaces.json
└── (optional)
    ├── history.jsonl     # Command history
    └── projects/         # Session history
```

## Tips

1. **First time?** Leave options unchecked, just click "Backup"
2. **Sharing backup?** Enable "Sanitize secrets" first
3. **Moving machines?** Enable "Include history" for complete migration
4. **Large backup?** "Include history" adds ~30 MB - only use if needed
5. **Check contents:** View `manifest.json` inside the ZIP for details

## Troubleshooting

- **Window not centered?** Try resizing terminal
- **Text cut off?** Make terminal wider/taller
- **Backup fails?** Check `./backups/` directory exists and is writable
- **Can't see output?** Status will show at bottom of window

## Comparison: TUI vs CLI

| Feature | TUI | CLI |
|---------|-----|-----|
| Easy to use | ✅ | ⚙️ |
| Fast | ✅ | ✅ |
| Dependencies | Textual | None |
| Scripting | ❌ | ✅ |
| Automation | ❌ | ✅ |
| Pretty output | ✅ | ⚙️ |

Choose TUI for interactive use, CLI for automation/scripts.
