#!/usr/bin/env python3
"""
Claude Code Configuration Backup Tool - TUI Version

Full-screen terminal UI inspired by cc-mirror with colors, emojis, and rich formatting.
"""

import sys
from pathlib import Path

from blessed import Terminal

from ccbackup import (
    create_backup,
    get_default_backup_path,
    get_machine_info,
)

term = Terminal()


def render_line(content: str, line: int) -> str:
    """Render a line at absolute position."""
    return term.move(line, 0) + content


def pad_right(text: str, width: int) -> str:
    """Pad text to right with spaces."""
    # Remove ANSI codes for length calculation
    clean_text = term.strip_seqs(text)
    padding = max(0, width - len(clean_text))
    return text + " " * padding


def show_main_menu() -> tuple[bool, bool]:
    """Show main interactive menu inspired by cc-mirror."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        hostname, username = get_machine_info()

        sanitize = False
        history = False
        selected = 0  # 0=sanitize, 1=history, 2=backup, 3=quit

        while True:
            print(term.home + term.clear, end="", flush=False)

            output = []

            # Header with branding
            output.append(render_line(
                term.bold_magenta("❯ CCBACKUP"),
                0
            ))

            # Title section
            output.append(render_line(
                term.bold(term.yellow("─ BACKUP ─")),
                2
            ))

            output.append(render_line(
                term.bright_cyan("Claude Code Configuration Backup"),
                3
            ))
            output.append(render_line(
                term.yellow("Backup your settings, prompts, and skills"),
                4
            ))

            # Decorative line
            output.append(render_line(
                term.magenta("─" * 60 + "◆" + "─" * (term.width - 62)),
                5
            ))

            # System info
            output.append(render_line(
                term.bold(f"★ System: {hostname} / {username}"),
                7
            ))

            # Menu options
            options = [
                ("Sanitize secrets", "🔐", "Replace API tokens & secrets"),
                ("Include history", "📚", "Include session history data"),
                ("Backup", "💾", "Start backup process"),
                ("Quit", "❌", "Exit application"),
            ]

            for i, (name, emoji, desc) in enumerate(options):
                line_no = 9 + i * 2

                # Highlight selected option
                if i == selected:
                    if i < 2:  # Toggles
                        check = "☑" if (sanitize if i == 0 else history) else "☐"
                        line_content = f"  {emoji} {check} {name}"
                        output.append(render_line(
                            term.reverse(term.bold(line_content)),
                            line_no
                        ))
                    else:  # Buttons
                        line_content = f"  {emoji} {name}"
                        output.append(render_line(
                            term.reverse(term.bold(line_content)),
                            line_no
                        ))
                else:
                    if i < 2:  # Toggles
                        check = "☑" if (sanitize if i == 0 else history) else "☐"
                        line_content = f"  {emoji} {check} {name}"
                        output.append(render_line(
                            term.bright_cyan(line_content),
                            line_no
                        ))
                    else:  # Buttons
                        line_content = f"  {emoji} {name}"
                        output.append(render_line(
                            term.bright_cyan(line_content),
                            line_no
                        ))

                # Description
                if i < 2:
                    output.append(render_line(
                        term.dim_cyan(f"       {desc}"),
                        line_no + 1
                    ))

            # Summary section
            output.append(render_line(
                term.magenta("─" * term.width),
                17
            ))

            output.append(render_line(
                term.bold(f"Sanitize: {'✅' if sanitize else '❌'}  │  History: {'✅' if history else '❌'}"),
                19
            ))

            output.append(render_line(
                term.dim_cyan("Output: ./backups/"),
                20
            ))

            # Footer
            output.append(render_line(
                term.magenta("─" * term.width),
                term.height - 3
            ))

            output.append(render_line(
                term.dim_cyan("↑↓ Navigate  ·  Space Toggle  ·  Enter Confirm  ·  q Quit"),
                term.height - 2
            ))

            # Print all output
            print("".join(output), end="", flush=True)

            # Get input
            key = term.inkey(timeout=0.1)

            if key is None:
                continue

            if key.code == term.KEY_UP:
                selected = (selected - 1) % 4
            elif key.code == term.KEY_DOWN:
                selected = (selected + 1) % 4
            elif key == " ":  # Space to toggle
                if selected == 0:
                    sanitize = not sanitize
                elif selected == 1:
                    history = not history
            elif key.code == term.KEY_ENTER:
                if selected == 3:  # Quit
                    raise KeyboardInterrupt
                elif selected == 2:  # Backup
                    return sanitize, history
            elif key in ("q", "Q"):
                raise KeyboardInterrupt


def show_progress():
    """Show backup progress screen."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        output = []

        output.append(render_line(
            term.bold_magenta("❯ CCBACKUP"),
            0
        ))

        output.append(render_line(
            term.bold(term.yellow("─ BACKING UP ─")),
            2
        ))

        output.append(render_line(
            term.bright_cyan("Preparing backup..."),
            5
        ))

        output.append(render_line(
            term.dim_cyan("⏳ Please wait"),
            7
        ))

        print(term.home + term.clear + "".join(output), end="", flush=True)


