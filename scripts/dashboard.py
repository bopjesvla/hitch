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
    "select * from points where not banned and datetime is not null",
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

# Duplicates
df = pd.read_sql(
    "select * from duplicates",
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
    "select * from hitchwiki",
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

# TODO: necessary to track user prgress, move elsewhere later
import html
def e(s):
    return html.escape(s.replace("\n", "<br>"))


user_accounts = ""
users = pd.read_sql(
    "select * from user", sqlite3.connect(DATABASE)
)

for i, user in users.iterrows():
    user_accounts += "<a href='/?user=" + e(user.username) + "#filters'>" + e(user.username) + "</a>"
    user_accounts += "<br>"
    

output = Template(template).substitute(
    {
        "timeline": timeline_plot,
        "timeline_duplicate": timeline_plot_duplicate,
        "timeline_hitchwiki": timeline_plot_hitchwiki,
        "user_accounts": user_accounts,
    }
)

open(outname, "w", encoding="utf-8").write(output)
