#!/usr/bin/env python3
"""
Claude Code Configuration Backup Tool - TUI Version

A terminal user interface for backing up Claude Code configuration files.
Built with Textual framework.
"""

import asyncio
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ProgressBar,
    RichLog,
    Static,
    Switch,
)
from textual.worker import Worker, WorkerState

# Import core backup functions from ccbackup
from ccbackup import (
    create_backup,
    get_claude_dir,
    get_default_backup_path,
    get_machine_info,
    list_contents,
    scan_for_sensitive,
)


class OptionPanel(Static):
    """Panel for backup options."""

    def compose(self) -> ComposeResult:
        yield Label("⚙️  Backup Options", classes="panel-title")
        with Horizontal(classes="option-row"):
            yield Switch(id="sanitize", value=False)
            yield Label("Sanitize secrets", classes="option-label")
        with Horizontal(classes="option-row"):
            yield Switch(id="include-history", value=False)
            yield Label("Include history", classes="option-label")


class InfoPanel(Static):
    """Panel for displaying system information."""

    def compose(self) -> ComposeResult:
        hostname, username = get_machine_info()
        claude_dir = get_claude_dir()

        yield Label("📋 System Info", classes="panel-title")
        yield Label(f"Host: [bold]{hostname}[/bold]", classes="info-item", markup=True)
        yield Label(f"User: [bold]{username}[/bold]", classes="info-item", markup=True)
        yield Label(f"Source: [dim]{claude_dir}[/dim]", classes="info-item", markup=True)


class ActionPanel(Static):
    """Panel for action buttons."""

    def compose(self) -> ComposeResult:
        yield Label("🚀 Actions", classes="panel-title")
        with Horizontal(classes="button-row"):
            yield Button("📂 List", id="list", variant="default")
            yield Button("🔍 Scan", id="scan", variant="warning")
        with Horizontal(classes="button-row"):
            yield Button("💾 Backup", id="backup", variant="primary")
            yield Button("❌ Quit", id="quit", variant="error")


