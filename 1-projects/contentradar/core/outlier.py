"""Outlier score calculation engine."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from statistics import mean, median
from typing import Optional


@dataclass
class OutlierResult:
    video_id: str
    title: str
    url: str
    views: int
    likes: int
    comments: int
    duration_seconds: int
    published_at: Optional[str]
    channel_avg: float
    outlier_score: float
    percentile: float
    thumbnail_url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _filter_by_window(videos: list[dict], window_days: Optional[int]) -> list[dict]:
    """Filter videos to those published within window_days of today."""
    if window_days is None:
        return videos

    cutoff = datetime.utcnow() - timedelta(days=window_days)
    filtered = []
    for v in videos:
        pub = v.get("published_at") or v.get("upload_date")
        if pub is None:
            # No date info — include by default
            filtered.append(v)
            continue
        try:
            if len(pub) == 8:
                dt = datetime.strptime(pub, "%Y%m%d")
            else:
                dt = datetime.strptime(pub[:10], "%Y-%m-%d")
            if dt >= cutoff:
                filtered.append(v)
        except ValueError:
            filtered.append(v)  # can't parse — include
    return filtered


def _calculate_percentile(views: int, all_videos: list[dict]) -> float:
    """What percentage of videos does this one beat?"""
    total = len(all_videos)
    if total <= 1:
        return 100.0
    count_below = sum(1 for v in all_videos if v["views"] < views)
    return round((count_below / total) * 100, 1)


def calculate_outliers(
    videos: list[dict],
    method: str = "mean",
    window_days: Optional[int] = None,
    threshold: float = 3.0,
) -> tuple[list[OutlierResult], float, int]:
    """Calculate outlier scores for a list of videos.

    Returns:
        (outliers, channel_avg, total_videos_in_window)
    """
    filtered = _filter_by_window(videos, window_days)

    if not filtered:
        return [], 0.0, 0

    view_counts = [v["views"] for v in filtered]

    if method == "median":
        avg = median(view_counts)
    else:
        avg = mean(view_counts)

    # Prevent division by zero
    if avg <= 0:
        avg = 1.0

    results = []
    for v in filtered:
        score = v["views"] / avg
        if score >= threshold:
            results.append(
                OutlierResult(
                    video_id=v["id"],
                    title=v["title"],
                    url=v.get("url", f"https://www.youtube.com/watch?v={v['id']}"),
                    views=v["views"],
                    likes=v.get("likes", 0),
                    comments=v.get("comments", 0),
                    duration_seconds=v.get("duration_seconds", 0),
                    published_at=v.get("published_at"),
                    channel_avg=round(avg, 2),
                    outlier_score=round(score, 2),
                    percentile=_calculate_percentile(v["views"], filtered),
                    thumbnail_url=v.get("thumbnail_url", ""),
                )
            )

    results.sort(key=lambda r: r.outlier_score, reverse=True)
    return results, round(avg, 2), len(filtered)


def save_outliers(
    outliers: list[OutlierResult],
    channel_id: str,
    channel_name: str,
    channel_avg: float,
    method: str,
    threshold: float,
    window_days: Optional[int],
    total_videos: int,
    base_path: str = "data/outliers/youtube",
) -> str:
    """Save outlier results to JSON. Returns file path."""
    os.makedirs(base_path, exist_ok=True)
    path = os.path.join(base_path, f"{channel_id}.json")

    payload = {
        "channel_id": channel_id,
        "channel_name": channel_name,
        "channel_avg_views": channel_avg,
        "method": method,
        "threshold": threshold,
        "window_days": window_days,
        "total_videos_scanned": total_videos,
        "outlier_count": len(outliers),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "outliers": [o.to_dict() for o in outliers],
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    return path
