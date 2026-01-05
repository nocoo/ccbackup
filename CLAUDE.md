# Claude Code Backup Tool (ccbackup)

A Python utility to backup and restore Claude Code configuration files for machine migration.

## Project Purpose

This tool helps users backup their Claude Code settings when migrating between machines, including:
- Global prompts (`CLAUDE.md`)
- User settings and API configuration (`settings.json`)
- Custom skills (`skills/`)
- Installed plugins list (`plugins/`)
- Optional: command history and session data

## Usage

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

## Output

Backups are saved to `./backups/` directory with naming format:
```
ccbackup_<hostname>_<username>_<YYYYMMDD_HHMMSS>.zip
```

## Key Files

- `ccbackup.py` - Main backup script (Python 3, zero dependencies)

## Development Notes

- Use Python standard library only (no external dependencies)
- Support both sanitized and full backup modes
- Cross-platform compatible (macOS, Linux, Windows)
