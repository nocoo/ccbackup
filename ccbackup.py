#!/usr/bin/env python3
"""
Claude Code Configuration Backup Tool

Backs up Claude Code configuration files including:
- CLAUDE.md (global prompts)
- settings.json (user settings)
- skills/ (custom skills)
- plugins/installed_plugins.json (installed plugins)
- plugins/known_marketplaces.json (marketplace config)

Optional:
- history.jsonl (command history)
- projects/ (session history)
"""

import argparse
import getpass
import json
import os
import platform
import re
import shutil
import socket
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


# Default backup directory
BACKUP_DIR = Path("./backups")


# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log_info(msg: str) -> None:
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def log_success(msg: str) -> None:
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_warning(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def log_error(msg: str) -> None:
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def log_section(msg: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}📦 {msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'─' * 50}{Colors.RESET}")


# Patterns to detect sensitive information
SENSITIVE_PATTERNS = [
    # API tokens and keys
    (r'"ANTHROPIC_AUTH_TOKEN"\s*:\s*"([^"]+)"', "ANTHROPIC_AUTH_TOKEN"),
    (r'"ANTHROPIC_API_KEY"\s*:\s*"([^"]+)"', "ANTHROPIC_API_KEY"),
    (r'"api_key"\s*:\s*"([^"]+)"', "api_key"),
    (r'"apiKey"\s*:\s*"([^"]+)"', "apiKey"),
    (r'"bark_key"\s*:\s*"([^"]+)"', "bark_key"),
    (r'"token"\s*:\s*"([^"]+)"', "token"),
    (r'"secret"\s*:\s*"([^"]+)"', "secret"),
    # Generic patterns for sk-ant-* tokens
    (r'sk-ant-[a-zA-Z0-9\-_]+', "anthropic_token"),
]


def get_claude_dir() -> Path:
    """Get the .claude directory path."""
    home = Path.home()
    claude_dir = home / ".claude"
    return claude_dir


def get_machine_info() -> tuple[str, str]:
    """
    Get hostname and username for backup naming.
    Returns (hostname, username) tuple.
    """
    # Get hostname (machine name)
    try:
        hostname = socket.gethostname()
        # Clean up hostname (remove domain suffix if present)
        hostname = hostname.split(".")[0]
    except Exception:
        hostname = platform.node() or "unknown"

    # Get username
    try:
        username = getpass.getuser()
    except Exception:
        username = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    # Sanitize for filename (remove special characters)
    hostname = re.sub(r"[^\w\-]", "_", hostname)
    username = re.sub(r"[^\w\-]", "_", username)

    return hostname, username


def get_default_backup_path() -> Path:
    """
    Generate default backup file path.
    Format: backups/ccbackup_<hostname>_<username>_<YYYYMMDD_HHMMSS>.zip
    """
    hostname, username = get_machine_info()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ccbackup_{hostname}_{username}_{timestamp}.zip"

    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    return BACKUP_DIR / filename


def detect_sensitive_in_file(file_path: Path) -> list[tuple[str, str]]:
    """
    Detect sensitive information in a file.
    Returns list of (pattern_name, matched_value) tuples.
    """
    if not file_path.exists() or not file_path.is_file():
        return []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return []

    findings = []
    for pattern, name in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, content)
        for match in matches:
            # Only report if the match looks like a real secret (not a placeholder)
            if match and not match.startswith("<") and not match.endswith(">"):
                findings.append((name, match))

    return findings


def sanitize_content(content: str) -> str:
    """Replace sensitive information with placeholders."""
    sanitized = content

    for pattern, name in SENSITIVE_PATTERNS:
        def replace_match(m):
            full_match = m.group(0)
            if name == "anthropic_token":
                # For standalone tokens, replace the entire match
                return f"<YOUR_{name.upper()}>"
            else:
                # For key-value patterns, preserve the key
                return full_match.replace(m.group(1), f"<YOUR_{name.upper()}>")

        sanitized = re.sub(pattern, replace_match, sanitized)

    return sanitized


