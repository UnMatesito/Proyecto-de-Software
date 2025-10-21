from datetime import datetime

import pytest

from core.models import (
    City,
    ConservationState,
    HistoricSite,
    Province,
    Tag,
    historic_site_tag,
)
from core.utils import search


@pytest.fixture(autouse=True, scope="function")
def clean_db(db_session):
    db_session.execute(historic_site_tag.delete())

    # Delete in reverse dependency order to avoid FK issues
    db_session.query(HistoricSite).delete()
    db_session.query(City).delete()
    db_session.query(Province).delete()
    db_session.query(Tag).delete()
    db_session.query(ConservationState).delete()
    db_session.commit()


@pytest.fixture
def setup_data(db_session):
    """Fixture to set up initial data for tests."""

    # Datos de prueba - Agregar lo que se necesite aca

    tag1 = Tag(name="Hielo Continental")
    tag2 = Tag(name="Patagonia")

    province = Province(name="Chubut")
    city = City(name="Buenos Aires", province=province)
    conservation_state = ConservationState(state="Bueno")

    site = HistoricSite(
        name="Test",
        city=city,
        brief_description="Desc",
        full_description="Full Desc",
        latitude=-34.6037,
        longitude=-58.3816,
        inauguration_year=1900,
        registration_date=datetime.now(),
        conservation_state=conservation_state,
        is_visible=True,
        pending_validation=False,
    )

    site.add_tag(tag1)
    site.add_tag(tag2)

    db_session.add_all([city, site, province, tag1, tag2, conservation_state])
    db_session.commit()

    return site


def test_search_sites_with_the_name(setup_data):
    """Test searching historic sites by its name."""

    # Aplicar el filtro a ciudades
    query = search.build_search_query(HistoricSite, {"search_text": "Test"})
    results = query.all()

    # Verificar que el sitio se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_the_brief_description(setup_data):
    """Test searching historic sites by its brief description."""

    # Aplicar el filtro a ciudades
    query = search.build_search_query(HistoricSite, {"search_text": "Desc"})
    results = query.all()

    # Verificar que el sitio se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_a_city(setup_data, db_session):
    """Test searching historic sites by city."""

    site2 = HistoricSite(
        name="Test2",
        city=setup_data.city,
        brief_description="Desc2",
        full_description="Full Desc2",
        latitude=-34.6037,
        longitude=-58.3816,
        inauguration_year=1900,
        registration_date=datetime.now(),
        is_visible=True,
        pending_validation=False,
    )

    db_session.add(site2)
    db_session.commit()

    # Aplicar el filtro a ciudades
    query = search.build_search_query(HistoricSite, {"city_name": setup_data.city.name})
    results = query.all()

    # Verificar que los sitios historicos se encuentra en los resultados
    assert setup_data in results
    assert site2 in results


def test_search_sites_with_a_province(setup_data):
    """Test searching historic sites by province."""

    # Aplicar el filtro a provincias
    query = search.build_search_query(
        HistoricSite, {"province_name": setup_data.city.province.name}
    )
    results = query.all()

    # Verificar que el sitio historico se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_a_tag(setup_data):
    """Test searching historic sites with a single tag."""

    # Aplicar el filtro a tags
    query = search.build_search_query(
        HistoricSite, {"tag_name": setup_data.tags[0].name}
    )
    results = query.all()

    # Verificar que el sitio historico se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_conservation_status(setup_data):
    """Test searching historic sites by conservation status."""

    # Aplicar el filtro a sitios historicos con estado de conservacion 'Bueno'
    query = search.build_search_query(HistoricSite, {"conservation_state": "Bueno"})
    results = query.all()

    # Verificar que el sitio historico se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_a_range_of_dates(setup_data):
    """Test searching historic sites registrated within a date range."""

    # Aplicar el filtro a sitios historicos creados entre dos fechas
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2026, 1, 1)

    query = search.build_search_query(
        HistoricSite, {"start_date": start_date, "end_date": end_date}
    )
    results = query.all()

    # Verificar que el sitio historico se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_on_visibility(setup_data):
    """Test searching visible historic sites."""

    # Aplicar el filtro a sitios historicos visibles
    query = search.build_search_query(HistoricSite, {"is_visible": True})
    results = query.all()

    # Verificar que el sitio historico se encuentra en los resultados
    assert setup_data in results


def test_search_sites_with_off_visibility(setup_data):
    """Test searching non-visible historic sites."""

    # Aplicar el filtro a sitios historicos no visibles
    query = search.build_search_query(HistoricSite, {"is_visible": False})
    results = query.all()

    # Verificar que el sitio historico no se encuentra en los resultados
    assert setup_data not in results
