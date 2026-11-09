"""Transparent, evidence-based job filtering and profile matching.

The match score is a heuristic fit indicator, not a hiring probability.
It uses configured skill keywords, requirement language and explicit
proficiency cues near matched keywords. It does not infer qualifications.
"""

# CODE MAP / COMMENTING GUIDE
# File purpose: Job posting analysis, skill requirement detection, and profile matching.
# Structure: imports and settings first, followed by data structures and helper functions, with main operations last.
# Navigation map: worldwide-remote validation -> text normalization -> keyword matching -> requirement classification -> experience analysis -> match scoring.
# Editing tip: update keyword dictionaries and regular expressions near the top before changing matching logic below.
# Function start/end markers identify the boundaries of each processing step.

import re
import unicodedata

# SECTION 1 START: phrases that indicate a role may be open to applicants worldwide.
WORLDWIDE_MARKERS = (
    "work from anywhere", "anywhere in the world", "worldwide",
    "global remote", "globally remote", "any location", "open to any location",
    "remote - global", "remote worldwide",
)

# SECTION 2 START: weighting used when a listing labels requirements as required, preferred, or optional.
REQUIREMENT_WEIGHTS = {
    "required": 1.5,
    "preferred": 1.0,
    "optional": 0.75,
    "unspecified": 1.0,
}

