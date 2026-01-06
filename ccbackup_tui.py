#!/usr/bin/env python3
"""
Claude Code Configuration Backup Tool - TUI Version

Centered window dialog using Blessed library (inspired by cc-mirror).
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


class Window:
    """A centered window dialog."""

    def __init__(self, width=50, height=20):
        self.width = width
        self.height = height
        self.x = (term.width - width) // 2
        self.y = (term.height - height) // 2

    def draw_box(self):
        """Draw the window border."""
        output = []

        # Top border
        output.append(
            term.move(self.y, self.x)
            + "┏" + "━" * (self.width - 2) + "┓"
        )

        # Side borders
        for i in range(1, self.height - 1):
            output.append(
                term.move(self.y + i, self.x) + "┃" + " " * (self.width - 2) + "┃"
            )

        # Bottom border
        output.append(
            term.move(self.y + self.height - 1, self.x)
            + "┗" + "━" * (self.width - 2) + "┛"
        )

        return "".join(output)

    def text(self, line: int, content: str, centered: bool = False) -> str:
        """Position text inside the window."""
        if centered:
            padding = (self.width - 2 - len(content)) // 2
            content = " " * padding + content
        else:
            content = content[: self.width - 3]

        return term.move(self.y + line, self.x + 1) + content

    def button(self, line: int, text: str, selected: bool = False) -> str:
        """Draw a button."""
        btn = f"[ {text} ]"
        if selected:
            btn = term.reverse(btn)
        padding = (self.width - 2 - len(btn)) // 2
        content = " " * padding + btn + " " * (self.width - 3 - padding - len(btn))
        return term.move(self.y + line, self.x + 1) + content


def show_backup_dialog() -> tuple[bool, bool]:
    """Show the main backup dialog."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        window = Window(width=52, height=16)

        hostname, username = get_machine_info()
        selected_option = 0  # 0=sanitize, 1=history, 2=backup, 3=quit

        while True:
            # Clear screen
            print(term.home + term.clear, end="", flush=False)

            # Draw window
            output = [window.draw_box()]

            # Title
            output.append(window.text(1, "🔧 Backup Options", centered=True))

            # System info
            output.append(window.text(3, f"{hostname} / {username}", centered=True))

            # Options
            sanitize_text = "☑ Sanitize secrets" if selected_option == 0 else "☐ Sanitize secrets"
            history_text = "☑ Include history" if selected_option == 1 else "☐ Include history"

            output.append(window.text(5, sanitize_text, centered=True))
            output.append(window.text(6, history_text, centered=True))

            # Buttons
            backup_selected = selected_option == 2
            quit_selected = selected_option == 3

            output.append(window.button(8, "💾 Backup", backup_selected))
            output.append(window.button(9, "❌ Quit", quit_selected))

            # Instructions
            output.append(
                window.text(11, "↑↓ Navigate  Space Toggle  Enter Confirm", centered=False)
            )

            # Print all output
            print("".join(output), end="", flush=True)

            # Get input
            key = term.inkey()

            if key.code == term.KEY_UP:
                selected_option = (selected_option - 1) % 4
            elif key.code == term.KEY_DOWN:
                selected_option = (selected_option + 1) % 4
            elif key == " ":  # Space to toggle
                if selected_option == 0 or selected_option == 1:
                    selected_option = (selected_option + 1) % 2
            elif key.code == term.KEY_ENTER or key == "q":
                if selected_option == 3:  # Quit
                    raise KeyboardInterrupt
                elif selected_option == 2:  # Backup
                    sanitize = selected_option >= 0
                    include_history = selected_option >= 1
                    return sanitize, include_history
            elif key in ("q", "Q"):
                raise KeyboardInterrupt