def scan_for_sensitive(claude_dir: Path) -> dict[str, list[tuple[str, str]]]:
    """
    Scan the .claude directory for sensitive information.
    Returns dict mapping file paths to their sensitive findings.
    """
    results = {}

    # Files to scan
    files_to_scan = [
        claude_dir / "settings.json",
        claude_dir / "CLAUDE.md",
    ]

    # Also scan skills config files
    skills_dir = claude_dir / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                config_file = skill_dir / "config.json"
                if config_file.exists():
                    files_to_scan.append(config_file)

    for file_path in files_to_scan:
        if file_path.exists():
            findings = detect_sensitive_in_file(file_path)
            if findings:
                results[str(file_path.relative_to(claude_dir))] = findings

    return results


def copy_file_with_sanitize(
    src: Path, dest: Path, sanitize: bool = False
) -> None:
    """Copy a file, optionally sanitizing sensitive content."""
    dest.parent.mkdir(parents=True, exist_ok=True)

    if sanitize and src.suffix in [".json", ".md", ".txt", ".jsonl"]:
        try:
            content = src.read_text(encoding="utf-8")
            sanitized = sanitize_content(content)
            dest.write_text(sanitized, encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            # Fall back to binary copy
            shutil.copy2(src, dest)
    else:
        shutil.copy2(src, dest)


def copy_directory_with_sanitize(
    src: Path, dest: Path, sanitize: bool = False
) -> None:
    """Copy a directory recursively, optionally sanitizing sensitive content."""
    if not src.exists() or not src.is_dir():
        return

    dest.mkdir(parents=True, exist_ok=True)

    for item in src.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src)
            dest_file = dest / rel_path
            copy_file_with_sanitize(item, dest_file, sanitize)


