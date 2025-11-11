from flask_wtf.file import FileAllowed
from wtforms import BooleanField, SubmitField, FileField

from core.services import (
    get_all_categories,
    get_all_cities,
    get_all_conservation_state,
    get_all_not_deleted_tags,
    get_all_provinces,
)

from .create_site_form import CreateSiteForm


class EditSiteForm(CreateSiteForm):

    is_visible = BooleanField("Visibilizar")

    # Sobrescribir el campo images para NO exigirlo
    images = FileField(
        "Imágenes del sitio (máximo 10)",
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes'),
        ],
        render_kw={'multiple': True, 'accept': 'image/*', 'max': 10}
    )

    submit = SubmitField("Editar")

    def __init__(self, *args, **kwargs):
        """Constructor"""
        if kwargs.get("site"):
            site = kwargs.get("site")
            super(EditSiteForm, self).__init__(
                *args,
                name=site.name,
                brief_description=site.brief_description,
                full_description=site.full_description,
                inauguration_year=site.inauguration_year,
                latitude=site.latitude,
                longitude=site.longitude,
                is_visible=site.is_visible
            )

            self.province.choices = [
                (site.city.province.id, site.city.province.name)
            ] + [  # Cargo las provincias en el select
                (province.id, province.name)
                for province in get_all_provinces()
                if province.id != site.city.province.id
            ]

            self.city.choices = [
                (site.city.id, site.city.name)
            ] + [  # Cargo las provincias en el select
                (city.id, city.name)
                for city in get_all_cities()
                if city.id != site.city.id and city.province.id == site.city.province.id
            ]

            self.conservation_state.choices = [
                (site.conservation_state.id, site.conservation_state.state)
            ] + [  # Cargo los estados en el select
                (state.id, state.state)
                for state in get_all_conservation_state()
                if state.id != site.conservation_state.id
            ]

            self.category.choices = [
                (site.category.id, site.category.name)
            ] + [  # Cargo las categorias en el select
                (category.id, category.name)
                for category in get_all_categories()
                if category.id != site.category.id
            ]

            self.tags.choices = [  # Cargo las tags en el select
                (tag.id, tag.name) for tag in get_all_not_deleted_tags()
            ]
        else:
            super(EditSiteForm, self).__init__(*args, **kwargs)
