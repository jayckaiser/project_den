import os

from project_den import transform
from project_den import poster
from project_den.util import sql

import logging
logging.basicConfig(level=logging.INFO)

PATH_TO_DATA: str = "./data/FINAL_SampleData.csv"
POSTER_TITLE: str =  "Tito's Den Visit Overview"
IMAGES_DIR: str = "./data"


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
    POSTER = poster.build_poster(visit_data, poster_title=POSTER_TITLE)
    POSTER.write_image(os.path.join(IMAGES_DIR, 'overview.pdf'))
    POSTER.write_html(os.path.join(IMAGES_DIR, 'overview.html'))
    logging.info(f"PDF and HTML of poster are saved: {IMAGES_DIR}")

    return


if __name__ == "__main__":
    main()
