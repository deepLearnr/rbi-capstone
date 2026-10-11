from app.services.learning_progress import (
    calculate_section_progress,
    update_completed_sections,
)


def test_section_progress_is_based_on_unique_completed_sections():
    ids = update_completed_sections([], 10, True)
    ids = update_completed_sections(ids, 11, True)
    assert ids == [10, 11]
    assert calculate_section_progress(ids, 4) == 50


def test_unchecking_section_reduces_progress():
    ids = update_completed_sections([10, 11, 12], 11, False)
    assert ids == [10, 12]
    assert calculate_section_progress(ids, 4) == 50


def test_empty_module_never_reports_completion_percentage():
    assert calculate_section_progress([10], 0) == 0


def test_repeated_completion_toggle_does_not_double_count():
    ids = update_completed_sections([10], 10, True)
    assert ids == [10]
    assert calculate_section_progress(ids, 2) == 50
