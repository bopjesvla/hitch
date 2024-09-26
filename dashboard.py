import sqlite3
import pandas as pd
import plotly.express as px
from string import Template
import os

# see
# https://realpython.com/python-dash/
# https://stackoverflow.com/a/47715493

DATABASE = (
    "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
)

df = pd.read_sql(
    "select * from points where not banned order by datetime is not null desc, datetime desc",
    sqlite3.connect(DATABASE),
)

df["datetime"] = df["datetime"].astype("datetime64[ns]")

hist_data = df["datetime"]
fig = px.histogram(df["datetime"], title="Entries per month")


fig.update_xaxes(
    range=[
        "2006-01-01",
        pd.Timestamp.today().strftime("%Y-%m-%d"),
    ],
    rangeselector=dict(
        buttons=list(
            [
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=2, label="2y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(count=10, label="10y", step="year", stepmode="backward"),
                dict(step="all"),
            ]
        )
    ),
)

fig.update_layout(showlegend=False)
fig.update_layout(xaxis_title=None)
fig.update_layout(yaxis_title="# of entries")


timeline_plot = fig.to_html("dash.html", full_html=False)

template = open("dashboard_template.html").read()

output = Template(template).substitute(
    {
        "timeline": timeline_plot,
    }
)

open("dashboard.html", "w").write(output)
