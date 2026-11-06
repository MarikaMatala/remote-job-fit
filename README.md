# Remote Job Fit

An open-source, configurable experiment for exploring job discovery and comparing job requirements with a private skills profile. It is being developed as a practical way to map skills, identify possible career directions, and learn how a job-matching tool could work. It includes a Python command-line tool, a TypeScript browser dashboard, and an editable example profile.

The first version was created to help its author map their own skills and explore suitable job titles across IT, ICT, software development, digital media, design, and communications. The public project has since been made generic so anyone can adapt it to their own background, interests, experience, and career goals. The example role titles and skill groups are starting points only—not a CV, a list of required skills, or verified qualifications. Keep your personal profile in the private local configuration file. The public repository contains no personal profile, contact details, passwords, API keys, access tokens, or email credentials.

> **Project status: WORK IN PROGRESS — EXPERIMENTAL.** This is an unfinished learning and development experiment. Features, configuration formats, and interfaces may change. Some planned functionality is not implemented yet. Do not use it as a production recruitment, security, or eligibility decision system.

## Features

- Fetches job listings from supported public sources (Remotive and Remote OK).
- Filters for roles advertised as worldwide / work-from-anywhere remote. Treats ambiguous location policies cautiously.
- Compares job descriptions with skills from a local, private profile.
- Shows a transparent **skill-match score (0–10)**, matched skills, missing skills, and evidence coverage.
- Records publication date, application deadline (when supplied), and the date the listing was first discovered.
- Stores discovered jobs in a local SQLite database.
- Optionally sends an email digest through an SMTP server configured locally.
- Supports CSV export for further analysis.
- Includes an optional TypeScript dashboard (Vite) backed by a local Python FastAPI service.
- Includes editable role-title examples and skill groups spanning software development, web and mobile development, IT support, infrastructure, cloud, cybersecurity, data, UI/UX, graphic design, media production, digital marketing, communications, testing, and project coordination.

## Technology stack

| Language / technology | Responsibility |
| --- | --- |
| Python | Job-source adapters, filtering, skill matching, database access, command-line interface, and HTTP API |
| TypeScript | Browser dashboard behavior and API communication |
| HTML | Dashboard document structure |
| CSS | Responsive dashboard layout and visual styling |
| SQL | SQLite schema and data queries |
| JSON | API request/response data and serialized analysis |
| YAML | Local profile and job-source configuration |

These are integrated parts of one application. The TypeScript dashboard calls the Python API; it does not duplicate the job-matching engine.

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
- Node.js 22 or newer and npm (only if you want to use the browser dashboard)
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
.venv\\Scripts\\Activate.ps1
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

Windows PowerShell:

```powershell
Copy-Item config/profile.example.yaml config/profile.yaml
```

macOS / Linux:

```bash
cp config/profile.example.yaml config/profile.yaml
```

Open `config/profile.yaml` in a text editor. Replace the example job titles, skill groups, levels, and keywords with your own. Remove anything that does not fit you and add your own roles, tools, technologies, and media or communications skills. The private file is excluded from Git.

### 5. Configure job sources (optional)

If you want to change source settings, copy the example:

```bash
cp config/sources.example.yaml config/sources.yaml
```

Edit `config/sources.yaml` locally. You can enable or disable supported sources and change the restriction phrases used by the filter. The local file is ignored by Git.

### 6. Configure email (optional)

Copy `.env.example` to `.env`:

Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

macOS / Linux:
```bash
cp .env.example .env
```

Open `.env` in a text editor and enter your own SMTP server settings. Leave email settings blank if you do not want email digests. Never commit `.env` or share its contents.

## What can I customize?

| File | What to change | Where the information belongs |
| --- | --- | --- |
| `config/profile.yaml` | Target job titles, skill names, skill levels, skill keywords, experience keywords, excluded keywords | Your own private local profile |
| `config/sources.yaml` | Enable/disable supported job sources, source endpoint URLs, phrases that indicate geographic restrictions | Your own local source settings |
| `.env` | SMTP host, port, username, password, sender, recipient, TLS option, database path | Local environment settings; never commit |
| `config/profile.example.yaml` | Generic example structure only | Public template; use fictional data only |
| `config/sources.example.yaml` | Generic source defaults and example filter phrases | Public template; do not add personal data |
| `.env.example` | Empty setting names and safe defaults | Public template; never put real credentials here |

The example profile is deliberately broad so you can make the project your own. You do not need to keep every suggested role or skill. For a field-by-field guide and safe customization steps, read **[Configuration Guide](docs/CONFIGURATION.md)**. The example job families and skills are informed by public job adverts and market listings reviewed in November 2026; see **[Role and Skill Research](docs/ROLE-RESEARCH.md)** for the dated source list, examples and limitations.

## Usage

Run a search:

```bash
remotefit scan
```

List saved jobs:

```bash
remotefit list
```

Export saved jobs to CSV:

```bash
remotefit export --output exports/jobs.csv
```

Send an email digest (requires local SMTP settings):

```bash
remotefit digest
```

Run tests:

```bash
pytest
```

## Browser dashboard (Python + TypeScript)

The repository includes a small browser dashboard. Python continues to handle job-source requests, filtering, scoring, and SQLite storage. TypeScript handles the browser interface. The dashboard communicates with the local FastAPI service over HTTP; it does not contain profile data or SMTP credentials.

Install the Python project and create your private profile using the steps above. Then install the dashboard dependencies:

```bash
cd web
npm install
```

Start the Python API from the repository root in one terminal:

```bash
uvicorn remotefit.api:app --host 127.0.0.1 --port 8000
```

Start the TypeScript development server in a second terminal:

```bash
cd web
npm run dev
```

Open the local address printed by Vite (normally `http://127.0.0.1:5173`). The dashboard can display saved listings and trigger a scan of the configured public sources.

To create a production frontend build:

```bash
cd web
npm run build
```

The generated static files are written to `web/dist/`. The current setup keeps the dashboard and API as separate local processes; it does not publish either service to the internet. Keep the API bound to `127.0.0.1` unless you have deliberately configured authentication and network security for another deployment.

## Scoring

The current MVP uses a transparent keyword overlap calculation:
- **Match score:** proportion of distinct profile skill keywords found in the job text, scaled to 0–10.
- **Evidence coverage:** proportion of the profile's skill groups with at least one matching keyword.
- **Matched / missing skills:** displayed so the score can be reviewed rather than treated as a black box.

Only the `skills` section and its `keywords` are currently used by the Python job-scoring function. Target titles, skill levels, experience keywords, and excluded keywords are stored as configurable profile fields but are not yet applied to that score or filtering logic. The separate portfolio browser demo has its own illustrative sample roles and scoring logic. See the configuration guide for this distinction.

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

Never commit personal data, passwords, access tokens, API keys, private email addresses, private API URLs, or database files. The current public job-source adapters do not require API keys. Do not add secrets to frontend files or public examples.

## Project status

This is an unfinished work-in-progress experiment and early MVP, not a completed product. It began as a personal skills-mapping and career-exploration exercise; the public example configuration is now intentionally generic and can be reshaped for different IT, ICT, media, design, and communications paths. The first version focuses on public-source discovery, worldwide-remote filtering, private profile matching, local tracking, and optional email digests. The browser dashboard and local API are also experimental and have not been security-audited for public deployment. Applicant-count extraction, deadline parsing across varied formats, richer company research, and additional source adapters are future improvements.

## Contributing

Issues and pull requests are welcome. Keep examples fictional and generic. Never submit real personal information, credentials, private job-search data, or database exports.

## License

MIT. See [LICENSE](LICENSE).
