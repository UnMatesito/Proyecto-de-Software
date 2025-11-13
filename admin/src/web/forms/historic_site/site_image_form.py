from __future__ import annotations

from typing import List, Optional

from flask_wtf import FlaskForm
from werkzeug.datastructures import FileStorage
from wtforms import Field, HiddenField, MultipleFileField
from wtforms.validators import ValidationError


class MultiStringField(Field):
    """Campo que almacena una lista de cadenas provenientes de múltiples entradas."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: List[str] = []

    def process_formdata(
        self, valuelist: List[str]
    ) -> None:  # pragma: no cover - wtforms hook
        if not valuelist:
            self.data = []
            return

        self.data = [value.strip() if value is not None else "" for value in valuelist]


class SiteImageUploadForm(FlaskForm):
    """Formulario usado para validar los metadatos al subir nuevas imágenes de un sitio."""

    images = MultipleFileField("Imágenes del sitio")
    image_titles = MultiStringField("Títulos de las imágenes")
    image_descriptions = MultiStringField("Descripciones de las imágenes")
    existing_images = HiddenField()

    class Meta:
        csrf = False

    def __init__(
        self,
        *,
        existing_images: int = 0,
        require_images: bool = False,
        max_images: int = 10,
        **kwargs,
    ) -> None:
        self.require_images = require_images
        self.max_images = max_images
        self.existing_images_count = max(0, existing_images)
        super().__init__(**kwargs)

        # Mantener el campo oculto sincronizado con el valor calculado en el servidor.
        self.existing_images.data = str(self.existing_images_count)

    def validate_images(self, field: MultipleFileField) -> None:
        files: List[FileStorage] = [
            file
            for file in (field.data or [])
            if file is not None and getattr(file, "filename", "")
        ]

        if self.require_images and not files:
            raise ValidationError("Debe subir al menos una imágen.")

        if not files:
            field.data = []
            return

        allowed_extensions = {"jpg", "jpeg", "png", "webp"}
        invalid_files: List[str] = []

        for file in files:
            filename = (file.filename or "").strip()
            if "." not in filename:
                invalid_files.append(filename or "Archivo sin nombre")
                continue

            extension = filename.rsplit(".", 1)[1].lower()
            if extension not in allowed_extensions:
                invalid_files.append(filename)

        if invalid_files:
            raise ValidationError(
                "Solo se permiten imágenes en formato JPG, JPEG, PNG o WEBP."
            )

        total_images = self.existing_images_count + len(files)
        if total_images > self.max_images:
            remaining_slots = max(0, self.max_images - self.existing_images_count)
            if remaining_slots <= 0:
                raise ValidationError(
                    "Ya se alcanzó el máximo de 10 imágenes para el sitio."
                )

            raise ValidationError(
                f"Solo podés agregar {remaining_slots} imágenes nuevas para no superar el máximo de {self.max_images}."
            )

        field.data = files

    def validate_image_titles(self, field: MultiStringField) -> None:
        files: List[FileStorage] = self.images.data or []

        if not files:
            field.data = []
            return

        titles = field.data or []

        if len(titles) < len(files):
            raise ValidationError("Cada imagen nueva debe tener un título.")

        cleaned_titles: List[str] = []

        for index, title in enumerate(titles[: len(files)]):
            normalized = (title or "").strip()
            if not normalized:
                raise ValidationError("Cada imagen nueva debe tener un título.")

            if len(normalized) > 100:
                raise ValidationError(
                    "El título de cada imagen debe tener a lo sumo 100 caracteres."
                )

            cleaned_titles.append(normalized)

        field.data = cleaned_titles

    def validate_image_descriptions(self, field: MultiStringField) -> None:
        files: List[FileStorage] = self.images.data or []

        if not files:
            field.data = []
            return

        descriptions = field.data or []
        cleaned: List[Optional[str]] = []

        for index in range(len(files)):
            value = descriptions[index] if index < len(descriptions) else ""
            normalized = (value or "").strip()

            if normalized and len(normalized) > 255:
                raise ValidationError(
                    "La descripción de cada imagen puede tener como máximo 255 caracteres."
                )

            cleaned.append(normalized or None)

        field.data = cleaned
