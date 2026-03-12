"""Rich terminal output for ContentRadar."""

from __future__ import annotations

from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def _format_number(n: int | float) -> str:
    """Human-readable number formatting."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


def _format_duration(seconds: int) -> str:
    """Convert seconds to MM:SS or HH:MM:SS."""
    if seconds <= 0:
        return "—"
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def print_scan_header(
    channel_handle: str,
    channel_name: str,
    total_videos: int,
    channel_avg: float,
    method: str,
    threshold: float,
    window_days: Optional[int],
) -> None:
    """Print the scan summary header."""
    window_label = f"last {window_days} days" if window_days else "all time"

    header = Text()
    header.append("📡 ContentRadar", style="bold cyan")
    header.append(" — YouTube Outlier Scan\n", style="dim")
    header.append("━" * 44, style="dim")

    console.print()
    console.print(header)
    console.print()
    console.print(f"  Channel:         [bold]{channel_handle}[/bold] ({channel_name})")
    console.print(f"  Videos scanned:  [bold]{total_videos}[/bold] ({window_label})")
    console.print(f"  Channel average: [bold]{_format_number(channel_avg)}[/bold] views")
    console.print(f"  Method:          {method} | Threshold: {threshold}x")
    console.print()


def print_outliers_table(outliers: list, channel_avg: float) -> None:
    """Print the outlier results as a rich table."""
    if not outliers:
        console.print("[yellow]  No outliers found above threshold.[/yellow]")
        console.print("[dim]  Try lowering --threshold (e.g. 2.0) or increasing --limit.[/dim]")
        return

    console.print(f"[bold green]🏆 OUTLIERS FOUND: {len(outliers)}[/bold green]")
    console.print()

    table = Table(show_header=True, header_style="bold", padding=(0, 1))
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Score", style="bold yellow", width=7, justify="right")
    table.add_column("Views", width=10, justify="right")
    table.add_column("Duration", width=8, justify="right", style="dim")
    table.add_column("Published", width=10, style="dim")
    table.add_column("Title", max_width=55, no_wrap=True)

    for i, o in enumerate(outliers, 1):
        # Color score based on magnitude
        score_val = o.outlier_score if hasattr(o, "outlier_score") else o["outlier_score"]
        views_val = o.views if hasattr(o, "views") else o["views"]
        title_val = o.title if hasattr(o, "title") else o["title"]
        dur_val = o.duration_seconds if hasattr(o, "duration_seconds") else o.get("duration_seconds", 0)
        pub_val = o.published_at if hasattr(o, "published_at") else o.get("published_at", "")

        if score_val >= 10:
            score_style = "bold red"
        elif score_val >= 5:
            score_style = "bold yellow"
        else:
            score_style = "bold green"

        table.add_row(
            str(i),
            Text(f"{score_val}x", style=score_style),
            _format_number(views_val),
            _format_duration(dur_val),
            pub_val or "—",
            title_val[:55],
        )

    console.print(table)
    console.print()


def print_save_info(raw_path: str | None, outlier_path: str | None) -> None:
    """Print where data was saved."""
    if raw_path:
        console.print(f"  [dim]💾 Raw data:[/dim]     {raw_path}")
    if outlier_path:
        console.print(f"  [dim]📊 Outliers:[/dim]     {outlier_path}")
    console.print()


def print_error(message: str) -> None:
    """Print a formatted error."""
    console.print(f"[bold red]✗ Error:[/bold red] {message}")
