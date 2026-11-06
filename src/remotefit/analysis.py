"""Transparent, heuristic job filtering and profile matching.

To customize profile matching, edit the keywords under profile.skills in
config/profile.yaml. This module intentionally contains no personal profile
defaults. Skill levels and several other profile fields are not used by the
current MVP scoring calculation.
"""

import re

# A listing must contain at least one of these phrases to pass the current
# worldwide-remote check. Add or adjust generic phrases here only when the
# intended meaning is clear; user-specific preferences belong in local YAML.
WORLDWIDE_MARKERS = (
    "work from anywhere", "anywhere in the world", "worldwide",
    "global remote", "globally remote", "any location", "open to any location",
    "remote - global", "remote worldwide",
)


def is_worldwide_remote(job, reject_restrictions=None):
    """Return True only when the listing explicitly signals global eligibility."""
    text = " ".join(str(job.get(key, "")) for key in (
        "title", "description", "location", "candidate_required_location",
        "workplace_type", "tags"
    )).lower()
    restrictions = reject_restrictions or []
    if any(str(item).lower() in text for item in restrictions):
        return False
    # Explicit worldwide terms are required; the generic word 'remote' is insufficient.
    return any(marker in text for marker in WORLDWIDE_MARKERS)


def score_job(profile, job):
    """Return a 0-10 keyword match score and its supporting evidence.

    The current implementation compares only profile.skills[].keywords
    (or the skill name when no keywords are provided) with the job text.
    It does not infer a hiring probability or validate a skill level.
    """
    text = " ".join(str(job.get(key, "")) for key in (
        "title", "description", "tags", "category"
    )).lower()
    skills = profile.get("skills", [])
    matched = []
    missing = []
    matched_groups = 0
    total_keywords = 0
    matched_keywords = 0

    for skill in skills:
        keywords = [str(word).strip().lower() for word in skill.get("keywords", []) if str(word).strip()]
        if not keywords:
            keywords = [str(skill.get("name", "")).strip().lower()]
        keywords = [word for word in keywords if word]
        if not keywords:
            continue
        total_keywords += len(keywords)
        found = [word for word in keywords if re.search(r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])", text)]
        matched_keywords += len(found)
        if found:
            matched_groups += 1
            matched.append({"skill": skill.get("name", "Unnamed skill"), "keywords": found})
        else:
            missing.append(skill.get("name", "Unnamed skill"))

    score = round((matched_keywords / total_keywords) * 10, 1) if total_keywords else 0.0
    coverage = round((matched_groups / len(skills)) * 100) if skills else 0
    return {
        "score": score,
        "evidence_coverage_percent": coverage,
        "matched_skills": matched,
        "missing_skills": missing,
        "score_type": "keyword_match_not_hiring_probability",
    }


def applicant_baseline(applicant_count, openings=1):
    """Return a descriptive applicant/opening ratio, never a hiring probability."""
    if not isinstance(applicant_count, int) or applicant_count < 0:
        return None
    if not isinstance(openings, int) or openings < 1:
        return None
    return round(openings / applicant_count * 100, 2) if applicant_count else None
