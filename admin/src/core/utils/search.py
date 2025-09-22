from datetime import datetime
<<<<<<< HEAD
from sqlalchemy import and_, or_, inspect
from sqlalchemy.orm import Query
from typing import Dict, List, Any, Optional, Union
=======
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, inspect, or_
from sqlalchemy.orm import Query
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522


class GenericSearchBuilder:
    """Constructor genérico de queries de búsqueda para cualquier modelo SQLAlchemy"""

    def __init__(self, model_class):
        """
        Inicializa el builder para un modelo específico

        Args:
            model_class: Clase del modelo SQLAlchemy
        """
        self.model_class = model_class
        self.inspector = inspect(model_class)
        self.columns = {col.name: col for col in self.inspector.columns}

    def build_query(self, filters: Dict[str, Any]) -> Query:
        """
        Construye una query basada en filtros genéricos

        Args:
            filters: Diccionario con filtros a aplicar

        Returns:
            Query de SQLAlchemy filtrada
        """
        query = self.model_class.query

        # Procesar cada filtro
        for filter_name, filter_value in filters.items():
<<<<<<< HEAD
            if filter_value is None or filter_value == '':
=======
            if filter_value is None or filter_value == "":
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
                continue

            query = self._apply_filter(query, filter_name, filter_value)

        return query

    def _apply_filter(self, query: Query, filter_name: str, filter_value: Any) -> Query:
        """Aplica un filtro específico a la query"""

        # Filtros especiales (no corresponden directamente a columnas)
        special_filters = {
<<<<<<< HEAD
            'search_text': self._apply_text_search,
            'date_from': self._apply_date_from,
            'date_to': self._apply_date_to,
            'date_range': self._apply_date_range,
            'in_list': self._apply_in_list,
=======
            "search_text": self._apply_text_search,
            "date_from": self._apply_date_from,
            "date_to": self._apply_date_to,
            "date_range": self._apply_date_range,
            "in_list": self._apply_in_list,
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
        }

        if filter_name in special_filters:
            return special_filters[filter_name](query, filter_value)

        # Filtros de columna directos
        return self._apply_column_filter(query, filter_name, filter_value)

    def _apply_text_search(self, query: Query, search_text: str) -> Query:
        """Aplica búsqueda de texto en columnas de texto configurables"""
        if not search_text:
            return query

        # Buscar en todas las columnas de tipo String/Text
        text_columns = [
            getattr(self.model_class, col_name)
            for col_name, col in self.columns.items()
<<<<<<< HEAD
            if str(col.type).upper().startswith(('VARCHAR', 'TEXT', 'STRING'))
=======
            if str(col.type).upper().startswith(("VARCHAR", "TEXT", "STRING"))
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
        ]

        if not text_columns:
            return query

        search_pattern = f"%{search_text}%"
        conditions = [col.ilike(search_pattern) for col in text_columns]

        return query.filter(or_(*conditions))

    def _apply_date_from(self, query: Query, date_from: Union[str, datetime]) -> Query:
        """Aplica filtro de fecha desde"""
        date_columns = self._get_date_columns()
        if not date_columns:
            return query

        date_value = self._parse_date(date_from)
        if not date_value:
            return query

        # Por defecto usar la primera columna de fecha (generalmente created_at)
        date_column = date_columns[0]
        return query.filter(date_column >= date_value)

    def _apply_date_to(self, query: Query, date_to: Union[str, datetime]) -> Query:
        """Aplica filtro de fecha hasta"""
        date_columns = self._get_date_columns()
        if not date_columns:
            return query

        date_value = self._parse_date(date_to)
        if not date_value:
            return query

        # Ajustar a final del día
        date_value = date_value.replace(hour=23, minute=59, second=59)

        date_column = date_columns[0]
        return query.filter(date_column <= date_value)

    def _apply_date_range(self, query: Query, date_range: Dict[str, str]) -> Query:
        """Aplica filtro de rango de fechas"""
<<<<<<< HEAD
        if 'from' in date_range:
            query = self._apply_date_from(query, date_range['from'])
        if 'to' in date_range:
            query = self._apply_date_to(query, date_range['to'])
=======
        if "from" in date_range:
            query = self._apply_date_from(query, date_range["from"])
        if "to" in date_range:
            query = self._apply_date_to(query, date_range["to"])
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
        return query

    def _apply_in_list(self, query: Query, in_filters: Dict[str, List]) -> Query:
        """Aplica filtros de tipo 'columna IN (lista)'"""
        for column_name, values in in_filters.items():
            if column_name in self.columns and values:
                column = getattr(self.model_class, column_name)
                query = query.filter(column.in_(values))
        return query

<<<<<<< HEAD
    def _apply_column_filter(self, query: Query, column_name: str, filter_value: Any) -> Query:
=======
    def _apply_column_filter(
        self, query: Query, column_name: str, filter_value: Any
    ) -> Query:
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
        """Aplica filtro directo a una columna"""
        if column_name not in self.columns:
            return query

        column = getattr(self.model_class, column_name)
        column_type = str(self.columns[column_name].type).upper()

        # Filtros según tipo de columna
        if isinstance(filter_value, dict):
            # Filtros complejos: {'operator': 'like', 'value': 'texto'}
            return self._apply_complex_filter(query, column, filter_value)
