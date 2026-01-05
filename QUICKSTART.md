# Quick Start Guide

## Installation

### Option 1: CLI Only (Recommended for scripts)
```bash
# No installation needed - just run
python3 ccbackup.py

# View all options
python3 ccbackup.py --help
```

### Option 2: With TUI (Recommended for interactive use)
```bash
# Install dependencies once
pip3 install -r requirements.txt

# Run the TUI
python3 ccbackup_tui.py
```

## Common Tasks

### 1. Quick Backup
```bash
# CLI
python3 ccbackup.py

# TUI
python3 ccbackup_tui.py
# Click "Backup" or press 'b'
```

### 2. Backup with Sanitization (Safe for sharing)
```bash
# CLI
python3 ccbackup.py --sanitize

# TUI
python3 ccbackup_tui.py
# Toggle "Sanitize secrets" on
# Click "Backup"
```

### 3. Check What Will Be Backed Up
```bash
# CLI
python3 ccbackup.py --list

# TUI
python3 ccbackup_tui.py
# Click "List" or press 'l'
```

### 4. Scan for Sensitive Information
```bash
# CLI
python3 ccbackup.py --scan

# TUI
python3 ccbackup_tui.py
# Click "Scan" or press 's'
```

### 5. Full Backup (including history)
```bash
# CLI
python3 ccbackup.py --include-history

# TUI
python3 ccbackup_tui.py
# Toggle "Include history" on
# Click "Backup"
```

## Machine Migration

### Step 1: Backup on Old Machine
```bash
# Create a sanitized backup with history
python3 ccbackup.py --sanitize --include-history

# Find the backup file
ls backups/

# Example: backups/ccbackup_MBP16_nocoo_20260106_073855.zip
```

### Step 2: Transfer to New Machine
```bash
# Copy the ZIP file to new machine
# Via cloud storage, USB, or network
```

### Step 3: Extract on New Machine
```bash
# Extract to a temporary location
mkdir -p ~/ccbackup_restore
unzip ~/Downloads/ccbackup_*.zip -d ~/ccbackup_restore

# Review the contents
cat ~/ccbackup_restore/manifest.json
```

### Step 4: Manual Restore
```bash
# 1. Restore global prompts
cp ~/ccbackup_restore/CLAUDE.md ~/.claude/

# 2. Restore settings (update API token!)
# Edit and copy the settings file
nano ~/ccbackup_restore/settings.json
# Update ANTHROPIC_AUTH_TOKEN with your new token
cp ~/ccbackup_restore/settings.json ~/.claude/

# 3. Restore skills
cp -r ~/ccbackup_restore/skills/* ~/.claude/skills/

# 4. (Optional) Restore plugins configuration
# Note: Plugins will auto-download, just restore the list
cp ~/ccbackup_restore/plugins/installed_plugins.json ~/.claude/plugins/
```

## TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `b` | Start backup |
| `s` | Scan for sensitive info |
| `l` | List backup contents |
| `d` | Toggle dark mode |
| `q` | Quit application |

## Understanding the Output

### Backup File Name
```
ccbackup_<hostname>_<username>_<timestamp>.zip
         └─ Machine name
                      └─ Login user
                                   └─ YYYYMMDD_HHMMSS
```

### Manifest.json
Contains metadata about your backup:
- `hostname`: Machine where backup was created
- `username`: User who created it
- `platform`: Operating system (Darwin, Linux, Windows)
- `sanitized`: Whether secrets were replaced
- `include_history`: Whether session data was included

### Output Locations
- **Backups**: `./backups/` directory
- **Manifest**: Inside each ZIP file as `manifest.json`
- **Logs**: Displayed in TUI or terminal

## Troubleshooting

### "backups directory not found"
→ First run creates it automatically. If permission denied, check folder permissions.

### "Claude directory not found"
→ Ensure Claude Code CLI is installed and ~/.claude exists.

### Backup size is large
→ History data (~30MB) adds to size. Use `--include-history` only when needed.

### TUI won't start
→ Install Textual: `pip3 install -r requirements.txt`

### Sensitive info shows up anyway
→ Use `--sanitize` flag to mask API tokens before sharing.

## Tips

1. **Before Migration**: Run `--scan` first to see what sensitive data exists
2. **Sharing Backups**: Always use `--sanitize` mode
3. **Regular Backups**: Useful for syncing settings between machines
4. **Version Control**: Check manifest.json to confirm what's backed up

## Need Help?

```bash
# See all CLI options
python3 ccbackup.py --help

# In TUI, use keyboard shortcuts
# Output log shows detailed progress and errors
```
