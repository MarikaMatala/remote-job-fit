from remotefit.analysis import applicant_baseline, is_worldwide_remote, score_job


def test_worldwide_requires_explicit_signal():
    assert is_worldwide_remote({"title": "Python Developer", "location": "Worldwide"})
    assert not is_worldwide_remote({"title": "Remote Python Developer", "location": "Remote"})


def test_restricted_listing_is_rejected():
    job = {"title": "Worldwide Remote Developer", "description": "US only"}
    assert not is_worldwide_remote(job, ["us only"])


def test_skill_score_and_evidence():
    profile = {"skills": [
        {"name": "Python", "keywords": ["python", "pytest"]},
        {"name": "Design", "keywords": ["figma"]},
    ]}
    result = score_job(profile, {"title": "Python Developer", "description": "Uses pytest"})
    # Two of the three configured keywords match: 2 / 3 * 10 = 6.7.
    assert result["score"] == 6.7
    assert result["evidence_coverage_percent"] == 50
    assert result["matched_skills"][0]["skill"] == "Python"


def test_score_matches_explicit_finnish_inflections_and_compounds():
    profile = {"skills": [
        {"name": "React", "keywords": ["react"], "aliases": {"react": ["reactin", "reactia"]}},
        {"name": "Accessibility", "keywords": ["accessibility"], "aliases": {"accessibility": ["saavutettavuusosaaminen", "saavutettavuusosaamisen"]}},
        {"name": "HTML", "keywords": ["html"], "aliases": {"html": ["html5"]}},
    ]}
    result = score_job(
        profile,
        {"title": "Frontend-kehittäjä", "description": "Reactin ja saavutettavuusosaamisen lisäksi HTML5."},
    )
    matches = {item["skill"]: item for item in result["matched_skills"]}
    assert matches["React"]["keywords"] == ["react"]
    assert matches["React"]["matched_aliases"] == {"react": "reactin"}
    assert matches["Accessibility"]["matched_aliases"] == {"accessibility": "saavutettavuusosaamisen"}
    assert matches["HTML"]["matched_aliases"] == {"html": "html5"}
    # Aliases are alternatives, not extra score items.
    assert result["score"] == 10.0


def test_keyword_boundaries_are_unicode_aware():
    profile = {"skills": [
        {"name": "Java", "keywords": ["java"]},
        {"name": "Cafe", "keywords": ["cafe"]},
    ]}
    result = score_job(
        profile,
        {"title": "JavaScript Developer", "description": "A café interface"},
    )
    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["Java", "Cafe"]


def test_keyword_matching_normalizes_unicode_compatibility_forms():
    profile = {"skills": [{"name": "JavaScript", "keywords": ["javascript"]}]}
    result = score_job(profile, {"description": "ＪａｖａＳｃｒｉｐｔ"})
    assert result["matched_skills"][0]["keywords"] == ["javascript"]


def test_applicant_baseline_is_not_probability():
    assert applicant_baseline(100, 1) == 1.0
    assert applicant_baseline(None) is None
