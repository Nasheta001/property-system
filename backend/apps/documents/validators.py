import os

from django.core.exceptions import ValidationError

ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".jpg", ".jpeg", ".png"}
MAX_DOCUMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25MB


def validate_document_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}."
        )
    if file.size > MAX_DOCUMENT_SIZE_BYTES:
        raise ValidationError("File is too large. Maximum size is 25MB.")
