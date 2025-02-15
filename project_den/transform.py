## Python imports and SqlMagic extensions
import duckdb
import glob
import os
from duckdb import sql


### Loader methods
# TODO: Load as JSONL to set nulls in schema changes.
def csv_to_raw(path: str) -> 'DataFrame':
    return sql(f"""

    select * from read_csv(
        '{path}',
        union_by_name=True,
        nullstr='N/A',
        filename=True,
        AUTO_DETECT=True
    )

    """)


# Macro helpers for transforming from raw
def force_datetime_format(date_col: str, time_col: str) -> str:

    timestamp_format1: str = "%Y-%m-%d %H:%M:%S %p"
    timestamp_format2: str = "%Y-%m-%d %H:%M"

    return f"""

    coalesce(
        try_strptime(concat("{date_col}", ' ', "{time_col}" ), '{timestamp_format1}'),
        try_strptime(concat("{date_col}", ' ', "{time_col}" ), '{timestamp_format2}')
    )
    
    """

def fix_am_pm(col: str) -> str:

    return f"""

    CASE
        WHEN HOUR("{col}") < 7
            THEN "{col}" + INTERVAL 12 HOURS
        WHEN HOUR("{col}") > 16
            THEN "{col}" - INTERVAL 12 HOURS
        ELSE "{col}"
    END

    """

def clean_name(col: str, dashes_to_spaces: bool = False) -> str:

    if dashes_to_spaces:
        col = f"""replace("{col}", '-', ' ')"""

    # Remove anything non-alphabetic (globally)
    return f"""lower(regexp_replace("{col}", '[^a-zA-Z]', '', 'g'))"""

def build_unique_id(first_col: str, last_col: str, num_chars: int = 1) -> str:

    return f"""

    array_to_string(flatten([

        -- First Name: Joe -> [J]
        [substring(upper("{first_col}"), 1, {num_chars})],  --Cut N Uppercase initials into a list

        -- Last Name: Martinez-Hernandex -> [M, H]
        list_transform(
            regexp_split_to_array(upper("{last_col}"), '[- ]'),  --Split Uppercase by either hyphen or space
            x -> substring(x, 1, {num_chars})  --Take the first N initials of each name
        )
    ]), '')

    """


def raw_to_clean(
    _raw_visit_data: 'DataFrame'  # Hard-coded variable name for string interpolation in SQL query
) -> 'DataFrame':

    date_format: str = "%Y-%m-%d"
    timestamp_format1: str = "%Y-%m-%d %H:%M:%S %p"
    timestamp_format2: str = "%Y-%m-%d %H:%M"

    return sql(f"""

    select
        -- Datetime columns
        strptime("Date of Visit"::text, '{date_format}')::date as visit_date,

        CASE WHEN MONTH(visit_date) >= 9
            THEN YEAR(visit_date) + 1
            ELSE YEAR(visit_date)
        END::text AS school_year,

        {force_datetime_format("Date of Visit", "Time in" )} AS raw_time_in,
        {force_datetime_format("Date of Visit", "Time out")} AS raw_time_out,

        -- This section fixes input-mistake where AM and PM is chosen incorrectly.
        {fix_am_pm("raw_time_in" )} AS time_in,
        {fix_am_pm("raw_time_out")} AS time_out,


        -- Demographics columns
        "First Name" as first_name_original,
        "Last Name" as last_name_original,

        {clean_name("First Name")} as first_name,
        {clean_name("Last Name", dashes_to_spaces=True)} as last_name,
        
        concat(first_name, ' ', last_name) as full_name,
        "Grade Level"::text as grade_level,


        -- Setting "unique" IDs
        {build_unique_id("first_name", "last_name", num_chars=1)} as initials,          -- Joe Martinez-Hernandez -> JMH
        {build_unique_id("first_name", "last_name", num_chars=2)} as program_id_xyear,  -- Joe Martinez-Hernandez -> JOMAHE
        concat(program_id_xyear, grade_level)                     as program_id,        -- JOMAHE -> JOMAHE4


        -- Metadata columns
        date_diff('second', time_in, time_out) as visit_length_sec,

        case
            when "*Zones of Regulation Check* Entry" = '' then null
            else lower("*Zones of Regulation Check* Entry")
        end as zor_entry,
    
        case
            when "*Zones of Regulation Check* Exit" = '' then null
            else lower("*Zones of Regulation Check* Exit")
        end as zor_exit,

        "Escorting Staff" as staff_name,

        -- -- External metadata (optional)
        -- strptime("Timestamp", '%m/%d/%Y %H:%M:%S') as _updated_at,  -- Different format
        filename as _filepath,

    from _raw_visit_data;

    """)
