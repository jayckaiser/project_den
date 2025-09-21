import plotly.express as px
import plotly.graph_objects as go

from project_den import util

from typing import List, Optional, Union


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
        sql: str, type: str,
        data: List[dict],
        title: Optional[str] = None,
        layout: Optional[dict] = None,
        traces: Optional[dict] = None,
        show: bool = False
    ):
        self.type = type
        self.title = title

        self.sql = sql
        self.data_frame = util.sql(sql)
        self.figure = go.Figure()  # Traces added to empty figure

        # Figure construction
        for fig_kwargs in data:
            sub_figure = self.figure_callable(self.data_frame, **fig_kwargs)
            for trace in sub_figure.data:
                self.figure.add_trace(trace)
        
        # Optional formatting
        if layout:
            self.figure.update_layout(**layout)
        if traces:
            self.figure.update_traces(**traces)

        # Show the figure immediately if specified
        if show:
            self.show()

    @property
    def data(self):
        return self.figure.data

    def show(self):
        self.figure.show()

    @classmethod
    def figure_callable(cls,*args, **kwargs) -> 'go.Figure':
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
    @classmethod
    def figure_callable(cls,*args, **kwargs) -> 'go.Figure':
        return px.bar(*args, **kwargs)


class PieFigure(Figure):
    """
    https://plotly.com/python-api-reference/generated/plotly.express.pie
    """
    @classmethod
    def figure_callable(cls,*args, **kwargs) -> 'go.Figure':
        return px.pie(*args, **kwargs)


class TableFigure(Figure):
    """
    There is no px.table(), so we need to define our own.
    Override default argument names with those that align with px.
    """
    @classmethod
    def figure_callable(cls,
        data_frame: 'DataFrame',
        header: Union[str, List[str]] = None,
        values: Union[str, List[object]] = None,
        pivot: bool = False,
        **kwargs
    ) -> 'go.Figure':
        """
        https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Table.html
        """
        # Check whether passed data is column names or raw values.
        header = cls.try_dataframe_extract(data_frame, header)
        values = cls.try_dataframe_extract(data_frame, values)

        # By default, the cell data is transposed.
        # If specified, "pivot" the data (i.e., send as is).
        if not pivot:
            values = values.T

        table_fig = go.Table(
            header={'values': header},
            cells={'values': values},
            **kwargs
        )
        return go.Figure(table_fig)
    
    @staticmethod
    def try_dataframe_extract(data_frame: 'DataFrame', columns: Union[str, List[object]]):
        """
        We cannot ensure the user is passing static strings or column names.
        This method tries extracting the data from the dataframe.
        If this fails, return the values as is.
        """
        if isinstance(columns, str):
            columns = [columns]

        try:
            return data_frame[columns]
        except:
            return columns
