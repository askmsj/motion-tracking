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
import alert

#def __init__(self):
#    a = alert(4)
is_alert = False        
        
q = LifoQueue()

def post_request(url, data):
    #print('thread start')
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    r = requests.post(url = url, data = {'data': data})
    #print(r.content)
    print('is_alert', is_alert) 
    if r.status_code:# == 200:
        if r.json()['is_alert'] and is_alert == False:
            #runAlert()
            
            print('aalleerrtt', is_alert) 
        #print(url, r)
        print('thread end', url, r.status_code, r.json(), datetime.fromtimestamp(timestamp))
        q.put({url, r.json()['is_alert'], timestamp})
        print(q.qsize())
    #print('thread end')

    

baseURL = "http://192.168.0.199:8080/index.php/api/"

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
        
        print('main wait', q.qsize(),q.empty())
        while not q.empty():
            #url, r.json()['is_alert'], timestamp
            url, content, timestamp = q.get()
            print(url, content, timestamp)
            print('thread data;', url, content)#, datetime.fromtimestamp(timestamp))
            #do_work(item)
            q.task_done()
            return content
            
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
    #runAlert()
    out = dict(gateId=71,temp=77)
    #out['gateId'] = 71
    #out['temp'] = 78
    print(out, json.dumps(out))
    baseURL = "http://192.168.0.199:8080/index.php/api/"
    post("device/0000000006a4317e", out)

import RPi.GPIO as GPIO


def a_thread(LED_PIN):
    LED_PIN = 4
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    print(GPIO.getmode())
    GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)
    print('gpio start')
    GPIO.output(LED_PIN, False)
    time.sleep(10)
    GPIO.output(LED_PIN, True)
    print('gpio end')
        
def runAlert1():
    #GPIO.setwarnings(False)
    #GPIO.setmode(GPIO.BCM)
    
    LED_PIN = 4
    #GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)
    a_thread(LED_PIN)
    #at = threading.Thread(target=a_thread, args=(LED_PIN,))
    #at.start()
        
    #GPIO.cleanup()

def runAlert():
    is_alert = True
    LED_PIN = 4
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    print(GPIO.getmode())
    GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)
    print('gpio start')
    GPIO.output(LED_PIN, False)
    time.sleep(10)
    GPIO.output(LED_PIN, True)
    print('gpio end')
    is_alert = False

if __name__ == "__main__":
    main()
    
  

