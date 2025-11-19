from typing import List, Optional, Sequence

from werkzeug.datastructures import FileStorage

from core.database import db
from core.models import HistoricSite, SiteImage
from core.storage import storage


def create_site_image(
    historic_site_id: int,
    file: FileStorage,
    order: int,
    is_cover: bool = False,
    title: str = None,
    description: Optional[str] = None,
) -> SiteImage:
    """Crea una imagen para un sitio histórico"""

    # Subir imagen a MinIO con URL pública permanente
    result = storage.upload_file(
        file_storage=file,
        folder=f"sites/{historic_site_id}",
        validate=True,
        public=True,  # URL pública sin vencimiento
    )
    # Crear registro en BD
    normalized_title = (title or "").strip()

    if not normalized_title:
        raise ValueError("El título de la imagen es obligatorio")

    normalized_description = (description or "").strip() or None
    image = SiteImage(
        historic_site_id=historic_site_id,
        public_url=result["url"],
        title=normalized_title,
        description=normalized_description,
        is_cover=is_cover,
        order=order,
    )

    db.session.add(image)
    db.session.commit()

    return image


def create_multiple_images(
    historic_site_id: int,
    files: List[FileStorage],
    set_first_as_cover: bool = True,
    titles: Sequence[str] = None,
    descriptions: Optional[Sequence[str]] = None,
) -> List[SiteImage]:
    """Crea múltiples imágenes para un sitio histórico"""

    if len(files) > 10:
        raise ValueError("No se pueden subir más de 10 imágenes")

    if titles is not None and len(titles) < len(files):
        raise ValueError("Cada imagen debe incluir un título")

    images = []
    for index, file in enumerate(files):
        if file and file.filename:  # Verificar que el archivo existe
            is_cover = index == 0 and set_first_as_cover
            title_value = None
            if titles is not None:
                title_value = titles[index].strip() if titles[index] is not None else ""

            description_value = None
            if descriptions is not None and index < len(descriptions):
                raw_description = descriptions[index]
                description_value = raw_description.strip() if raw_description else None

            image = create_site_image(
                historic_site_id=historic_site_id,
                file=file,
                order=index,
                is_cover=is_cover,
                title=title_value,
                description=description_value,
            )
            images.append(image)

    return images


def _resequence_site_images(historic_site_id: int) -> None:
    """Normaliza el orden y portada de las imágenes restantes."""

    remaining_images = (
        SiteImage.query.filter_by(historic_site_id=historic_site_id)
        .order_by(SiteImage.order.asc(), SiteImage.id.asc())
        .all()
    )

    if not remaining_images:
        return

    for index, image in enumerate(remaining_images):
        image.order = index
        image.is_cover = index == 0

    db.session.commit()


def delete_site_image(image_id: int) -> bool:
    """Elimina una imagen del sitio histórico"""
    image = SiteImage.query.get_or_404(image_id)

    total_images = SiteImage.query.filter_by(
        historic_site_id=image.historic_site_id
    ).count()

    if total_images <= 1:
        raise ValueError("El sitio debe conservar al menos una imagen")

    # Eliminar de MinIO
    try:
        storage.delete_file(file_url=image.public_url)
    except Exception as e:
        print(f"Error al eliminar imagen de MinIO: {e}")

    # Eliminar de BD
    historic_site_id = image.historic_site_id

    db.session.delete(image)
    db.session.commit()

    _resequence_site_images(historic_site_id)

    return True


def delete_all_site_images(historic_site_id: int) -> bool:
    """Elimina todas las imágenes de un sitio histórico"""
    images = SiteImage.query.filter_by(historic_site_id=historic_site_id).all()

    for image in images:
        try:
            storage.delete_file(file_url=image.public_url)
        except Exception as e:
            print(f"Error al eliminar imagen de MinIO: {e}")

        db.session.delete(image)

    db.session.commit()
    return True


def update_image_order(image_id: int, new_order: int) -> SiteImage:
    """Actualiza el orden de una imagen"""
    image = SiteImage.query.get_or_404(image_id)
    image.order = new_order
    db.session.commit()
    return image


def set_cover_image(image_id: int, historic_site_id: int) -> SiteImage:
    """Establece una imagen como portada del sitio"""

    # Quitar portada actual
    current_cover = SiteImage.query.filter_by(
        historic_site_id=historic_site_id, is_cover=True
    ).first()

    if current_cover:
        current_cover.is_cover = False

    # Establecer nueva portada
    new_cover = SiteImage.query.get_or_404(image_id)
    new_cover.is_cover = True

    db.session.commit()
    return new_cover


def get_site_images(historic_site_id: int, ordered: bool = True) -> List[SiteImage]:
    """Obtiene todas las imágenes de un sitio histórico"""
    query = SiteImage.query.filter_by(historic_site_id=historic_site_id)

    if ordered:
        query = query.order_by(SiteImage.order.asc())

    return query.all()


def reorder_site_images(historic_site_id: int, ordered_image_ids: List[int]) -> None:
    """Reordena las imágenes asignando la portada a la primera."""

    if not ordered_image_ids:
        return

    images = SiteImage.query.filter_by(historic_site_id=historic_site_id).all()
    existing_ids = {image.id for image in images}
    incoming_ids = list(dict.fromkeys(ordered_image_ids))

    if existing_ids != set(incoming_ids):
        raise ValueError("El orden recibido no coincide con las imágenes del sitio")

    image_map = {image.id: image for image in images}

    for index, image_id in enumerate(incoming_ids):
        image = image_map.get(image_id)
        if image is None:
            raise ValueError("Imagen no encontrada para reordenar")

        image.order = index
        image.is_cover = index == 0

    db.session.commit()
