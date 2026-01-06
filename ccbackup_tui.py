#!/usr/bin/env python3
"""
Claude Code Configuration Backup Tool - TUI Version (Simple)

A minimal terminal user interface for backing up Claude Code configuration files.
Built with Textual framework.
"""

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Button, Footer, Header, Label, Static, Switch
from textual.worker import Worker, WorkerState

# Import core backup functions from ccbackup
from ccbackup import (
    create_backup,
    get_default_backup_path,
    get_machine_info,
)


class SimpleBackupApp(App):
    """Claude Code Backup Tool - Simple TUI Application."""

    TITLE = "Claude Code Backup Tool"
    SUB_TITLE = "Backup Configuration"

    CSS = """
    Screen {
        align: center middle;
    }

    #main-box {
        width: 50;
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    #info {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    .option-row {
        height: 3;
        margin-bottom: 1;
    }

    .option-row Switch {
        width: 1fr;
    }

    #button-row {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #button-row Button {
        width: 1fr;
        margin-bottom: 1;
    }

    #status {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
        height: 3;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "backup", "Backup"),
        Binding("d", "toggle_dark", "Dark"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        with Vertical(id="main-box"):
            yield Label("🔧 Backup Options", id="title")

            hostname, username = get_machine_info()
            yield Label(f"{hostname} / {username}", id="info")

            with Vertical(classes="option-row"):
                yield Switch(id="sanitize", value=False)
                yield Label("Sanitize secrets", classes="option-label")

            with Vertical(classes="option-row"):
                yield Switch(id="include-history", value=False)
                yield Label("Include history", classes="option-label")

            with Vertical(id="button-row"):
                yield Button("💾 Backup", id="backup", variant="primary")
                yield Button("❌ Quit", id="quit", variant="error")

            yield Label("", id="status")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "quit":
            self.action_quit()
        elif button_id == "backup":
            self.action_backup()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_backup(self) -> None:
        """Start the backup process."""
        self.run_worker(self._do_backup(), exclusive=True)

    async def _do_backup(self) -> None:
        """Perform the backup operation."""
        status = self.query_one("#status", Label)
        sanitize = self.query_one("#sanitize", Switch).value
        include_history = self.query_one("#include-history", Switch).value

        try:
            status.update("⏳ Backing up...")

            output_path = get_default_backup_path()

            # Perform backup
            success, message = create_backup(
                output_path,
                include_history=include_history,
                sanitize=sanitize,
            )

            if success:
                backup_size = Path(message).stat().st_size / 1024
                status.update(f"✅ Saved: {Path(message).name} ({backup_size:.0f}KB)")
                self.notify("Backup completed!", title="Success")
            else:
                status.update(f"❌ Failed: {message}")
                self.notify(f"Error: {message}", title="Error", severity="error")

        except Exception as e:
            status.update(f"❌ Error: {e}")
            self.notify(str(e), title="Error", severity="error")


def main():
    """Run the TUI application."""
    app = SimpleBackupApp()
    app.run()


if __name__ == "__main__":
    main()
