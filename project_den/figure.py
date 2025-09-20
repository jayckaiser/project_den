import plotly.express as px
import plotly.graph_objects as go

from project_den import util

from typing import Optional


class Figure:
    # TODO: Make this dynamic
    PALETTE = px.colors.diverging.Fall

    def __new__(cls, *args, type: str, **kwargs):
        if type == "bar":
            return object.__new__(BarFigure)
        if type == "pie":
            return object.__new__(PieFigure)
        if type == "table":
            return object.__new__(TableFigure)
        raise NotImplementedError(f"! Figure type `{type}` is undefined!")

    def __init__(self, sql: str, name: str, title: Optional[str] = None, **kwargs):
        self.name = name
        self.title = title

        self.sql = sql
        self.data = util.sql(sql)
        self.figure = None  # Initialize empty figure

    def show(self):
        self.figure.show()

    def parse_optional_cols(self, column: str):

        # Return all column names if no data specified
        if column == "*":
            return list(self.data.columns)
        
        # Return all values if all columns are specified
        if column == "$*":
            return self.data

        if column.startswith("$"):
            return self.data[column.lstrip("$")]
        
        return column


class BarFigure(Figure):

    def __init__(self, *args, x, y, labels, color, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(x, str):
            x = [x]
        if isinstance(y, str):
            y = [y]
        if isinstance(labels, str):
            labels = [labels]
        if isinstance(color, str):
            color = [color]
        
        for idx, (
            fig_x, fig_y, fig_labels, fig_color
        ) in enumerate(zip(
            x, y, labels, color
        )):
            fig = px.bar(
                self.data,
                title=self.title,
                color_discrete_sequence=self.PALETTE,

                x=fig_x,
                y=fig_y,
                color=fig_color,
                text=fig_labels,
            )

            # TODO: Overlaying figures should be genericized
            if idx == 0:
                self.figure = go.Figure(fig)
            else:
                for dd in fig.data:
                    self.figure.add_trace(dd)

        self.figure.update_layout(
            yaxis=dict(tickformat="d"),
            showlegend=False,
            xaxis_title=None,
            yaxis_title=None,
            barmode="overlay",
        )

        self.figure.update_traces(
            textfont_size=16,
        )


class PieFigure(Figure):
    def __init__(self, *args, values, labels, color, color_mapping, **kwargs):
        super().__init__(*args, **kwargs)

        # Convert to lists to allow easier column-parsing
        data = px.pie(
            self.data,
            title=self.title,
            values=values,
            names=labels,
            color=color,
            color_discrete_map=color_mapping,
            hole=0.5
        )

        self.figure = go.Figure(data=data)

        self.figure.update_layout(
            showlegend=False,
        )

        self.figure.update_traces(
            hoverinfo='label+percent', textinfo='label+percent+value', textfont_size=16,
        )


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

