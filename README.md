# Remote Job Fit

<!-- Last reviewed: 2026-11-06 22:13 (Europe/Helsinki). -->

An open-source, configurable experiment for exploring job discovery and comparing job requirements with a private skills profile. It is being developed as a practical way to map skills, identify possible career directions, and learn how a job-matching tool could work. It includes a Python command-line tool, a TypeScript browser dashboard, and an editable example profile.

The first version was created to help its author map their own skills and explore suitable job titles across IT, ICT, software development, digital media, design, and communications. The public project has since been made generic so anyone can adapt it to their own background, interests, experience, and career goals. The example role titles and skill groups are starting points only—not a CV, a list of required skills, or verified qualifications. Keep your personal profile in the private local configuration file. The public repository contains no personal profile, contact details, passwords, API keys, access tokens, or email credentials.

## Why this project exists

Remote Job Fit has four connected purposes:

1. **A practical portfolio and work sample.** The project demonstrates its author's approach to planning, building, testing, documenting, reviewing, and improving a software project. It is intended to support job applications and make practical skills and development decisions visible. The repository and its history show an evolving process—not a claim that the author is an experienced specialist in every technology used.
2. **Learning through making.** The project is a hands-on environment for learning new tools, strengthening existing skills, experimenting with implementation choices, and understanding the full development cycle. Bugs, limitations, tests, and iterative improvements are part of that process.
3. **An open example others can learn from.** Job seekers, students, and developers are welcome to explore the source, use the project as inspiration, and adapt the ideas to their own job search, portfolio, or learning projects. The generic example profile is a starting point, not a prescribed career path or a claim about anyone's skills.
4. **A project that others can extend.** Contributions, constructive feedback, forks, and independent adaptations are welcome under the applicable licence and third-party data terms. You do not need to use the project exactly as provided; make it fit your needs and share improvements where useful.

The project is intentionally public so that its implementation and learning process can be inspected. It is an open-source learning and portfolio project with a practical job-search use case—not a commercial recruitment product or an automated decision-maker. See [CONTRIBUTING.md](CONTRIBUTING.md) for ways to participate.

> **Project status: WORK IN PROGRESS — EXPERIMENTAL.** This is an unfinished learning and development experiment. Features, configuration formats, and interfaces may change. Some planned functionality is not implemented yet. Do not use it as a production recruitment, security, or eligibility decision system.

> **CI status:** GitHub Actions runs the Python tests, TypeScript dashboard build, and browser-demo JavaScript syntax check on pushes and pull requests. These checks are blocking: a failure makes the workflow fail. Branch protection is not currently configured, so maintainers should require the checks and pull requests through a GitHub branch protection rule or repository ruleset.

## Live demo

