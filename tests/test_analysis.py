# KOMMENTOINTIOHJE / CODE MAP
# Tiedoston tarkoitus: Testit työpaikkailmoitusten analysoinnille ja osaamisvaatimusten vertailulle.
# Rakenne: testien valmistelut ja apufunktiot ensin, yksittäiset testitapaukset seuraavaksi.
# Jokainen testifunktio on oma tarkistuskokonaisuutensa.

from remotefit.analysis import analyze_experience_requirements, applicant_baseline, is_worldwide_remote, score_job


# TESTIOSIO ALKAA: test_worldwide_requires_explicit_structured_eligibility_signal.
def test_worldwide_requires_explicit_structured_eligibility_signal():
    assert is_worldwide_remote({"title": "Python Developer", "location": "Worldwide"})
    assert is_worldwide_remote({"location": "Remote - Worldwide"})
    assert is_worldwide_remote({"eligible_countries": ["Worldwide"]})
    assert not is_worldwide_remote({"title": "Remote Python Developer", "location": "Remote"})
    assert not is_worldwide_remote({
        "title": "Worldwide Python Developer",
        "location": "Remote",
        "description": "We are a worldwide company and work remotely."
    })
    assert not is_worldwide_remote({
        "location": "Remote",
        "description": "Work from anywhere in the world."
    })


# TESTIOSIO ALKAA: test_restricted_listing_is_rejected.
# FUNKTIO-OSIO PÄÄTTYY: test_worldwide_requires_explicit_structured_eligibility_signal. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_restricted_listing_is_rejected():
    job = {"title": "Worldwide Remote Developer", "description": "US only"}
    assert not is_worldwide_remote(job, ["us only"])


# TESTIOSIO ALKAA: test_skill_score_and_evidence.
# FUNKTIO-OSIO PÄÄTTYY: test_restricted_listing_is_rejected. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_skill_score_and_evidence():
    profile = {"skills": [
        {"name": "Python", "keywords": ["python", "pytest"]},
        {"name": "Design", "keywords": ["figma"]},
    ]}
    result = score_job(profile, {"title": "Python Developer", "description": "Uses pytest"})
    assert result["score"] == 6.7
    assert result["evidence_coverage_percent"] == 50
    assert result["matched_skills"][0]["skill"] == "Python"


# TESTIOSIO ALKAA: test_score_matches_explicit_finnish_inflections_and_compounds.
# FUNKTIO-OSIO PÄÄTTYY: test_skill_score_and_evidence. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
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
    assert result["score"] == 10.0


# TESTIOSIO ALKAA: test_keyword_boundaries_are_unicode_aware.
# FUNKTIO-OSIO PÄÄTTYY: test_score_matches_explicit_finnish_inflections_and_compounds. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
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


# TESTIOSIO ALKAA: test_keyword_matching_normalizes_unicode_compatibility_forms.
# FUNKTIO-OSIO PÄÄTTYY: test_keyword_boundaries_are_unicode_aware. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_keyword_matching_normalizes_unicode_compatibility_forms():
    profile = {"skills": [{"name": "JavaScript", "keywords": ["javascript"]}]}
    result = score_job(profile, {"description": "ＪａｖａＳｃｒｉｐｔ"})
    assert result["matched_skills"][0]["keywords"] == ["javascript"]


# TESTIOSIO ALKAA: test_required_skill_has_more_weight_than_preferred_skill.
# FUNKTIO-OSIO PÄÄTTYY: test_keyword_matching_normalizes_unicode_compatibility_forms. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_required_skill_has_more_weight_than_preferred_skill():
    profile = {"skills": [
        {"name": "Python", "level": 3, "keywords": ["python"]},
        {"name": "Docker", "level": 3, "keywords": ["docker"]},
    ]}
    result = score_job(profile, {
        "description": "Python is required. Docker is nice to have."
    })
    assert result["score"] == 10.0
    assert result["requirement_summary"]["required"] == ["Python"]
    assert result["requirement_summary"]["preferred"] == ["Docker"]


# TESTIOSIO ALKAA: test_explicit_level_requirement_affects_match_score.
# FUNKTIO-OSIO PÄÄTTYY: test_required_skill_has_more_weight_than_preferred_skill. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_explicit_level_requirement_affects_match_score():
    profile = {"skills": [{"name": "Python", "level": 2, "keywords": ["python"]}]}
    low_level = score_job(profile, {"description": "Basic knowledge of Python required."})
    advanced_level = score_job(profile, {"description": "Expert Python experience required."})
    assert low_level["score"] == 10.0
    assert advanced_level["score"] < low_level["score"]
    detail = advanced_level["matched_skills"][0]["details"][0]
    assert detail["advertised_level"] == 4
    assert detail["level_fit"] == 0.5


