import calendar
import pandas as pd
import sqlparse
from duckdb import sql
from typing import List, Union

import plotly.graph_objects as go


class TitoFig:
    CELL_FONT_SIZE = 12  # How big are the cells in the tables?

    def __init__(self, data: Union[str, pd.DataFrame]):
        if isinstance(data, str):
            self.sql = sqlparse.format(data, reindent=True)
            self.data = sql(self.sql).df()
        elif isinstance(data, pd.DataFrame):
            self.sql = None
            self.data = data
        else:
            raise Exception(f"Unknown {self.__name__} datatype: {type(data)}")

        # Make figure and title attributes for easy access (TODO: Streamline further)
        self.title = None
        self.figure = None

    @property
    def figdata(self):
        return self.figure.data[0]

    def table(self,
        title: str,
        header: Union[str, list, pd.Series],
        values: Union[str, list, pd.Series, pd.DataFrame],
        **kwargs
    ):
        self.title = title

        self.figure = go.Figure(data=[go.Table(
            name=title,
            header={'values': self.data[header] if isinstance(header, str) else header},
            cells={'values': self.data[values] if isinstance(values, str) else values},
            **kwargs
        )])

        self.figure.update_traces(
            cells_font={'size': self.CELL_FONT_SIZE},
        )

        return self.figure

    def pie(self,
        title: str,
        labels: Union[str, list, pd.Series],
        values: Union[str, list, pd.Series],
        colors: list,
        **kwargs
    ):
        self.title = title

        self.figure = go.Figure(data=[go.Pie(
            title=title,
            labels=self.data[labels] if isinstance(labels, str) else labels,
            values=self.data[values] if isinstance(values, str) else values,
            hole=0.5,
            **kwargs
        )])

        self.figure.update_traces(
            hoverinfo='label+percent', textinfo='label+percent+value', textfont_size=16,
        )

        if colors:
            self.figure.update_traces(
                marker_colors=colors,
            )

        return self.figure

    def bar(self,
        title: str,
        labels: Union[str, list, pd.Series],
        x: Union[str, list, pd.Series],
        y: Union[str, list, pd.Series],
        colors: list,
        **kwargs
    ):
        self.title = title

        self.figure = go.Figure(data=[go.Bar(
            name=title,
            text=self.data[labels] if isinstance(labels, str) else labels,
            x=self.data[x] if isinstance(x, str) else x,
            y=self.data[y] if isinstance(y, str) else y,
            **kwargs
        )])

        self.figure.update_layout(
            yaxis=dict(tickformat="d")
        )

        self.figure.update_traces(
            textfont_size=16,
            marker=dict(color=colors)
        )

        return self.figure

    def show(self):
        self.figure.show()

    ### Poster title is dynamic based on selector.
    @classmethod
    def time_filter(cls, years: List[int], months: List[int]):
        months_repr = None  # Initialize optionals as Nones
        years_repr = None

        if months:
            # Months repeat at 12
            months_modulo_list = sorted((mm + 12) if mm < 6 else mm for mm in months)

            if cls._is_consecutive(months_modulo_list):
                months_repr = "{}-{}".format(
                calendar.month_name[cls._from_mod12(min(months_modulo_list))],
                calendar.month_name[cls._from_mod12(max(months_modulo_list))]
                )
            else:
                months_repr = ", ".join(calendar.month_name[cls._from_mod12(mm)] for mm in months_modulo_list)

        if years:
            years_list = sorted(years)

            if cls._is_consecutive(years_list):
                years_repr = "{}-{}".format(
                min(years_list),
                max(years_list)
                )
            else:
                years_repr = ", ".join(years_list)

        time_filter_string = " ".join(filter(None, (months_repr, years_repr)))
        return f"({time_filter_string})"

    @staticmethod
    def _is_consecutive(elements: list) -> bool:
        elements = list(map(int, elements))
        if len(elements) <= 1:
            return False

        sorted_list = sorted(elements)
        return all(sorted_list[i] == sorted_list[i-1] + 1 for i in range(1, len(sorted_list)))

    @staticmethod
    def _from_mod12(item: int) -> int:
        if remainder := item % 12:
            return remainder
        else:
            return 12
