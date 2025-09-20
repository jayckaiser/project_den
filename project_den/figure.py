import plotly.express as px
import plotly.graph_objects as go

from project_den import util

from typing import List, Optional


class Figure:
    def __new__(cls, *args, type: str, **kwargs):
        if type == "bar":
            return object.__new__(BarFigure)
        if type == "pie":
            return object.__new__(PieFigure)
        if type == "table":
            return object.__new__(TableFigure)
        raise NotImplementedError(f"! Figure type `{type}` is undefined!")

    def __init__(self,
        name: str, sql: str,
        figures: List[dict],
        layout: Optional[dict] = None,
        traces: Optional[dict] = None,
        **kwargs  # Stores `type` to avoid collision with built-in
    ):
        self.name = name
        self.sql = sql
        self.data = util.sql(sql)
        self.figure = go.Figure()  # Traces added to empty figure

        # Figure construction
        for fig_kwargs in figures:
            sub_figure = self.figure_callable(self.data, **fig_kwargs)
            for trace in sub_figure.data:
                self.figure.add_trace(trace)
        
        # Optional formatting
        if layout:
            self.figure.update_layout(**layout)
        if traces:
            self.figure.update_traces(**traces)

    def show(self):
        self.figure.show()

    @staticmethod
    def figure_callable(*args, **kwargs):
        """
        Defined in child classes. 

        TODO: Ideally, I'd just use `figure_callable = px.bar` or similar, but it is not static.
              We get errors because `self` is passed into `px.METHOD`.
        """
        raise NotImplementedError


class BarFigure(Figure):
    """
    https://plotly.com/python-api-reference/generated/plotly.express.bar
    """
    @staticmethod
    def figure_callable(*args, **kwargs):
        return px.bar(*args, **kwargs)


class PieFigure(Figure):
    """
    https://plotly.com/python-api-reference/generated/plotly.express.pie
    """
    @staticmethod
    def figure_callable(*args, **kwargs):
        return px.pie(*args, **kwargs)


# TODO: Finish table
class TableFigure(Figure):

    CELL_FONT_SIZE = 12  # How big are the cells in the tables?

    def __init__(self, *args, header, values, **kwargs):
        super().__init__(*args, **kwargs)

        data = px.Table(
            self.data,
            title=self.title,
            header=self.parse_optional_cols(header),
            cells=self.parse_optional_cols(values),
        )

        self.figure = go.Figure(data=data)

        self.figure.update_traces(
            cells_font={'size': self.CELL_FONT_SIZE},
        )

# TODO: Refactor so that all values (except data) are definable via YAML.
# TODO: Swap to go.Bar, go.Pie, go.Table  (Gonna be a PITA to add these complete figures to the final picture)

