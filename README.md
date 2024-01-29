# Hitchmap
Join the conversation about a map for hitchhiking in our [Signal Chat](https://signal.group/#CjQKIDyYgIxcOUCEPYu8-JawC_tv1bcgkAhvbISRZkN45MMVEhBPKVnUzWhl5khm5ybTWi9G)


## Description
 
- show.py builds the main HTML page. This is where the magic happens.
- server.py runs the server
- dump.py runs the monthly dump
- cron.sh is the crontab running above files
- hitchmap.conf is the NGINX configuration

## Installation

```bash
pip install numpy pandas folium pydantic flask        #Install packages
curl https://hitchmap.com/dump.sqlite > points.sqlite #Get hitchspots
python show.py                                        #Create index.html
flask --app server run                                #Run server
```
