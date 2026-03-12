"""YouTube channel video metadata fetcher using yt-dlp."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console(stderr=True)


def _sanitise_handle(channel: str) -> str:
    """Turn a channel handle/URL into a safe filename-friendly string."""
    name = channel.strip().rstrip("/")
    # Strip URL parts
    for prefix in ("https://www.youtube.com/", "https://youtube.com/", "http://"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = name.strip("/").replace("/videos", "").replace("/", "_")
    return name or "unknown"


def _resolve_channel_url(channel: str) -> str:
    """Normalise a channel identifier into a YouTube videos URL."""
    channel = channel.strip()
    # Already a full URL
    if channel.startswith("http"):
        url = channel.rstrip("/")
        if not url.endswith("/videos"):
            url += "/videos"
        return url
    # Handle or channel ID
    if channel.startswith("@"):
        return f"https://www.youtube.com/{channel}/videos"
    if channel.startswith("UC"):
        return f"https://www.youtube.com/channel/{channel}/videos"
    # Treat as handle without @
    return f"https://www.youtube.com/@{channel}/videos"


def get_channel_videos(
    channel: str,
    limit: int = 50,
    sleep_interval: int = 2,
    max_sleep_interval: int = 5,
) -> dict:
    """Fetch video metadata for a channel via yt-dlp.

    Returns a dict with keys:
        channel_id, channel_name, channel_handle, videos: list[dict]
    """
    url = _resolve_channel_url(channel)

    # Use yt-dlp JSON dump — most reliable for metadata extraction
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--playlist-end", str(limit),
        "--sleep-interval", str(sleep_interval),
        "--max-sleep-interval", str(max_sleep_interval),
        "--no-warnings",
        "--extractor-args", "youtube:player_skip=webpage",
        url,
    ]

    console.print(f"[dim]Fetching up to {limit} videos from [cyan]{channel}[/cyan]…[/dim]")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min max
        )
    except subprocess.TimeoutExpired:
        console.print("[red]✗ yt-dlp timed out after 10 minutes[/red]")
        raise SystemExit(1)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "private" in stderr.lower() or "unavailable" in stderr.lower():
            console.print(f"[red]✗ Channel is private or unavailable: {channel}[/red]")
        elif "rate" in stderr.lower() or "429" in stderr:
            console.print(f"[red]✗ Rate-limited by YouTube. Try again later or increase sleep interval.[/red]")
        else:
            console.print(f"[red]✗ yt-dlp error:[/red] {stderr[:500]}")
        raise SystemExit(1)

    # Parse JSONL output (one JSON object per line)
    videos = []
    channel_id = None
    channel_name = None
    channel_handle = channel

    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Extract channel info from first entry
        if channel_id is None:
            channel_id = (
                entry.get("channel_id")
                or entry.get("uploader_id")
                or entry.get("playlist_uploader_id")
                or _sanitise_handle(channel)
            )
            channel_name = (
                entry.get("channel")
                or entry.get("uploader")
                or entry.get("playlist_uploader")
                or channel
            )

        view_count = entry.get("view_count")
        if view_count is None:
            # Skip entries without view data (e.g. upcoming premieres)
            continue

        upload_date = entry.get("upload_date")  # YYYYMMDD
        published_at = None
        if upload_date and len(upload_date) == 8:
            try:
                published_at = datetime.strptime(upload_date, "%Y%m%d").strftime("%Y-%m-%d")
            except ValueError:
                published_at = None

        duration = entry.get("duration") or 0

        videos.append({
            "id": entry.get("id", entry.get("url", "")),
            "title": entry.get("title", "Untitled"),
            "url": f"https://www.youtube.com/watch?v={entry.get('id', '')}",
            "views": int(view_count),
            "likes": int(entry.get("like_count") or 0),
            "comments": int(entry.get("comment_count") or 0),
            "duration_seconds": int(duration),
            "published_at": published_at,
            "upload_date": upload_date,
            "thumbnail_url": entry.get("thumbnail") or entry.get("thumbnails", [{}])[0].get("url", ""),
        })

    if not videos:
        console.print(f"[yellow]⚠ No videos found for {channel}[/yellow]")
        raise SystemExit(1)

    console.print(f"[green]✓ Found {len(videos)} videos for [bold]{channel_name}[/bold][/green]")

    return {
        "channel_id": channel_id,
        "channel_name": channel_name,
        "channel_handle": channel_handle,
        "videos": videos,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def save_raw_data(data: dict, base_path: str = "data/raw/youtube") -> str:
    """Persist raw channel data to JSON. Returns file path."""
    os.makedirs(base_path, exist_ok=True)
    channel_id = data.get("channel_id", "unknown")
    path = os.path.join(base_path, f"{channel_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path