_REQUIRED_RE = re.compile(
    r"\b(?:must[- ]have|required|requirements?|essential|mandatory|"
    r"need to|you will need|we require|strong knowledge of|proficient in|vaaditaan|edellytetään|pakollinen|vähintään)\b",
    re.IGNORECASE,
)
_PREFERRED_RE = re.compile(
    r"\b(?:preferred|preferably|nice to have|good to have|"
    r"a plus|would be an advantage|bonus|desirable|eduksi|katsotaan eduksi|toivottavaa)\b",
    re.IGNORECASE,
)
_OPTIONAL_RE = re.compile(
    r"\b(?:optional|not required|would be helpful|familiarity with)\b",
    re.IGNORECASE,
)
_ADVANCED_RE = re.compile(
    r"\b(?:expert|advanced|senior|deep expertise|extensive experience|"
    r"highly experienced)\b", re.IGNORECASE
)
_INTERMEDIATE_RE = re.compile(
    r"\b(?:intermediate|solid experience|good understanding|"
    r"hands[- ]on experience|proven experience)\b", re.IGNORECASE
)
_ENTRY_RE = re.compile(
    r"\b(?:junior|entry[- ]level|beginner|basic knowledge|"
    r"working knowledge|familiarity)\b", re.IGNORECASE
)
_YEARS_RE = re.compile(r"\b(\d+)\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)


_BUILTIN_RESTRICTIONS = (
    r"\b(?:us|u\.s\.|united states) citizens? only\b",
    r"\b(?:uk|u\.k\.|united kingdom) citizens? only\b",
    r"\b(?:eu|europe|emea|north america|canada|australia) only\b",
    r"\bany location in (?:the )?(?:eu|europe|emea|north america|canada|australia)\b",
    r"\b(?:must be based|must reside|must live|must be located) in\b",
    r"\b(?:only applicants|candidates) (?:located|based|residing) in\b",
    r"\b(?:authorized|authorised|eligible) to work in\b",
    r"\b(?:work authorization|work authorisation) (?:in|for)\b",
    r"\b(?:time zone|timezone) (?:overlap|alignment|restriction|required)\b",
    r"\b(?:overlap|aligned) with (?:the )?(?:[a-z]{2,4}|utc|gmt)[+-]?\d{0,2}\b",
)

# Checks whether a role is genuinely worldwide remote or whether the listing restricts location or eligible work countries.
# SECTION 3 START: location eligibility and worldwide-remote checks.
def is_worldwide_remote(job, reject_restrictions=None):
    """Conservatively filter worldwide roles; this is not a legal parser.

    Positive evidence must come from a provider's structured eligibility fields.
    Common restrictions are checked across all listing text and override global
    markers. Always verify eligibility on the employer's original advert.
    """
    all_text = " ".join(str(job.get(key, "")) for key in (
        "title", "description", "location", "candidate_required_location",
        "workplace_type", "tags", "eligible_locations", "eligible_countries",
        "work_location", "remote_scope", "requirements", "qualifications",
    )).casefold()
    for phrase in reject_restrictions or []:
        normalized = str(phrase).strip().casefold()
        if normalized and normalized in all_text:
            return False
    if any(re.search(pattern, all_text, re.IGNORECASE) for pattern in _BUILTIN_RESTRICTIONS):
        return False

    structured_fields = (
        "location", "candidate_required_location", "eligible_locations",
        "eligible_countries", "work_location", "remote_scope", "tags",
    )
    eligibility_text = " ".join(
        str(job.get(key, "")) for key in structured_fields
        if job.get(key) is not None
    ).casefold()
    return any(
        re.search(r"(?<!\w)" + re.escape(marker) + r"(?!\w)", eligibility_text)
        for marker in WORLDWIDE_MARKERS
        if marker not in {"any location", "open to any location"}
    )


# Normalizes text for searching so that letter case and punctuation do not prevent keyword matching.
# FUNCTION SECTION END: is_worldwide_remote. The next section starts at the next function or class.
# SECTION 4 START: text cleanup and keyword matching helpers.
def _normalise_match_text(value):
    """Normalize Unicode and case for consistent Finnish/English matching."""
    return unicodedata.normalize("NFKC", str(value)).casefold()


# Builds a search pattern that matches complete keywords rather than accidental partial matches.
# FUNCTION SECTION END: _normalise_match_text. The next section starts at the next function or class.
def _keyword_pattern(keyword):
    """Match a complete Unicode word/phrase, not a substring of another word."""
    normalized = _normalise_match_text(keyword).strip()
    if not normalized:
        return None
    return r"(?<!\w)" + re.escape(normalized) + r"(?!\w)"


# Uses the listing context to determine whether a skill is required or preferred.
# FUNCTION SECTION END: _keyword_pattern. The next section starts at the next function or class.
def _requirement_type(context):
    """Classify requirement language close to a matched skill mention."""
    if _OPTIONAL_RE.search(context):
        return "optional"
    if _PREFERRED_RE.search(context):
        return "preferred"
    if _REQUIRED_RE.search(context):
        return "required"
    return "unspecified"


# Estimates the required skill or experience level from the surrounding text.
# FUNCTION SECTION END: _requirement_type. The next section starts at the next function or class.
def _required_level(context):
    """Infer a conservative 1–5 level only from explicit nearby wording."""
    years = _YEARS_RE.search(context)
    if years:
        count = int(years.group(1))
        return 1 if count <= 1 else 2 if count <= 2 else 3 if count <= 4 else 4
    if _ADVANCED_RE.search(context):
        return 4
    if _INTERMEDIATE_RE.search(context):
        return 3
    if _ENTRY_RE.search(context):
        return 1
    return None


# Searches for a keyword in the text and returns its position when found.
# FUNCTION SECTION END: _required_level. The next section starts at the next function or class.
def _find_keyword(text, keyword):
    pattern = _keyword_pattern(keyword)
    return re.search(pattern, text) if pattern else None


# Extracts a short text snippet around a keyword so the requirement can be interpreted in context.
# FUNCTION SECTION END: _find_keyword. The next section starts at the next function or class.
def _local_context(text, start, end):
    """Keep requirement cues within the sentence containing the skill mention."""
    boundaries = ".!?;" + chr(10)
    left = max((text.rfind(mark, 0, start) for mark in boundaries), default=-1) + 1
    right_candidates = [text.find(mark, end) for mark in boundaries]
    right_candidates = [position for position in right_candidates if position >= 0]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left:right]



