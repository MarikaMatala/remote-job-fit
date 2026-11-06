"""Command-line interface.

WORK IN PROGRESS: configure personal job-search data in the ignored local
config/profile.yaml file. Configure SMTP credentials only in the ignored local
.env file. Never hard-code personal details, API keys, or passwords here.
"""

import argparse
import csv
from pathlib import Path

from .analysis import is_worldwide_remote, score_job
from .config import load_settings
from .db import connect, list_jobs, save_jobs
from .emailer import send_digest
from .sources import fetch_all


def scan(settings):
    jobs, errors = fetch_all(settings["sources"])
    accepted = []
    for job in jobs:
        if not is_worldwide_remote(job, settings["filters"].get("reject_restrictions", [])):
            continue
        job["analysis"] = score_job(settings["profile"], job)
        accepted.append(job)
    connection = connect(settings["database_path"])
    inserted = save_jobs(connection, accepted)
    connection.close()
    print(f"Fetched {len(jobs)} listings; {len(accepted)} passed the worldwide-remote filter.")
    print(f"Saved {inserted} new listings. Existing listings are not duplicated.")
    for error in errors:
        print(f"Source warning: {error}")


def show_list(settings):
    connection = connect(settings["database_path"])
    rows = list_jobs(connection)
    connection.close()
    if not rows:
        print("No jobs saved yet. Run 'remotefit scan' first.")
        return
    for row in rows:
        print(
            f"[{row['score'] if row['score'] is not None else 'N/A'}/10] "
            f"{row['title']} — {row['company']} | "
            f"Published: {row['published_at'] or 'unknown'} | "
            f"Deadline: {row['deadline'] or 'not provided'} | "
            f"First seen: {row['first_seen_at']}\n{row['url']}\n"
        )


def export_jobs(settings, output):
    connection = connect(settings["database_path"])
    rows = list_jobs(connection, limit=10000)
    connection.close()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["title", "company", "location", "score", "published_at", "deadline", "first_seen_at", "url"])
        for row in rows:
            writer.writerow([row["title"], row["company"], row["location"], row["score"], row["published_at"], row["deadline"], row["first_seen_at"], row["url"]])
    print(f"Exported {len(rows)} jobs to {output}")


def digest(settings):
    connection = connect(settings["database_path"])
    rows = list_jobs(connection, limit=25)
    connection.close()
    jobs = [dict(row) for row in rows]
    for job in jobs:
        import json
        job["analysis"] = json.loads(job.get("analysis_json") or "{}")
    send_digest(settings["smtp"], jobs)
    print(f"Email digest sent with {len(jobs)} saved listings.")


def main():
    parser = argparse.ArgumentParser(prog="remotefit", description="Discover and analyse worldwide-remote jobs.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan", help="Fetch and analyse current public listings.")
    subparsers.add_parser("list", help="List saved job listings.")
    export_parser = subparsers.add_parser("export", help="Export saved listings to CSV.")
    export_parser.add_argument("--output", default="exports/jobs.csv")
    subparsers.add_parser("digest", help="Email a digest of saved listings.")
    args = parser.parse_args()
    try:
        settings = load_settings()
        if args.command == "scan":
            scan(settings)
        elif args.command == "list":
            show_list(settings)
        elif args.command == "export":
            export_jobs(settings, args.output)
        elif args.command == "digest":
            digest(settings)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
