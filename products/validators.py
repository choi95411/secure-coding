from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_product_image(upload):
    extension = Path(upload.name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("JPG, PNG 또는 WebP 이미지만 업로드할 수 있습니다.")
    if upload.size > MAX_IMAGE_BYTES:
        raise ValidationError("이미지는 5MB 이하여야 합니다.")
    content_type = getattr(upload, "content_type", "")
    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES:
        raise ValidationError("허용되지 않은 이미지 MIME 형식입니다.")
    try:
        image = Image.open(upload)
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("손상되었거나 유효하지 않은 이미지입니다.") from exc
    finally:
        upload.seek(0)
