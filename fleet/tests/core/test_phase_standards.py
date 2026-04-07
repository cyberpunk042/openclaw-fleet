"""Comprehensive tests for check_phase_standards.

Tests against REAL config/phases.yaml definitions.
Every standard type tested. Every edge case covered.
Every phase in both progressions verified.
"""

import pytest
from fleet.core.phases import (
    check_phase_standards,
    PhaseStandardResult,
    get_phase_definition,
    get_phase_standards,
    get_required_contributions,
    get_next_phase,
    is_phase_gate,
    load_progressions,
)


# ─── Config loading verification ─────────────────────────────────────


def test_progressions_load():
    progs = load_progressions()
    assert "standard" in progs
    assert "release" in progs
    assert len(progs["standard"].phases) == 6  # idea→production
    assert len(progs["release"].phases) == 4   # alpha→release


def test_standard_progression_phase_names():
    progs = load_progressions()
    names = progs["standard"].phase_names
    assert names == ["idea", "conceptual", "poc", "mvp", "staging", "production"]


def test_release_progression_phase_names():
    progs = load_progressions()
    names = progs["release"].phase_names
    assert names == ["alpha", "beta", "rc", "release"]


# ─── Phase definition lookup ─────────────────────────────────────────


def test_get_phase_definition_standard():
    phase = get_phase_definition("poc", "standard")
    assert phase is not None
    assert phase.name == "poc"
    assert "tests" in phase.standards
    assert "docs" in phase.standards
    assert "security" in phase.standards


def test_get_phase_definition_release():
    phase = get_phase_definition("beta", "release")
    assert phase is not None
    assert phase.name == "beta"


def test_get_phase_definition_cross_search():
    """Searching in wrong progression — current behavior returns None
    when progression exists but doesn't contain the phase.
    Falls back to all-search ONLY when progression_name doesn't exist."""
    # beta is in 'release' not 'standard' — standard exists so no fallback
    phase = get_phase_definition("beta", "standard")
    assert phase is None  # standard progression exists, beta not in it

    # Searching with nonexistent progression DOES fallback to search all
    phase = get_phase_definition("beta", "nonexistent")
    assert phase is not None  # found via all-search fallback
    assert phase.name == "beta"


def test_get_phase_definition_unknown():
    phase = get_phase_definition("nonexistent", "standard")
    assert phase is None


def test_get_next_phase_standard():
    assert get_next_phase("poc", "standard") == "mvp"
    assert get_next_phase("mvp", "standard") == "staging"
    assert get_next_phase("production", "standard") is None  # last phase


def test_get_next_phase_release():
    assert get_next_phase("alpha", "release") == "beta"
    assert get_next_phase("release", "release") is None


def test_is_phase_gate():
    assert is_phase_gate("idea", "standard") is False  # only one without gate
    assert is_phase_gate("conceptual", "standard") is True
    assert is_phase_gate("poc", "standard") is True
    assert is_phase_gate("production", "standard") is True


# ─── Required contributions per phase ─────────────────────────────────


def test_idea_no_contributions():
    contribs = get_required_contributions("idea", "standard")
    assert contribs == []


def test_conceptual_architect_required():
    contribs = get_required_contributions("conceptual", "standard")
    assert "architect" in contribs
    assert len(contribs) == 1


def test_mvp_three_contributors():
    contribs = get_required_contributions("mvp", "standard")
    assert "architect" in contribs
    assert "qa-engineer" in contribs
    assert "devsecops-expert" in contribs
    assert len(contribs) == 3


def test_production_all_contributors():
    contribs = get_required_contributions("production", "standard")
    assert "architect" in contribs
    assert "qa-engineer" in contribs
    assert "devsecops-expert" in contribs
    assert "technical-writer" in contribs
    assert "accountability-generator" in contribs
    assert len(contribs) == 5


def test_release_no_contributions():
    """Release progression has no required contributions."""
    for phase in ["alpha", "beta", "rc", "release"]:
        contribs = get_required_contributions(phase, "release")
        assert contribs == [], f"{phase} should have no contributions"


# ─── check_phase_standards — idea phase ───────────────────────────────


def test_idea_phase_always_passes():
    """Idea phase has no standards — always passes."""
    result = check_phase_standards({}, "idea")
    assert result.all_met is True
    assert result.met_pct == 100.0
    assert len(result.gaps) == 0


def test_idea_phase_with_extra_data():
    """Idea phase passes even with random task data."""
    result = check_phase_standards({"random": "stuff", "tests": True}, "idea")
    assert result.all_met is True


# ─── check_phase_standards — conceptual phase ─────────────────────────


def test_conceptual_all_met():
    result = check_phase_standards(
        {"design": True, "requirements": True, "contributions_received": ["architect"]},
        "conceptual",
    )
    assert result.all_met is True
    assert result.met_pct == 100.0


def test_conceptual_missing_design():
    result = check_phase_standards(
        {"requirements": True, "contributions_received": ["architect"]},
        "conceptual",
    )
    assert result.all_met is False
    assert "design" in result.gaps[0]


def test_conceptual_missing_architect_contribution():
    result = check_phase_standards(
        {"design": True, "requirements": True, "contributions_received": []},
        "conceptual",
    )
    assert result.all_met is False
    any_contrib_gap = any("architect" in g for g in result.gaps)
    assert any_contrib_gap, f"Expected architect contribution gap, got: {result.gaps}"


def test_conceptual_missing_everything():
    result = check_phase_standards({}, "conceptual")
    assert result.all_met is False
    assert len(result.gaps) >= 2  # design + requirements + architect contribution


# ─── check_phase_standards — poc phase ─────────────────────────────────