def create_backup(
    output_path: Path,
    include_history: bool = False,
    sanitize: bool = False,
) -> tuple[bool, str]:
    """
    Create a backup of Claude Code configuration.

    Args:
        output_path: Path to save the backup ZIP file
        include_history: Whether to include history.jsonl and projects/
        sanitize: Whether to sanitize sensitive information

    Returns:
        Tuple of (success, message)
    """
    claude_dir = get_claude_dir()

    if not claude_dir.exists():
        return False, f"Claude directory not found: {claude_dir}"

    # Create temporary directory for backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = Path(f"/tmp/ccbackup_{timestamp}")

    try:
        temp_dir.mkdir(parents=True, exist_ok=True)

        log_section("Core Configuration")

        # 1. CLAUDE.md
        claude_md = claude_dir / "CLAUDE.md"
        if claude_md.exists():
            copy_file_with_sanitize(
                claude_md, temp_dir / "CLAUDE.md", sanitize
            )
            log_success("CLAUDE.md")
        else:
            log_warning("CLAUDE.md not found")

        # 2. settings.json
        settings = claude_dir / "settings.json"
        if settings.exists():
            copy_file_with_sanitize(
                settings, temp_dir / "settings.json", sanitize
            )
            log_success("settings.json")
        else:
            log_warning("settings.json not found")

        # 3. skills/
        skills_dir = claude_dir / "skills"
        if skills_dir.exists() and any(skills_dir.iterdir()):
            copy_directory_with_sanitize(
                skills_dir, temp_dir / "skills", sanitize
            )
            skill_count = len(
                [d for d in skills_dir.iterdir() if d.is_dir()]
            )
            log_success(f"skills/ ({skill_count} skills)")
        else:
            log_warning("skills/ not found or empty")

        log_section("Plugin Configuration")

        # 4. plugins/installed_plugins.json
        installed_plugins = claude_dir / "plugins" / "installed_plugins.json"
        if installed_plugins.exists():
            copy_file_with_sanitize(
                installed_plugins,
                temp_dir / "plugins" / "installed_plugins.json",
                sanitize,
            )
            # Count plugins
            try:
                plugins_data = json.loads(
                    installed_plugins.read_text(encoding="utf-8")
                )
                plugin_count = len(plugins_data.get("plugins", {}))
                log_success(
                    f"plugins/installed_plugins.json ({plugin_count} plugins)"
                )
            except (json.JSONDecodeError, KeyError):
                log_success("plugins/installed_plugins.json")
        else:
            log_warning("plugins/installed_plugins.json not found")

        # 5. plugins/known_marketplaces.json
        known_marketplaces = (
            claude_dir / "plugins" / "known_marketplaces.json"
        )
        if known_marketplaces.exists():
            copy_file_with_sanitize(
                known_marketplaces,
                temp_dir / "plugins" / "known_marketplaces.json",
                sanitize,
            )
            log_success("plugins/known_marketplaces.json")
        else:
            log_warning("plugins/known_marketplaces.json not found")

        # Optional: history and projects
        if include_history:
            log_section("History Data (Optional)")

            # history.jsonl
            history = claude_dir / "history.jsonl"
            if history.exists():
                copy_file_with_sanitize(
                    history, temp_dir / "history.jsonl", sanitize
                )
                size_kb = history.stat().st_size / 1024
                log_success(f"history.jsonl ({size_kb:.1f} KB)")
            else:
                log_warning("history.jsonl not found")

            # projects/
            projects_dir = claude_dir / "projects"
            if projects_dir.exists() and any(projects_dir.iterdir()):
                copy_directory_with_sanitize(
                    projects_dir, temp_dir / "projects", sanitize
                )
                project_count = len(
                    [d for d in projects_dir.iterdir() if d.is_dir()]
                )
                total_size = sum(
                    f.stat().st_size for f in projects_dir.rglob("*") if f.is_file()
                )
                size_mb = total_size / (1024 * 1024)
                log_success(
                    f"projects/ ({project_count} projects, {size_mb:.2f} MB)"
                )
            else:
                log_warning("projects/ not found or empty")

        # Create manifest file
        log_section("Creating Manifest")
        hostname, username = get_machine_info()
        manifest = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "hostname": hostname,
            "username": username,
            "platform": platform.system(),
            "sanitized": sanitize,
            "include_history": include_history,
            "source_dir": str(claude_dir),
            "contents": {
                "core": [
                    "CLAUDE.md",
                    "settings.json",
                    "skills/",
                ],
                "plugins": [
                    "plugins/installed_plugins.json",
                    "plugins/known_marketplaces.json",
                ],
            },
        }

        if include_history:
            manifest["contents"]["history"] = [
                "history.jsonl",
                "projects/",
            ]

        manifest_path = temp_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log_success("manifest.json")

        # Create ZIP file
        log_section("Creating ZIP Archive")
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zf.write(file_path, arcname)
                    log_info(f"  Adding: {arcname}")

        # Get final size
        final_size = output_path.stat().st_size / 1024
        log_success(f"Created: {output_path} ({final_size:.1f} KB)")

        return True, str(output_path)

    finally:
        # Cleanup temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def list_contents(claude_dir: Path) -> None:
    """List the contents of .claude directory that would be backed up."""
    log_section("Backup Contents Preview")

    print(f"\n{Colors.BOLD}📂 Core Configuration:{Colors.RESET}")
    items = [
        ("CLAUDE.md", "Global prompts and instructions"),
        ("settings.json", "User settings (model, plugins, env)"),
        ("skills/", "Custom skills"),
    ]
    for name, desc in items:
        path = claude_dir / name
        exists = path.exists()
        status = Colors.GREEN + "✓" if exists else Colors.RED + "✗"
        print(f"  {status} {name}{Colors.RESET} - {desc}")
        if name == "skills/" and exists:
            for skill in path.iterdir():
                if skill.is_dir():
                    print(f"      └─ {skill.name}/")

    print(f"\n{Colors.BOLD}🔌 Plugin Configuration:{Colors.RESET}")
    items = [
        ("plugins/installed_plugins.json", "Installed plugin list"),
        ("plugins/known_marketplaces.json", "Marketplace config"),
    ]
    for name, desc in items:
        path = claude_dir / name
        exists = path.exists()
        status = Colors.GREEN + "✓" if exists else Colors.RED + "✗"
        print(f"  {status} {name}{Colors.RESET} - {desc}")

    print(f"\n{Colors.BOLD}📜 History Data (optional):{Colors.RESET}")
    items = [
        ("history.jsonl", "Command history"),
        ("projects/", "Session history"),
    ]
    for name, desc in items:
        path = claude_dir / name
        exists = path.exists()
        status = Colors.GREEN + "✓" if exists else Colors.RED + "✗"
        size_info = ""
        if exists:
            if path.is_file():
                size_kb = path.stat().st_size / 1024
                size_info = f" ({size_kb:.1f} KB)"
            elif path.is_dir():
                total = sum(
                    f.stat().st_size for f in path.rglob("*") if f.is_file()
                )
                size_mb = total / (1024 * 1024)
                size_info = f" ({size_mb:.2f} MB)"
        print(f"  {status} {name}{Colors.RESET} - {desc}{size_info}")