<<<<<<< HEAD
        elif column_type.startswith(('VARCHAR', 'TEXT', 'STRING')):
            # Búsqueda LIKE para strings
            return query.filter(column.ilike(f"%{filter_value}%"))
        elif column_type.startswith('BOOLEAN'):
=======
        elif column_type.startswith(("VARCHAR", "TEXT", "STRING")):
            # Búsqueda LIKE para strings
            return query.filter(column.ilike(f"%{filter_value}%"))
        elif column_type.startswith("BOOLEAN"):
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
            # Filtro exacto para booleanos
            return query.filter(column == bool(filter_value))
        else:
            # Filtro exacto para otros tipos
            return query.filter(column == filter_value)

    def _apply_complex_filter(self, query: Query, column, filter_config: Dict) -> Query:
        """Aplica filtros complejos con operadores específicos"""
<<<<<<< HEAD
        operator = filter_config.get('operator', 'eq')
        value = filter_config.get('value')

        operators = {
            'eq': lambda c, v: c == v,
            'ne': lambda c, v: c != v,
            'lt': lambda c, v: c < v,
            'le': lambda c, v: c <= v,
            'gt': lambda c, v: c > v,
            'ge': lambda c, v: c >= v,
            'like': lambda c, v: c.ilike(f"%{v}%"),
            'ilike': lambda c, v: c.ilike(f"%{v}%"),
            'startswith': lambda c, v: c.ilike(f"{v}%"),
            'endswith': lambda c, v: c.ilike(f"%{v}"),
            'in': lambda c, v: c.in_(v) if isinstance(v, list) else c == v,
            'not_in': lambda c, v: ~c.in_(v) if isinstance(v, list) else c != v,
=======
        operator = filter_config.get("operator", "eq")
        value = filter_config.get("value")

        operators = {
            "eq": lambda c, v: c == v,
            "ne": lambda c, v: c != v,
            "lt": lambda c, v: c < v,
            "le": lambda c, v: c <= v,
            "gt": lambda c, v: c > v,
            "ge": lambda c, v: c >= v,
            "like": lambda c, v: c.ilike(f"%{v}%"),
            "ilike": lambda c, v: c.ilike(f"%{v}%"),
            "startswith": lambda c, v: c.ilike(f"{v}%"),
            "endswith": lambda c, v: c.ilike(f"%{v}"),
            "in": lambda c, v: c.in_(v) if isinstance(v, list) else c == v,
            "not_in": lambda c, v: ~c.in_(v) if isinstance(v, list) else c != v,
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
        }

        if operator in operators:
            return query.filter(operators[operator](column, value))

        return query

    def _get_date_columns(self):
        """Obtiene las columnas de tipo fecha/datetime"""
        date_columns = []
        for col_name, col in self.columns.items():
            col_type = str(col.type).upper()
<<<<<<< HEAD
            if any(date_type in col_type for date_type in ['DATETIME', 'DATE', 'TIMESTAMP']):
=======
            if any(
                date_type in col_type for date_type in ["DATETIME", "DATE", "TIMESTAMP"]
            ):
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
                date_columns.append(getattr(self.model_class, col_name))
        return date_columns

    def _parse_date(self, date_input: Union[str, datetime]) -> Optional[datetime]:
        """Convierte string a datetime"""
        if isinstance(date_input, datetime):
            return date_input

        if isinstance(date_input, str):
            try:
                return datetime.strptime(date_input, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return None

        return None


# Funciones de conveniencia
def build_search_query(model_class, filters: Dict[str, Any]) -> Query:
    """
    Función de conveniencia para construir queries de búsqueda

    Args:
        model_class: Clase del modelo SQLAlchemy
        filters: Diccionario con filtros

    Returns:
        Query filtrada
    """
    builder = GenericSearchBuilder(model_class)
    return builder.build_query(filters)


<<<<<<< HEAD
def apply_ordering(query: Query, model_class, order_by: str, order_dir: str = "asc") -> Query:
=======
def apply_ordering(
    query: Query, model_class, order_by: str, order_dir: str = "asc"
) -> Query:
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
    """
    Aplica ordenamiento a una query de forma genérica

    Args:
        query: Query de SQLAlchemy
        model_class: Clase del modelo
        order_by: Campo por el cual ordenar
        order_dir: Dirección ('asc' o 'desc')
    """
    if not order_by or not hasattr(model_class, order_by):
        return query

    field = getattr(model_class, order_by)
    if order_dir.lower() == "desc":
        return query.order_by(field.desc())
    else:
        return query.order_by(field.asc())

<<<<<<< HEAD
# Función completa que combina todo
def search_with_pagination(model_class, filters: Dict, page: int = 1,
                           per_page: int = 25, order_by: str = None,
                           order_dir: str = "asc"):
=======

# Función completa que combina todo
def search_with_pagination(
    model_class,
    filters: Dict,
    page: int = 1,
    per_page: int = 25,
    order_by: str = None,
    order_dir: str = "asc",
):
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
    """
    Función completa que combina búsqueda, ordenamiento y paginación
    """
    from .pagination import paginate_query

    # Construir query con filtros
    query = build_search_query(model_class, filters)

    # Aplicar ordenamiento
    if order_by:
        query = apply_ordering(query, model_class, order_by, order_dir)

    # Aplicar paginación
<<<<<<< HEAD
    return paginate_query(query, page, per_page)
=======
    return paginate_query(query, page, per_page)
>>>>>>> b3993202772a16e7a333a95b16553bc88327f522
