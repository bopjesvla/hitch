import pandas as pd
import os
import sqlite3
import plotly.express as px

from dash import Dash, dcc, html


fn = "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
df = pd.read_sql(
    "select * from points where not banned order by datetime is not null desc, datetime desc",
    sqlite3.connect(fn),
)

df["datetime"] = df["datetime"].astype("datetime64[ns]")

hist_data = df['datetime'].groupby([df["datetime"].dt.year]).count()
fig = px.histogram(hist_data, x=hist_data.index, y=hist_data.values, nbins=100, title="Points per year")

app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Stats"),
        html.P(
            children=(
                "Insights about hitchhiking."
            ),
        ),
        dcc.Graph(
            figure=fig,
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
