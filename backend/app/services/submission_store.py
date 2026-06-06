from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.grading_schema import GradeRequest
from app.schemas.submission_schema import (
    SubmissionApproveRequest,
    SubmissionApproveResponse,
    SubmissionCreateRequest,
    SubmissionCreateResponse,
    SubmissionDetailResponse,
    SubmissionGrade,
    criteria_scores_to_details,
)
from app.services.grading_service import grade_student_answer

_submissions: dict[str, SubmissionDetailResponse] = {}


def create_submission(request: SubmissionCreateRequest) -> SubmissionCreateResponse:
    submission_id = str(uuid4())
    grade_id = str(uuid4())
    now = datetime.now(UTC)

    draft_grade = grade_student_answer(
        GradeRequest(
            assignment_question=request.assignment_question,
            student_answer_text=request.confirmed_text,
            approved_rubric=request.approved_rubric,
            max_score=request.max_score,
            grade_level=request.grade_level,
        )
    )

    grade = SubmissionGrade(
        id=grade_id,
        proposed_score=draft_grade.draft_total_score,
        ai_feedback=draft_grade.student_feedback,
        grading_details=criteria_scores_to_details(draft_grade.criteria_scores),
        graded_at=now,
    )
    _submissions[submission_id] = SubmissionDetailResponse(
        id=submission_id,
        assignment_id=request.assignment_id,
        student_name=request.student_name,
        image_url=request.image_url,
        ocr_text=request.confirmed_text,
        status="graded",
        submitted_at=now,
        grade=grade,
    )

    return SubmissionCreateResponse(
        id=submission_id,
        status="graded",
        message="Nộp bài thành công. Hệ thống đã tạo điểm AI nháp để giáo viên duyệt.",
    )


def get_submission(submission_id: str) -> SubmissionDetailResponse | None:
    submission = _submissions.get(submission_id)
    return deepcopy(submission) if submission else None


def delete_submission(submission_id: str) -> bool:
    submission = _submissions.get(submission_id)
    if not submission:
        return False
    if submission.grade and submission.grade.is_approved:
        raise ValueError("Cannot delete an approved submission.")
    del _submissions[submission_id]
    return True


def approve_submission(
    submission_id: str,
    request: SubmissionApproveRequest,
) -> SubmissionApproveResponse | None:
    submission = _submissions.get(submission_id)
    if not submission:
        return None
    if not submission.grade:
        raise ValueError("Submission has no grade to approve.")

    approved_at = datetime.now(UTC)
    submission.grade.final_score = request.final_score
    submission.grade.final_feedback = request.final_feedback
    submission.grade.is_approved = True
    if request.grading_details is not None:
        submission.grade.grading_details = request.grading_details

    return SubmissionApproveResponse(
        submission_id=submission_id,
        final_score=request.final_score,
        is_approved=True,
        approved_at=approved_at,
    )
