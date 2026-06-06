from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.submission_schema import (
    SubmissionApproveRequest,
    SubmissionApproveResponse,
    SubmissionCreateRequest,
    SubmissionCreateResponse,
    SubmissionDetailResponse,
)
from app.services.submission_store import (
    approve_submission,
    create_submission,
    delete_submission,
    get_submission,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_assignment(request: SubmissionCreateRequest) -> SubmissionCreateResponse:
    try:
        return create_submission(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
def read_submission(submission_id: str) -> SubmissionDetailResponse:
    submission = get_submission(submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )
    return submission


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_submission(submission_id: str) -> Response:
    try:
        deleted = delete_submission(submission_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{submission_id}/approve", response_model=SubmissionApproveResponse)
def approve_submission_grade(
    submission_id: str,
    request: SubmissionApproveRequest,
) -> SubmissionApproveResponse:
    try:
        approved = approve_submission(submission_id, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if not approved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )
    return approved
