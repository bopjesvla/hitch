import os
from string import Template

import pandas as pd
import plotly.express as px

from hitch.helpers import get_db, get_dirs

dirs = get_dirs()

os.makedirs(dirs['dist'], exist_ok=True)

template_path = os.path.join(dirs['templates'], "dashboard_template.html")
template = open(template_path, encoding="utf-8").read()

outname = os.path.join(dirs['dist'], "dashboard.html")

# Spots
df = pd.read_sql(
    "select * from points where not banned and datetime is not null",
    get_db(),
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
    get_db(),
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

# TODO: necessary to track user prgress, move elsewhere later
import html


def e(s):
    return html.escape(s.replace("\n", "<br>"))


points = pd.read_sql(
    sql="select * from points where not banned order by datetime is not null desc, datetime desc",
    con=get_db(),
)
points["user_id"] = points["user_id"].astype(pd.Int64Dtype())
users = pd.read_sql("select * from user", get_db())
points["username"] = pd.merge(
    left=points[["user_id"]],
    right=users[["id", "username"]],
    left_on="user_id",
    right_on="id",
    how="left",
)["username"]
points["hitchhiker"] = points["nickname"].fillna(points["username"])
points["hitchhiker"] = points["hitchhiker"].str.lower()


def get_num_reviews(username):
    return len(points[points["hitchhiker"] == username.lower()])


user_accounts = ""
count_inactive_users = 0
for i, user in users.iterrows():
    if get_num_reviews(user.username) >= 1:
        user_accounts += f'<a href="/account/{e(user.username)}">{e(user.username)}</a> - <a href="/?user={e(user.username)}#filters">Their spots</a>'
        user_accounts += "<br>"
    else:
        count_inactive_users += 1
user_accounts += f"<br>There are {count_inactive_users} inactive users"


### Put together ###
output = Template(template).substitute(
    {
        "timeline": timeline_plot,
        "timeline_duplicate": timeline_plot_duplicate,
        "user_accounts": user_accounts,
    }
)

open(outname, "w", encoding="utf-8").write(output)
