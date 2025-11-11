from core.database import db
from core.models import SiteImage, HistoricSite
from core.storage import storage
from werkzeug.datastructures import FileStorage
from typing import List, Optional


def create_site_image(
        historic_site_id: int,
        file: FileStorage,
        order: int,
        is_cover: bool = False,
        title: Optional[str] = None,
        description: Optional[str] = None
) -> SiteImage:
    """Crea una imagen para un sitio histórico"""

    # Subir imagen a MinIO con URL pública permanente
    result = storage.upload_file(
        file_storage=file,
        folder=f"sites/{historic_site_id}",
        validate=True,
        public=True  # URL pública sin vencimiento
    )
    # Crear registro en BD
    image = SiteImage(
        historic_site_id=historic_site_id,
        public_url=result['url'],
        title=title or file.filename,
        description=description,
        is_cover=is_cover,
        order=order
    )

    db.session.add(image)
    db.session.commit()

    return image


def create_multiple_images(
        historic_site_id: int,
        files: List[FileStorage],
        set_first_as_cover: bool = True
) -> List[SiteImage]:
    """Crea múltiples imágenes para un sitio histórico"""

    if len(files) > 10:
        raise ValueError("No se pueden subir más de 10 imágenes")

    images = []
    for index, file in enumerate(files):
        if file and file.filename:  # Verificar que el archivo existe
            is_cover = (index == 0 and set_first_as_cover)
            image = create_site_image(
                historic_site_id=historic_site_id,
                file=file,
                order=index,
                is_cover=is_cover
            )
            images.append(image)

    return images


def delete_site_image(image_id: int) -> bool:
    """Elimina una imagen del sitio histórico"""
    image = SiteImage.query.get_or_404(image_id)

    # Eliminar de MinIO
    try:
        storage.delete_file(file_url=image.public_url)
    except Exception as e:
        print(f"Error al eliminar imagen de MinIO: {e}")

    # Eliminar de BD
    db.session.delete(image)
    db.session.commit()

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
        historic_site_id=historic_site_id,
        is_cover=True
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