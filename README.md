# Hitchmap

The map to hitchhiking the world.


## Description

- `show.py` builds the main HTML page. This is where the magic happens.
- `server.py` runs the server
- `dump.py` runs the monthly dump
- `cron.sh` is the crontab running above files
- `hitchmap.conf` is the NGINX configuration

## License

The software provided in this repository is licensed under AGPL 3.0. The Hitchmap database is licensed under the ODBL, the license used by OpenStreetMap.

## Installation

```bash
pip install numpy pandas folium==0.16.0 networkx==3.2.1
curl https://hitchmap.com/dump.sqlite > points.sqlite

OR

conda install folium==0.16.0 networkx==3.2.1
curl https://hitchmap.com/dump.sqlite > points.sqlite
```

## Contributing
Join the conversation about a map for hitchhiking in our [Signal Chat](https://signal.group/#CjQKIDyYgIxcOUCEPYu8-JawC_tv1bcgkAhvbISRZkN45MMVEhCtydy3DOOCKEAE_tsR6g9s).

File an issue for feature requests/bug reports.

Perform a pull request if you solved an issue.

