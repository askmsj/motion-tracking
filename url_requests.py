# importing the requests library 
import requests
import json
from pprint import pprint
from urllib.parse import urlencode

import threading
from queue import Queue
from queue import LifoQueue
import time
from datetime import datetime


q = LifoQueue()

def post_request(url, data):
    #print('thread start')
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    r = requests.post(url = url, data = {'data': data})
    #if r.status_code == 200:
    #    print('thread end', url, r.status_code, r.json(), datetime.fromtimestamp(timestamp))
    #q.put({url, r.content, timestamp})
    #print('thread end')

    

baseURL = "http://192.168.0.199/index.php/api/"

def wait_for_internet_connection():
    while True:
        try:
            response = urllib2.urlopen('http://74.125.113.99',timeout=1)
            return
        except urllib2.URLError:
            pass

def get(_url, _params = {}):
    PARAMS = _params
        
    r = requests.get(url = _url, params = PARAMS)
    #print(r)
    return r
    
def post(_url, _params = {}):
    
    url = (baseURL if baseURL.endswith('/') else baseURL + '/') + _url
    
    if baseURL == "":
        return None
    
    headers = {'content-type': 'application/json'}
    
    # defining the api-endpoint  
    #API_ENDPOINT = "http://pastebin.com/api/api_post.php"  
    # your API key here 
    #API_KEY = "XXXXXXXXXXXXXXXXX"
    
    # data to be sent to api
    _data = json.dumps(_params)
    #data = {'api_dev_key':API_KEY, 
    #    'api_option':'paste',
    #    'api_paste_format':'python'} 
    
    r = None
    try:
        
        #r = requests.post(url = url, data = {'data': _data})
        #q.queue.clear()#tylko ostatni url nas interesuje
        t = threading.Thread(target=post_request, args=(url, _data,))
        #print('main before')
        t.start()
        #print('main wait')
        #while not q.empty():
        #    url, content, timestamp = q.get()
         #   print(url, content, datetime.fromtimestamp(timestamp))
        
        #print(r.content)
    except ValueError:
        r = None
    except requests.exceptions.ConnectionError as e2:
        print(e2)
        r = None
    except requests.exceptions.RequestException as e3:  # This is the correct syntax
        print(e3)
        sys.exit(1)
    except Exception as e:
        print(e)
        r = None
        
        
    #print(r)
    return r


def main():
    out = dict(gateId=71,temp=77)
    #out['gateId'] = 71
    #out['temp'] = 78
    print(out, json.dumps(out))
    baseURL = "http://192.168.0.199/index.php/api/"
    post("device/" + str(112233) + "/q", out)
    
    
    
if __name__ == "__main__":
    main()
    
  