def show_options_dialog() -> tuple[bool, bool]:
    """Show dialog to select backup options."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        window = Window(width=52, height=18)

        sanitize = False
        history = False
        selected_option = 0  # 0=sanitize, 1=history, 2=backup, 3=quit

        while True:
            # Clear screen
            print(term.home + term.clear, end="", flush=False)

            # Draw window
            output = [window.draw_box()]

            # Title
            output.append(window.text(1, "🔧 Backup Options", centered=True))

            # System info
            hostname, username = get_machine_info()
            output.append(window.text(3, f"{hostname} / {username}", centered=True))

            # Options with checkboxes
            sanitize_check = "☑" if sanitize else "☐"
            history_check = "☑" if history else "☐"

            sanitize_line = f"{sanitize_check} Sanitize secrets"
            history_line = f"{history_check} Include history"

            if selected_option == 0:
                sanitize_line = term.reverse(sanitize_line)
            if selected_option == 1:
                history_line = term.reverse(history_line)

            output.append(window.text(5, sanitize_line, centered=True))
            output.append(window.text(6, history_line, centered=True))

            # Summary
            output.append(window.text(8, "─" * 48, centered=False))
            output.append(
                window.text(9, f"Sanitize: {'✅' if sanitize else '❌'}", centered=True)
            )
            output.append(
                window.text(10, f"History: {'✅' if history else '❌'}", centered=True)
            )
            output.append(window.text(11, f"Output: ./backups/", centered=True))

            # Buttons
            backup_selected = selected_option == 2
            quit_selected = selected_option == 3

            output.append(window.button(13, "💾 Backup", backup_selected))
            output.append(window.button(14, "❌ Quit", quit_selected))

            # Instructions
            output.append(window.text(16, "↑↓ Navigate  Space Toggle  Enter Confirm", centered=False))

            # Print all output
            print("".join(output), end="", flush=True)

            # Get input
            key = term.inkey(timeout=0.1)

            if key is None:
                continue

            if key.code == term.KEY_UP:
                selected_option = (selected_option - 1) % 4
            elif key.code == term.KEY_DOWN:
                selected_option = (selected_option + 1) % 4
            elif key == " ":  # Space to toggle
                if selected_option == 0:
                    sanitize = not sanitize
                elif selected_option == 1:
                    history = not history
            elif key.code == term.KEY_ENTER:
                if selected_option == 3:  # Quit
                    raise KeyboardInterrupt
                elif selected_option == 2:  # Backup
                    return sanitize, history
            elif key in ("q", "Q"):
                raise KeyboardInterrupt


def show_result_dialog(success: bool, message: str, size: float = 0):
    """Show result dialog."""
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        if success:
            window = Window(width=52, height=14)
            icon = "✅"
            title = "Backup Completed"
            color = term.green
        else:
            window = Window(width=52, height=14)
            icon = "❌"
            title = "Backup Failed"
            color = term.red

        output = [window.draw_box()]

        output.append(window.text(1, f"{icon} {title}", centered=True))
        output.append(window.text(2, "─" * 48, centered=False))

        if success:
            filename = Path(message).name
            output.append(window.text(4, filename, centered=True))
            output.append(window.text(5, f"{size:.0f} KB", centered=True))
            output.append(window.text(7, "✅ Ready for migration", centered=True))
        else:
            # Truncate message if too long
            msg_lines = message.split("\n")
            for i, line in enumerate(msg_lines[:5]):
                output.append(window.text(4 + i, line[: window.width - 3], centered=False))

        output.append(window.text(11, "Press any key to exit", centered=True))

        print("".join(output), end="", flush=True)

        term.inkey()


def main():
    """Run the interactive backup TUI."""
    try:
        # Show options dialog
        sanitize, include_history = show_options_dialog()

        # Perform backup
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            window = Window(width=52, height=10)

            output = [window.draw_box()]
            output.append(window.text(1, "💾 Backing up...", centered=True))
            output.append(window.text(3, "Preparing files...", centered=True))
            output.append(window.text(5, "Please wait", centered=True))

            print(term.home + term.clear + "".join(output), end="", flush=True)

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
        print(term.home + term.clear + term.move_y(term.height // 2) + term.center("Cancelled."), flush=True)
        return 0
    except Exception as e:
        print(term.home + term.clear + term.move_y(term.height // 2) + term.center(f"Error: {e}"), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
