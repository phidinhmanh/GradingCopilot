from app.prompts.rubric_prompt import build_rubric_prompt
from app.schemas.rubric_schema import GenerateRubricRequest, RubricGenerateResponse
from app.services.gemini_client import call_gemini_json
from app.services.validation import assert_score_total_equal


def generate_draft_rubric(request: GenerateRubricRequest) -> RubricGenerateResponse:
    prompt = build_rubric_prompt(
        assignment_question=request.assignment_question,
        max_score=request.max_score,
        grade_level=request.grade_level,
    )
    model_output = call_gemini_json(prompt)
    response = RubricGenerateResponse.model_validate(model_output)

    assert_score_total_equal(
        actual=response.total_score,
        expected=request.max_score,
        field_name="draft_rubric total_score",
    )
    assert_score_total_equal(
        actual=sum(item.max_score for item in response.draft_rubric),
        expected=request.max_score,
        field_name="sum of draft_rubric max_score",
    )

    if response.teacher_review_required is not True:
        raise ValueError("teacher_review_required must be true for draft rubrics.")

    return response