An interactive browser-only preview is available at **[Remote Job Fit Demo](https://marikamatala.github.io/remote-job-fit/)** after the GitHub Pages deployment has been enabled and the changes have been merged into `main`. The public demo uses a simplified client-side matcher; it does not run the Python backend or fetch live job listings. For the full matching engine, use the local installation instructions below.

## Features

- Fetches job listings from supported public sources (Remotive and Remote OK), with a six-hour minimum interval for Remotive requests and validation/storage of Remote OK's live API legal notice.
- Identifies each provider and links back to the original listing in dashboard, CLI, CSV and email outputs.
- Filters for roles advertised as worldwide / work-from-anywhere remote. Treats ambiguous location policies cautiously.
- Compares job descriptions with skills from a local, private profile.
- Shows a transparent **skill-match score (0–10)**, matched skills, missing skills, and evidence coverage.
- Extracts explicit experience signals from job adverts, including years of experience, junior/mid/senior wording, and whether experience is described as project, industry, professional, or relevant experience.
- Records publication date, application deadline (when supplied), and the date the listing was first discovered.
- Stores discovered jobs in a local SQLite database.
- Optionally sends an email digest through a locally configured SMTP server, tracking which listings have already been sent so repeat digests do not resend them.
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

The example profile is deliberately broad so you can make the project your own. You do not need to keep every suggested role or skill. For a field-by-field guide and safe customization steps, read **[Configuration Guide](docs/CONFIGURATION.md)**. See the **[Quality Assurance Checklist](docs/QUALITY-CHECKLIST.md)** for automated checks, manual accessibility review, repository safeguards, and local database backup/deletion guidance. The example job families and skills are informed by public job adverts and market listings reviewed in November 2026; see **[Role and Skill Research](docs/ROLE-RESEARCH.md)** for the dated source list, examples and limitations.

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

The Python MVP uses a transparent, weighted keyword-matching heuristic:
- **Match score (0–10):** matched profile keywords contribute to the score; unmatched configured keywords remain in the denominator.
- **Requirement weighting:** skill mentions near phrases such as "required" receive more weight than preferred or optional mentions. Unclassified mentions use a neutral weight.
- **Proficiency fit:** a self-rated skill level (1–5) is compared with an explicitly stated proficiency cue near that skill mention. No level penalty is applied when the advert does not state a level.
- **Evidence coverage:** proportion of configured skill groups with at least one matching keyword.
- **Evidence details:** matched skills, missing skill groups, requirement classifications, and per-keyword level comparisons are returned for review.
- **Experience evidence:** explicit year ranges, seniority labels, experience scope, and required/preferred wording are extracted from job-ad sentences. This is a separate descriptive signal and does not currently change the skill score or compare years against a candidate profile.

Matching normalizes Unicode text and uses Unicode-aware word boundaries, so Finnish letters are handled correctly and terms are not matched as arbitrary substrings. Use each skill's optional `aliases` mapping for alternate spellings and Finnish inflections. Aliases are alternatives to a canonical keyword, so they do not inflate the score denominator. The matcher does not guess Finnish grammar or automatically stem words. Target titles, experience keywords, and excluded keywords are stored as configurable profile fields but are not yet applied to the score. The public browser demo at the GitHub Pages project URL is the canonical interactive demo (`docs/index.html`). It has a simplified client-side matcher and illustrative sample roles; it does not run the Python backend or fetch live job listings. The older portfolio-root demo URL now redirects visitors to this canonical version. See the configuration guide for this distinction.

Requirement and proficiency cues are heuristic text classifications. They may miss wording, interpret context imperfectly, or fail to recognize an employer's intended meaning. This is a preliminary screening aid, not a hiring probability, qualification verification, or eligibility decision. It does not yet evaluate legal work eligibility, compensation, language requirements, interview performance, or company culture.

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

This is an unfinished work-in-progress experiment and early MVP, not a completed product. It began as a personal skills-mapping and career-exploration exercise and also serves as its author's evolving software-development portfolio and practical work sample. The public example configuration is intentionally generic so that other people can adapt it to different IT, ICT, media, design, communications, or other career paths. Its open development process is part of the learning objective: implementation choices, limitations, tests, and future ideas are documented so others can study and build on them. The first version focuses on public-source discovery, worldwide-remote filtering, private profile matching, local tracking, and optional email digests. The browser dashboard and local API are also experimental and have not been security-audited for public deployment. Applicant-count extraction, deadline parsing across varied formats, richer company research, and additional source adapters are future improvements.

## Development and test status

The project is being built and tested incrementally. GitHub Actions runs the Python test suite, TypeScript dashboard build, and browser-demo JavaScript syntax check on pushes and pull requests. These checks are blocking and fail the workflow when a check fails. Branch protection is not currently configured; requiring pull requests and successful checks before merging is recommended. GitHub Actions workflow notifications remain subject to each account's notification settings.

The optional email digest is a separate feature. It sends a message only when the user explicitly runs the `remotefit digest` command and has configured local SMTP settings. GitHub Actions test results do not trigger that digest.

The canonical public browser demo is maintained only in this repository at `docs/index.html` and is published through GitHub Pages. The older demo URL in the portfolio repository is retained as a lightweight redirect so existing bookmarks continue to work. Do not develop or publish a second copy of the demo in the portfolio repository; make demo changes here to avoid version drift.

The project is being modified and updated during this testing phase. Please expect incomplete features, changing configuration, and occasional test failures. The repository is shared as a work in progress, not as a stable release or production-ready service.

## Contributing

Issues and pull requests are welcome. Keep examples fictional and generic. Never submit real personal information, credentials, private job-search data, or database exports.

## License and third-party materials

The MIT License in [LICENSE](LICENSE) applies only to the original project code and documentation authored for this repository, to the extent those materials are owned by the project contributors. It does **not** grant rights to third-party job advertisements, job-listing descriptions or metadata, provider APIs or datasets, employer names, trademarks, logos, images, or other externally supplied content. Those materials remain subject to their respective owners' rights, licences, API terms, and usage restrictions.

Job listings are fetched from external providers and should be used only in accordance with the provider's current terms. Attribution and links to original listings do not by themselves grant permission to republish, redistribute, or commercially reuse listing content. The project does not claim ownership of third-party data. Remove externally sourced content if a provider's terms or rights holder requires it.


