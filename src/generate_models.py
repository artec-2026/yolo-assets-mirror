"""
Fetch ultralytics/assets latest release and generate yolo_models.json.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import requests

GITHUB_API = "https://api.github.com/repos/ultralytics/assets/releases/latest"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "yolo_models.json")

TASK_RULES = [
    # special suffixes first (most specific)
    (r"-semseg\.pt$", "Semantic Segmentation"),
    (r"-seg-pf\.pt$", "Instance Segmentation"),
    (r"-seg\.pt$", "Instance Segmentation"),
    (r"-objv1-seg\.pt$", "Instance Segmentation"),
    (r"-pose\.pt$", "Pose Estimation"),
    (r"-obb\.pt$", "Oriented Bounding Box"),
    (r"-cls\.pt$", "Classification"),
    (r"-depth\.pt$", "Depth Estimation"),
    (r"-s3d\.pt$", "3D Object Detection"),
    (r"-stereo3ddet", "Stereo 3D Detection"),
    (r"-objv1-\d+\.pt$", "Object Detection"),
    # model-family prefixes
    (r"(?i)^(fast)?sam", "Segmentation"),
    (r"(?i)^mobile_sam", "Segmentation"),
    (r"(?i)^sam2", "Segmentation"),
    (r"(?i)^yoloe", "Instance Segmentation"),
    (r"(?i)^rtdetr", "Object Detection"),
    (r"(?i)^yolo_nas", "Object Detection"),
    # catch-all
    (r"\.pt$", "Object Detection"),
]

VERSION_PATTERNS = [
    (r"^yolo26", "YOLO26"),
    (r"^yoloe-26", "YOLO26"),
    (r"^yolo12", "YOLO12"),
    (r"^yolo11", "YOLO11"),
    (r"^yoloe-11", "YOLO11"),
    (r"^yolov10", "YOLOv10"),
    (r"^yolov9", "YOLOv9"),
    (r"^yoloe-v8", "YOLOv8"),
    (r"^yolov8", "YOLOv8"),
    (r"^yolov5", "YOLOv5"),
    (r"^yolov3", "YOLOv3"),
    (r"^yolo_nas", "YOLO-NAS"),
    (r"(?i)^(fast)?sam|^mobile_sam|^sam2", "SAM"),
    (r"(?i)^rtdetr", "RT-DETR"),
]


def detect_task(filename: str) -> str:
    for pattern, task in TASK_RULES:
        if re.search(pattern, filename):
            return task
    return "Unknown"


def detect_version_series(filename: str) -> str:
    lower = filename.lower()
    for pattern, label in VERSION_PATTERNS:
        if re.match(pattern, lower):
            return label
    return "YOLO"


def bytes_to_mb(size: int) -> float:
    return round(size / (1024 * 1024), 1)


def fetch_latest_release(token: str | None = None) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(GITHUB_API, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_registry(release: dict) -> dict:
    tag = release["tag_name"]
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    models = []
    for asset in release.get("assets", []):
        name = asset["name"]
        if not name.endswith(".pt"):
            continue
        stem = name[: name.rfind(".")]  # strip .pt
        models.append(
            {
                "name": stem,
                "version": detect_version_series(name),
                "task": detect_task(name),
                "download_url": asset["browser_download_url"],
                "file_size_mb": bytes_to_mb(asset["size"]),
            }
        )

    models.sort(key=lambda m: (m["version"], m["name"]))

    return {
        "version": tag,
        "last_updated": updated,
        "models": models,
    }


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    try:
        release = fetch_latest_release(token)
    except requests.HTTPError as exc:
        print(f"GitHub API error: {exc}", file=sys.stderr)
        sys.exit(1)

    registry = build_registry(release)

    output = os.path.abspath(OUTPUT_PATH)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"Generated {output}")
    print(f"  version : {registry['version']}")
    print(f"  models  : {len(registry['models'])}")


if __name__ == "__main__":
    main()
