import uuid
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")
PRODUCT_IMAGE_DIR = settings.UPLOAD_DIR / "products"
PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
MAX_IMAGE_SIZE_MB = 5


def save_product_image(upload_file: UploadFile) -> str:
    """Persist a vendor product image locally. Returns a path relative to
    UPLOAD_DIR (e.g. 'products/<uuid>_photo.jpg'), used to build the public
    /static URL and stored on VendorProduct.image_path."""
    suffix = Path(upload_file.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{suffix}'. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )

    stored_filename = f"{uuid.uuid4()}{suffix}"
    destination = PRODUCT_IMAGE_DIR / stored_filename

    size = 0
    max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024
    with open(destination, "wb") as buffer:
        while chunk := upload_file.file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                buffer.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image exceeds the {MAX_IMAGE_SIZE_MB}MB upload limit",
                )
            buffer.write(chunk)

    return f"products/{stored_filename}"


def delete_product_image(relative_path: Optional[str]) -> None:
    if not relative_path:
        return
    path = settings.UPLOAD_DIR / relative_path
    path.unlink(missing_ok=True)


def validate_upload_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{suffix}'. Allowed types: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}",
        )
    return suffix.lstrip(".")


def save_upload_file(upload_file: UploadFile) -> Tuple[str, str, str]:
    """Persist an uploaded file to disk. Returns (stored_filename, file_path, file_type)."""
    file_type = validate_upload_extension(upload_file.filename)
    stored_filename = f"{uuid.uuid4()}_{upload_file.filename}"
    destination = settings.UPLOAD_DIR / stored_filename

    size = 0
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    with open(destination, "wb") as buffer:
        while chunk := upload_file.file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                buffer.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit",
                )
            buffer.write(chunk)

    return stored_filename, str(destination), file_type


def read_dataset(file_path: str, file_type: str) -> pd.DataFrame:
    try:
        if file_type == "csv":
            return pd.read_csv(file_path)
        return pd.read_excel(file_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse dataset: {exc}",
        ) from exc


def write_cleaned_dataset(df: pd.DataFrame, dataset_id: uuid.UUID) -> str:
    destination = settings.CLEANED_DATA_DIR / f"{dataset_id}.csv"
    df.to_csv(destination, index=False)
    return str(destination)
