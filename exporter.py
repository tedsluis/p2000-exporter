from ast import Continue
from ctypes import util
from urllib import request
from flask import Flask, request
import requests
import xmltodict
import json
from re import search
from datetime import datetime
import getopt, sys
import time

def help():
    print("\nHelp\n")
    print("Execute:")
    print("    exporter.py [-u <url>|--url=<url>] \ ")
    print("                [-f <location>[,<location>]|--filter=<location>[,<location>]] \ ")
    print("                [-p <port>|--port=<port>] \ ")
    print("                [-h|--help]")
    print("    exporter.py --url=www.alarmeringdroid.nl/rss/d0a55295 \ ")
    print("                --filter=schoonhoven,leiden \ ") 
    print("                --port=2000\n")
    print("Endpoints:")
    print("    # curl http://127.0.0.1:2000/metrics")
    print("    # curl http://127.0.0.1:2000/status\n")
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

_url_cmd,_filter_cmd,_port = parameters(sys.argv[1:])
print("filter: %s, url: %s, port: %s\n" % (_filter_cmd,_url_cmd,_port))

_url_url = ''
_filter_url = ['']
_scrape_counter = 0
_event_counter = {}
_response_time = ""
_status_code = ""
_response_size = ""
_utc_time_last_scrape = datetime.now().timestamp()

_css = '''    <style>
    div.navbar {
        position: absolute;
        top: 10px;
        right: 10px;
        left: 10px;
        background-color: #343a40;
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
        font-size: 1.5rem;
        font-weight: 400;
        line-height: 1.5;
        color: #212529;
        text-align: left;
        padding: 10px;    
    }
    .white {
    	color: #ffff;
        text-decoration: none; 
    }
    .white:hover {
    	color: #c2c2d6;
    }
    .gray {
    	color: #c2c2d6;
        text-decoration: none; 
    }
    .gray:hover {
    	color: #ffff;
    }
    lu {
    	padding: 10px;
    }
    div.bottom {
        position: absolute;
        bottom: 10px;
        right: 10px;
    }
    div.content {
        position: relative;
        top: 100px;
        right: 10px;
        left: 10px;
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";
        font-size: 1rem;
        font-weight: 400;
        line-height: 1.5;
        color: #212529;
        text-align: left;
        padding: 10px;    
    }
    </style>'''

_bottom = '''    <div class="bottom">
        <a href="https://github.com/tedsluis/p2000-exporter">https://github.com/tedsluis/p2000-exporter</a>
    </div>'''

def unique(_list):
    _unique_list = []
    for _item in _list:
        if _item not in _unique_list:
            _unique_list.append(_item)
    return _unique_list

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    _home = '''<!DOCTYPE html>
<html>
<head>
''' + _css + '''
</head>
<body>
    <div class="navbar">
        <lu><a class="white" href="/">P2000-exporter</a></lu>
        <lu><a class="gray" href="/status">status</a></lu>
        <lu><a class="gray" href="/metrics">metrics</a></lu>
        <lu><a class="gray" href="https://github.com/tedsluis/p2000-exporter">help</a></lu>
    </div>
    <div class="content">
        ..........
    </div>
''' + _bottom + '''
</body>
</html>
'''
    return _home

