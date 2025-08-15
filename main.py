from project_den import transform
from project_den import poster
from project_den.util import sql

import logging
logging.basicConfig(level=logging.INFO)


PATH_TO_DATA: str = "./data/FINAL_SampleData.csv"
POSTER_TITLE: str =  "Tito's Den Visit Overview"


def to_df(_sql: str):
    _sql: str = sqlparse.format(_sql, reindent=True)
    return sql(_sql).df()


def main():

    # Load downloaded CSV
    # Fix errors (e.g., deviant time formats, "9PM", etc.) 
    sql_raw_visit_data = transform.sql_csv_to_raw(PATH_TO_DATA)
    logging.debug(f"sql_csv_to_raw('{PATH_TO_DATA}')\n{sql_raw_visit_data}")
    raw_visit_data = sql(sql_raw_visit_data)
    logging.debug(raw_visit_data)

    sql_visit_data = transform.sql_raw_to_clean("raw_visit_data")
    logging.debug(f"sql_raw_to_clean('raw_visit_data')\n{sql_visit_data}")
    visit_data = sql(sql_visit_data)
    logging.debug(visit_data)

    # Create poster and save to disk.
    output_poster = poster.build_poster(visit_data, poster_title=POSTER_TITLE)
    

    return


if __name__ == "__main__":
    main()
