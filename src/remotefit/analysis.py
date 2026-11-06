"""Transparent, heuristic job filtering and profile matching.

To customize profile matching, edit the keywords under profile.skills in
config/profile.yaml. This module intentionally contains no personal profile
defaults. Skill levels and several other profile fields are not used by the
current MVP scoring calculation.
"""

import re
import unicodedata

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


def _normalise_match_text(value):
    """Normalize Unicode and case for consistent Finnish/English keyword matching."""
    return unicodedata.normalize("NFKC", str(value)).casefold()


def _keyword_pattern(keyword):
    """Match a complete Unicode word/phrase, not a substring of another word."""
    normalized = _normalise_match_text(keyword).strip()
    if not normalized:
        return None
    # Python's Unicode-aware \w includes Finnish letters (ä, ö, å), unlike
    # the former [a-z0-9] boundary which could match inside accented words.
    return r"(?<!\\w)" + re.escape(normalized) + r"(?!\\w)"


def score_job(profile, job):
    """Return a 0-10 keyword match score and its supporting evidence.

    The current implementation compares only profile.skills[].keywords
    (or the skill name when no keywords are provided) with the job text.
    It does not infer a hiring probability or validate a skill level.
    """
    text = _normalise_match_text(" ".join(str(job.get(key, "")) for key in (
        "title", "description", "tags", "category"
    )))
    skills = profile.get("skills", [])
    matched = []
    missing = []
    matched_groups = 0
    total_keywords = 0
    matched_keywords = 0

    for skill in skills:
        keywords = [
            _normalise_match_text(word).strip()
            for word in skill.get("keywords", [])
            if str(word).strip()
        ]
        if not keywords:
            name = _normalise_match_text(skill.get("name", "")).strip()
            keywords = [name] if name else []
        keywords = list(dict.fromkeys(word for word in keywords if word))
        if not keywords:
            continue
        total_keywords += len(keywords)
        found = [
            word for word in keywords
            if (pattern := _keyword_pattern(word)) and re.search(pattern, text)
        ]
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
