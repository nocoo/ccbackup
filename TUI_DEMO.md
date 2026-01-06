# Interactive TUI - Questionary + Rich

Simple, clean interactive backup wizard inspired by Ink's React component model.

## Architecture

```
┌─────────────────────────────────────────┐
│    Claude Code Backup Tool              │
│    Interactive backup wizard            │
├─────────────────────────────────────────┤
│                                         │
│  Host: MBP16M426LZ                      │
│  User: nocoo                            │
│                                         │
│  🔧 Backup Options                      │
│                                         │
│  ? Sanitize secrets (replace with       │
│    placeholders)? (y/n) [n]: _          │
│                                         │
│  ? Include history and session data?    │
│    (y/n) [n]: _                         │
│                                         │
│  Sanitize: ❌ No                        │
│  History:  ✅ Yes                       │
│  Output:   ./backups/                   │
│                                         │
│  ? Start backup? (Y/n): _               │
│                                         │
│  ⏳ Backing up...                       │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │ ✅ Backup Completed              │   │
│  │                                  │   │
│  │ ccbackup_MBP16_nocoo_20260106... │   │
│  │ 45 KB                            │   │
│  └──────────────────────────────────┘   │
│                                         │
│  Done!                                  │
│                                         │
└─────────────────────────────────────────┘
```

## UI Flow

1. **Banner** - Welcome message and app title
2. **System Info** - Show hostname and username
3. **Options** - Ask for backup preferences
4. **Summary** - Show what will be backed up
5. **Confirm** - Ask to start backup
6. **Progress** - Show "Backing up..." status
7. **Result** - Show success or error with details

## Features

✨ **Simple & Clean**
- Question-based interface (like Ink)
- No complex layouts
- Easy to follow

🎨 **Beautiful Output**
- Rich panels and tables
- Colored text and emojis
- Professional appearance

⚡ **Fast & Responsive**
- Minimal dependencies
- Quick startup
- No loading delays

🤖 **Intelligent Defaults**
- Auto-enter on confirmations
- Sensible defaults (No/No)
- Easy to skip with Enter

## Comparison: Questionary + Rich vs Textual vs Ink

| Feature | Questionary + Rich | Textual | Ink |
|---------|-------------------|---------|-----|
| Complexity | Low ✅ | High | Medium |
| Code lines | ~100 | 350+ | Various |
| Learning curve | Easy ✅ | Steep | Medium |
| Dependencies | 2 light ✅ | 1 heavy | Many |
| Flexibility | High ✅ | Very high | High |
| Use case | **Simple CLI** ✅ | Complex TUI | Rich UIs |
| Python support | ✅ | ✅ | ❌ |

## Why Questionary + Rich?

1. **Inspired by Ink** - Question/answer flow like React components
2. **Simple to code** - Just plain Python functions
3. **Clean output** - Rich library handles all styling
4. **Easy to maintain** - No complex state management
5. **Lightweight** - Two small, focused libraries
6. **Perfect fit** - For this use case (wizard-style backup)

## Code Structure

```python
# 1. Show banner (display only)
show_banner()

# 2. Show system info (display only)
show_system_info()

# 3. Ask options (interactive)
sanitize, include_history = ask_options()

# 4. Show summary (display only)
confirm_backup(sanitize, include_history)

# 5. Do backup (blocking operation)
perform_backup(sanitize, include_history)
```

No state management, no event handlers, just linear flow!

## Usage

```bash
# Run interactive backup
python3 ccbackup_tui.py

# Or with the CLI
python3 ccbackup.py --sanitize --include-history
```

## Keyboard Usage

```
Space / y     → Yes
n / Backspace → No
Enter         → Confirm / Use default
Ctrl+C        → Cancel / Exit
```

## Example Interaction

```bash
$ python3 ccbackup_tui.py

┌─────────────────────────────────────┐
│  Claude Code Backup Tool            │
│  Interactive backup wizard          │
└─────────────────────────────────────┘

Host: MBP16M426LZ
User: nocoo

🔧 Backup Options

? Sanitize secrets (replace with placeholders)? (y/n) [n]: n
? Include history and session data? (y/n) [n]: y

Sanitize: ❌ No
History:  ✅ Yes
Output:   ./backups/

? Start backup? (Y/n): y

⏳ Backing up...

┌──────────────────────────────────────┐
│ ✅ Backup Completed                  │
│                                      │
│ ccbackup_MBP16M426LZ_nocoo_20260106  │
│ 45 KB                                │
└──────────────────────────────────────┘

⚠️  Backup contains sensitive information - store securely!

Done!
```

## Files Backed Up

Each backup includes:
- `CLAUDE.md` - Global prompts
- `settings.json` - User config
- `skills/` - Custom skills
- `plugins/` - Plugin info
- (optional) `history.jsonl` - Command history
- (optional) `projects/` - Session data
- `manifest.json` - Backup metadata

## Tips

1. **Fastest way**: Just press Enter 3 times → creates basic backup
2. **Complete backup**: Answer `y` to history question
3. **Safe to share**: Enable sanitize option before backing up to cloud
4. **Check output**: Look in `./backups/` for the ZIP file

## Troubleshooting

| Issue | Solution |
|-------|----------|
| TUI won't start | `pip3 install -r requirements.txt` |
| No backup output | Check `./backups/` directory exists |
| Backup failed | Run with CLI: `python3 ccbackup.py --list` |
| Terminal garbled | Resize terminal or clear screen |

## Benefits Over Previous Versions

✅ **vs Textual:**
- 50% less code
- Simpler to understand
- No complex layouts
- Lighter dependencies

✅ **vs Ink (TypeScript):**
- Same question-based flow
- Pure Python
- Minimal dependencies
- Easy to maintain

✅ **vs Raw CLI:**
- More user-friendly
- Better visual feedback
- Interactive prompts
- Professional appearance
