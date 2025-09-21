from core.database import db
from core.models import HistoricSite
from datetime import datetime, timezone
from core.services import city_service, category_site_service, conservation_state_service

def list_historic_sites():
    return HistoricSite.query.all()

def create_historic_site(**kwargs):
    historic_site = HistoricSite(**kwargs)
    db.session.add(historic_site)
    db.session.commit()
    return historic_site

def assign_relations_to_historic_site(
    historic_site, conservation_state, category_site, user, city, tags = None
):
    historic_site.conservation_state = conservation_state
    historic_site.category_site = category_site
    historic_site.user = user
    historic_site.city = city
    if (tags):
        for t in tags:
            historic_site.tags.append(t)
    db.session.commit()
    return historic_site

def update_conservation_state(site_id, conservation_id):
    site = get_historic_site_by_id(site_id)
    conservation_state = conservation_state_service.get_conservation_state_by_id(conservation_id)
    site.conservation_state = conservation_state
    site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return site

def update_category_site(site_id, category_id):
    site = get_historic_site_by_id(site_id)
    category_site = category_site_service.get_category_site_by_id(category_id)
    site.category_site = category_site
    site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return site

def update_city(site_id, city_id):
    site = get_historic_site_by_id(site_id)
    city = city_service.get_city_by_id(city_id)
    site.city = city
    site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return site

def assigin_tags(historic_site, tags):
    if (tags):
        raise ValueError(f"Tags invalidos")
    for t in tags:
        historic_site.tags.append(t)
        historic_site.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return historic_site

def get_historic_site_by_id(site_id):
    site = HistoricSite.query.get(site_id)
    if (not site):
        raise ValueError(f"No existe el sitio historico con id {site_id}")
    return site

def delete_hitoric_site(site_id):
    site = get_historic_site_by_id(site_id)
    if (site.is_deleted()):
        raise ValueError(f"El sitio hitorico con id {site_id} ya se encuentra borrado")
    site.detelete_at = datetime.now(timezone.utc)
    db.session.commit()
    return site
