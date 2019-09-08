# importing the requests library 
import requests
import json
from pprint import pprint
from urllib.parse import urlencode

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
    #PARAMS = {'address': 'dehli technological university'}
    #_url = "http://maps.googleapis.com/maps/api/geocode/json"
    
    r = requests.get(url = _url, params = PARAMS)
    #print(r)
    return r
    #data = r.json()
    #print(data)
    #print(data['status'])
    
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

    #json data?
    #json.dumps(data)
    # sending post request and saving response as response object
    #s = requests.Session()
    
    r = None
    try:
        #print('ttt',json.dumps(_params))      
        print(type(_params))
        print(url, _params, _data)
        r = requests.post(url = url, data = {'data': _data})
        print(r)
        print(r.headers['content-type'])
        print(r.content)
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
    
  

