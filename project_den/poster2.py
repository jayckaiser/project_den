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
    figure_map: Dict[str, 'Figure'],
    design: str,
    layout: Optional[dict] = None,
    subplot_kwargs: Optional[dict] = None
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
    distinct_indexes = np.unique(design)  # Also used for title order
    for idx in distinct_indexes:
        if idx not in figure_map:
            logging.error(f"Figure index {idx} defined in design but missing in figure mapping!")
            exit(1)

    # Generate the spans (no figure information required)
    rowspan_map, colspan_map = get_spans_from_design(design)

    # Generate the specs and traces
    plot_specs_array = []  # Shape the array at the end
    plot_trace_map = {}
    already_processed = set()

    for array_idx, fig_idx in enumerate(design.flat):
        
        if fig_idx in already_processed:
            plot_specs_array.append(None)
            continue
        
        # Update specs
        spec = {
            'type': figure_map[fig_idx].type,
            'rowspan': rowspan_map[fig_idx],
            'colspan': colspan_map[fig_idx]
        }

        plot_specs_array.append(spec)
        already_processed.add(fig_idx)

        # Update traces (i.e., where spacs are being saved in array)
        plot_trace_map[str(fig_idx)] = (
            array_idx // num_cols + 1,  # row
            array_idx % num_cols + 1    # col
        )

    # Reshape the specs into a 2D array
    plot_specs = np.reshape(plot_specs_array, shape=design.shape).tolist()

    # Collect the figure titles in order of appearance in design
    # (Assume titles are defined in first data trace of each figure)
    subplot_titles = [
        figure_map[idx].title
        for idx in distinct_indexes
    ]

    ### Build the poster using the generated artifacts 
    poster = make_subplots(
        rows=num_rows, cols=num_cols,
        subplot_titles=subplot_titles,
        specs=plot_specs,
        **subplot_kwargs
    )

    for idx, plot in figure_map.items():
        for trace in plot.figure.data:
            row = plot_trace_map[idx][0]
            col = plot_trace_map[idx][1]
            poster.add_trace(trace, row=row, col=col)

    # Optional formatting
    if layout:
        poster.update_layout(**layout)

    return poster
