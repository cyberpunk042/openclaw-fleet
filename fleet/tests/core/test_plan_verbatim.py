"""Comprehensive tests for check_plan_references_verbatim.

Verifies key term extraction, coverage analysis, threshold behavior,
edge cases, and the warning messages produced.
"""

from fleet.core.plan_quality import check_plan_references_verbatim


# ─── Good plans that reference verbatim ──────────────────────────────


def test_plan_fully_references_verbatim():
    result = check_plan_references_verbatim(
        plan_text="I will add type hints to the fleet engine module and write tests for all public functions.",
        verbatim="Add type hints to the fleet engine module. Ensure all public functions have proper typing.",
    )
    assert result.references_verbatim is True
    assert result.coverage_pct >= 30.0
    assert "hints" in result.matched_terms
    assert "engine" in result.matched_terms


def test_plan_uses_different_words_but_same_concepts():
    """Plan uses synonyms — key terms from verbatim should still match."""
    result = check_plan_references_verbatim(
        plan_text="Implement JWT-based authentication for the REST API endpoints using RS256 signing.",
        verbatim="Add JWT authentication to the REST API endpoints with RS256.",
    )
    assert result.references_verbatim is True
    assert "authentication" in result.matched_terms or "endpoints" in result.matched_terms


def test_plan_with_specific_file_references():
    result = check_plan_references_verbatim(
        plan_text="Will modify fleet/core/engine.py to add type annotations. Also update fleet/core/models.py.",
        verbatim="Add type annotations to engine.py and models.py in fleet/core.",
    )
    assert result.references_verbatim is True
    assert "engine" in result.matched_terms or "annotations" in result.matched_terms


# ─── Plans that DON'T reference verbatim ──────────────────────────────


def test_plan_completely_unrelated():
    result = check_plan_references_verbatim(
        plan_text="I will refactor the database schema and add new migrations for the user table.",
        verbatim="Add fleet controls to the header bar with status indicators.",
    )
    assert result.references_verbatim is False
    assert result.coverage_pct < 30.0
    assert len(result.warning) > 0
    assert "may not reference" in result.warning.lower()


def test_plan_vague_no_specifics():
    result = check_plan_references_verbatim(
        plan_text="I will work on the task and implement what's needed.",
        verbatim="Implement real-time websocket notifications for sprint progress updates.",
    )
    assert result.references_verbatim is False
    assert result.coverage_pct < 30.0


def test_plan_partially_related():
    """Plan mentions some terms but misses the core requirement."""
    result = check_plan_references_verbatim(
        plan_text="I will update the configuration files and add some tests.",
        verbatim="Add real-time websocket notifications for sprint progress updates with channel routing.",
    )
    # Very low coverage — plan doesn't mention websocket, notifications, sprint, progress, routing
    assert result.coverage_pct < 30.0


# ─── Empty and edge cases ──────────────────────────────────────────────


def test_empty_verbatim():
    """No verbatim — can't check, defaults to True with warning."""
    result = check_plan_references_verbatim(
        plan_text="I will implement the feature.",
        verbatim="",
    )
    assert result.references_verbatim is True
    assert "No verbatim" in result.warning


def test_empty_plan():
    """Empty plan — fails with warning."""
    result = check_plan_references_verbatim(
        plan_text="",
        verbatim="Add type hints to the engine module.",
    )
    assert result.references_verbatim is False
    assert "empty" in result.warning.lower()


def test_whitespace_only_verbatim():
    result = check_plan_references_verbatim(
        plan_text="I will do the work.",
        verbatim="   ",
    )
    assert result.references_verbatim is True  # Can't check against whitespace


def test_very_short_verbatim():
    """Verbatim with only short common words — no key terms extractable."""
    result = check_plan_references_verbatim(
        plan_text="I will fix the bug.",
        verbatim="Fix it.",
    )
    # "Fix" and "it" are too short or common — no key terms
    assert result.references_verbatim is True
    assert "no significant key terms" in result.warning.lower() or result.total_key_terms == 0


def test_none_verbatim():
    """None verbatim — should handle gracefully."""
    result = check_plan_references_verbatim(
        plan_text="I will implement.",
        verbatim=None,
    )
    # Should not crash — treat as empty
    assert result.references_verbatim is True


def test_none_plan():
    """None plan — should handle gracefully."""
    result = check_plan_references_verbatim(
        plan_text=None,
        verbatim="Add something.",
    )
    assert result.references_verbatim is False


# ─── Coverage threshold behavior ──────────────────────────────────────


def test_exactly_at_threshold():
    """Coverage right at 30% threshold."""
    # Create verbatim with 10 key terms, plan mentions 3 of them
    verbatim = "implement authentication middleware validation security endpoint controller database migration schema"
    plan = "I will implement the authentication middleware."
    result = check_plan_references_verbatim(plan, verbatim)
    # 3/10 = 30% — at threshold
    assert result.references_verbatim is True


def test_just_below_threshold():
    """Coverage just below 30%."""
    verbatim = "implement authentication middleware validation security endpoint controller database migration schema deployment"
    plan = "I will implement something."
    result = check_plan_references_verbatim(plan, verbatim)
    # only "implement" matches — 1/11 = 9%
    assert result.references_verbatim is False


# ─── Key term extraction ──────────────────────────────────────────────


def test_short_words_excluded():
    """Words under 4 chars should be excluded from key terms."""
    result = check_plan_references_verbatim(
        plan_text="Add a new API for the CLI.",
        verbatim="Add a new API for the CLI tool.",
    )
    # "add", "new", "api", "for", "the", "cli" — most under 4 chars
    # Only "tool" is 4+ and not common
    assert result.total_key_terms <= 2  # very few key terms from short words


def test_common_words_excluded():
    """Common words (that, this, with, etc.) excluded from key terms."""
    result = check_plan_references_verbatim(
        plan_text="I will implement the authentication system with proper validation.",
        verbatim="This system should have authentication with proper validation.",
    )
    # "this", "should", "have", "with" are common — excluded
    # "system", "authentication", "proper", "validation" are key terms
    assert "authentication" in result.matched_terms or "validation" in result.matched_terms


def test_matched_terms_list():
    """Verify matched_terms contains actual matches."""
    result = check_plan_references_verbatim(
        plan_text="The engine module needs type hints on all functions.",
        verbatim="Add type hints to the engine module functions.",
    )
    for term in result.matched_terms:
        assert term in "add type hints to the engine module functions".lower()


def test_deduplication():
    """Repeated words in verbatim counted once."""
    result = check_plan_references_verbatim(
        plan_text="Authentication system.",
        verbatim="Authentication authentication authentication system system.",
    )
    # Should deduplicate: only "authentication" and "system" as key terms
    assert result.total_key_terms == 2


# ─── Warning messages ──────────────────────────────────────────────────


def test_warning_includes_missing_terms():
    """Warning should list missing key terms when plan doesn't reference verbatim."""
    result = check_plan_references_verbatim(
        plan_text="I will do something completely different.",
        verbatim="Implement websocket notifications for sprint progress.",
    )
    assert result.references_verbatim is False
    assert "Missing key terms" in result.warning or "missing" in result.warning.lower()


def test_no_warning_when_references():
    """No warning when plan references verbatim properly."""
    result = check_plan_references_verbatim(
        plan_text="I will implement websocket notifications for sprint progress updates.",
        verbatim="Implement websocket notifications for sprint progress.",
    )
    assert result.references_verbatim is True
    assert result.warning == ""
