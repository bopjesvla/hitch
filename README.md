# Hitchmap

- show.py builds the main HTML page. This is where the magic happens.
- server.py runs the server
- dump.py runs the monthly dump
- cron.sh is the crontab running above files
- hitchmap.conf is the NGINX configuration

## Installation

```bash
pip install numpy pandas folium
curl https://hitchmap.com/dump.sqlite > points.sqlite

OR

conda install folium
curl https://hitchmap.com/dump.sqlite > points.sqlite
```