def main():
    parser = argparse.ArgumentParser(
        description="Backup Claude Code configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic backup (core config only)
  python ccbackup.py

  # Include history data
  python ccbackup.py --include-history

  # Sanitize sensitive information
  python ccbackup.py --sanitize

  # Specify output file
  python ccbackup.py -o my_backup.zip

  # Scan for sensitive information
  python ccbackup.py --scan

  # Preview what would be backed up
  python ccbackup.py --list
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output ZIP file path (default: backups/ccbackup_<hostname>_<user>_<timestamp>.zip)",
    )
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Include history.jsonl and projects/ in backup",
    )
    parser.add_argument(
        "--sanitize",
        action="store_true",
        help="Replace sensitive information with placeholders",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for sensitive information without creating backup",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List contents that would be backed up",
    )

    args = parser.parse_args()

    claude_dir = get_claude_dir()

    if not claude_dir.exists():
        log_error(f"Claude directory not found: {claude_dir}")
        sys.exit(1)

    hostname, username = get_machine_info()
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔧 Claude Code Backup Tool{Colors.RESET}")
    print(f"{Colors.CYAN}   Source: {claude_dir}{Colors.RESET}")
    print(f"{Colors.CYAN}   Host: {hostname} | User: {username}{Colors.RESET}\n")

    # List mode
    if args.list:
        list_contents(claude_dir)
        return

    # Scan mode
    if args.scan:
        log_section("Scanning for Sensitive Information")
        findings = scan_for_sensitive(claude_dir)

        if not findings:
            log_success("No sensitive information detected")
        else:
            log_warning("Sensitive information found:")
            for file_path, items in findings.items():
                print(f"\n  📄 {file_path}:")
                for name, value in items:
                    # Mask the value
                    masked = value[:8] + "..." if len(value) > 12 else "***"
                    print(f"      • {name}: {masked}")

            print(
                f"\n{Colors.YELLOW}💡 Tip: Use --sanitize to replace these with placeholders{Colors.RESET}"
            )
        return

    # Backup mode
    if args.output:
        output_path = Path(args.output)
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = get_default_backup_path()

    # Show settings
    print(f"{Colors.BOLD}Settings:{Colors.RESET}")
    print(f"  • Include history: {args.include_history}")
    print(f"  • Sanitize secrets: {args.sanitize}")
    print(f"  • Output: {output_path}")

    if args.sanitize:
        log_warning(
            "Sanitize mode enabled - sensitive info will be replaced with placeholders"
        )
    else:
        # Scan and warn about sensitive info
        findings = scan_for_sensitive(claude_dir)
        if findings:
            log_warning(
                "Sensitive information detected! Use --sanitize to mask, or keep safely."
            )

    success, message = create_backup(
        output_path,
        include_history=args.include_history,
        sanitize=args.sanitize,
    )

    if success:
        log_section("Backup Complete")
        log_success(f"Backup saved to: {message}")

        if not args.sanitize:
            print(
                f"\n{Colors.YELLOW}⚠️  This backup contains sensitive information.{Colors.RESET}"
            )
            print(f"{Colors.YELLOW}   Store it securely!{Colors.RESET}")
    else:
        log_error(f"Backup failed: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
