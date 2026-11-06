# Remote Job Fit

An open-source, configurable tool for discovering worldwide-remote jobs, comparing job requirements with a private skills profile, tracking application deadlines, and optionally sending email digests.

The project is designed for anyone. It contains no personal profile, personal contact details, account names, passwords, API keys, or email credentials.

## Features

- Fetches job listings from supported public sources (Remotive and Remote OK).
- Filters for roles advertised as worldwide / work-from-anywhere remote. Treats ambiguous location policies cautiously.
- Compares job descriptions with skills from a local, private profile.
- Shows a transparent **skill-match score (0–10)**, matched skills, missing skills, and evidence coverage.
- Records publication date, application deadline (when supplied), and the date the listing was first discovered.
- Stores discovered jobs in a local SQLite database.
- Optionally sends an email digest through an SMTP server configured locally.
- Supports CSV export for further analysis.

## Important limitations

- A skill-match score is an estimate based on text matching. It is **not** a hiring probability, an assessment of personal worth, or a guarantee of eligibility.
- Applicant counts are shown only when a source explicitly provides them. A simple applicant-to-opening ratio is not a probability of being hired.
- Company hiring success rates from previous recruitment processes are not inferred. They are reported as unavailable unless reliable, public, role-specific data is supplied.
- Company fit is not currently calculated automatically. Company research should be recorded separately with dated, verifiable evidence.
- "Remote" does not necessarily mean "work from anywhere". Listings with country, region, residency, or time-zone restrictions are excluded where the restriction is identifiable. Always verify eligibility on the employer's application page.
- Job sources can change their APIs, terms, and availability. Respect each source's terms and rate limits.
- LinkedIn is not scraped. Use LinkedIn's own saved-search notifications or manually import a listing only where permitted. Do not automate login, bypass access controls, or scrape restricted pages.

## Requirements

- Python 3.11 or newer
- Internet access for public job-source requests
- Optional: an SMTP account if email digests are required

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/MarikaMatala/remote-job-fit.git
cd remote-job-fit
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Create your private profile

Copy the example file:

Windows PowerShell:
```powershell
Copy-Item config/profile.example.yaml config/profile.yaml
```

macOS / Linux:
```bash
cp config/profile.example.yaml config/profile.yaml
```

Edit `config/profile.yaml` on your own device. Add only the information you want the local tool to use, such as skills, target job titles, experience keywords, and excluded keywords.

**Do not commit your private profile.** The file is ignored by Git.

### 5. Configure sources

Copy the source example if you want to customize source settings:

```bash
cp config/sources.example.yaml config/sources.yaml
```

The built-in public sources are configured in the example. The local `config/sources.yaml` file is ignored by Git.

### 6. Optional email configuration

Copy `.env.example` to `.env` and fill in your own SMTP settings:

```bash
cp .env.example .env
```

Never commit `.env`. Use an app-specific password or provider-approved authentication method where applicable. Do not place credentials in YAML files, source code, command-line arguments, or commits.

## Usage

Run a search:

```bash
remotefit scan
```

List saved jobs:

```bash
remotefit list
```

Show jobs as CSV:

```bash
remotefit export --output jobs.csv
```

Send an email digest (requires local SMTP settings):

```bash
remotefit digest
```

Run tests:

```bash
pytest
```

## Private configuration

The example profile uses fictional placeholders. Replace them locally:

```yaml
profile:
  target_titles:
    - "Example Developer"
  skills:
    - name: "Python"
      level: 3
      keywords: ["python", "pytest"]
    - name: "Accessibility"
      level: 2
      keywords: ["accessibility", "wcag", "a11y"]
  experience_keywords:
    - "teamwork"
  excluded_keywords:
    - "on-site only"
```

Skill levels are user-defined from 1 to 5. They are used for context only; the matching algorithm does not claim to validate proficiency.

## Scoring

The current MVP uses a transparent keyword overlap calculation:
- **Match score:** proportion of distinct profile skill keywords found in the job text, scaled to 0–10.
- **Evidence coverage:** proportion of the profile's skill groups with at least one matching keyword.
- **Matched / missing skills:** displayed so the score can be reviewed rather than treated as a black box.

This is a preliminary screening aid. It does not yet evaluate seniority, legal work eligibility, compensation, language requirements, interview performance, or company culture.

## Data and privacy

- Personal profile: `config/profile.yaml` (local only; ignored by Git).
- Local source overrides: `config/sources.yaml` (ignored by Git).
- Email secrets: `.env` (ignored by Git).
- Database: `data/jobs.sqlite3` (ignored by Git).
- Exports: `exports/` (ignored by Git).

Before committing, check:

```bash
git status --short
git check-ignore config/profile.yaml .env data/jobs.sqlite3
```

Never commit personal data, passwords, access tokens, API keys, private email addresses, or database files.

## Project status

This is an early MVP. The first version focuses on public-source discovery, worldwide-remote filtering, private profile matching, local tracking, and optional email digests. Applicant-count extraction, deadline parsing across varied formats, richer company research, and additional source adapters are future improvements.

## Contributing

Issues and pull requests are welcome. Keep examples fictional and generic. Never submit real personal information, credentials, private job-search data, or database exports.

## License

MIT. See [LICENSE](LICENSE).
