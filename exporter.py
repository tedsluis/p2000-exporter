from flask import Flask
import requests
import xmltodict
import json
from re import search
from datetime import datetime
import getopt, sys

def help():
    print("\nHelp\n")
    print("Execute:")
    print("    exporter.py [-u <url>|--url=<url>] \ ")
    print("                [-m <match>[,<match>]|--matches=<match>[,<match>]] \ ")
    print("                [-p <port>|--port=<port>] \ ")
    print("                [-h|--help]")
    print("    exporter.py --url=www.alarmeringdroid.nl/rss/d0a55295 \ ")
    print("                --matches=schoonhoven,leiden \ ") 
    print("                --port=2000\n")
    print("Endpoints:")
    print("    # curl http://127.0.0.1:2000/metrics")
    print("    # curl http://127.0.0.1:2000/config\n")
    print("notes:")
    print("    Get your own rss url at https://www.alarmeringdroid.nl/rssbuilder")
    print("    --matches is a list of locations.")
    print("    Default port: 2000\n")

def parameters(argv):
    _matches = [""]
    _url = "www.alarmeringdroid.nl/rss/d0a55295"
    _port = 2000
    try:
        opts, args = getopt.getopt(argv,"u:m:p:h",["url=","matches=","port="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-u", "--url"):
            _url = arg
        elif opt in ("-m", "--matches"):
            _matches = arg.split(',')
        elif opt in ("-p", "--port"):
            _port = arg
    print ('url is:', _url)
    print ('matches is:', _matches)
    print ('port is:', _port)
    return (_url,_matches,_port)

_url,_matches,_port = parameters(sys.argv[1:])
print("matches: %s, url: %s, port: %s\n" % (_matches,_url,_port))

_scrape_counter = 0
_event_counter = {}
_response_time = ""
_status_code = ""
_response_size = ""

def unique(_list):
    _unique_list = []
    for _item in _list:
        if _item not in _unique_list:
            _unique_list.append(_item)
    return _unique_list

app = Flask(__name__)
@app.route('/metrics', methods=['GET', 'POST'])
def metrics():

    global _scrape_counter
    global _event_counter
    global _response_time
    global _status_code
    global _response_size

    _scrape_counter = _scrape_counter + 1
    _metrics=["# P2000 events"]
    
    try:
        _resp = requests.get(url=f"https://"+ _url)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        
        _metrics.append("# Failed! No repsonse.")

    try: 
        _status_code = str(_resp.status_code)
    except:
        _metrics.append('p2000_scrape_counter{status=failed}=' + str(_scrape_counter))
        return "\n".join(unique(_metrics))

    _response_time = str(_resp.elapsed.microseconds / 1000000)
    _response_size = str(len(_resp.text))
    _metrics.append('p2000_scrape_response_time_seconds{status=' + _status_code + '}=' + _response_time)
    _metrics.append('p2000_scrape_counter{status=' + _status_code + '}=' + str(_scrape_counter))
    _metrics.append('p2000_scrape_response_size_bytes{status=' + _status_code + '}=' + _response_size)
    
    if not search('^2\d*', str(_resp.status_code)):
        _metrics.append("# Failed! No 2xx status code.")
        return "\n".join(unique(_metrics))

    try:
        _meldingen = json.loads(json.dumps(xmltodict.parse(_resp.text)))["rss"]["channel"]["item"]
    except parse.xlm.to.json as e:
        _metrics.append("# Failed! No rss feed in response.")
        return "\n".join(unique(_metrics))

    _metrics.append("# Succesfull rss feed in response.")
        
    for _key in _meldingen:
        
        try:
            _title = str(_key["title"])
        except:
            print("Empty title! key: %s" % _key)
            continue

        _description = str(_key["description"])
        _link = str(_key["link"])
        _pubdate = str(_key["pubDate"])
        _guid = str(_key['guid'])

        for _match in _matches:
            print("title=%s, description=%s, match %s" % (_title,_description, _match))
            if search(_match.lower(), _title.lower()) or search(_match.lower(), _description.lower()):
                # "title": "P 2 BDH-07 BR afval Broekpolder Warmond 164230",
                # "description": "Brandweer: : WARMOND",
                # "link": "https://www.alarmeringdroid.nl/toonmelding/18645535",
                # "pubDate": "Sat, 19 Mar 2022 21:36:43 +0000",
                # "image": "https://www.alarmeringdroid.nl/images/Brandweer.png",
                # "guid": "6c841365efffa86ff87809eb1c9ef5cc"
                # _pubdate_string = " ".join(_pubdate.split(' ')[1:5])
                
                _utc_time_event = datetime.strptime(" ".join(_pubdate.split(' ')[1:5]), "%d %b %Y %H:%M:%S").timestamp()
                _utc_time_now =  datetime.now().timestamp()
                _seconds_since_first_alert = _utc_time_now - _utc_time_event
                print("_utc_time_event:%s, _utc_time_now:%s, seconds_since_first_alert:%s\n" % (_utc_time_event,_utc_time_now,_seconds_since_first_alert))
                
                _metrics.append('p2000_seconds_since_event{title="' + _title + '",link="' + _link +'",description="' + _description + '",pubdate="' + _pubdate + '"}=' + str(int(_seconds_since_first_alert)))

                _event_counter.update({ _guid:"1"})

    _metrics.append('p2000_event_counter=' + str(len(_event_counter)))        
    
    return "\n".join(unique(_metrics))

@app.route('/config', methods=['GET', 'POST'])
def config():
    _config = '\nConfig\n\n    url: ' + _url + '\n    matches: ' + ",".join(_matches) + '\n    scrape counter: ' + str(_scrape_counter) + '\n    event counter: ' + str(len(_event_counter)) + '\n    http_code: ' + _status_code + '\n    response time: ' + _response_time+' sec\n    response size: ' + _response_size + ' bytes\n\n'
    return _config

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=_port)