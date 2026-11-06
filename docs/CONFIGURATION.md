# Configuration Guide

This guide explains which files you can edit, what each setting means, and where private information belongs.

## 1. Configuration file map

| File | Purpose | Should it be committed? |
| --- | --- | --- |
| `config/profile.example.yaml` | Public, generic profile template | Yes |
| `config/profile.yaml` | Your personal skills and job-search preferences | **No** |
| `config/sources.example.yaml` | Public, generic job-source template | Yes |
| `config/sources.yaml` | Your local source and filter overrides | **No** |
| `.env.example` | Public template with empty secret fields | Yes |
| `.env` | Your local SMTP credentials and database path | **No** |

The application reads the private profile from `config/profile.yaml`. If `config/sources.yaml` does not exist, it uses `config/sources.example.yaml`.

## 2. Create your private files

Run these commands from the repository root.

Windows PowerShell:

```powershell
Copy-Item config/profile.example.yaml config/profile.yaml
Copy-Item config/sources.example.yaml config/sources.yaml
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp config/profile.example.yaml config/profile.yaml
cp config/sources.example.yaml config/sources.yaml
cp .env.example .env
```

You do not need to configure email if you only want to search and view jobs. You do need to create `config/profile.yaml` before running the application.

## 3. Personal profile: config/profile.yaml

This file describes the skills and job-search terms you want the tool to use. Do not add passwords, account credentials, private contact details, or any information you do not want stored locally.

### target_titles

A list of job titles you are interested in.

```yaml
target_titles:
  - "Frontend Developer"
  - "Junior Software Engineer"
  - "Technical Writer"
```

**Current behavior:** saved in the profile, but not yet used to filter the current job results. It is intended for a future title-matching feature.

### skills

Add one entry for each skill or skill group.

```yaml
skills:
  - name: "Frontend Development"
    level: 3
    keywords:
      - "frontend"
      - "javascript"
      - "typescript"
      - "react"
      - "css"
  - name: "Testing"
    level: 2
    keywords:
      - "unit testing"
      - "pytest"
      - "jest"
```

- `name`: A short label displayed in match results.
- `level`: Your own level from 1 to 5. It is informational in the current MVP and does not change the score.
- `keywords`: The important field for the current matching feature. Add alternative spellings, abbreviations, tools, frameworks, and related phrases that employers may use.

**You are not limited to a predefined list of programming languages.** Add any language or technology you want to track, provided you can write its name as a text keyword. Examples include Python, JavaScript, TypeScript, Java, C, C++, C#, F#, Go, Rust, Ruby, PHP, Swift, Kotlin, Dart, Scala, R, MATLAB, Perl, Lua, Elixir, Erlang, Haskell, Clojure, Objective-C, SQL, PL/SQL, HTML, CSS, Bash, and PowerShell. You can also add languages or tools not listed here.

For best results, create a separate skill entry for each language or a meaningful group. Include aliases and related ecosystem terms because job advertisements may use different names. For example:

```yaml
skills:
  - name: "Rust"
    level: 2
    keywords:
      - "rust"
      - "rustlang"
      - "cargo"
  - name: "Kotlin"
    level: 3
    keywords:
      - "kotlin"
      - "android"
      - "jetpack compose"
  - name: "Your own language"
    level: 1
    keywords:
      - "your-language-name"
      - "common alias"
      - "related framework"
```

Replace these examples with your own skills. The language name does not need to be added to the Python source code; profile keywords are read from your local YAML file.

**Current behavior:** keywords are compared with the job title, description, tags, and category. A keyword match is not proof of experience or proficiency. Avoid adding very broad words that will match unrelated jobs.

### experience_keywords

A list of phrases describing experience you may want to track.

```yaml
experience_keywords:
  - "team projects"
  - "customer support"
  - "content management"
```

**Current behavior:** stored but not yet used in the score. Do not expect these terms to affect the current results.

### excluded_keywords

A list of terms you may want to exclude from job results.

```yaml
excluded_keywords:
  - "unpaid"
  - "volunteer only"
```

**Current behavior:** stored but not yet applied by the current filtering code. Adding terms here will not currently remove matching jobs.

### YAML editing tips

- Keep indentation consistent. YAML uses spaces, not tabs.
- Use two spaces for nested fields, as shown in the examples.
- Put each list item on a new line beginning with a hyphen.
- Put quotation marks around phrases containing punctuation such as colons.
- Keep the top-level `profile:` key in place.
- If you remove all skills, the score will be zero because there are no keywords to compare.

## 4. Job sources and location filters: config/sources.yaml

### Enable or disable a supported source

```yaml
sources:
  remotive:
    enabled: true
    url: "https://remotive.com/api/remote-jobs"
  remoteok:
    enabled: false
    url: "https://remoteok.com/api"
```

