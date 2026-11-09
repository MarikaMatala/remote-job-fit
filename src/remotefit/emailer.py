"""Optional SMTP email digest delivery.

WORK IN PROGRESS: configure your own SMTP host, username, app password,
sender, and recipient in the ignored local .env file. Never hard-code them
here or commit them. Do not use this module to send credentials in email.
"""

import smtplib
from email.message import EmailMessage


def send_digest(settings, jobs):
    required = ("host", "username", "password", "from", "to")
    missing = [key for key in required if not settings.get(key)]
    if missing:
        raise RuntimeError(
            "Email is not configured. Set the required SMTP values in your local .env file."
        )
    message = EmailMessage()
    message["Subject"] = f"Remote Job Fit: {len(jobs)} saved matching listings"
    message["From"] = settings["from"]
    message["To"] = settings["to"]
    lines = []
    for job in jobs:
        lines.extend([
            f"{job.get('title', 'Untitled')} — {job.get('company', 'Unknown company')}",
            f"Source: {job.get('source') or 'Unknown source'}",
            f"Match score: {job.get('analysis', {}).get('score', 'N/A')}/10",
            f"Published: {job.get('published_at') or 'Not provided'}",
            f"Deadline: {job.get('deadline') or 'Not provided'}",
            f"First seen: {job.get('fetched_at') or 'Not recorded'}",
            f"Original listing: {job.get('url', '')}",
            "",
        ])
    message.set_content("\n".join(lines) if lines else "No new matching jobs were found.")
    with smtplib.SMTP(settings["host"], settings["port"], timeout=20) as server:
        if settings.get("use_tls", True):
            server.starttls()
        server.login(settings["username"], settings["password"])
        server.send_message(message)