@app.route('/metrics', methods=['GET', 'POST'])
def metrics():
    _args = request.args

    global _scrape_counter
    global _event_counter
    global _response_time
    global _status_code
    global _response_size
    global _utc_time_last_scrape
    global _filter_url
    global _url_url

    for _arg_key, _arg_value in _args.items():
        print("k: %s v: %s \n" % (_arg_key,_arg_value))

    try:
        _filter_url = _args.get('filter','').split(',')
        print('FILTER: %s' % _filter_url)
    except:
        print('no filter \n')
        pass

    try:
        _url_url = _args.get('url','')
        print('URL: %s' % _url_url)
    except:
        print('no url \n')
        pass

    print('url - URL: %s  FILTER: %s' % (_url_url,_filter_url))
    print('cmd - URL: %s  FILTER: %s' % (_url_cmd,_filter_cmd))

    if _url_url != '':
        _url = _url_url
    else:
        _url = _url_cmd

    if "".join(_filter_url) != '':
        _filter = _filter_url
    else:
        _filter = _filter_cmd
        
    print('eff - URL: %s  FILTER: %s' % (_url,_filter))

    _scrape_counter = _scrape_counter + 1
    _metrics=[]
    _status =""
    _retry = 0
    _utc_time_start_scrape = datetime.now().timestamp()

    _metrics.append('# HELP p2000_scrape_counter Number of scrapes since exporter started')
    _metrics.append('# TYPE p2000_scrape_counter counter')
    
    while (not search('^2\d*', _status)) and ((datetime.now().timestamp() -_utc_time_start_scrape) < 6):

        try:
            _resp = requests.get(url=f"https://"+ _url, timeout=1)
            _resp.raise_for_status()

        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            _status = "httpError"
            pass

        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            _status = "connectionError"
            pass

        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            _status = "Timeout"
            pass

        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
            _status = "requestException"
            pass

        try: 
            _status_code = str(_resp.status_code)
            print('STATUS: %s' % _status_code)
        except:
            print('unable to get http code')
            if _status != "":
                _status_code = _status
            else:
                _status_code = "failed"
            pass
        else:
            break

        time.sleep(1)
        _retry = _retry + 1 
    

    print('_status_code: %s, retry: %s' % (_status_code,_retry))
    _metrics.append('p2000_scrape_counter{status="' + _status_code + '"} ' + str(_scrape_counter))

    try:
        _response_time = str(_resp.elapsed.microseconds / 1000000)
        print('_response_time1: %s' % _response_time)
    except:
        _response_time = str(datetime.now().timestamp() - _utc_time_start_scrape)
        print('_response_time2: %s' % _response_time)
        pass

    _metrics.append('# HELP p2000_scrape_response_time_seconds Number of seconds elapsed')
    _metrics.append('# TYPE p2000_scrape_response_time_seconds gauge')
    _metrics.append('p2000_scrape_response_time_seconds{status="' + _status_code + '"} ' + _response_time)
    
    try:
        _response_size = str(len(_resp.text))
    except:
        _response_size = "0"

    print('_response_size: %s' % _response_size)

    _metrics.append('# HELP p2000_scrape_response_size_bytes Number of bytes')
    _metrics.append('# TYPE p2000_scrape_response_size_bytes gauge')
    _metrics.append('p2000_scrape_response_size_bytes{status="' + _status_code + '"} ' + _response_size)
    
    _seconds_since_previous_scrape = datetime.now().timestamp() - _utc_time_last_scrape
    print('_seconds_since_previous_scrape: %s' % _seconds_since_previous_scrape)
    _utc_time_last_scrape =  datetime.now().timestamp()
    _metrics.append("# HELP p2000_seconds_since_previous_scrape Number of seconds")
    _metrics.append("# TYPE p2000_seconds_since_previous_scrape gauge")

    if not search('^2\d*', _status_code):
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

@app.route('/status', methods=['GET', 'POST'])
def status():
    _seconds_since_previous_scrape = datetime.now().timestamp() - _utc_time_last_scrape
    
    _filter = ""
    if "".join(_filter_url) != "" and "".join(_filter_cmd) != "":
        _filter = ",".join(_filter_url) + " (url)<br><del>" + ",".join(_filter_cmd) + "</del> (cmd line)"
    elif "".join(_filter_url) != "":
        _filter = ",".join(_filter_url) + " (url)"
    elif "".join(_filter_cmd) != "":
        _filter = ",".join(_filter_cmd) + " (cmd line)"

    _url = ""
    if _url_url != "" and _url_cmd != "":
        _url = _url_url + " (url)<br><del>" + _url_cmd + "</del> (cmd line)"
    elif _url_url != "":
        _url = _url_url + " (url)"
    elif _url_cmd != "":
        _url = _url_cmd + " (cmd line)"

    _status = '''<!DOCTYPE html>
<html>
<head>
''' + _css + '''
</head>
<body>
    <div class="navbar">
        <lu><a class="gray" href="/">P2000-exporter</a></lu>
        <lu><a class="white" href="/status">status</a></lu>
        <lu><a class="gray" href="/metrics">metrics</a></lu>
        <lu><a class="gray" href="https://github.com/tedsluis/p2000-exporter">help</a></lu>
    </div>
    <div class="content"; width: 100%;>
        <h1>
            <a href="/metrics">scrape status</a>
        </h1>
        <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
            <thead>
                <tr align="left">
                    <th>Last scrape</th>
                    <th>Scrape count</th>
                </tr>
            </thead>
            <tbody>
                <tr bgcolor="#dee2e6">
                    <td>''' + str(_seconds_since_previous_scrape) + ''' sec ago</td>
                    <td>''' + str(_scrape_counter) + '''</td>
                </tr>
            </tbody>
        </table>

        <h1>
            <a href="/metrics">target status</a>
        </h1>
        <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
            <thead>
                <tr align="left">
                    <th>Endpoint</th>
                    <th>HTTP status code</th>
                    <th>Response time</th>
                    <th>Response size</th>
                </tr>
            </thead>
            <tbody>
                <tr bgcolor="#dee2e6">
                    <td>''' + _url + '''</td>
                    <td>''' + _status_code + '''</td>
                    <td>''' + _response_time + ''' sec</td>
                    <td>''' + _response_size + ''' bytes</td>
                </tr>
            </tbody>
        </table>


        <h1>
            <a href="/metrics">event status</a>
        </h1>
        <table border="1" bordercolor=gray cellpadding="3" cellspacing="0" style="width: 100%" >
            <thead>
                <tr align="left">
                    <th>Event count</th>
                    <th>filter</th>
                </tr>
            </thead>
            <tbody>
                <tr bgcolor="#dee2e6">
                    <td>''' + str(len(_event_counter)) + '''</td>
                    <td>''' + _filter + '''</td>
                </tr>
            </tbody>
        </table>

    </div>
''' + _bottom + '''
<body>
</html>
'''
    return _status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=_port)