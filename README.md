# P2000 exporter

prometheus metrics exporter for P2000

### Build container image

````bash
# podman build -t p2000-exporter:latest .
````

### Run container

````bash
# podman run --rm --name p2000-exporter -p 2000:2000 localhost/p2000-exporter \
          --filter=leiden,gouda \
          --url=www.alarmeringdroid.nl/rss/d0a55295 \
          --port=2000
````

### help

````bash
# podman run --rm --name p2000-exporter -p 2000:2000 localhost/p2000-exporter --help

Help

Execute:
   # exporter.py [-u <url>|--url=<url>] \
                 [-m <location>[,<location>]|--filter=<location>[,<location>]] \
                 [-p <port>|--port=<port>]
                 [-h|--help]

   # exporter.py --url=www.alarmeringdroid.nl/rss/d0a55295 \
                 --filter=schoonhoven,leiden \
                 --port=2000

Endpoints:
    # curl http://127.0.0.1:2000/metrics
    # curl http://127.0.0.1:2000/config

Notes:
    Get your own rss url at https://www.alarmeringdroid.nl/rssbuilder
    --filter is a list of locations.
    Default port: 2000
````

### Metrics

````bash
# curl http://localhost:2000/metrics


# HELP p2000_scrape_counter Number of scrapes since exporter started
# TYPE p2000_scrape_counter counter
p2000_scrape_counter{status=200} 3827
# HELP p2000_scrape_response_time_seconds Number of seconds elapsed
# TYPE p2000_scrape_response_time_seconds gauge
p2000_scrape_response_time_seconds{status=200} 0.395585
# HELP p2000_scrape_response_size_bytes Number of bytes
# TYPE p2000_scrape_response_size_bytes gauge
p2000_scrape_response_size_bytes{status=200} 13025
# HELP p2000_seconds_since_previous_scrape Number of seconds
# TYPE p2000_seconds_since_previous_scrape gauge
p2000_seconds_since_previous_scrape{status="200",description="succesfull"} 15.32132
# HELP p2000_seconds_since_event Number of seconds
# TYPE p2000_seconds_since_event gauge
p2000_seconds_since_event{title="P 2 BDH-04 DV aan derden Bernhardhof Gouda 163130",link="https://www.alarmeringdroid.nl/toonmelding/18666985",description="Brandweer: : GOUDA",pubdate="Thu, 24 Mar 2022 18:03:20 +0000"} 68798
p2000_seconds_since_event{title="P 1 BDH-03 BR woning Willem van der Madeweg Leiden 164252 169192 164230 164330",link="https://www.alarmeringdroid.nl/toonmelding/18667079",description="Brandweer: : LEIDEN",pubdate="Thu, 24 Mar 2022 18:27:37 +0000"} 67557
# HELP p2000_event_counter Number of events
# TYPE p2000_event_counter counter
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

grafana dashboard: https://github.com/tedsluis/dsm-prometheus-grafana/blob/main/roles/dsm/files/dashboard-p2000.json

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-1.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-1.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-2.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-2.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

### Karma

Karma config: https://github.com/tedsluis/dsm-prometheus-grafana/blob/main/roles/dsm/templates/karma.yml.j2

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-4.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-4.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>


### Prometheus

prometheus rules: https://github.com/tedsluis/dsm-prometheus-grafana/blob/main/roles/dsm/files/rules-p2000.yml
prometheus config: https://github.com/tedsluis/dsm-prometheus-grafana/blob/main/roles/dsm/templates/prometheus.yml.j2

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-5.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-5.png"
alt="dashboard1" width="800" height=auto border="10" /></a><br>

### Slack alert

alertmanager config: https://github.com/tedsluis/dsm-prometheus-grafana/blob/main/roles/dsm/templates/alertmanager.yml.j2

<a href="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-6.png"
 target="_blank"><img src="https://raw.githubusercontent.com/tedsluis/p2000-exporter/main/media/p2000-6.png"
alt="dashboard1" width="400" height=auto border="10" /></a><br>