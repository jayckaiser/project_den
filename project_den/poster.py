import plotly.express as px  # Cannot be used to make subplots.
from plotly.subplots import make_subplots

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import plotly.graph_objects as go

from project_den.util import sql_get, time_filter
from project_den.tito_fig import TitoFig


### Figure settings (should not need to be changed)

# What should the grades be called in charts?
GRADE_LABELS = {
    'K': 'K',
    '1': '1st',
    '2': '2nd',
    '3': '3rd',
    '4': '4th',
    '5': '5th',
    '6': '6th',
    None: 'n/a',  # We should never see this one on charts!
}

# What is the generic color palette?  There's LOTS of options here.
COLOR_PALETTE = px.colors.diverging.Fall

# What colors are the ZORs? ("#000000" codes or "words")
ZOR_COLORS = {
    'red'   : "rgb(215,48,39)",  # 'darkred',
    'green' : COLOR_PALETTE[1],  #'forestgreen',
    'blue'  : 'royalblue',
    'yellow': 'palegoldenrod',
    None    : 'black',  # We should never see this one on charts!
}


################################################################################

### Poster Main
def build_poster(
    _visit_data: 'DataFrame',
    poster_title: str,
    
    FREQ_VISIT_COUNT: int = 5,
    SHOW_TOP: int = 5,
    LONG_VISIT_LENGTH_MIN: int = 20,
    
) -> 'go.Figure':
    """
    Build a poster with all the visuals we've specified.
    TODO: Incorporate year and month arguments.
    """

    # Total Visit Count and Total Long Visit Count
    totals = TitoFig(f"""
        SELECT
        COUNT(*) AS count,
        COUNT(*) FILTER (WHERE visit_length_sec >= {LONG_VISIT_LENGTH_MIN} * 60) AS long_visits,
        ROUND(AVG(visit_length_sec) / 60, 1) AS avg_visit_min,
        FROM _visit_data
    """)

    totals.table(
        title=f"Total Visits",
        header=[
            'Total Count',
            f'Total Count > {LONG_VISIT_LENGTH_MIN} min.',
            "Average Visit Length (min.)"
        ],
        values=[
        totals.data['count'],
        totals.data['long_visits'],
        totals.data['avg_visit_min']
        ],
    )

    # Top N busiest days
    by_day = TitoFig(f"""
        SELECT
        STRFTIME(visit_date, '%m/%d/%Y') AS date,
        COUNT(*) AS count
        FROM _visit_data
        GROUP BY date
        ORDER BY count DESC
        LIMIT {SHOW_TOP}
    """)

    by_day.table(
        title=f"Top {SHOW_TOP} busiest days",
        header="date",
        values="count"
    )

    # Count by hour: Bar Chart
    by_hour = TitoFig(f"""
        SELECT
        hour(time_in) AS hour,
        strftime(time_in, '%I %p') AS time,
        COUNT(*) AS count
        FROM _visit_data
        GROUP BY hour, time
        ORDER BY hour
    """)

    by_hour.bar(
        title="Visits by Hour",
        labels="count",
        x="time",
        y="count",
        colors=COLOR_PALETTE,
    )

    # Count by day-of-week: Bar Chart
    by_dow = TitoFig(f"""
        SELECT
        dayofweek(visit_date) AS dow,
        dayname(visit_date) as day,
        COUNT(*) AS count
        FROM _visit_data
        WHERE day NOT IN ('Saturday', 'Sunday')
        GROUP BY dow, day
        ORDER BY dow
    """)

    by_dow.bar(
        title="Visits by Weekday",
        labels="count",
        x="day",
        y="count",
        colors=COLOR_PALETTE,
    )

    # High Flyers: > N visits
    high_flyers = TitoFig(f"""
        SELECT
        full_name,
        initials,
        grade_level,
        COUNT(*) AS count
        FROM _visit_data
        GROUP BY full_name, initials, grade_level
        HAVING count >= {FREQ_VISIT_COUNT}
        ORDER BY count DESC
    """)

    high_flyers.table(
        title=f"High flyers (n > {FREQ_VISIT_COUNT})",
        header=['student', 'grade', 'visits'],
        values=high_flyers.data[['initials', 'grade_level', 'count']].T
    )

    # Escorting Staff: > N visits
    staff_escort_count = FREQ_VISIT_COUNT

    esc_staff = TitoFig(f"""
        SELECT
        staff_name,
        COUNT(*) AS count
        FROM _visit_data
        GROUP BY staff_name
        HAVING count >= {staff_escort_count}
        ORDER BY count DESC
    """)

    esc_staff.table(
        title=f"Staff escorts (n > {staff_escort_count})",
        header=['escort', 'visits'],
        values=esc_staff.data.T
    )

    # Count by grade level: Pie Chart
    by_grade = TitoFig(f"""
        SELECT
        grade_level,
        COUNT(*) AS count
        FROM _visit_data
        WHERE grade_level IS NOT NULL
        GROUP BY grade_level
        ORDER BY CASE grade_level::text
        WHEN 'PK' THEN '-2'
        WHEN 'K' THEN '-1'
        ELSE grade_level
        END

    """)

    by_grade.bar(
        title="Visits by Grade Level",
        labels="count",
        x=list(map(GRADE_LABELS.get, by_grade.data['grade_level'])),
        y="count",
        colors=COLOR_PALETTE,
    )

    # by_grade_null_count = sql_get(f"""
    #   SELECT COUNT(*)
    #   FROM _visit_data
    #   WHERE grade_level IS NULL
    #     AND {time_filter(year, month)}
    # """)

    # Count by entry zone-of-regulation: Pie Chart
    by_entry_zor = TitoFig(f"""
        SELECT
        zor_entry,
        COUNT(*) AS count
        FROM _visit_data
        WHERE zor_entry IS NOT NULL
        GROUP BY zor_entry
        ORDER BY zor_entry
    """)

    by_entry_zor.pie(
        title="Zones of Reg. at Entry",
        labels="zor_entry",
        values="count",
        colors=list(map(ZOR_COLORS.get, by_entry_zor.data['zor_entry'])),
    )

    by_entry_zor_null_count = sql_get(f"""
        SELECT COUNT(*)
        FROM _visit_data
        WHERE zor_entry IS NULL
    """)

    # Count by exit zone-of-regulation: Pie Chart
    by_exit_zor = TitoFig(f"""
        SELECT
        zor_exit,
        COUNT(*) AS count
        FROM _visit_data
        WHERE zor_exit IS NOT NULL
        GROUP BY zor_exit
        ORDER BY zor_exit
    """)

    by_exit_zor.pie(
        title="Zones of Reg. at Exit",
        labels="zor_exit",
        values="count",
        colors=list(map(ZOR_COLORS.get, by_exit_zor.data['zor_exit'])),
    )

    by_exit_zor_null_count = sql_get(f"""
        SELECT COUNT(*)
        FROM _visit_data
        WHERE zor_exit IS NULL
    """)

    ### Design the poster
    poster = make_subplots(
        rows=6, cols=3,
        row_heights=[0.1, 0.1, 0.2, 0.2, 0.2, 0.2],
        column_widths=[0.3, 0.3, 0.4],
        subplot_titles=(
        None,  # Total counts
        by_dow.title,
        by_day.title,
        high_flyers.title, esc_staff.title,
        by_hour.title, by_grade.title,
        None, None  # ZOR pie charts
        ),
        specs=[
        [{"type": "table", "colspan": 2}, None, {"type": "bar", "rowspan": 2}],
        [{"type": "table", "colspan": 2}, None, None],
        [{"type": "table", "rowspan": 4}, {"type": "table", "rowspan": 4}, {"type": "bar"}],
        [None, None, {"type": "bar"}],
        [None, None, {"type": "pie"}],
        [None, None, {"type": "pie"}],
        ],
        vertical_spacing=0.05
    )

    poster.update_layout(
        title_text=poster_title,
        title_font_size=24,
        autosize=False, height=3300 / 2, width=2550 / 2,
        showlegend=False,
    )

    # # Add the graphs to the subplots
    poster.add_trace(totals.figdata, row=1, col=1)
    poster.add_trace(by_day.figdata, row=2, col=1)
    poster.add_trace(by_dow.figdata, row=1, col=3)
    poster.add_trace(by_hour.figdata, row=3, col=3)
    poster.add_trace(high_flyers.figdata, row=3, col=1)
    poster.add_trace(esc_staff.figdata, row=3, col=2)
    poster.add_trace(by_grade.figdata, row=4, col=3)
    poster.add_trace(by_entry_zor.figdata, row=5, col=3)
    poster.add_trace(by_exit_zor.figdata, row=6, col=3)

    # # Display total null rows in relevant graphs.
    # poster.add_annotation(
    #     text=f"Total N/A: {by_grade_null_count}",
    #     xref='x domain', yref='y domain',
    #     x=1.1, y=1.1, showarrow=False,
    #     row=4, col=3
    # )

    poster.add_annotation(
        text=f"Total N/A: {by_entry_zor_null_count}",
        xref='paper', yref='paper',
        x=1.035, y=0.35, showarrow=False,
    )

    poster.add_annotation(
        text=f"Total N/A: {by_exit_zor_null_count}",
        xref='paper', yref='paper',
        x=1.035, y=0.15, showarrow=False,
    )

    return poster
