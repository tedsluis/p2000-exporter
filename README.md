# P2000 exporter

prometheus metrics exporter for P2000

### Build container image

````bash
# podman build -t p2000-exporter:latest .
````

### Run container

````bash
# podman run --rm --name p2000-exporter -p 2000:2000 localhost/p2000-exporter \
          --matches=leiden,gouda \
          --url=www.alarmeringdroid.nl/rss/d0a55295 \
          --port=2000
````

### help

````bash
# podman run --rm --name p2000-exporter -p 2000:2000 localhost/p2000-exporter --help

Help

Execute:
   # exporter.py [-u <url>|--url=<url>] \
                 [-m <match>[,<match>]|--matches=<match>[,<match>]] \
                 [-p <port>|--port=<port>]
                 [-h|--help]

   # exporter.py --url=www.alarmeringdroid.nl/rss/d0a55295 \
                 --matches=schoonhoven,leiden \
                 --port=2000

Endpoints:
    # curl http://127.0.0.1:2000/metrics
    # curl http://127.0.0.1:2000/config

Notes:
    Get your own rss url at https://www.alarmeringdroid.nl/rssbuilder
    --matches is a list of locations.
    Default port: 2000
````

### Metrics

````bash
# curl http://localhost:2000/metrics

# P2000 events
p2000_scrape_response_time_seconds{status=200} 0.395585
p2000_scrape_counter{status=200} 3827
p2000_scrape_response_size_bytes{status=200} 13025
# Succesfull rss feed in response.
p2000_seconds_since_event{title="P 2 BDH-04 DV aan derden Bernhardhof Gouda 163130",link="https://www.alarmeringdroid.nl/toonmelding/18666985",description="Brandweer: : GOUDA",pubdate="Thu, 24 Mar 2022 18:03:20 +0000"} 68798
p2000_seconds_since_event{title="P 1 BDH-03 BR woning Willem van der Madeweg Leiden 164252 169192 164230 164330",link="https://www.alarmeringdroid.nl/toonmelding/18667079",description="Brandweer: : LEIDEN",pubdate="Thu, 24 Mar 2022 18:27:37 +0000"} 67557
p2000_event_counter 2
````

### Config

````bash
# curl http://localhost:2000/config
````
<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-3.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-3.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

### grafana dashboards

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-1.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-1.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-2.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-2.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

### Karma

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-4.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-4.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>


### Prometheus

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-5.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-5.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

### Slack alert

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-6.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-6.png"
alt="dashboard1" width="400" height=auto border="10" /></a><br>