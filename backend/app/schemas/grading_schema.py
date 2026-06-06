from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.rubric_schema import RubricCriterion


class CriterionScore(BaseModel):
    criterion: str = Field(..., min_length=1)
    score: float = Field(..., ge=0)
    max_score: float = Field(..., gt=0)
    comment: str = Field(..., min_length=1)


class GradeRequest(BaseModel):
    assignment_question: str = Field(..., min_length=5)
    student_answer_text: str = Field(..., min_length=10)
    approved_rubric: list[RubricCriterion] = Field(..., min_length=1)
    max_score: float = Field(..., gt=0)
    grade_level: str | None = None


class GradeFromFileRequest(BaseModel):
    assignment_file: str = Field(..., min_length=5)
    student_answer_file: str = Field(..., min_length=5)
    approved_rubric: list[RubricCriterion] = Field(..., min_length=1)
    max_score: float = Field(..., gt=0)
    grade_level: str | None = None


class GradeResponse(BaseModel):
    draft_total_score: float = Field(..., ge=0)
    max_score: float = Field(..., gt=0)
    criteria_scores: list[CriterionScore] = Field(..., min_length=1)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    student_feedback: str
    confidence: Literal["low", "medium", "high"]
    teacher_review_required: bool = True
    raw_model_output: dict[str, Any] = Field(default_factory=dict)


class ApproveGradeRequest(BaseModel):
    student_name: str = Field(..., min_length=1)
    assignment_question: str = Field(..., min_length=5)
    final_criteria_scores: list[CriterionScore] = Field(..., min_length=1)
    final_feedback: str = Field(..., min_length=1)
    teacher_note: str | None = None


class ApprovedGradeResponse(BaseModel):
    student_name: str
    final_total_score: float
    status: Literal["approved"]
    final_criteria_scores: list[CriterionScore]
    final_feedback: str
    teacher_note: str | None = None
