from math import isclose
from typing import Iterable, Protocol

from app.schemas.rubric_schema import RubricCriterion


class ScoredCriterion(Protocol):
    criterion: str
    score: float
    max_score: float


def assert_score_total_equal(
    actual: float,
    expected: float,
    field_name: str,
    tolerance: float = 0.01,
) -> None:
    if not isclose(actual, expected, abs_tol=tolerance):
        raise ValueError(
            f"{field_name} must equal max_score. Expected {expected}, got {actual}."
        )


def assert_scores_within_max(criteria_scores: Iterable[ScoredCriterion]) -> None:
    for item in criteria_scores:
        if item.score > item.max_score:
            raise ValueError(
                f"Score for criterion '{item.criterion}' exceeds max_score "
                f"({item.score} > {item.max_score})."
            )


def assert_criteria_match_rubric(
    criteria_scores: list[ScoredCriterion],
    approved_rubric: list[RubricCriterion],
) -> None:
    if len(criteria_scores) != len(approved_rubric):
        raise ValueError("Model criteria_scores must match approved_rubric length.")

    rubric_by_name = {item.criterion: item for item in approved_rubric}
    for item in criteria_scores:
        rubric_item = rubric_by_name.get(item.criterion)
        if rubric_item is None:
            raise ValueError(
                f"Model returned criterion '{item.criterion}' outside approved_rubric."
            )
        assert_score_total_equal(
            actual=item.max_score,
            expected=rubric_item.max_score,
            field_name=f"max_score for criterion '{item.criterion}'",
        )
