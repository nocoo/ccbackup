# Claude Code Backup Tool (ccbackup)

A Python utility to backup and restore Claude Code configuration files for machine migration.

## Project Purpose

This tool helps users backup their Claude Code settings when migrating between machines, including:
- Global prompts (`CLAUDE.md`)
- User settings and API configuration (`settings.json`)
- Custom skills (`skills/`)
- Installed plugins list (`plugins/`)
- Optional: command history and session data

Provides both CLI and TUI interfaces for flexibility.

## Usage

### CLI (Zero Dependencies)

```bash
# Basic backup (core config only)
python3 ccbackup.py

# Include history data
python3 ccbackup.py --include-history

# Sanitize sensitive information (API tokens, keys)
python3 ccbackup.py --sanitize

# Scan for sensitive information
python3 ccbackup.py --scan

# Preview backup contents
python3 ccbackup.py --list
```

### TUI (Questionary + Rich)

```bash
pip3 install -r requirements.txt
python3 ccbackup_tui.py
```

Interactive wizard-style interface inspired by Ink (React TUI):
- 📝 Question-based interaction
- 🎨 Beautiful Rich formatting
- 🔧 Simple backup options (Sanitize, Include history)
- 📊 System info display
- ⏳ Progress feedback
- ✅ Result confirmation

## Output

Backups are saved to `./backups/` directory with naming format:
```
ccbackup_<hostname>_<username>_<YYYYMMDD_HHMMSS>.zip
```

Includes `manifest.json` with backup metadata (hostname, username, timestamp, platform).

## Key Files

- `ccbackup.py` - Core backup logic (Python 3, zero external dependencies)
- `ccbackup_tui.py` - Terminal UI interface (requires Textual >= 0.40.0)
- `requirements.txt` - TUI dependencies
- `README.md` - Comprehensive usage guide

## Development Notes

- Core library uses only Python standard library (no external dependencies)
- TUI uses Textual framework for cross-platform terminal UI
- Modular design allows easy reuse of backup functions
- Support both sanitized and full backup modes
- Cross-platform compatible (macOS, Linux, Windows)
- All backups include sensitive data detection and optional sanitization