def show_result_dialog(success: bool, message: str, size: float = 0):
    """Show result dialog."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        output = []

        output.append(render_line(
            term.bold_magenta("❯ CCBACKUP"),
            0
        ))

        if success:
            output.append(render_line(
                term.bold(term.green("─ SUCCESS ✅ ─")),
                2
            ))
            output.append(render_line(
                term.bright_cyan("Backup completed successfully!"),
                4
            ))

            filename = Path(message).name
            output.append(render_line(
                term.yellow(filename),
                6
            ))
            output.append(render_line(
                term.dim_cyan(f"Size: {size:.0f} KB"),
                7
            ))

            output.append(render_line(
                term.bright_green("✅ Ready for migration"),
                9
            ))
        else:
            output.append(render_line(
                term.bold(term.red("─ FAILED ❌ ─")),
                2
            ))
            output.append(render_line(
                term.bright_cyan("Backup failed"),
                4
            ))

            msg_lines = message.split("\n")
            for i, line in enumerate(msg_lines[:5]):
                output.append(render_line(
                    term.red(line[:term.width - 1]),
                    6 + i
                ))

        output.append(render_line(
            term.magenta("─" * term.width),
            term.height - 2
        ))

        output.append(render_line(
            term.dim_cyan("Press any key to exit"),
            term.height - 1
        ))

        print("".join(output), end="", flush=True)
        term.inkey()


def main():
    """Run the interactive backup TUI."""
    try:
        # Show main menu
        sanitize, include_history = show_main_menu()

        # Perform backup
        show_progress()

        try:
            output_path = get_default_backup_path()
            success, message = create_backup(
                output_path,
                include_history=include_history,
                sanitize=sanitize,
            )

            if success:
                backup_size = Path(message).stat().st_size / 1024
                show_result_dialog(True, message, backup_size)
            else:
                show_result_dialog(False, message)

            return 0 if success else 1

        except Exception as e:
            show_result_dialog(False, str(e))
            return 1

    except KeyboardInterrupt:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            output = []
            output.append(render_line(
                term.bold_magenta("❯ CCBACKUP"),
                0
            ))
            output.append(render_line(
                term.dim_cyan("Cancelled."),
                term.height // 2
            ))
            print(term.home + term.clear + "".join(output), end="", flush=True)
            import time
            time.sleep(1)
        return 0
    except Exception as e:
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            output = []
            output.append(render_line(
                term.bold_magenta("❯ CCBACKUP"),
                0
            ))
            output.append(render_line(
                term.red(f"Error: {e}"),
                term.height // 2
            ))
            print(term.home + term.clear + "".join(output), end="", flush=True)
            import time
            time.sleep(2)
        return 1


if __name__ == "__main__":
    sys.exit(main())
