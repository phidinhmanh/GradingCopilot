from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.grading_schema import CriterionScore
from app.schemas.rubric_schema import RubricCriterion


SubmissionStatus = Literal["processing", "graded", "error"]


class SubmissionCreateRequest(BaseModel):
    assignment_id: str | None = None
    assignment_question: str = Field(..., min_length=5)
    confirmed_text: str = Field(..., min_length=10)
    approved_rubric: list[RubricCriterion] = Field(..., min_length=1)
    max_score: float = Field(..., gt=0)
    student_name: str = Field(default="Học sinh", min_length=1)
    image_url: str | None = None
    grade_level: str | None = None


class SubmissionCreateResponse(BaseModel):
    id: str
    status: SubmissionStatus
    message: str


class SubmissionGradeDetail(BaseModel):
    score: float = Field(..., ge=0)
    max_points: float = Field(..., gt=0)
    reason: str


class SubmissionGrade(BaseModel):
    id: str
    proposed_score: float = Field(..., ge=0)
    final_score: float | None = None
    is_approved: bool = False
    ai_feedback: str
    final_feedback: str | None = None
    grading_details: dict[str, SubmissionGradeDetail]
    graded_at: datetime


class SubmissionDetailResponse(BaseModel):
    id: str
    assignment_id: str | None = None
    student_name: str
    image_url: str | None = None
    ocr_text: str
    status: SubmissionStatus
    submitted_at: datetime
    grade: SubmissionGrade | None = None


class SubmissionApproveRequest(BaseModel):
    final_score: float = Field(..., ge=0)
    final_feedback: str = Field(..., min_length=1)
    grading_details: dict[str, SubmissionGradeDetail] | None = None


class SubmissionApproveResponse(BaseModel):
    submission_id: str
    final_score: float
    is_approved: bool
    approved_at: datetime


def criteria_scores_to_details(
    criteria_scores: list[CriterionScore],
) -> dict[str, SubmissionGradeDetail]:
    details: dict[str, SubmissionGradeDetail] = {}
    for index, item in enumerate(criteria_scores, start=1):
        details[f"c{index}"] = SubmissionGradeDetail(
            score=item.score,
            max_points=item.max_score,
            reason=item.comment,
        )
    return details
