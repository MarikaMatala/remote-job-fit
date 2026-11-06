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
    assert result["score"] == 5.0
    assert result["evidence_coverage_percent"] == 50
    assert result["matched_skills"][0]["skill"] == "Python"


def test_applicant_baseline_is_not_probability():
    assert applicant_baseline(100, 1) == 1.0
    assert applicant_baseline(None) is None
