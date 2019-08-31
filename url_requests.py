# importing the requests library 
import requests 

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
    
    # defining the api-endpoint  
    #API_ENDPOINT = "http://pastebin.com/api/api_post.php"  
    # your API key here 
    #API_KEY = "XXXXXXXXXXXXXXXXX"
    
    # data to be sent to api
    data = {}
    #data = {'api_dev_key':API_KEY, 
    #    'api_option':'paste',
    #    'api_paste_format':'python'} 

    #json data?
    #json.dumps(data)
    # sending post request and saving response as response object
    r = None
    try:
        r = requests.post(url = _url, data = data)
                
    except ValueError:
        r = None
    except requests.exceptions.ConnectionError:
        r = None
    except Exception as e:
        r = None
    
    #print(r)
    return r
    # extracting response text  
    #pastebin_url = r.text 
    #print("The pastebin URL is:%s"%pastebin_url) 
  

