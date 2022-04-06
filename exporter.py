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
    print("                [-m <location>[,<location>]|--filter=<location>[,<location>]] \ ")
    print("                [-p <port>|--port=<port>] \ ")
    print("                [-h|--help]")
    print("    exporter.py --url=www.alarmeringdroid.nl/rss/d0a55295 \ ")
    print("                --filter=schoonhoven,leiden \ ") 
    print("                --port=2000\n")
    print("Endpoints:")
    print("    # curl http://127.0.0.1:2000/metrics")
    print("    # curl http://127.0.0.1:2000/config\n")
    print("notes:")
    print("    Get your own rss url at https://www.alarmeringdroid.nl/rssbuilder")
    print("    --filter is a list of locations.")
    print("    Default port: 2000\n")

def parameters(argv):
    _filter = [""]
    _url = "www.alarmeringdroid.nl/rss/d0a55295"
    _port = 2000
    try:
        opts, args = getopt.getopt(argv,"u:m:p:h",["url=","filter=","port="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-u", "--url"):
            _url = arg
        elif opt in ("-m", "--filter"):
            _filter = arg.split(',')
        elif opt in ("-p", "--port"):
            _port = arg
    print ('url is:', _url)
    print ('filter is:', _filter)
    print ('port is:', _port)
    return (_url,_filter,_port)

_url,_filter,_port = parameters(sys.argv[1:])
print("filter: %s, url: %s, port: %s\n" % (_filter,_url,_port))

_scrape_counter = 0
_event_counter = {}
_response_time = ""
_status_code = ""
_response_size = ""
_utc_time_last_scrape = datetime.now().timestamp()

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
    global _utc_time_last_scrape

    _scrape_counter = _scrape_counter + 1
    _metrics=[]

    _metrics.append('# HELP p2000_scrape_counter Number of scrapes since exporter started')
    _metrics.append('# TYPE p2000_scrape_counter counter')
    
    try:
        _resp = requests.get(url=f"https://"+ _url, timeout=5)
        _resp.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        _metrics.append('p2000_scrape_counter{status="httpError"} ' + str(_scrape_counter))
        return "\n".join(unique(_metrics))

    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        _metrics.append('p2000_scrape_counter{status="connectionError"} ' + str(_scrape_counter))
        return "\n".join(unique(_metrics))

    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        _metrics.append('p2000_scrape_counter{status="Timeout"} ' + str(_scrape_counter))
        return "\n".join(unique(_metrics))

    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        _metrics.append('p2000_scrape_counter{status="requestException"} ' + str(_scrape_counter))
        return "\n".join(unique(_metrics))

    try: 
        _status_code = str(_resp.status_code)
    except:
        _metrics.append('p2000_scrape_counter{status="failed"} ' + str(_scrape_counter))
        return "\n".join(unique(_metrics))

    _metrics.append('p2000_scrape_counter{status="' + _status_code + '"} ' + str(_scrape_counter))

    _response_time = str(_resp.elapsed.microseconds / 1000000)
    _metrics.append('# HELP p2000_scrape_response_time_seconds Number of seconds elapsed')
    _metrics.append('# TYPE p2000_scrape_response_time_seconds gauge')
    _metrics.append('p2000_scrape_response_time_seconds{status="' + _status_code + '"} ' + _response_time)
    
    
    _response_size = str(len(_resp.text))
    _metrics.append('# HELP p2000_scrape_response_size_bytes Number of bytes')
    _metrics.append('# TYPE p2000_scrape_response_size_bytes gauge')
    _metrics.append('p2000_scrape_response_size_bytes{status="' + _status_code + '"} ' + _response_size)
    
    _seconds_since_previous_scrape = datetime.now().timestamp() - _utc_time_last_scrape
    _utc_time_last_scrape =  datetime.now().timestamp()
    _metrics.append("# HELP p2000_seconds_since_previous_scrape Number of seconds")
    _metrics.append("# TYPE p2000_seconds_since_previous_scrape gauge")

    if not search('^2\d*', str(_resp.status_code)):
        _metrics.append('p2000_seconds_since_previous_scrape{status="' + _status_code + '",description="failed"} ' + str(_seconds_since_previous_scrape))
        return "\n".join(unique(_metrics))

    try:
        _meldingen = json.loads(json.dumps(xmltodict.parse(_resp.text)))["rss"]["channel"]["item"]
    except parse.xlm.to.json as e:
        _metrics.append('p2000_seconds_since_previous_scrape{status="' + _status_code + '",description="no_rss"} ' + str(_seconds_since_previous_scrape))
        return "\n".join(unique(_metrics))

    _metrics.append('p2000_seconds_since_previous_scrape{status="' + _status_code + '",description="succesfull"} ' + str(_seconds_since_previous_scrape))
        
    for _key in _meldingen:
        
        try:
            _title = str(_key["title"]).replace(' ','_')
        except:
            print("Empty title! key: %s" % _key)
            continue

        _description = str(_key["description"]).replace(' ','_').replace(':','').replace('__','_')
        _link = str(_key["link"])
        _pubdate = str(_key["pubDate"])
        _guid = str(_key['guid'])

        for _location in _filter:
            print("title=%s, description=%s, location %s" % (_title,_description, _location))
            if search(_location.lower(), _title.lower()) or search(_location.lower(), _description.lower()):
                # "title": "P 2 BDH-07 BR afval Broekpolder Warmond 164230",
                # "description": "Brandweer: : WARMOND",
                # "link": "https://www.alarmeringdroid.nl/toonmelding/18645535",
                # "pubDate": "Sat, 19 Mar 2022 21:36:43 +0000",
                # "image": "https://www.alarmeringdroid.nl/images/Brandweer.png",
                # "guid": "6c841365efffa86ff87809eb1c9ef5cc"
                # _pubdate_string = " ".join(_pubdate.split(' ')[1:5])
                
                _utc_time_event = datetime.strptime(" ".join(_pubdate.split(' ')[1:5]), "%d %b %Y %H:%M:%S").timestamp() - 7200
                _seconds_since_first_alert = _utc_time_last_scrape - _utc_time_event
                print("_utc_time_event:%s, _utc_time_last_scrape:%s, seconds_since_first_alert:%s\n" % (_utc_time_event,_utc_time_last_scrape,_seconds_since_first_alert))
                _pubdate=datetime.fromtimestamp(_utc_time_event)

                _metrics.append('# HELP p2000_seconds_since_event Number of seconds')
                _metrics.append('# TYPE p2000_seconds_since_event gauge')
                _metrics.append('p2000_seconds_since_event{title="' + _title + '",link="' + _link +'",description="' + _description + '",pubdate="' + str(_pubdate) + '"} ' + str(int(_seconds_since_first_alert)))

                _event_counter.update({ _guid:"1"})

    _metrics.append('# HELP p2000_event_counter Number of events')
    _metrics.append('# TYPE p2000_event_counter counter')
    _metrics.append('p2000_event_counter ' + str(len(_event_counter)))        
    
    return "\n".join(unique(_metrics)) + '\n'

@app.route('/config', methods=['GET', 'POST'])
def config():
    _seconds_since_previous_scrape = datetime.now().timestamp() - _utc_time_last_scrape
    _config = '''<!DOCTYPE html>
<html>
    <div width: 100%;>
        <h2>
            <a href="/metrics">p2000-exporter (1/1 up)</a>
        </h2>
        <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
            <thead>
                <tr align="left">
                    <th>Endpoint</th>
                    <th>HTTP status code</th>
                    <th>Last scrape</th>
                    <th>Response time</th>
                    <th>Response size</th>
                    <th>Scrape count</th>
                    <th>Event count</th>
                    <th>filter</th>
                </tr>
            </thead>
            <tbody>
                <tr bgcolor="#dee2e6">
                    <td><a href="https://''' + _url +'''">https://''' + _url + '''</a><br></td>
                    <td>''' + _status_code + '''</td>
                    <td>''' + str(_seconds_since_previous_scrape) + ''' sec ago</td>
                    <td>''' + _response_time + ''' sec</td>
                    <td>''' + _response_size + ''' bytes</td>
                    <td>''' + str(_scrape_counter) + '''</td>
                    <td>''' + str(len(_event_counter)) + '''</td>
                    <td>''' + ",".join(_filter) + '''</td>
                </tr>
            </tbody>
        </table>
    </div>
</html>
'''
    return _config

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=_port)