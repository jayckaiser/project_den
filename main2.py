import logging

from project_den import figure, poster2, util


logging.basicConfig(level=logging.INFO)


PATH_TO_CONFIGS: str = "./sample.yml"


# Parse YAML configs, using a second pass to inject Jinja variables.
logging.info(f"Parsing configs defined at {PATH_TO_CONFIGS}")
jinja_variables = util.load_yaml(PATH_TO_CONFIGS).get("variables", {})
configs = util.load_yaml(PATH_TO_CONFIGS, **jinja_variables)

# Register named datasets before building the poster.
logging.info("Creating datasets...")
for dataset_name, dataset_sql in configs["datasets"].items():
    dataset = util.sql(dataset_sql, dataset_name)
    logging.debug(f"Dataset created: {dataset_name}\n{dataset[:5]}")

# Parse each of the poster plots into figures.
logging.info("Creating figures...")
figures = {}
for fig_name, fig_config in configs['figures'].items():
    fig = figure.Figure(**fig_config)
    figures[fig_name] = fig
    logging.debug(f"Figure created: {fig_name}")

# Combine figures into each poster.
logging.info("Building poster from figures and layout...")
for poster_name, poster_kwargs in configs['posters'].items():
    poster = poster2.build_poster(figures=figures, **poster_kwargs)
    logging.debug(f"Poster created: {poster_name}")
    poster.show()
