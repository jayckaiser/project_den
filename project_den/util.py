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
