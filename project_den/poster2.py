import itertools
import logging
import numpy as np
import pandas as pd

from collections import Counter
from plotly.subplots import make_subplots

from typing import Dict, Optional, Tuple


def get_spans_from_design(design: 'np.array') -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Get row and column spans from design array.

    AABB
    AACD
    EEEE

    rowspan_map

    """
    rowspan_map = {}
    colspan_map = {}

    # Iterate the rows and columns separately, using the same logic
    for col in design:
        counter = Counter(col)
        for idx, count in counter.items():
            colspan_map[idx] = count

    for row in design.T:
        counter = Counter(row)
        for idx, count in counter.items():
            rowspan_map[idx] = count

    return rowspan_map, colspan_map


def build_poster(
    design: str,
    figures: Dict[str, 'Figure'],  # Map figure name to figure
    figure_map: Dict[str, str],  # Map design idx to figure name
    layout: Optional[dict] = None,
    subplot_kwargs: Optional[dict] = None,
    show: bool = False,
    write_path: Optional[str] = None,
):
    """
    Convert text representation of design into complete poster.

    Plotly builds subplots using four elements:
    - Specs:  Represent the plots using primary (i.e., upperleft-most) indexes and nulls
    - Traces: Represent the (row, col) of the specs
    - Spans:  Represent how many rows and cols the subplot takes up
    - Order:  Used for titles, the order the plots appear in the specs

    Layout    Specs     Traces     Spans

    AABB      A~B~      A: (1,1)   A: (2,2)
    AACD      ~~CD      B: (1,3)   B: (2,1)
    EEEE      E~~~      C: (2,3)   C: (1,1)
                        D: (2,4)   D: (1,1)
                        E: (3,1)   E: (1,4)

    Raise an error if any of the design indexes are absent from figure mapping.
    TODO: Raise an error if an irregular index shape is passed. (e.g., L-shape).
    """
    ### Prepare artifacts using design and figures
    # Clean up the design and convert to a dataframe
    design = [
        list(row.strip())
        for row in design.strip().split("\n")
    ]
    design = np.array(design)
    num_rows, num_cols = design.shape

    # Warn if unknown figures are referenced
    for idx in np.unique(design):
        if idx not in figure_map:
            logging.error(f"Figure index {idx} defined in design but missing in figure mapping!")
            exit(1)

    # Build a mapping from design indexes to figures
    idx_to_figure_map = {}
    for idx, figure_name in figure_map.items():
        figure = figures.get(figure_name)
        if not figure:
            logging.error(f"Figure name {figure_name} not defined!")
            exit(1)
        idx_to_figure_map[idx] = figure

    # Generate the spans (no figure information required)
    rowspan_map, colspan_map = get_spans_from_design(design)

    # Generate the specs, traces, and titles in order of appearance
    subplot_specs_array = []  # Shape the array at the end
    subplot_trace_map = {}
    subplot_titles = []
    already_processed = set()

    for array_idx, fig_idx in enumerate(design.flat):
        
        if fig_idx in already_processed:
            subplot_specs_array.append(None)
            continue
        
        # Update specs
        spec = {
            'type': idx_to_figure_map[fig_idx].type,
            'rowspan': rowspan_map[fig_idx],
            'colspan': colspan_map[fig_idx]
        }

        subplot_specs_array.append(spec)
        already_processed.add(fig_idx)

        # Update traces (i.e., where spacs are being saved in array)
        subplot_trace_map[str(fig_idx)] = (
            array_idx // num_cols + 1,  # row
            array_idx % num_cols + 1    # col
        )

        # Update titles
        subplot_titles.append(idx_to_figure_map[fig_idx].title)

    # Reshape the specs into a 2D array
    subplot_specs = np.reshape(subplot_specs_array, shape=design.shape).tolist()

    ### Build the poster using the generated artifacts 
    poster = make_subplots(
        rows=num_rows, cols=num_cols,
        subplot_titles=subplot_titles,
        specs=subplot_specs,
        **subplot_kwargs
    )

    for idx, figure in idx_to_figure_map.items():
        for trace in figure.data:
            row = subplot_trace_map[idx][0]
            col = subplot_trace_map[idx][1]
            poster.add_trace(trace, row=row, col=col)

    # Optional formatting
    if layout:
        poster.update_layout(**layout)

     # Show the poster immediately if specified
    if show:
        poster.show()

    # Write the poster to disc if specified
    if write_path:
        poster.write_html(write_path)

    return poster
