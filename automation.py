"""
automation.py
==============
Portfolio Example — "Automate Any Repetitive Task with a Custom Python Script"
By: juitindev @ GitHub | Fiverr

Scenario:
    Client has a folder of mixed files dumped in one place every day.
    This script:
    - Watches a folder for new files
    - Auto-sorts them into subfolders by type (images/docs/data/video/other)
    - Renames files with a timestamp prefix to avoid collisions
    - Logs every action to a daily log file
    - Sends a summary report at the end
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
WATCH_FOLDER  = "./inbox"          # folder to monitor
OUTPUT_FOLDER = "./sorted"         # destination root
LOG_FOLDER    = "./logs"

FILE_TYPES = {
    "images" : [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
    "docs"   : [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv", ".pptx"],
    "data"   : [".json", ".xml", ".yaml", ".yml", ".sql", ".db"],
    "video"  : [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "code"   : [".py", ".js", ".ts", ".html", ".css", ".sh"],
    "audio"  : [".mp3", ".wav", ".flac", ".aac"],
}

# ── Setup ──────────────────────────────────────────────────────────────────────
def setup_logging():
    os.makedirs(LOG_FOLDER, exist_ok=True)
    log_file = os.path.join(LOG_FOLDER, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file


def get_category(ext: str) -> str:
    ext = ext.lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "other"


def add_timestamp(filename: str) -> str:
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{stem}{suffix}"


def sort_files(watch_folder: str) -> dict:
    stats = {"moved": 0, "skipped": 0, "errors": 0, "breakdown": {}}

    files = [f for f in Path(watch_folder).iterdir() if f.is_file()]
    if not files:
        logging.info("No files found in inbox.")
        return stats

    for file_path in files:
        try:
            category = get_category(file_path.suffix)
            dest_dir = Path(OUTPUT_FOLDER) / category
            dest_dir.mkdir(parents=True, exist_ok=True)

            new_name = add_timestamp(file_path.name)
            dest_path = dest_dir / new_name

            # Avoid overwriting
            if dest_path.exists():
                logging.warning(f"SKIP (exists): {file_path.name}")
                stats["skipped"] += 1
                continue

            shutil.move(str(file_path), str(dest_path))
            logging.info(f"MOVED  [{category:6}]  {file_path.name} → {new_name}")
            stats["moved"] += 1
            stats["breakdown"][category] = stats["breakdown"].get(category, 0) + 1

        except Exception as e:
            logging.error(f"ERROR: {file_path.name} — {e}")
            stats["errors"] += 1

    return stats


def print_summary(stats: dict, log_file: str):
    print("\n" + "="*50)
    print("  AUTOMATION SUMMARY")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    print(f"  Files moved   : {stats['moved']}")
    print(f"  Files skipped : {stats['skipped']}")
    print(f"  Errors        : {stats['errors']}")
    if stats["breakdown"]:
        print("\n  Breakdown by type:")
        for cat, count in sorted(stats["breakdown"].items()):
            print(f"    {cat:<10} : {count} file(s)")
    print(f"\n  Log saved → {log_file}")
    print("="*50)


# ── Demo Setup ─────────────────────────────────────────────────────────────────
def create_demo_files():
    os.makedirs(WATCH_FOLDER, exist_ok=True)
    demo_files = [
        "invoice_march.pdf", "profile_photo.jpg", "sales_data.csv",
        "config.json", "intro_video.mp4", "notes.txt",
        "script.py", "unknown_file.xyz", "report.xlsx"
    ]
    for f in demo_files:
        Path(os.path.join(WATCH_FOLDER, f)).touch()
    print(f"[Demo] Created {len(demo_files)} sample files in {WATCH_FOLDER}/\n")


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log_file = setup_logging()

    if not os.path.exists(WATCH_FOLDER) or not os.listdir(WATCH_FOLDER):
        create_demo_files()

    logging.info(f"Starting file sorter — watching: {WATCH_FOLDER}")
    stats = sort_files(WATCH_FOLDER)
    print_summary(stats, log_file)
