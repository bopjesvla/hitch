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

hist_data = df['datetime'].groupby([df["datetime"].dt.year]).count()
fig = px.histogram(hist_data, x=hist_data.index, y=hist_data.values, nbins=100, title="Points per year")

fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=2, label="2y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(count=10, label="10y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)


timeline_plot = fig.to_html("dash.html", full_html=False)

template = open("dashboard_template.html").read()

output = Template(template).substitute(
    {
        "timeline": timeline_plot,
    }
)

open("dashboard.html", "w").write(output)