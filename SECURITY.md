# Security Policy

## Scope and project status

Remote Job Fit is an experimental, locally configured job-search and skills-matching project. It is not a production recruitment system or a security-reviewed service.

The public repository is intended to contain generic examples only. Keep personal skills profiles, local source configuration, exports, databases and credentials outside version control. The repository's `.gitignore` excludes the local profile configuration and common secret and data files, but contributors must still review staged changes before committing.

## Protect local data

- Keep personal profile data in the ignored local configuration files documented in the README.
- Keep email credentials and other secrets in a local `.env` file; never put them in source code, issue reports, screenshots or pull requests.
- Treat downloaded job listings and provider responses as untrusted external input.
- Review CSV and other exported files before sharing them; they may contain saved job data or notes.
- Do not use real personal data in fixtures or public examples. Use synthetic test data.

## Reporting a vulnerability

Please do not publish exploitable details in a public issue or pull request.

Use GitHub's private vulnerability reporting feature for this repository if it is enabled. If it is unavailable, contact the maintainer privately through the contact options on the GitHub profile. Include the affected component, steps to reproduce, expected and actual behaviour, and potential impact. Avoid sending real credentials or personal profile data.

## Responsible use

Matching scores are heuristic indicators, not hiring probabilities or verified assessments of a person's qualifications. Always review the original job advertisement and the provider's eligibility terms. Do not use the project as an automated employment decision system.
