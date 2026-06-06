import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.grading_schema import (
    ApproveGradeRequest,
    ApprovedGradeResponse,
    GradeFromFileRequest,
    GradeRequest,
    GradeResponse,
)
from app.services.data_file_service import read_data_text_file, read_uploaded_text_file
from app.services.grading_service import approve_grade, grade_student_answer

router = APIRouter(tags=["grading"])


@router.post("/grade", response_model=GradeResponse)
def grade(request: GradeRequest) -> GradeResponse:
    try:
        return grade_student_answer(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/grade/from-files", response_model=GradeResponse)
def grade_from_files(request: GradeFromFileRequest) -> GradeResponse:
    try:
        assignment_question = read_data_text_file(request.assignment_file)
        student_answer_text = read_data_text_file(request.student_answer_file)
        return grade_student_answer(
            GradeRequest(
                assignment_question=assignment_question,
                student_answer_text=student_answer_text,
                approved_rubric=request.approved_rubric,
                max_score=request.max_score,
                grade_level=request.grade_level,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/grade/upload", response_model=GradeResponse)
async def grade_from_upload(
    assignment_file: UploadFile = File(...),
    student_answer_file: UploadFile = File(...),
    approved_rubric: str = Form(...),
    max_score: float = Form(..., gt=0),
    grade_level: str | None = Form(None),
) -> GradeResponse:
    try:
        assignment_question = await read_uploaded_text_file(assignment_file)
        student_answer_text = await read_uploaded_text_file(student_answer_file)
        rubric_data = json.loads(approved_rubric)

        return grade_student_answer(
            GradeRequest(
                assignment_question=assignment_question,
                student_answer_text=student_answer_text,
                approved_rubric=rubric_data,
                max_score=max_score,
                grade_level=grade_level,
            )
        )
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="approved_rubric must be valid JSON.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/grade/approve", response_model=ApprovedGradeResponse)
def approve(request: ApproveGradeRequest) -> ApprovedGradeResponse:
    try:
        return approve_grade(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