Set `enabled` to `true` to request listings or `false` to skip that source. The current version has adapters for `remotive` and `remoteok`. The source key must match an adapter in `src/remotefit/sources.py`.

Changing an endpoint URL does not automatically support a new job board. A new provider usually needs a new adapter that maps its response fields to the application's common job format. Review provider terms, documentation, and rate limits before using an endpoint.

### Add or remove location restriction phrases

```yaml
filters:
  worldwide_only: true
  reject_restrictions:
    - "us only"
    - "must be based in"
    - "must reside in"
    - "europe only"
```

Add phrases that commonly indicate the job is limited to a country, region, or residency. Remove a phrase only if you understand the consequences.

**Important:** the current filter is a basic phrase check. It requires an explicit worldwide marker such as "worldwide", "work from anywhere", or "anywhere in the world", and rejects listings containing a configured restriction phrase. The `worldwide_only` setting is descriptive in this MVP; the code currently applies the worldwide check regardless of that value. The filter can miss restrictions expressed in other wording or languages. Always check the employer's original listing.

## 5. Email settings: .env

Email is optional. If you do not want email notifications, leave these values empty and do not run the `digest` command.

Example structure (use your own values only in your private `.env` file):

```dotenv
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_TO=
SMTP_USE_TLS=true
```

| Variable | What to enter |
| --- | --- |
| `SMTP_HOST` | SMTP server hostname provided by your email provider |
| `SMTP_PORT` | SMTP port specified by your provider; 587 is a common STARTTLS port |
| `SMTP_USERNAME` | SMTP login name, if required |
| `SMTP_PASSWORD` | SMTP password or app-specific password |
| `SMTP_FROM` | Sender address accepted by the SMTP server |
| `SMTP_TO` | Address where you want to receive the digest |
| `SMTP_USE_TLS` | `true` to use STARTTLS, as expected for the common port 587 setup |
| `DATABASE_PATH` | Optional local path for the SQLite database |

Use your provider's official SMTP documentation to find the correct server and port. Some providers require an app password or OAuth-based setup and may not allow ordinary account-password SMTP login. Never put real values in `.env.example`, YAML examples, Python source files, issues, or pull requests.

## 6. Database and CSV export

By default, the local database is stored at `data/jobs.sqlite3`. It contains collected job listing details and first-seen timestamps. It is not uploaded by this application.

Change `DATABASE_PATH` in your private `.env` file if you want another local location. CSV exports are created where you specify them, for example:

```bash
remotefit export --output exports/jobs.csv
```

The `data/` and `exports/` folders and common database/export file extensions are excluded by `.gitignore`.

## 7. Run the application

After creating your profile and installing the project:

```bash
remotefit scan
remotefit list
remotefit export --output exports/jobs.csv
```

To send a digest, configure the SMTP variables in `.env` first:

```bash
remotefit digest
```

## 8. Verify that private files are ignored

Run from the repository root:

```bash
git check-ignore config/profile.yaml config/sources.yaml .env data/jobs.sqlite3
```

Git should print the paths it is ignoring. You can also inspect pending changes:

```bash
git status --short
```

Do not force-add private files with `git add -f`. If you accidentally commit a secret, removing it in a later commit is not enough: revoke or rotate the exposed credential immediately and follow GitHub's guidance for removing sensitive data from repository history.

## 9. What is configurable now, and what is planned?

| Setting / feature | Current status |
| --- | --- |
| Skill keywords and skill groups | Used by the match score |
| Skill level (1–5) | Stored for reference; does not affect score |
| Target job titles | Stored; title filtering is planned |
| Experience keywords | Stored; not yet analyzed |
| Excluded keywords | Stored; not yet applied |
| Supported source enable/disable | Works for the two built-in adapters |
| Source endpoint URL | Used by the matching built-in adapter |
| Restriction phrases | Used by the worldwide filter |
| SMTP settings | Used by the optional email digest |
| Database path | Used for local SQLite storage |
| Applicant counts and hiring probabilities | Not currently collected or predicted |
| Company hiring history and company-fit score | Not currently implemented |

## 10. Adding a new job source (developer task)

Adding a new source requires a code change, not just a YAML entry:

1. Read the provider's official API documentation and terms.
2. Add a fetch function in `src/remotefit/sources.py`.
3. Map each provider result to the same fields used by the existing adapters: `source`, `source_id`, `title`, `company`, `location`, `description`, `url`, `published_at`, `deadline`, `applicant_count`, `fetched_at`, `tags`, and `category`.
4. Register the adapter in the `adapters` mapping in `fetch_all`.
5. Add a matching source section to `config/sources.example.yaml`.
6. Add tests using fictional sample responses. Never commit real user profiles, credentials, or private job-search records.

Do not scrape login-protected pages, bypass access controls, or violate a job board's terms.
