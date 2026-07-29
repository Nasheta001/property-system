import os

from django.core.exceptions import ValidationError

ALLOWED_ATTACHMENT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".webm"}
MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25MB


def validate_attachment_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_ATTACHMENT_EXTENSIONS))}."
        )
    if file.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValidationError("File is too large. Maximum size is 25MB.")
