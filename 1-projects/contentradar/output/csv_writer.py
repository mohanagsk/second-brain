"""CSV export for ContentRadar outlier results."""

from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Optional


def export_csv(
    outliers: list,
    channel_id: str,
    channel_name: str,
    channel_avg: float,
    method: str,
    base_path: str = "data/outliers/youtube",
) -> str:
    """Export outlier results to CSV. Returns file path."""
    os.makedirs(base_path, exist_ok=True)
    path = os.path.join(base_path, f"{channel_id}.csv")

    fieldnames = [
        "rank",
        "platform",
        "channel",
        "title",
        "url",
        "views",
        "channel_avg",
        "outlier_score",
        "likes",
        "comments",
        "duration_seconds",
        "published_at",
        "percentile",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, o in enumerate(outliers, 1):
            d = o.to_dict() if hasattr(o, "to_dict") else dict(o)
            writer.writerow({
                "rank": i,
                "platform": "youtube",
                "channel": channel_name,
                "title": d.get("title", ""),
                "url": d.get("url", ""),
                "views": d.get("views", 0),
                "channel_avg": channel_avg,
                "outlier_score": f"{d.get('outlier_score', 0)}x",
                "likes": d.get("likes", 0),
                "comments": d.get("comments", 0),
                "duration_seconds": d.get("duration_seconds", 0),
                "published_at": d.get("published_at", ""),
                "percentile": d.get("percentile", 0),
            })

    return path
