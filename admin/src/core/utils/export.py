import csv
from datetime import datetime
from io import StringIO

def export_sites_to_csv(sites):
    """
    Exporta sitios históricos a formato CSV según los requisitos del enunciado.
    """
    output = StringIO()

    # Definir columnas mínimas requeridas
    fieldnames = [
        "ID",
        "Nombre",
        "Descripción Breve",
        "Ciudad",
        "Provincia",
        "Estado de Conservación",
        "Fecha de Registro",
        "Latitud",
        "Longitud",
        "Tags",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=",")
    writer.writeheader()

    for site in sites:
        tags_str = ", ".join([tag.name for tag in site.tags]) if site.tags else ""

        writer.writerow(
            {
                "ID": site.id,
                "Nombre": site.name,
                "Descripción Breve": site.brief_description,
                "Ciudad": site.city.name if site.city else "",
                "Provincia": site.city.province.name if site.city and site.city.province else "",
                "Estado de Conservación": site.conservation_state.state if site.conservation_state else "",
                "Fecha de Registro": site.registration_date.strftime("%Y-%m-%d %H:%M:%S") if site.registration_date else "",
                "Latitud": site.latitude,
                "Longitud": site.longitude,
                "Tags": tags_str,
            }
        )
    # "\ufeff" es denominado BOM y es utilizado para que excel detecte correctamente la codificación
    content = "\ufeff" + output.getvalue()
    output.close()
    return content


def get_csv_filename():
    """Genera nombre del archivo CSV con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"sitios_{timestamp}.csv"
