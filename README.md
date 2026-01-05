# Claude Code Backup Tool (ccbackup)

A Python utility to backup and restore Claude Code configuration files for machine migration.

## Features

- 🎯 **Backup Core Config**: CLAUDE.md, settings.json, skills, plugins
- 🔐 **Sensitive Data Handling**: Detect and sanitize API tokens and secrets
- 📦 **Smart Naming**: Backups include hostname, username, and timestamp
- 💾 **Optional History**: Include command history and session data
- 🖥️ **TUI Interface**: Beautiful terminal UI for easy interaction (with Textual)
- 🔍 **Scan Mode**: Preview sensitive information before backup
- 🎨 **List Mode**: See what would be backed up

## Installation

### Basic (CLI only)
```bash
# No external dependencies needed
python3 ccbackup.py --help
```

### With TUI
```bash
# Install Textual framework
pip3 install -r requirements.txt

# Run TUI version
python3 ccbackup_tui.py
```

## Usage

### Command Line Interface

```bash
# Basic backup (core config only)
python3 ccbackup.py

# Include history data (larger file)
python3 ccbackup.py --include-history

# Sanitize sensitive information (replace with placeholders)
python3 ccbackup.py --sanitize

# Scan for sensitive information first
python3 ccbackup.py --scan

# Preview backup contents
python3 ccbackup.py --list

# Specify custom output path
python3 ccbackup.py -o ~/backups/my_backup.zip
```

### Terminal User Interface (TUI)

```bash
python3 ccbackup_tui.py
```

**Keyboard Shortcuts:**
- `q` - Quit
- `b` - Start backup
- `s` - Scan for sensitive info
- `l` - List contents
- `d` - Toggle dark mode

**UI Elements:**
- **Options Panel**: Toggle sanitize and history options
- **System Info**: Shows hostname, username, and source directory
- **Output Log**: Real-time backup progress and messages
- **Progress Bar**: Visual feedback during backup
- **Action Buttons**: Scan, Backup, List, Quit

## Backup Output

Backups are saved to `./backups/` with format:
```
ccbackup_<hostname>_<username>_<YYYYMMDD_HHMMSS>.zip
```

Example:
```
backups/ccbackup_MBP16M426LZ_nocoo_20260106_073855.zip
```

### Manifest File

Each backup includes a `manifest.json` with metadata:
```json
{
  "version": "1.0.0",
  "created_at": "2026-01-06T07:38:55.462063",
  "hostname": "MBP16M426LZ",
  "username": "nocoo",
  "platform": "Darwin",
  "sanitized": true,
  "include_history": false,
  "source_dir": "/Users/nocoo/.claude",
  "contents": {
    "core": ["CLAUDE.md", "settings.json", "skills/"],
    "plugins": ["plugins/installed_plugins.json", "plugins/known_marketplaces.json"]
  }
}
```

## What Gets Backed Up

### Core Configuration (Always)
- `CLAUDE.md` - Global prompts and instructions
- `settings.json` - User settings (model, plugins, env vars)
- `skills/` - Custom skills directory
- `plugins/installed_plugins.json` - Installed plugins list
- `plugins/known_marketplaces.json` - Marketplace configuration

### Optional (with --include-history)
- `history.jsonl` - Command history (~75 KB)
- `projects/` - Session history (~30+ MB)

### Not Backed Up (Cached/Temporary)
- `debug/` - Debug logs
- `file-history/` - File modification history
- `plugins/cache/` - Plugin cache (re-downloaded automatically)
- Shell snapshots and telemetry

## Sensitive Information Handling

The tool detects and can sanitize:
- `ANTHROPIC_AUTH_TOKEN` (API authentication)
- `bark_key` (Notification service)
- Other API keys and secrets

**Modes:**
1. **Full Backup** - Keeps all data (default, secure it!)
2. **Sanitized Backup** - Replaces secrets with `<YOUR_KEY>` placeholders

Use `--sanitize` when sharing backups or for migration prep.

## Machine Migration Workflow

1. **On old machine:**
   ```bash
   python3 ccbackup.py --sanitize --include-history
   # Transfer the ZIP file to new machine
   ```

2. **On new machine:**
   ```bash
   # Extract the ZIP
   unzip backups/ccbackup_*.zip -d ~/.claude_backup

   # Manually restore:
   # - Copy CLAUDE.md to ~/.claude/
   # - Copy skills/ to ~/.claude/
   # - Update settings.json with your new API token
   # - Restore plugins if needed
   ```

## Development

- **Language**: Python 3.10+
- **Dependencies**:
  - CLI: None (zero dependencies)
  - TUI: Textual >= 0.40.0
- **Architecture**: Modular functions for easy reuse

## Troubleshooting

### "Claude directory not found"
- Ensure Claude Code is installed
- Check `~/.claude` directory exists

### Backup file not created
- Verify write permissions in `./backups/`
- Check available disk space

### TUI not starting
- Install Textual: `pip3 install -r requirements.txt`
- Check terminal supports TUI (modern terminal on macOS/Linux/Windows)

## License

MIT
