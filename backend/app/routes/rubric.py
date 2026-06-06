from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.rubric_schema import (
    GenerateRubricFromFileRequest,
    GenerateRubricRequest,
    RubricGenerateResponse,
)
from app.services.data_file_service import read_data_text_file, read_uploaded_text_file
from app.services.rubric_service import generate_draft_rubric

router = APIRouter(prefix="/rubric", tags=["rubric"])


@router.post("/generate", response_model=RubricGenerateResponse)
def generate_rubric(request: GenerateRubricRequest) -> RubricGenerateResponse:
    try:
        return generate_draft_rubric(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/generate-from-files", response_model=RubricGenerateResponse)
def generate_rubric_from_files(
    request: GenerateRubricFromFileRequest,
) -> RubricGenerateResponse:
    try:
        assignment_question = read_data_text_file(request.assignment_file)
        return generate_draft_rubric(
            GenerateRubricRequest(
                assignment_question=assignment_question,
                max_score=request.max_score,
                grade_level=request.grade_level,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post("/generate-upload", response_model=RubricGenerateResponse)
async def generate_rubric_from_upload(
    assignment_file: UploadFile = File(...),
    max_score: float = Form(..., gt=0),
    grade_level: str | None = Form(None),
) -> RubricGenerateResponse:
    try:
        assignment_question = await read_uploaded_text_file(assignment_file)
        return generate_draft_rubric(
            GenerateRubricRequest(
                assignment_question=assignment_question,
                max_score=max_score,
                grade_level=grade_level,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
