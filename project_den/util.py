import duckdb
import jinja2
import sqlparse
import yaml

from typing import List, Optional, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


def sql(query: Union[str, 'DataFrame'], name: Optional[str] = None) -> 'DataFrame':
    # QoL to use remove dataframe type-checking
    if isinstance(query, str):
        query: str = sqlparse.format(query, reindent=True)
        dataframe = duckdb.sql(query).df()
    else:
        dataframe = query
    
    # Avoids trying to fix CatalogErrors 
    if name:
        duckdb.register(name, dataframe)
    
    return dataframe

def sql_get(data: Union[str, 'DataFrame']) -> Union['column', 'DataFrame']:
    """
    Return a singleton, a list, or a dataframe
    """
    # Force to dataframe if a string
    data = sql(data)

    # Optimize return type by data shape
    # if data.shape == (1, 1):  # Return a singleton unnested
    #   return data.iat[0, 0]
    if data.shape[1] == 1:  # Return a single column as a list
        return data.iloc[:,0].tolist()
    else:
        return data

def time_filter(years: List[int], months: List[int]) -> str:
    """
    school_year IN ('{year_str}')
    AND MONTH(visit_date) IN ('{month_str}')
    """
    import calendar

    # Force to strings for easy-joining.
    years = list(map(str, years))
    months = list(map(str, months))

    # Build the filter to return
    time_clauses = []
    if years:
        time_clauses.append("school_year IN ('{}')".format("','".join(years)))
    if months:
        time_clauses.append("MONTH(visit_date) IN ('{}')".format("', '".join(months)))

    filter_clause = " AND ".join(time_clauses)
    return filter_clause

def load_yaml(path: str, **kwargs) -> dict:
    # Load the YAML as a string to optionally apply templating.
    with open(path, 'r') as fp:
        configs = fp.read() 

    # Inject kwarg Jinja variables if specified.
    if kwargs:
        env = jinja2.Environment()
        template = env.from_string(configs)
        configs = template.render(kwargs)

    return yaml.safe_load(configs)

def time_filter(years: List[int], months: List[int]):
    months_repr = None  # Initialize optionals as Nones
    years_repr = None

    if months:
        # Months repeat at 12
        months_modulo_list = sorted((mm + 12) if mm < 6 else mm for mm in months)

        if _is_consecutive(months_modulo_list):
            months_repr = "{}-{}".format(
            calendar.month_name[_from_mod12(min(months_modulo_list))],
            calendar.month_name[_from_mod12(max(months_modulo_list))]
            )
        else:
            months_repr = ", ".join(calendar.month_name[_from_mod12(mm)] for mm in months_modulo_list)

    if years:
        years_list = sorted(years)

        if _is_consecutive(years_list):
            years_repr = "{}-{}".format(
            min(years_list),
            max(years_list)
            )
        else:
            years_repr = ", ".join(years_list)

    time_filter_string = " ".join(filter(None, (months_repr, years_repr)))
    return f"({time_filter_string})"

def _is_consecutive(elements: list) -> bool:
    elements = list(map(int, elements))
    if len(elements) <= 1:
        return False

    sorted_list = sorted(elements)
    return all(sorted_list[i] == sorted_list[i-1] + 1 for i in range(1, len(sorted_list)))

def _from_mod12(item: int) -> int:
    if remainder := item % 12:
        return remainder
    else:
        return 12