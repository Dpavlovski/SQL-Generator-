import decimal
from datetime import datetime
from typing import Set, List, Union, Tuple, Any

from app.models.database import Table
from app.models.outputs import SearchOutput


def format_table_info(tables: Set[Table | None]) -> str:
    return "\n".join([str(table) for table in tables])


def format_proper_nouns(values_objs: List[SearchOutput]) -> str:
    return ", ".join([value.value for value in values_objs if value.value is not None])


def format_results(results: List[Tuple]) -> List[Tuple]:
    formatted_results = []
    for row in results:
        formatted_row = tuple(format_column(col) for col in row)
        formatted_results.append(formatted_row)

    return formatted_results[:5]


def format_column(col: Union[datetime, decimal.Decimal, Any]) -> Union[str, Any]:
    if isinstance(col, datetime):
        return col.strftime("%d.%m.%y %H:%M")
    elif isinstance(col, decimal.Decimal):
        return str(col)
    else:
        return col
