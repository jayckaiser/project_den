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
logging.info("Creating plots...")
figure_map = {}
for plot_index, plot_config in configs['plots'].items():
    plot = figure.Figure(**plot_config)
    figure_map[plot_index] = plot
    logging.debug(f"Plot created at index {plot_index}: {plot.name}")
    # plot.show()

logging.info("Building poster from figures and layout...")
poster = poster2.build_poster(figure_map, **configs['poster'])
poster.show()