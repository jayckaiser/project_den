import argparse
import importlib
import logging
import yaml

from project_den import figure, poster, util


logging.basicConfig(level=logging.INFO)


def main():
    """
    Parse the configs YAML.
    Build datasets, figures, and posters.
    """
    ### Create a CLI for passing variables to main.
    description = """Project Den: create graphical representations of sign-in visit data."""
    epilog = "Full documentation at https://github.com/jayckaiser/project_den"

    parser = argparse.ArgumentParser(
        prog="project_den",
        description=description,
        epilog=epilog
    )

    package_resources = importlib.resources.files("projects")
    parser.add_argument("-c", "--config",
        nargs="?",
        type=str,
        help="Specify YAML config file where datasets, figures, and posters are defined",
        default=package_resources.joinpath("titos_den.yml")
    )

    parser.add_argument("-v", "--variables",
        nargs="?",
        type=str,
        help="Specify variable overrides to template into the config YAML",
        default="{}"
    )

    args, _ = parser.parse_known_args()

    PATH_TO_CONFIGS = args.config
    VARIABLE_OVERRIDES = yaml.safe_load(args.variables)


    ### Initial pass to retrieve/override variables before main run.
    # Parse YAML configs, using a second pass to inject Jinja variables.
    logging.info(f"Parsing configs defined at {PATH_TO_CONFIGS}")
    jinja_variables = util.load_yaml(PATH_TO_CONFIGS).get("variables", {})
    
    # Override variables if passed as CLI arguments.
    if VARIABLE_OVERRIDES:
        jinja_variables = {**jinja_variables, **VARIABLE_OVERRIDES}


    ### Main
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
        poster.build_poster(figures=figures, **poster_kwargs)
        logging.debug(f"Poster created: {poster_name}")
