# Remote Job Fit — Development TODO

Internal development checklist; not part of the deployed demo interface.

## High priority
- [ ] Run the complete Python and TypeScript test suites and record current results.
- [ ] Verify setup and development commands on a clean environment.
- [ ] Review job-provider integrations against current APIs, terms, attribution and rate limits.
- [ ] Test missing, malformed, unavailable and rate-limited provider responses.
- [ ] Verify private profile data stays local and is excluded from logs, exports and committed files.

## Matching and data quality
- [ ] Review how required, preferred and optional skills are distinguished.
- [ ] Explain scoring, weighting, missing-skill handling and matching limitations.
- [ ] Add tests for empty profiles, duplicate skills, synonyms, partial matches and unknown requirements.
- [ ] Check interpretation of remote-location eligibility and worldwide roles.
- [ ] Keep source links and listing dates consistent across dashboard, CLI and exports.

## User experience
- [ ] Review keyboard accessibility, focus states, labels and responsive layouts.
- [ ] Check empty, loading, error and no-results states.
- [ ] Align terminology across CLI, dashboard and documentation.
- [ ] Verify CSV exports handle special characters and untrusted text safely.

## Security and maintenance
- [ ] Review .env.example, .gitignore and configuration defaults.
- [ ] Check dependency versions and known vulnerabilities.
- [ ] Review privacy, security, contribution and license documentation against current behaviour.
- [ ] Confirm example profiles contain generic sample data only.