#!/usr/bin/env python3
"""
Claude Code Configuration Backup Tool - TUI Version

Interactive terminal UI using Questionary + Rich.
Inspired by Ink (React-based TUI) architecture.
"""

import sys
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ccbackup import (
    create_backup,
    get_default_backup_path,
    get_machine_info,
)

console = Console()


def show_banner():
    """Show welcome banner."""
    banner = Panel(
        "[bold cyan]Claude Code Backup Tool[/bold cyan]\n"
        "[dim]Interactive backup wizard[/dim]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(banner)


def show_system_info():
    """Display system information."""
    hostname, username = get_machine_info()

    info_table = Table(show_header=False, box=None, padding=(0, 1))
    info_table.add_row("[dim]Host:[/dim]", f"[cyan]{hostname}[/cyan]")
    info_table.add_row("[dim]User:[/dim]", f"[cyan]{username}[/cyan]")

    console.print(info_table)
    console.print()


def ask_options() -> tuple[bool, bool]:
    """
    Ask user for backup options.
    Returns (sanitize, include_history) tuple.
    """
    console.print("[bold]🔧 Backup Options[/bold]\n")

    sanitize = questionary.confirm(
        "Sanitize secrets (replace with placeholders)?",
        default=False,
        auto_enter=True,
    ).ask()

    if sanitize is None:
        raise KeyboardInterrupt

    include_history = questionary.confirm(
        "Include history and session data?",
        default=False,
        auto_enter=True,
    ).ask()

    if include_history is None:
        raise KeyboardInterrupt

    return sanitize, include_history


def confirm_backup(sanitize: bool, include_history: bool) -> bool:
    """Show summary and confirm backup."""
    console.print()
    summary = Table(show_header=False, box=None, padding=(0, 1))
    summary.add_row("[dim]Sanitize:[/dim]", "✅ Yes" if sanitize else "❌ No")
    summary.add_row("[dim]History:[/dim]", "✅ Yes" if include_history else "❌ No")
    summary.add_row("[dim]Output:[/dim]", f"[cyan]{Path('.').joinpath('backups')}[/cyan]")

    console.print(summary)
    console.print()

    confirm = questionary.confirm("Start backup?", default=True, auto_enter=True).ask()

    return confirm if confirm is not None else False


def perform_backup(sanitize: bool, include_history: bool) -> bool:
    """Perform the backup operation."""
    with console.status("[bold cyan]⏳ Backing up...[/bold cyan]", spinner="dots"):
        try:
            output_path = get_default_backup_path()
            success, message = create_backup(
                output_path,
                include_history=include_history,
                sanitize=sanitize,
            )

            if success:
                backup_size = Path(message).stat().st_size / 1024
                filename = Path(message).name

                result_panel = Panel(
                    f"[green]✅ Backup Completed[/green]\n\n"
                    f"[cyan]{filename}[/cyan]\n"
                    f"[dim]{backup_size:.0f} KB[/dim]",
                    border_style="green",
                    padding=(1, 2),
                )
                console.print(result_panel)

                if not sanitize:
                    console.print(
                        "\n[yellow]⚠️  Backup contains sensitive information - store securely![/yellow]"
                    )

                return True
            else:
                error_panel = Panel(
                    f"[red]❌ Backup Failed[/red]\n\n{message}",
                    border_style="red",
                    padding=(1, 2),
                )
                console.print(error_panel)
                return False

        except Exception as e:
            error_panel = Panel(
                f"[red]❌ Error[/red]\n\n{e}",
                border_style="red",
                padding=(1, 2),
            )
            console.print(error_panel)
            return False


def main():
    """Run the interactive backup wizard."""
    try:
        show_banner()
        show_system_info()

        # Ask for options
        sanitize, include_history = ask_options()

        # Confirm before backup
        if not confirm_backup(sanitize, include_history):
            console.print("[dim]Cancelled.[/dim]")
            return

        # Perform backup
        success = perform_backup(sanitize, include_history)

        if success:
            console.print("\n[green]Done![/green]")
            sys.exit(0)
        else:
            console.print("\n[red]Failed![/red]")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled by user.[/dim]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