class CCBackupApp(App):
    """Claude Code Backup Tool - TUI Application."""

    TITLE = "Claude Code Backup Tool"
    SUB_TITLE = "Backup your Claude Code configuration"

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 1fr 2fr;
        grid-rows: auto 1fr auto;
    }

    #left-panel {
        row-span: 2;
        padding: 1;
        border: solid $primary;
        margin: 1;
    }

    #log-panel {
        padding: 1;
        border: solid $accent;
        margin: 1;
    }

    #progress-panel {
        column-span: 2;
        padding: 1;
        margin: 0 1;
        height: auto;
    }

    .panel-title {
        text-style: bold;
        color: $text;
        padding: 0 0 1 0;
        border: none none solid none;
        border-title-color: $primary;
        margin-bottom: 1;
    }

    .option-row {
        height: 3;
        align: left middle;
        margin: 0 0 1 0;
    }

    .option-label {
        margin-left: 1;
    }

    .info-item {
        margin: 0 0 1 1;
    }

    .button-row {
        height: auto;
        margin: 1 0;
    }

    .button-row Button {
        margin: 0 1 0 0;
        min-width: 12;
    }

    RichLog {
        height: 100%;
        scrollbar-gutter: stable;
    }

    ProgressBar {
        padding: 1 0;
    }

    #status-label {
        text-align: center;
        margin-top: 1;
        color: $text-muted;
    }

    OptionPanel {
        margin-bottom: 1;
    }

    InfoPanel {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "backup", "Backup"),
        Binding("s", "scan", "Scan"),
        Binding("l", "list", "List"),
        Binding("d", "toggle_dark", "Toggle Dark"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="left-panel"):
            yield OptionPanel()
            yield InfoPanel()
            yield ActionPanel()

        with Container(id="log-panel"):
            yield Label("📜 Output Log", classes="panel-title")
            yield RichLog(id="log", highlight=True, markup=True)

        with Container(id="progress-panel"):
            yield ProgressBar(id="progress", total=100, show_eta=False)
            yield Label("Ready", id="status-label")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app."""
        log = self.query_one("#log", RichLog)
        log.write("[bold blue]Claude Code Backup Tool[/bold blue]")
        log.write("─" * 40)

        hostname, username = get_machine_info()
        log.write(f"🖥️  Host: [cyan]{hostname}[/cyan]")
        log.write(f"👤 User: [cyan]{username}[/cyan]")
        log.write("")
        log.write("[dim]Use the buttons or keyboard shortcuts to perform actions.[/dim]")
        log.write("[dim]Press 'q' to quit, 'b' for backup, 's' to scan.[/dim]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "quit":
            self.action_quit()
        elif button_id == "backup":
            self.action_backup()
        elif button_id == "scan":
            self.action_scan()
        elif button_id == "list":
            self.action_list()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_list(self) -> None:
        """List backup contents."""
        log = self.query_one("#log", RichLog)
        log.clear()
        log.write("[bold]📂 Backup Contents Preview[/bold]")
        log.write("─" * 40)

        claude_dir = get_claude_dir()

        if not claude_dir.exists():
            log.write("[red]❌ Claude directory not found![/red]")
            return

        # Core configuration
        log.write("\n[bold]📂 Core Configuration:[/bold]")
        items = [
            ("CLAUDE.md", "Global prompts"),
            ("settings.json", "User settings"),
            ("skills/", "Custom skills"),
        ]
        for name, desc in items:
            path = claude_dir / name
            exists = path.exists()
            status = "[green]✓[/green]" if exists else "[red]✗[/red]"
            log.write(f"  {status} {name} - {desc}")

            if name == "skills/" and exists:
                for skill in path.iterdir():
                    if skill.is_dir():
                        log.write(f"      └─ {skill.name}/")

        # Plugin configuration
        log.write("\n[bold]🔌 Plugin Configuration:[/bold]")
        items = [
            ("plugins/installed_plugins.json", "Installed plugins"),
            ("plugins/known_marketplaces.json", "Marketplaces"),
        ]
        for name, desc in items:
            path = claude_dir / name
            exists = path.exists()
            status = "[green]✓[/green]" if exists else "[red]✗[/red]"
            log.write(f"  {status} {name} - {desc}")

        # History data
        log.write("\n[bold]📜 History Data (optional):[/bold]")
        items = [
            ("history.jsonl", "Command history"),
            ("projects/", "Session history"),
        ]
        for name, desc in items:
            path = claude_dir / name
            exists = path.exists()
            status = "[green]✓[/green]" if exists else "[red]✗[/red]"
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
            log.write(f"  {status} {name} - {desc}{size_info}")

    def action_scan(self) -> None:
        """Scan for sensitive information."""
        log = self.query_one("#log", RichLog)
        log.clear()
        log.write("[bold]🔍 Scanning for Sensitive Information[/bold]")
        log.write("─" * 40)

        claude_dir = get_claude_dir()

        if not claude_dir.exists():
            log.write("[red]❌ Claude directory not found![/red]")
            return

        findings = scan_for_sensitive(claude_dir)

        if not findings:
            log.write("[green]✅ No sensitive information detected[/green]")
        else:
            log.write("[yellow]⚠️  Sensitive information found:[/yellow]")
            for file_path, items in findings.items():
                log.write(f"\n  📄 [cyan]{file_path}[/cyan]:")
                for name, value in items:
                    # Mask the value
                    masked = value[:8] + "..." if len(value) > 12 else "***"
                    log.write(f"      • {name}: [dim]{masked}[/dim]")

            log.write("")
            log.write("[yellow]💡 Tip: Enable 'Sanitize secrets' to replace with placeholders[/yellow]")

    def action_backup(self) -> None:
        """Start the backup process."""
        self.run_backup_worker()

    @property
    def backup_options(self) -> tuple[bool, bool]:
        """Get current backup options from switches."""
        sanitize = self.query_one("#sanitize", Switch).value
        include_history = self.query_one("#include-history", Switch).value
        return sanitize, include_history

    def run_backup_worker(self) -> None:
        """Run backup in a worker thread."""
        self.run_worker(self._do_backup(), exclusive=True)

    async def _do_backup(self) -> str:
        """Perform the backup operation."""
        log = self.query_one("#log", RichLog)
        progress = self.query_one("#progress", ProgressBar)
        status_label = self.query_one("#status-label", Label)

        log.clear()
        log.write("[bold]💾 Starting Backup[/bold]")
        log.write("─" * 40)

        sanitize, include_history = self.backup_options

        log.write(f"Options:")
        log.write(f"  • Sanitize: {'[green]Yes[/green]' if sanitize else '[dim]No[/dim]'}")
        log.write(f"  • Include history: {'[green]Yes[/green]' if include_history else '[dim]No[/dim]'}")
        log.write("")

        # Update progress
        progress.update(progress=10)
        status_label.update("Preparing backup...")
        await asyncio.sleep(0.1)

        output_path = get_default_backup_path()
        log.write(f"📦 Output: [cyan]{output_path}[/cyan]")
        log.write("")

        progress.update(progress=20)
        status_label.update("Backing up core configuration...")
        await asyncio.sleep(0.1)

        # Perform backup
        try:
            success, message = create_backup(
                output_path,
                include_history=include_history,
                sanitize=sanitize,
            )

            if success:
                progress.update(progress=100)
                status_label.update("Backup complete!")

                log.write("")
                log.write("[green]✅ Backup Complete![/green]")
                log.write(f"📁 Saved to: [bold]{message}[/bold]")

                # Get file size
                backup_size = Path(message).stat().st_size / 1024
                log.write(f"📊 Size: {backup_size:.1f} KB")

                if not sanitize:
                    log.write("")
                    log.write("[yellow]⚠️  Backup contains sensitive information.[/yellow]")
                    log.write("[yellow]   Store it securely![/yellow]")

                self.notify("Backup completed successfully!", title="Success", severity="information")
                return message
            else:
                progress.update(progress=0)
                status_label.update("Backup failed!")
                log.write(f"[red]❌ Backup failed: {message}[/red]")
                self.notify(f"Backup failed: {message}", title="Error", severity="error")
                return ""

        except Exception as e:
            progress.update(progress=0)
            status_label.update("Backup failed!")
            log.write(f"[red]❌ Error: {e}[/red]")
            self.notify(f"Error: {e}", title="Error", severity="error")
            return ""

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.state == WorkerState.SUCCESS:
            pass  # Already handled in the worker
        elif event.state == WorkerState.ERROR:
            log = self.query_one("#log", RichLog)
            log.write(f"[red]❌ Worker error: {event.worker.error}[/red]")


def main():
    """Run the TUI application."""
    app = CCBackupApp()
    app.run()


if __name__ == "__main__":
    main()