def test_poc_all_met():
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            "contributions_received": ["architect"],
        },
        "poc",
    )
    assert result.all_met is True


def test_poc_missing_tests():
    result = check_phase_standards(
        {"docs": True, "security": True, "contributions_received": ["architect"]},
        "poc",
    )
    assert result.all_met is False
    any_test_gap = any("tests" in g for g in result.gaps)
    assert any_test_gap


def test_poc_missing_docs():
    result = check_phase_standards(
        {"tests": True, "security": True, "contributions_received": ["architect"]},
        "poc",
    )
    assert result.all_met is False
    any_doc_gap = any("docs" in g for g in result.gaps)
    assert any_doc_gap


def test_poc_has_prefixed_keys():
    """Task data can use has_tests instead of tests."""
    result = check_phase_standards(
        {
            "has_tests": True,
            "has_docs": True,
            "has_security": True,
            "contributions_received": ["architect"],
        },
        "poc",
    )
    assert result.all_met is True


# ─── check_phase_standards — mvp phase ─────────────────────────────────


def test_mvp_all_met():
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            "contributions_received": ["architect", "qa-engineer", "devsecops-expert"],
        },
        "mvp",
    )
    assert result.all_met is True


def test_mvp_missing_qa_contribution():
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            "contributions_received": ["architect"],  # missing qa-engineer and devsecops
        },
        "mvp",
    )
    assert result.all_met is False
    any_qa_gap = any("qa-engineer" in g for g in result.gaps)
    any_devsecops_gap = any("devsecops-expert" in g for g in result.gaps)
    assert any_qa_gap
    assert any_devsecops_gap


# ─── check_phase_standards — staging phase ─────────────────────────────


def test_staging_needs_monitoring():
    """Staging phase requires monitoring — unique to this phase."""
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            # monitoring MISSING
            "contributions_received": ["architect", "qa-engineer", "devsecops-expert", "technical-writer"],
        },
        "staging",
    )
    assert result.all_met is False
    any_monitoring_gap = any("monitoring" in g for g in result.gaps)
    assert any_monitoring_gap


def test_staging_all_met():
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            "monitoring": True,
            "contributions_received": ["architect", "qa-engineer", "devsecops-expert", "technical-writer"],
        },
        "staging",
    )
    assert result.all_met is True


# ─── check_phase_standards — production phase ──────────────────────────


def test_production_needs_all_five_contributors():
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            "monitoring": True,
            "contributions_received": ["architect", "qa-engineer", "devsecops-expert", "technical-writer"],
            # missing accountability-generator
        },
        "production",
    )
    assert result.all_met is False
    any_acct_gap = any("accountability-generator" in g for g in result.gaps)
    assert any_acct_gap


def test_production_all_met():
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": True,
            "monitoring": True,
            "contributions_received": [
                "architect", "qa-engineer", "devsecops-expert",
                "technical-writer", "accountability-generator",
            ],
        },
        "production",
    )
    assert result.all_met is True
    assert result.met_pct == 100.0


# ─── check_phase_standards — release progression ──────────────────────


def test_alpha_needs_tests_and_docs():
    result = check_phase_standards(
        {"tests": True},  # docs missing
        "alpha",
        "release",
    )
    assert result.all_met is False
    any_doc_gap = any("docs" in g for g in result.gaps)
    assert any_doc_gap


def test_release_phase_all_met():
    result = check_phase_standards(
        {"tests": True, "docs": True},
        "release",
        "release",
    )
    assert result.all_met is True


# ─── check_phase_standards — unknown phase ─────────────────────────────


def test_unknown_phase_passes():
    """Unknown phase can't be checked — defaults to met."""
    result = check_phase_standards({"anything": True}, "nonexistent_phase")
    assert result.all_met is True
    assert result.met_pct == 100.0


# ─── check_phase_standards — edge cases ────────────────────────────────


def test_empty_task_data():
    """Empty task data against poc phase — all standards are gaps."""
    result = check_phase_standards({}, "poc")
    assert result.all_met is False
    assert len(result.gaps) >= 3  # tests + docs + security + architect


def test_false_values_are_gaps():
    """Explicit False values should be gaps."""
    result = check_phase_standards(
        {"tests": False, "docs": False, "security": False, "contributions_received": []},
        "poc",
    )
    assert result.all_met is False
    assert len(result.gaps) >= 3


def test_empty_string_is_gap():
    """Empty string is falsy — should be a gap."""
    result = check_phase_standards(
        {"tests": "", "docs": "", "security": "", "contributions_received": ["architect"]},
        "poc",
    )
    assert result.all_met is False


def test_zero_is_gap():
    """Zero is falsy — should be a gap."""
    result = check_phase_standards(
        {"tests": 0, "docs": 0, "security": 0, "contributions_received": ["architect"]},
        "poc",
    )
    assert result.all_met is False


def test_met_pct_calculation():
    """Verify met_pct calculates correctly with partial results."""
    result = check_phase_standards(
        {
            "tests": True,
            "docs": True,
            "security": False,
            "contributions_received": ["architect"],
        },
        "poc",
    )
    # 3 standards (tests, docs, security) + 1 contribution (architect) = 4 checks
    # tests met, docs met, security not met, architect met = 3/4 = 75%
    assert 70.0 <= result.met_pct <= 80.0


def test_summary_format_met():
    result = check_phase_standards(
        {"tests": True, "docs": True, "contributions_received": []},
        "alpha",
        "release",
    )
    assert result.all_met is True
    assert "met" in result.summary().lower()


def test_summary_format_not_met():
    result = check_phase_standards({}, "poc")
    assert "NOT met" in result.summary()
    assert "poc" in result.summary()
