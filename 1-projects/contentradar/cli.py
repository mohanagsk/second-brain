"""ContentRadar CLI — typer-based entry point."""

from __future__ import annotations

import json
import sys
from typing import Optional

import typer
from rich.console import Console

from contentradar import __version__

app = typer.Typer(
    name="contentradar",
    help="📡 ContentRadar — DIY Viral Content Intelligence",
    add_completion=False,
    no_args_is_help=True,
)

scan_app = typer.Typer(help="Scan platforms for outlier content", no_args_is_help=True)
app.add_typer(scan_app, name="scan")

console = Console()


def _parse_window(window: Optional[str]) -> Optional[int]:
    """Parse a window string like '30d', '90d', '90', or None."""
    if window is None or window.lower() in ("all", "all-time", "none"):
        return None
    raw = window.lower().replace("d", "").strip()
    try:
        return int(raw)
    except ValueError:
        console.print(f"[red]Invalid window: {window}. Use e.g. 30d, 90d, or 'all'.[/red]")
        raise typer.Exit(1)


@scan_app.command("youtube")
def scan_youtube(
    channel: list[str] = typer.Option(
        ...,
        "--channel", "-c",
        help="YouTube channel handle (e.g. @MrBeast), URL, or channel ID. Repeatable.",
    ),
    limit: int = typer.Option(
        50,
        "--limit", "-l",
        help="Maximum number of recent videos to fetch per channel.",
    ),
    threshold: float = typer.Option(
        3.0,
        "--threshold", "-t",
        help="Minimum outlier score to flag (views / channel avg).",
    ),
    method: str = typer.Option(
        "mean",
        "--method", "-m",
        help="Average calculation method: 'mean' or 'median'.",
    ),
    window: Optional[str] = typer.Option(
        None,
        "--window", "-w",
        help="Time window filter: '30d', '90d', '365d', or 'all' (default: all).",
    ),
    output: str = typer.Option(
        "table",
        "--output", "-o",
        help="Output format: 'table', 'json', or 'csv'.",
    ),
    quick: bool = typer.Option(
        False,
        "--quick", "-q",
        help="Quick mode: terminal output only, skip saving files.",
    ),
    no_save: bool = typer.Option(
        False,
        "--no-save",
        help="Don't save raw data or outlier files.",
    ),
) -> None:
    """Scan YouTube channels for outlier videos."""
    from contentradar.core.youtube import get_channel_videos, save_raw_data
    from contentradar.core.outlier import calculate_outliers, save_outliers
    from contentradar.output.terminal import (
        print_scan_header,
        print_outliers_table,
        print_save_info,
    )
    from contentradar.output.csv_writer import export_csv

    if method not in ("mean", "median"):
        console.print("[red]--method must be 'mean' or 'median'[/red]")
        raise typer.Exit(1)

    if output not in ("table", "json", "csv"):
        console.print("[red]--output must be 'table', 'json', or 'csv'[/red]")
        raise typer.Exit(1)

    window_days = _parse_window(window)

    for ch in channel:
        try:
            _scan_one_channel(
                channel=ch,
                limit=limit,
                threshold=threshold,
                method=method,
                window_days=window_days,
                output_format=output,
                quick=quick,
                no_save=no_save,
            )
        except SystemExit:
            # Gracefully skip failed channels in multi-channel mode
            if len(channel) > 1:
                console.print(f"[yellow]⚠ Skipping {ch}, moving to next channel…[/yellow]\n")
                continue
            raise


def _scan_one_channel(
    channel: str,
    limit: int,
    threshold: float,
    method: str,
    window_days: Optional[int],
    output_format: str,
    quick: bool,
    no_save: bool,
) -> None:
    """Core scan logic for a single channel."""
    from contentradar.core.youtube import get_channel_videos, save_raw_data
    from contentradar.core.outlier import calculate_outliers, save_outliers
    from contentradar.output.terminal import (
        print_scan_header,
        print_outliers_table,
        print_save_info,
    )
    from contentradar.output.csv_writer import export_csv

    # 1. Fetch videos
    data = get_channel_videos(channel, limit=limit)

    # 2. Save raw data
    raw_path = None
    if not quick and not no_save:
        raw_path = save_raw_data(data)

    # 3. Calculate outliers
    outliers, channel_avg, total_videos = calculate_outliers(
        data["videos"],
        method=method,
        window_days=window_days,
        threshold=threshold,
    )

    # 4. Output
    if output_format == "json":
        result = {
            "channel": data["channel_handle"],
            "channel_name": data["channel_name"],
            "channel_id": data["channel_id"],
            "channel_avg_views": channel_avg,
            "method": method,
            "threshold": threshold,
            "total_videos": total_videos,
            "outlier_count": len(outliers),
            "outliers": [o.to_dict() for o in outliers],
        }
        console.print_json(json.dumps(result, default=str))
    else:
        # Table output (default + csv also prints table)
        print_scan_header(
            channel_handle=data["channel_handle"],
            channel_name=data["channel_name"],
            total_videos=total_videos,
            channel_avg=channel_avg,
            method=method,
            threshold=threshold,
            window_days=window_days,
        )
        print_outliers_table(outliers, channel_avg)

    # 5. Save outliers
    outlier_path = None
    csv_path = None
    if not quick and not no_save:
        outlier_path = save_outliers(
            outliers=outliers,
            channel_id=data["channel_id"],
            channel_name=data["channel_name"],
            channel_avg=channel_avg,
            method=method,
            threshold=threshold,
            window_days=window_days,
            total_videos=total_videos,
        )

        if output_format == "csv":
            csv_path = export_csv(
                outliers=outliers,
                channel_id=data["channel_id"],
                channel_name=data["channel_name"],
                channel_avg=channel_avg,
                method=method,
            )

    if output_format != "json":
        print_save_info(raw_path, outlier_path or csv_path)


@app.command("version")
def version() -> None:
    """Show ContentRadar version."""
    console.print(f"ContentRadar v{__version__}")


if __name__ == "__main__":
    app()
