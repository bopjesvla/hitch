import os
import sqlite3
import pandas as pd
import numpy as np
import networkx
import html


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    # 1.25 because the road distance is, on average, 25% larger than a straight flight
    return 1.25 * km


def get_bearing(lon1, lat1, lon2, lat2):
    dLon = lon2 - lon1
    x = np.cos(np.radians(lat2)) * np.sin(np.radians(dLon))
    y = np.cos(np.radians(lat1)) * np.sin(np.radians(lat2)) - np.sin(
        np.radians(lat1)
    ) * np.cos(np.radians(lat2)) * np.cos(np.radians(dLon))
    brng = np.arctan2(x, y)
    brng = np.degrees(brng)

    return brng


def load_as_places():
    fn = "prod-points.sqlite" if os.path.exists("prod-points.sqlite") else "points.sqlite"
    points = pd.read_sql(
        "select * from points where not banned order by datetime is not null desc, datetime desc",
        sqlite3.connect(fn),
    )
    print(f"{len(points)} points currently")

    duplicates = pd.read_sql(
        "select * from duplicates where reviewed = accepted", sqlite3.connect(fn)
    )

    dup_rads = duplicates[["from_lon", "from_lat", "to_lon", "to_lat"]].values.T

    duplicates["distance"] = haversine_np(*dup_rads)
    duplicates["from"] = duplicates[["from_lat", "from_lon"]].apply(tuple, axis=1)
    duplicates["to"] = duplicates[["to_lat", "to_lon"]].apply(tuple, axis=1)

    duplicates = duplicates[duplicates.distance < 1.25]

    dups = networkx.from_pandas_edgelist(duplicates, "from", "to")
    islands = networkx.connected_components(dups)

    replace_map = {}

    for island in islands:
        parents = [node for node in island if node not in duplicates["from"].tolist()]

        if len(parents) == 1:
            for node in island:
                if node != parents[0]:
                    replace_map[node] = parents[0]

    print(dups)

    points[["lat", "lon"]] = points[["lat", "lon"]].apply(
        lambda x: replace_map[tuple(x)] if tuple(x) in replace_map else x, axis=1, raw=True
    )

    # dups = duplicates.merge(points, left_on='child_id', right_on='id').merge(left_on='parent_id', right_on='id', suffixes=('child_', 'parent_'))

    points.loc[points.id.isin(range(1000000, 1040000)), "comment"] = (
        points.loc[points.id.isin(range(1000000, 1040000)), "comment"]
        .str.encode("cp1252", errors="ignore")
        .str.decode("utf-8", errors="ignore")
    )

    points.datetime = pd.to_datetime(points.datetime)

    rads = points[["lon", "lat", "dest_lon", "dest_lat"]].values.T

    points["distance"] = haversine_np(*rads)
    points["direction"] = get_bearing(*rads)

    points.loc[(points.distance < 1), "dest_lat"] = None
    points.loc[(points.distance < 1), "dest_lon"] = None
    points.loc[(points.distance < 1), "direction"] = None
    points.loc[(points.distance < 1), "distance"] = None

    rounded_dir = 45 * np.round(points.direction / 45)
    points["arrows"] = rounded_dir.replace(
        {
            -90: "←",
            90: "→",
            0: "↑",
            180: "↓",
            -180: "↓",
            -45: "↖",
            45: "↗",
            135: "↘",
            -135: "↙",
        }
    )

    rating_text = "rating: " + points.rating.astype(int).astype(str) + "/5"
    destination_text = (
        ", ride: "
        + np.round(points.distance).astype(str).str.replace(".0", "", regex=False)
        + " km "
        + points.arrows
    )

    points["wait_text"] = None
    has_accurate_wait = ~points.wait.isnull() & ~points.datetime.isnull()
    points.loc[has_accurate_wait, "wait_text"] = (
        ", wait: "
        + points.wait[has_accurate_wait].astype(int).astype(str)
        + " min"
        + (
            " "
            + points.signal[has_accurate_wait].replace(
                {"ask": "💬", "ask-sign": "💬+🪧", "sign": "🪧", "thumb": "👍"}
            )
        ).fillna("")
    )


    def e(s):
        s2 = s.copy()
        s2.loc[~s2.isnull()] = s2.loc[~s2.isnull()].map(
            lambda x: html.escape(x).replace("\n", "<br>")
        )
        return s2


    points['extra_text'] = rating_text + points.wait_text.fillna("") + destination_text.fillna("")

    comment_nl = points["comment"] + "\n\n"

    comment_nl.loc[~points.dest_lat.isnull() & points.comment.isnull()] = ""

    points["text"] = (
        e(comment_nl)
        + "<i>"
        + e(points['extra_text'])
        + "</i><br><br>―"
        + e(points["name"].fillna("Anonymous"))
        + points.datetime.dt.strftime(", %B %Y").fillna("")
    )

    oldies = points.datetime.dt.year <= 2021
    points.loc[oldies, "text"] = (
        e(comment_nl[oldies])
        + "―"
        + e(points[oldies].name.fillna("Anonymous"))
        + points[oldies].datetime.dt.strftime(", %B %Y").fillna("")
    )

    # has_text = ~points.text.isnull()
    # points.loc[has_text, 'text'] = points.loc[has_text, 'text'].map(lambda x: html.escape(x).replace('\n', '<br>'))

    groups = points.groupby(["lat", "lon"])

    places = groups[["country"]].first()
    places["rating"] = groups.rating.mean().round()
    places["wait"] = points[~points.wait.isnull()].groupby(["lat", "lon"]).wait.mean()
    places["distance"] = (
        points[~points.distance.isnull()].groupby(["lat", "lon"]).distance.mean()
    )
    places["text"] = groups.text.apply(lambda t: "<hr>".join(t.dropna()))
    places["review_count"] = groups.size()
    places["dest_lats"] = (
        points.dropna(subset=["dest_lat", "dest_lon"])
        .groupby(["lat", "lon"])
        .dest_lat.apply(list)
    )
    places["dest_lons"] = (
        points.dropna(subset=["dest_lat", "dest_lon"])
        .groupby(["lat", "lon"])
        .dest_lon.apply(list)
    )

    return places