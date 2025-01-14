import os
import sqlite3
from string import Template

import pandas as pd
import plotly.express as px

# see
# https://realpython.com/python-dash/
# https://stackoverflow.com/a/47715493


rootDir = os.path.join(os.path.dirname(__file__), "..")

dbDir = os.path.abspath(os.path.join(rootDir, "db"))
distDir = os.path.abspath(os.path.join(rootDir, "dist"))
templateDir = os.path.abspath(os.path.join(rootDir, "templates"))

os.makedirs(distDir, exist_ok=True)

templatePath = os.path.join(templateDir, "dashboard_template.html")
template = open(templatePath, encoding="utf-8").read()

outname = os.path.join(distDir, "dashboard.html")

# TODO: Use dotenv?
if os.path.exists(os.path.join(dbDir, "prod-points.sqlite")):
    DATABASE = os.path.join(dbDir, "prod-points.sqlite")
else:
    DATABASE = os.path.join(dbDir, "points.sqlite")

# Spots
df = pd.read_sql(
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

# Duplicates
df = pd.read_sql(
    """
    SELECT
        Duplicates.ID as id,
        FromPoint.Latitude as from_lat,
        FromPoint.Longitude as from_lon,
        ToPoint.Latitude as to_lat,
        ToPoint.Longitude as to_lon,
        0 as accepted,
        0 as reviewed,
        Duplicates.CreatedBy as ip,
        Duplicates.CreatedAt as datetime
    FROM
        Duplicates
    LEFT JOIN Points as FromPoint
        ON Duplicates.FromPointId = FromPoint.ID
    LEFT JOIN Points as ToPoint
        ON Duplicates.ToPointId = ToPoint.ID;
    """,
    sqlite3.connect(DATABASE),
)

df["datetime"] = df["datetime"].astype("datetime64[ns]")

hist_data = df["datetime"]
fig = px.histogram(df["datetime"], title="Entries per month")


fig.update_xaxes(
    range=[
        "2024-06-01",
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


timeline_plot_duplicate = fig.to_html("dash.html", full_html=False)

# Hitchwiki
df = pd.read_sql(
    """
    SELECT
        Hitchwiki.ID as id,
        Points.Latitude as from_lat,
        Points.Longitude as from_lon,
        0 as accepted,
        0 as reviewed,
        Hitchwiki.CreatedBy as ip,
        Hitchwiki.CreatedAt as datetime
    FROM
        Hitchwiki
    LEFT JOIN Points
        ON Hitchwiki.PointId = Points.ID
    WHERE
        Hitchwiki.CreatedAt NOT NULL;
    """,
    sqlite3.connect(DATABASE),
)

df["datetime"] = df["datetime"].astype("datetime64[ns]")

hist_data = df["datetime"]
fig = px.histogram(df["datetime"], title="Entries per month")


fig.update_xaxes(
    range=[
        "2024-10-01",
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


timeline_plot_hitchwiki = fig.to_html("dash.html", full_html=False)


output = Template(template).substitute(
    {
        "timeline": timeline_plot,
        "timeline_duplicate": timeline_plot_duplicate,
        "timeline_hitchwiki": timeline_plot_hitchwiki,
    }
)

open(outname, "w", encoding="utf-8").write(output)
