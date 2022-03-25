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

Config

    url: www.alarmeringdroid.nl/rss/d0a55295
    matches: gouda
    scrape counter: 3153
    event counter: 323
    http_code: 200
    response time: 0.395585 sec
    response size: 13025 bytes
````