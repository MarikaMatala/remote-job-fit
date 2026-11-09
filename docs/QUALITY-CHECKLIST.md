# Quality assurance checklist

This checklist separates automated regression checks from manual browser and accessibility review. A passing CI workflow does not mean that the application has passed a complete security or accessibility audit.

## Automated checks

The CI workflow runs:

- Python unit and regression tests.
- Python dependency vulnerability audit with `pip-audit`.
- TypeScript type-check and Vite production build.
- Browser demo JavaScript syntax check and Node-based interaction regression tests.
- npm dependency audit for high-severity findings.
- A separate scheduled and push-triggered Gitleaks repository-history scan.
- Dependabot weekly update checks for Python, npm and GitHub Actions dependencies.

Review audit output rather than automatically suppressing a finding. Upgrade or pin affected dependencies where possible, and document any accepted risk.

## Browser and accessibility review

Run this checklist against the published demo and the local dashboard after meaningful UI changes:

- [ ] Complete all controls using only Tab, Shift+Tab, Enter, Space and arrow keys where appropriate.
- [ ] Confirm visible focus is never hidden behind sticky content and follows a logical reading order.
- [ ] Test with a screen reader (NVDA + Firefox/Chrome on Windows, and VoiceOver + Safari on Apple platforms where available).
- [ ] Confirm headings, labels, button names, link purpose, status messages and result updates are announced meaningfully.
- [ ] Check text and non-text contrast against WCAG 2.2 AA; do not rely on colour alone to communicate status.
- [ ] Zoom to 200% and 400%; verify no content or functionality is lost and horizontal scrolling is limited to content that requires it.
- [ ] Test narrow mobile widths, tablet widths, desktop and high-density displays.
- [ ] Enable reduced motion and verify that non-essential movement is removed or reduced.
- [ ] Check error, empty, loading, long-text and unusual-character states.
- [ ] Confirm external links are descriptive and open safely.
- [ ] Test Finnish and English language switching, including accessible names and document language.

The Node demo tests use a lightweight mocked DOM. They are regression tests for selected interactions and escaping, not a real-browser, assistive-technology, responsive-layout or WCAG conformance test. A complete manual review is still required.

## Repository safeguards

- Enable branch protection or a repository ruleset for `main`.
- Require pull requests and successful `Tests` and `Secret scan` checks before merging.
- Prevent force pushes and deletion of `main`.
- Enable GitHub secret scanning and push protection if available for the repository plan.
- Review Dependabot alerts and security advisories regularly.
- Keep the local API bound to `127.0.0.1`; do not expose it publicly without authentication, authorization, rate limiting and a separate security review.

## Local database backup, restore and deletion

The SQLite database contains saved third-party listing information, timestamps, provider notices and email-digest delivery state. Keep backups private and respect the source providers' terms.

Create a consistent backup with SQLite's backup API (run from the repository root):

```bash
python -c "import sqlite3; source=sqlite3.connect('data/jobs.sqlite3'); backup=sqlite3.connect('data/jobs-backup.sqlite3'); source.backup(backup); backup.close(); source.close()"
```

To restore, stop the application first, keep a copy of the current database if needed, and copy the backup over the configured database path. If you use a custom `DATABASE_PATH`, replace the example paths with that location.

To remove locally saved application data, stop the application and delete the configured SQLite database file. Also remove its matching `-wal` and `-shm` files if present, any CSV exports you created, and any backups. This removes saved listings, provider notices and digest history. It does not delete the source provider's original listings or messages already delivered by email. The Remotive request-interval cache is separate under `~/.cache/remote-job-fit/` (or `REMOTE_JOB_FIT_CACHE_DIR`) and can be removed separately if you intentionally want to reset that local rate-limit record.