# TESTIOSIO ALKAA: test_unmatched_keywords_remain_in_denominator.
# FUNKTIO-OSIO PÄÄTTYY: test_explicit_level_requirement_affects_match_score. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_unmatched_keywords_remain_in_denominator():
    profile = {"skills": [{"name": "Python", "level": 3, "keywords": ["python", "pytest"]}]}
    result = score_job(profile, {"description": "Python is required."})
    assert result["score"] == 6.0


# TESTIOSIO ALKAA: test_applicant_baseline_is_not_probability.
# FUNKTIO-OSIO PÄÄTTYY: test_unmatched_keywords_remain_in_denominator. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_applicant_baseline_is_not_probability():
    assert applicant_baseline(100, 1) == 1.0
    assert applicant_baseline(None) is None



# TESTIOSIO ALKAA: test_extracts_required_years_and_seniority.
# FUNKTIO-OSIO PÄÄTTYY: test_applicant_baseline_is_not_probability. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_extracts_required_years_and_seniority():
    result = analyze_experience_requirements({
        "title": "Senior Python Developer",
        "description": "Required: 3+ years of professional experience with Python."
    })
    item = result["items"][0]
    assert item["years_min"] == 3
    assert item["years_max"] is None
    assert item["seniority"] == "senior"
    assert item["scope"] == "professional"
    assert item["requirement"] == "required"


# TESTIOSIO ALKAA: test_extracts_years_range_and_preferred_project_experience.
# FUNKTIO-OSIO PÄÄTTYY: test_extracts_required_years_and_seniority. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_extracts_years_range_and_preferred_project_experience():
    result = analyze_experience_requirements({
        "description": "2–4 years of project experience would be an advantage."
    })
    item = result["items"][0]
    assert item["years_min"] == 2
    assert item["years_max"] == 4
    assert item["scope"] == "project"
    assert item["requirement"] == "preferred"


# TESTIOSIO ALKAA: test_extracts_finnish_experience_and_junior_signals.
# FUNKTIO-OSIO PÄÄTTYY: test_extracts_years_range_and_preferred_project_experience. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_extracts_finnish_experience_and_junior_signals():
    result = analyze_experience_requirements({
        "title": "Junior-ohjelmistokehittäjä",
        "description": "Vähintään 2 vuotta työkokemusta katsotaan eduksi."
    })
    item = result["items"][0]
    assert item["years_min"] == 2
    assert item["seniority"] == "entry"
    assert item["scope"] == "professional"
    assert item["requirement"] == "preferred"


# TESTIOSIO ALKAA: test_experience_parser_does_not_invent_requirements.
# FUNKTIO-OSIO PÄÄTTYY: test_extracts_finnish_experience_and_junior_signals. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_experience_parser_does_not_invent_requirements():
    result = analyze_experience_requirements({
        "title": "Software Developer",
        "description": "We value curiosity, collaboration and learning."
    })
    assert result["items"] == []
    assert result["has_explicit_requirements"] is False


# TESTIOSIO ALKAA: test_score_includes_experience_evidence_without_changing_skill_score.
# FUNKTIO-OSIO PÄÄTTYY: test_experience_parser_does_not_invent_requirements. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_score_includes_experience_evidence_without_changing_skill_score():
    profile = {"skills": [{"name": "Python", "keywords": ["python"], "level": 3}]}
    result = score_job(profile, {
        "description": "Python developer. 5 years of industry experience required."
    })
    assert result["score"] == 10.0
    assert result["experience_requirements"]["items"][0]["years_min"] == 5



# TESTIOSIO ALKAA: test_worldwide_structured_signal_is_rejected_when_restriction_is_present.
# FUNKTIO-OSIO PÄÄTTYY: test_score_includes_experience_evidence_without_changing_skill_score. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.
def test_worldwide_structured_signal_is_rejected_when_restriction_is_present():
    job = {
        "location": "Worldwide",
        "description": "Applicants must be resident in the United States."
    }
    assert not is_worldwide_remote(job, ["United States"])

# FUNKTIO-OSIO PÄÄTTYY: test_worldwide_structured_signal_is_rejected_when_restriction_is_present. Seuraava osio alkaa seuraavasta funktiosta tai luokasta.