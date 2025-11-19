"""
이미지 업로드/전처리 관련 유틸리티.
"""

from __future__ import annotations

import io
from typing import Optional

from PIL import Image, ImageOps


def fix_image_orientation(image_file) -> Optional[Image.Image]:
    """
    EXIF orientation 메타데이터를 처리하여 이미지를 올바르게 회전합니다.
    """
    if image_file is None:
        return None

    image_bytes = None
    try:
        if hasattr(image_file, "read"):
            if hasattr(image_file, "tell"):
                original_position = image_file.tell()
            else:
                original_position = 0

            if hasattr(image_file, "seek"):
                image_file.seek(0)
            image_bytes = image_file.read()
            if hasattr(image_file, "seek"):
                image_file.seek(original_position)
        else:
            image_bytes = image_file

        if not image_bytes:
            return None

        image = Image.open(io.BytesIO(image_bytes))
        rotated_image = ImageOps.exif_transpose(image)
        return rotated_image if rotated_image is not None else image
    except Exception:
        try:
            if image_bytes:
                return Image.open(io.BytesIO(image_bytes))
        except Exception:
            return None
        return None


def convert_image_to_bytes(image: Optional[Image.Image]) -> Optional[bytes]:
    """PIL 이미지를 JPEG bytes로 변환."""
    if image is None:
        return None

    try:
        buffer = io.BytesIO()
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            mask = image.split()[-1] if image.mode in ("RGBA", "LA") else None
            background.paste(image, mask=mask)
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        image.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)
        data = buffer.read()
        return data or None
    except Exception:
        return None
