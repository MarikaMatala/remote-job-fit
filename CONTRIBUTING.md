# Contributing to Remote Job Fit

Thank you for taking an interest in Remote Job Fit.

This repository is an open-source portfolio and learning project with a practical job-search use case. It demonstrates an evolving development process and is shared so that job seekers, students, and developers can explore the implementation, learn from the examples, adapt the ideas, and contribute improvements.

You are welcome to use the project as inspiration for your own work. You do not need to contribute code to benefit from it, and you do not need to follow the existing design or approach when creating your own adaptation.

## Ways to participate

- Try the browser demo and report confusing behavior or accessibility barriers.
- Open an issue describing a reproducible bug or a concrete improvement.
- Suggest documentation clarifications, learning resources, or safer defaults.
- Improve tests, error handling, accessibility, privacy, security, or maintainability.
- Add a job-source adapter after reviewing that provider's official API documentation, terms, attribution rules, and rate limits.
- Fork the repository and develop a version suited to your own career goals or workflow.
- Share what you learned or a useful adaptation, while respecting the licence and third-party rights.

## Before opening an issue

Please include enough information to understand the suggestion:

- What you expected to happen.
- What actually happened.
- Steps to reproduce the issue.
- Relevant operating system, Python/Node version, browser, and command output, where applicable.
- A small fictional example if sample data is needed.

Do not include personal job-search records, real CVs, private contact details, credentials, access tokens, API keys, database files, or private email content. Redact sensitive information from screenshots and logs.

## Pull request guidelines

1. Fork the repository or create a feature branch.
2. Keep each pull request focused on one change where practical.
3. Explain the problem, the chosen approach, and any trade-offs.
4. Add or update tests for behavior changes.
5. Update documentation when configuration, behavior, limitations, or setup steps change.
6. Run the relevant checks before submitting:
   - Python: `pytest`
   - Dashboard: `cd web && npm ci && npm run build`
   - Browser demo syntax and interaction tests: `node --check docs/demo.js && node --test docs/demo.test.js`
7. Keep examples fictional and generic. Do not add private profile data or secrets.
8. Be respectful and constructive in review discussions.

The project is experimental and its architecture may change. For larger changes, opening an issue first is recommended so that scope and compatibility can be discussed.

## Design principles

When proposing changes, keep these goals in mind:

- **Useful, not authoritative:** matching results are exploratory hints, not hiring decisions, proof of qualifications, or legal eligibility assessments.
- **Transparent:** explain what a feature does, what data it uses, and where its limitations are.
- **Privacy-conscious:** keep personal profiles, credentials, and local job-search data out of the public repository.
- **Accessible:** consider keyboard use, screen readers, contrast, zoom, responsive layouts, plain language, and reduced motion.
- **Adaptable:** prefer generic examples and configurable behavior over assumptions about one person's career path.
- **Respectful of source rights:** use job-board APIs and content only in accordance with their current terms, licences, attribution requirements, and rate limits.

## Licence and third-party content

Contributions to the original project code and documentation are intended to be provided under the repository's MIT License, subject to the contributor's rights to submit them. By submitting a pull request, you confirm that you have the right to contribute the material.

The MIT License does not grant rights to third-party job advertisements, listing data, provider APIs or datasets, company names, logos, trademarks, images, or other externally supplied content. Those materials remain subject to their respective owners' rights and terms. Do not add copied job-ad databases, scraped restricted content, or assets unless their use and redistribution are permitted.

## Learning and independent adaptations

The project is shared to make learning visible and to encourage others to experiment. You may study the implementation, take inspiration from the approach, fork the repository, and build your own version in accordance with the licence and applicable third-party terms. If you publish an adaptation, make its changes and sources clear and do not imply endorsement by the original author.

Thank you for helping make the project more useful, understandable, and welcoming to others.
