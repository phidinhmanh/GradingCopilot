from app.prompts.grading_prompt import build_grading_prompt
from app.schemas.grading_schema import (
    ApproveGradeRequest,
    ApprovedGradeResponse,
    GradeRequest,
    GradeResponse,
)
from app.services.gemini_client import call_gemini_json
from app.services.validation import (
    assert_criteria_match_rubric,
    assert_score_total_equal,
    assert_scores_within_max,
)


def grade_student_answer(request: GradeRequest) -> GradeResponse:
    assert_score_total_equal(
        actual=sum(item.max_score for item in request.approved_rubric),
        expected=request.max_score,
        field_name="approved_rubric total",
    )

    prompt = build_grading_prompt(
        assignment_question=request.assignment_question,
        student_answer_text=request.student_answer_text,
        approved_rubric=request.approved_rubric,
        max_score=request.max_score,
        grade_level=request.grade_level,
    )
    model_output = call_gemini_json(prompt)
    response = GradeResponse.model_validate(
        {
            **model_output,
            "max_score": request.max_score,
            "raw_model_output": model_output,
        }
    )

    assert_criteria_match_rubric(response.criteria_scores, request.approved_rubric)
    assert_scores_within_max(response.criteria_scores)

    draft_total_score = sum(item.score for item in response.criteria_scores)
    response.draft_total_score = draft_total_score

    if response.teacher_review_required is not True:
        raise ValueError("teacher_review_required must be true for AI draft grades.")

    return response


def approve_grade(request: ApproveGradeRequest) -> ApprovedGradeResponse:
    assert_scores_within_max(request.final_criteria_scores)
    final_total_score = sum(item.score for item in request.final_criteria_scores)

    return ApprovedGradeResponse(
        student_name=request.student_name,
        final_total_score=final_total_score,
        status="approved",
        final_criteria_scores=request.final_criteria_scores,
        final_feedback=request.final_feedback,
        teacher_note=request.teacher_note,
    )
