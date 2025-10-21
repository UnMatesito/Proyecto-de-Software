from core.database import db
from core.models.site_image import SiteImage

def add_image(site_id: int, url: str, title: str, description: str = "", is_cover: bool = False) -> SiteImage:
    """Agrega una imagen al sitio histórico."""
    if is_cover:
        # Quitar portada actual si existe
        SiteImage.query.filter_by(historic_site_id=site_id, is_cover=True).update({"is_cover": False})

    new_image = SiteImage(
        historic_site_id=site_id,
        public_url=url,
        title=title,
        description=description,
        is_cover=is_cover,
    )
    db.session.add(new_image)
    db.session.commit()
    return new_image


def delete_image(image_id: int) -> bool:
    """Elimina una imagen (verifica que no sea portada)."""
    image = SiteImage.query.get(image_id)
    if not image:
        return False
    if image.is_cover:
        raise ValueError("No se puede eliminar la imagen de portada. Cambie la portada antes.")
    db.session.delete(image)
    db.session.commit()
    return True


def set_cover_image(image_id: int) -> bool:
    """Marca una imagen como portada y desmarca la anterior."""
    image = SiteImage.query.get(image_id)
    if not image:
        return False
    SiteImage.query.filter_by(historic_site_id=image.historic_site_id).update({"is_cover": False})
    image.is_cover = True
    db.session.commit()
    return True


def reorder_images(site_id: int, new_order: list[int]):
    """Actualiza el orden de las imágenes según una lista de IDs."""
    for idx, image_id in enumerate(new_order):
        SiteImage.query.filter_by(id=image_id, historic_site_id=site_id).update({"order": idx})
    db.session.commit()

def get_images_by_site_id(site_id: int) -> list[SiteImage]:
    """Obtiene todas las imágenes de un sitio histórico, ordenadas por el campo 'order'."""
    return SiteImage.query.filter_by(historic_site_id=site_id).order_by(SiteImage.order).all()

def get_image_by_id(image_id: int) -> SiteImage | None:
    """Obtiene una imagen por su ID."""
    return SiteImage.query.get(image_id)