from pathlib import Path

from fastapi import UploadFile

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def read_data_text_file(file_name: str) -> str:
    if not file_name.endswith(".txt"):
        raise ValueError("Only .txt files are supported.")

    file_path = (DATA_DIR / file_name).resolve()
    data_root = DATA_DIR.resolve()

    if data_root not in file_path.parents and file_path != data_root:
        raise ValueError("File name must point to a file inside the data folder.")

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"Data file not found: {file_name}")

    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Data file is empty: {file_name}")

    return text


async def read_uploaded_text_file(file: UploadFile) -> str:
    if not file.filename or not file.filename.endswith(".txt"):
        raise ValueError("Only .txt upload files are supported.")

    content = await file.read()
    try:
        text = content.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ValueError("Uploaded .txt file must be encoded as UTF-8.") from exc

    if not text:
        raise ValueError(f"Uploaded file is empty: {file.filename}")

    return text