_EXPERIENCE_RANGE_RE = re.compile(
    r"(?P<minimum>\d+)\s*(?:-|–|to)\s*(?P<maximum>\d+)\s*(?:years?|yrs?|vuotta|vuoden)",
    re.IGNORECASE,
)
_EXPERIENCE_SINGLE_RE = re.compile(
    r"(?P<minimum>\d+)\s*(?P<plus>\+)?\s*(?:years?|yrs?|vuotta|vuoden)",
    re.IGNORECASE,
)
_SENIORITY_PATTERNS = {
    "entry": re.compile(r"\b(?:intern|internship|graduate|entry[- ]level|junior|trainee)\b|\bharjoittelija\b", re.IGNORECASE),
    "mid": re.compile(r"\b(?:mid[- ]level|intermediate|regular)\b|\bkeskitaso\b", re.IGNORECASE),
    "senior": re.compile(r"\b(?:senior|lead|principal|staff engineer|head of)\b|\bseniori?\b|\bjohtava\b", re.IGNORECASE),
}
_EXPERIENCE_SCOPE_PATTERNS = {
    "project": re.compile(r"\b(?:project|projects|project-based|portfolio)\b|\bprojekti(?:työ|kokemus|ssa|sta)?\b", re.IGNORECASE),
    "industry": re.compile(r"\b(?:industry|sector|domain|commercial) experience\b|\b(?:toimiala|alakohtainen)kokemus\b", re.IGNORECASE),
    "professional": re.compile(r"\b(?:professional|employment|work) experience\b|\btyökokem\w*|\bammatillinen kokemus\b", re.IGNORECASE),
    "relevant": re.compile(r"\b(?:relevant|related|similar) experience\b|\b(?:tehtävään soveltuva|vastaava) kokemus\b", re.IGNORECASE),
}


# Detects text signals related to experience, seniority, and skill requirements in a job listing.
# FUNCTION SECTION END: _local_context. The next section starts at the next function or class.
# SECTION 5 START: experience and seniority signals from job descriptions.
def analyze_experience_requirements(job):
    """Extract explicit experience and seniority signals without guessing eligibility."""
    description = " ".join(str(job.get(key, "")) for key in (
        "title", "description", "requirements", "qualifications"
    ))
    sentences = [
        part.strip()
        for part in re.split(r"(?<=[.!?;])\s+|[\r\n]+", description)
        if part.strip()
    ]
    results = []
    seen = set()

    for sentence in sentences:
        range_match = _EXPERIENCE_RANGE_RE.search(sentence)
        single_match = _EXPERIENCE_SINGLE_RE.search(sentence)
        years_min = years_max = None
        if range_match:
            years_min = int(range_match.group("minimum"))
            years_max = int(range_match.group("maximum"))
        elif single_match:
            years_min = int(single_match.group("minimum"))
            years_max = None

        seniority = next(
            (level for level, pattern in _SENIORITY_PATTERNS.items() if pattern.search(sentence)),
            None,
        )
        if years_min is None and seniority is None:
            continue

        scope = next(
            (name for name, pattern in _EXPERIENCE_SCOPE_PATTERNS.items() if pattern.search(sentence)),
            "general",
        )
        item = {
            "years_min": years_min,
            "years_max": years_max,
            "seniority": seniority,
            "scope": scope,
            "requirement": _requirement_type(sentence),
            "evidence": sentence[:300],
        }
        key = (years_min, years_max, seniority, scope, item["requirement"], item["evidence"].casefold())
        if key not in seen:
            results.append(item)
            seen.add(key)

    return {
        "items": results,
        "has_explicit_requirements": bool(results),
        "scoring_note": "Experience is extracted as evidence only; it does not affect the skill-match score or determine eligibility.",
    }


