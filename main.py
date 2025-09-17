import os
import sys

import kaleido  # Required to generate the images.

from project_den import transform
from project_den import poster
from project_den.util import sql

import logging
logging.basicConfig(level=logging.INFO)

PATH_TO_DATA: str = "./data/FINAL_SampleData.csv"
POSTER_TITLE: str =  "Tito's Den Visit Overview"
IMAGES_DIR: str = "./images"


def main():

    # Load downloaded CSV
    # Fix errors (e.g., deviant time formats, "9PM", etc.) 
    sql_raw_visit_data = transform.sql_csv_to_raw(PATH_TO_DATA)
    logging.debug(f"sql_csv_to_raw('{PATH_TO_DATA}')\n{sql_raw_visit_data}")
    raw_visit_data = sql(sql_raw_visit_data, "raw_visit_data")
    logging.info(raw_visit_data.iloc[:5])

    sql_visit_data = transform.sql_raw_to_clean("raw_visit_data")
    logging.debug(f"sql_raw_to_clean('raw_visit_data')\n{sql_visit_data}")
    visit_data = sql(sql_visit_data, "visit_data")
    logging.info(visit_data.iloc[:5])

    # Create poster and save to disk.
    POSTER = poster.build_poster(visit_data, poster_title=POSTER_TITLE)
    # POSTER.write_image(os.path.join(IMAGES_DIR, 'overview.pdf'))  # TODO: Broken; use html download 
    POSTER.write_html(os.path.join(IMAGES_DIR, 'overview.html'))
    logging.info(f"HTML of poster is saved: {IMAGES_DIR}")

    return


if __name__ == "__main__":
   sys.exit(main()) 
