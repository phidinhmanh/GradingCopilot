from pydantic import BaseModel, Field


class RubricCriterion(BaseModel):
    criterion: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    max_score: float = Field(..., gt=0)


class GenerateRubricRequest(BaseModel):
    assignment_question: str = Field(..., min_length=5)
    max_score: float = Field(..., gt=0)
    grade_level: str | None = None


class GenerateRubricFromFileRequest(BaseModel):
    assignment_file: str = Field(..., min_length=5)
    max_score: float = Field(..., gt=0)
    grade_level: str | None = None


class RubricGenerateResponse(BaseModel):
    draft_rubric: list[RubricCriterion] = Field(..., min_length=1)
    total_score: float = Field(..., gt=0)
    teacher_review_required: bool = True
