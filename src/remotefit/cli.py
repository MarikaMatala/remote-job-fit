"""Command-line interface.

WORK IN PROGRESS: configure personal job-search data in the ignored local
config/profile.yaml file. Configure SMTP credentials only in the ignored local
.env file. Never hard-code personal details, API keys, or passwords here.
"""

# KOMMENTOINTIOHJE / CODE MAP
# Tiedoston tarkoitus: Komentorivikäyttöliittymä: komentojen ja käyttäjän syötteiden käsittely.
# Rakenne: tuonnit ja asetukset ensin, tietorakenteet ja apufunktiot seuraavaksi, päätoiminnot lopuksi.
# FUNKTIOIDEN ALKUKOHDAT on merkitty erikseen, jotta niitä on helpompi etsiä.

import argparse
import csv
from pathlib import Path

from .analysis import is_worldwide_remote, score_job
from .config import load_settings
from .db import (
    connect, list_jobs, list_unsent_jobs, mark_jobs_sent,
    save_jobs, save_source_notice,
)
from .emailer import send_digest
from .sources import fetch_all


# FUNKTIO-OSIO ALKAA: scan.
def scan(settings):
    notices = []
    jobs, errors = fetch_all(
        settings["sources"],
        notice_callback=lambda source, notice: notices.append((source, notice)),
    )
    accepted = []
    for job in jobs:
        if not is_worldwide_remote(job, settings["filters"].get("reject_restrictions", [])):
            continue
        job["analysis"] = score_job(settings["profile"], job)
        accepted.append(job)
    connection = connect(settings["database_path"])
    inserted = save_jobs(connection, accepted)
    for source, notice in notices:
        save_source_notice(connection, source, notice)
    connection.close()
    for source, notice in notices:
        print(f"{source} API notice (last_updated: {notice.get('last_updated', 'not supplied')}):")
        print(notice["legal"])
    print(f"Fetched {len(jobs)} listings; {len(accepted)} passed the worldwide-remote filter.")
    print(f"Saved {inserted} new listings. Existing listings are not duplicated.")
    for error in errors:
        print(f"Source warning: {error}")


# FUNKTIO-OSIO ALKAA: show_list.
# FUNKTIO-OSIO PÄÄTTYY: scan. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
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
            f"{row['title']} — {row['company']} | Source: {row['source']} | "
            f"Published: {row['published_at'] or 'unknown'} | "
            f"Deadline: {row['deadline'] or 'not provided'} | "
            f"First seen: {row['first_seen_at']}\nOriginal listing: {row['url']}\n"
        )


# FUNKTIO-OSIO ALKAA: export_jobs.
# FUNKTIO-OSIO PÄÄTTYY: show_list. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def export_jobs(settings, output):
    connection = connect(settings["database_path"])
    rows = list_jobs(connection, limit=10000)
    connection.close()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "title", "company", "location", "score", "published_at", "deadline", "first_seen_at", "url"])
        for row in rows:
            writer.writerow([row["source"], row["title"], row["company"], row["location"], row["score"], row["published_at"], row["deadline"], row["first_seen_at"], row["url"]])
    print(f"Exported {len(rows)} jobs to {output}")


# FUNKTIO-OSIO ALKAA: digest.
# FUNKTIO-OSIO PÄÄTTYY: export_jobs. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def digest(settings):
    connection = connect(settings["database_path"])
    rows = list_unsent_jobs(connection, limit=25)
    if not rows:
        connection.close()
        print("No unsent saved listings to email. Previously sent listings were skipped.")
        return
    jobs = [dict(row) for row in rows]
    for job in jobs:
        import json
        job["analysis"] = json.loads(job.get("analysis_json") or "{}")
    # Mark as sent only after SMTP confirms successful message delivery.
    try:
        send_digest(settings["smtp"], jobs)
        mark_jobs_sent(connection, [job["id"] for job in jobs])
    finally:
        connection.close()
    print(f"Email digest sent with {len(jobs)} unsent saved listings.")


# FUNKTIO-OSIO ALKAA: main.
# FUNKTIO-OSIO PÄÄTTYY: digest. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
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

# FUNKTIO-OSIO PÄÄTTYY: main. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.