# Compares the user's skills profile with a job listing and calculates a transparent, rule-based match score.
# FUNCTION SECTION END: analyze_experience_requirements. The next section starts at the next function or class.
# SECTION 6 START: final profile-to-vacancy matching and transparent score calculation.
def score_job(profile, job):
    """Return a 0–10 weighted skill-match score and auditable evidence.

    Skill levels are self-ratings from 1 (basic) to 5 (advanced). A level
    penalty is applied only when the advert contains an explicit proficiency
    cue close to the matched skill. Requirement language is classified from
    the local text surrounding each keyword occurrence.
    """
    text = _normalise_match_text(" ".join(str(job.get(key, "")) for key in (
        "title", "description", "tags", "category"
    )))
    skills = profile.get("skills", [])
    matched = []
    missing = []
    requirement_summary = {"required": [], "preferred": [], "optional": [], "unspecified": []}
    total_weight = 0.0
    earned_weight = 0.0
    matched_groups = 0
    valid_groups = 0

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

        valid_groups += 1
        try:
            user_level = max(1, min(5, int(skill.get("level", 3))))
        except (TypeError, ValueError):
            user_level = 3

        raw_aliases = skill.get("aliases", {})
        alias_map = {}
        if isinstance(raw_aliases, dict):
            for canonical, variants in raw_aliases.items():
                canonical = _normalise_match_text(canonical).strip()
                if isinstance(variants, str):
                    variants = [variants]
                if canonical in keywords and isinstance(variants, list):
                    alias_map[canonical] = list(dict.fromkeys(
                        _normalise_match_text(variant).strip()
                        for variant in variants if str(variant).strip()
                    ))

        found = []
        matched_aliases = {}
        details = []
        group_earned = 0.0
        group_possible = 0.0

        for word in keywords:
            variants = [word] + alias_map.get(word, [])
            match = next(
                ((variant, _find_keyword(text, variant)) for variant in variants
                 if _find_keyword(text, variant)),
                None,
            )
            if not match:
                continue

            matched_variant, occurrence = match
            context = _local_context(text, occurrence.start(), occurrence.end())
            requirement = _requirement_type(context)
            required_level = _required_level(context)
            requirement_weight = REQUIREMENT_WEIGHTS[requirement]
            level_fit = min(user_level / required_level, 1.0) if required_level else 1.0
            group_possible += requirement_weight
            group_earned += requirement_weight * level_fit
            found.append(word)
            if matched_variant != word:
                matched_aliases[word] = matched_variant
            details.append({
                "keyword": word,
                "requirement": requirement,
                "user_level": user_level,
                "advertised_level": required_level,
                "level_fit": round(level_fit, 2),
                "weight": requirement_weight,
            })
            requirement_summary[requirement].append(skill.get("name", "Unnamed skill"))

        # Unmatched keywords remain part of the denominator, preventing the
        # score from being inflated merely because one term in a group matched.
        unmatched_count = len(keywords) - len(found)
        group_possible += unmatched_count
        total_weight += group_possible
        earned_weight += group_earned

        if found:
            matched_groups += 1
            matched.append({
                "skill": skill.get("name", "Unnamed skill"),
                "keywords": found,
                "matched_aliases": matched_aliases,
                "details": details,
            })
        else:
            missing.append(skill.get("name", "Unnamed skill"))

    score = round((earned_weight / total_weight) * 10, 1) if total_weight else 0.0
    coverage = round((matched_groups / valid_groups) * 100) if valid_groups else 0
    # De-duplicate skill names while preserving their original order.
    requirement_summary = {
        key: list(dict.fromkeys(value)) for key, value in requirement_summary.items()
    }
    return {
        "score": score,
        "evidence_coverage_percent": coverage,
        "matched_skills": matched,
        "missing_skills": missing,
        "requirement_summary": requirement_summary,
        "score_type": "weighted_keyword_match_not_hiring_probability",
        "experience_requirements": analyze_experience_requirements(job),
        "scoring_notes": [
            "Required, preferred and optional wording is inferred from nearby advert text.",
            "Skill level is penalized only when an explicit proficiency cue is found nearby.",
            "Unmatched configured keywords remain in the score denominator.",
            "The result is a screening aid, not a hiring probability or eligibility decision.",
        ],
    }


# Calculates a rough comparison baseline from applicant and vacancy counts; this is not an estimate of the probability of getting the job.
# FUNCTION SECTION END: score_job. The next section starts at the next function or class.
def applicant_baseline(applicant_count, openings=1):
    """Return a descriptive applicant/opening ratio, never a hiring probability."""
    if not isinstance(applicant_count, int) or applicant_count < 0:
        return None
    if not isinstance(openings, int) or openings < 1:
        return None
    return round(openings / applicant_count * 100, 2) if applicant_count else None

# FUNCTION SECTION END: applicant_baseline. The next section starts at the next function or class.