#test
import numpy as np
import cv2
import cv2.aruco as aruco

from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time

import RPi.GPIO as GPIO

from classes import Marker
from classes import Item
import url_requests as r
import device_info as device

from alert import Alert
from hcsr04 import Distance

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
    help="path to input video file")
ap.add_argument("-mv", "--vehiclemarker", type=str, #default="kcf",
    help="marker id for vehicle")
ap.add_argument("-mg", "--gatemarker", type=str,
    help="marker id for gate")
ap.add_argument("-s", "--show",  action='store_false',
    help="run from command line - -s shows img frame")
ap.add_argument("-imgadj", "--imgcorrection", type=str,
    help="enable img correction functions")

_args = ap.parse_args()
args = vars(_args)

cli = args.get("show")
fromFile = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
        
#const
#gateid - id bramy zakres 51-69 - id id 1 do 19
#miejsca postojowego bramy (71-99) - id od 1 do 29
#CONST_GATE_ID = None

#get config params
config_data = device.getConfig()
r.baseURL = config_data['destination'] if 'destination' in config_data.keys() else ""
ALERT_PIN = config_data['led_pin'] if 'led_pin' in config_data.keys() else None
alert = Alert(ALERT_PIN)
alert.start()

#distance sensor
DIST_ENABLED = config_data['dist_enabled']=="1" if 'dist_enabled' in config_data.keys() else False
DIST_PIN_TRIG = config_data['dist_pin_trig'] if 'dist_pin_trig' in config_data.keys() else None
DIST_PIN_ECHO = config_data['dist_pin_echo'] if 'dist_pin_echo' in config_data.keys() else None
DIST_MAX = int(config_data['dist_max']) if 'dist_max' in config_data.keys() else -1
distance = Distance(DIST_PIN_TRIG, DIST_PIN_ECHO)

#flip img
CONFIG_FLIP_IMG = int(config_data['flip_img']) if 'flip_img' in config_data else None

#rtl - vertica or horizontal plane
RTL = int(config_data['rtl']) if 'rtl' in config_data else None

#video resolution
CONST_WIDTH = 640#1280#640#1920#1280
CONST_HEIGHT = 480#720#480#1080#720
CONST_VEHICLE_OUT = 100 if RTL else CONST_WIDTH - 100

#img correction on/off
CONST_IMG_ADJ = False
if args.get("imgcorrection") != None:
    CONST_IMG_ADJ = args.get("imgcorrection")
   
#define objects
item = None

#timer - every mnutes alive request - every 5 min rasp temp
every1min=time.time()
every5min=time.time()

#if vh is given - vehicle mode else gate (gate is default)
if args.get("vehiclemarker") != None or 'vehicle_id' in config_data.keys():
    item = Item('vehicle', RTL)
    mv = args.get("vehiclemarker") if args.get("vehiclemarker") != None else config_data['vehicle_id']
    item.setControlMarker(Marker(int(mv)))
    item.setConstants(None, None, 100, CONST_WIDTH - 100)
elif args.get("gatemarker") != None or 'gate_id' in config_data.keys():
    item = Item('gate', RTL)
    mg = args.get("gatemarker") if args.get("gatemarker") != None else config_data['gate_id']
    item.setControlMarker(Marker(int(mg)))
else:
    item = Item('gate', RTL) #default mode - read from marker


allMarkers = item.getMarkers()

#tak zeby przelecialo update dla all markers przy okazji szukania
def findMarkerInAllMarkers(id):
    _res = None;
    for _m in allMarkers:
        _m.update()
        if _m.id == id:
            _res = _m
    return _res

def hideAllMarkers(forceOnce = False):
    for _m in allMarkers:
        #if _m.wasVisible() == False
        _m.setVisible(False, forceOnce)

    #rezygnujemy z control marker dla vehicle, dla gate zakładamy że zawsze widoaczny
    #_cm = item.getControlMarker()
    #if _cm != None:
    #    _cm.setVisible(False, forceOnce)

        
# if a video path was not supplied, grab the reference to the web cam
if not fromFile and not args.get("video", False):
    print("[INFO] starting video stream...")
    #vs = VideoStream(src=0).start()
    vs = VideoStream(src=0, usePiCamera=True, resolution=(CONST_WIDTH,CONST_HEIGHT)).start()
    #warmup camera
    time.sleep(1.0)
    
# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
    #vs = cv2.VideoCapture("video/rolo_1.h264")

#set aruco params
aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
parameters = aruco.DetectorParameters_create()

#skip frames?
f_counter = 0
CONST_F_SKIP_QTY = 3 # skip frames -> run detection every f_skip_qty frame
status_table = []
skipped_frames = CONST_F_SKIP_QTY

#object status and position
status = None
position = None


fps = None
fps = FPS().start()
frame_counter = 0


# - should the frame be processed
# - camera is in active state and calculations should be done        

# loop over frames from the video stream
while True:
      
    #od ostatniej zmiany statusu minęła 1min
    #if ((time.time() - every1min) / 12 < 1):
    #    skipped_frames = 4
    
    #time.sleep(0.5)
    
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) or fromFile else frame

    # frame couter - skip
    f_counter += 1 #f_counter + 1
    
    # check to see if we have reached the end of the stream
    if frame is None:
        break

    #frame coutner
    frame_counter += 1
    
    # resize the frame (so we can process it faster) and grab the
    #frame = imutils.resize(frame, width=640)
    (H, W, L) = frame.shape#[:2]
    
    if CONFIG_FLIP_IMG:
        frame = cv2.flip(frame, -1)
        
    #colour off
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #img correction functions
    if CONST_IMG_ADJ:
        from img_correction import adjust_gamma as ag
        gamma = 2.0         # change the value here to get different result
        adjusted = ag(gray, gamma=gamma)

        frame = adjusted

        from img_correction import apply_brightness_contrast as abc
        frame = abc(frame, 80, 60)
    
    
    #arcuo part - skip frames CONST_F_SKIP_QTY > 1
    #problemy z detekcja markerow przy duzej ilosc fps - bierzemy 3 kolejne klatki i wybieramy jedną z nich (w ktorej jest marker)
        
    ids = []
    corners = []
    if f_counter >= skipped_frames: #CONST_F_SKIP_QTY:
              
        
        corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        frame = aruco.drawDetectedMarkers(frame, corners, ids)
        f_counter = 0
       
                
        #analiza odczytanych markerow
        #markery 0-10 level bramy lub pojazdu
        if not ids is None and len(ids) > 0:
            #hideAllMarkers()  #ide all markers
            for m in range(len(ids)):
                #ustawienie id bramy dla bramy / miejsca pojazdu na podstawie markera
                _cm_read = ids[m][0]
                if _cm_read >= 50 and _cm_read < 100:
                    if _cm_read >= 70:
                        item.name = 'vehicle'
                    else:
                        item.name = 'gate'
                    if item.id == None or item.id != _cm_read:
                        _cm = Marker(_cm_read)
                        item.setControlMarker(_cm)
                        
                    cm = item.getControlMarker()
                    #dla markerow gate (50-100) nie sprawdzamy polozenia
                    cm.setVisible(True)                  

                #vehicle - wsztstkie markery >100 to id pojazdow
                if item.name == 'vehicle' and ids[m][0] > 100 and ids[m][0] < 300:
                    item.vehicleId = ids[m][0] - 100
                    
                    #czy juz dodany?
                    idx = np.where(item.getMarkersIds() == ids[m][0])
                    
                    if len(idx[0]) == 0:                     
                        _nm = Marker(ids[m][0])
                        item.addMarker(_nm)                    
                
                #gate    
                _marker = findMarkerInAllMarkers(ids[m][0])             
                if _marker != None:               
                    _marker.setFullCoords(corners[m][0])                 
                        
                

        #statuses
        newStatus = item.status()
        newPosition = item.getPositionPercent()
        #print('***', status, newStatus, item.getControlMarker().visible, item.isVisible())
            
        # 3 samples for 3 successive frames
        status_table.append(item.status());
        if True: # len(status_table) >= 3:
            
            #alert.setAlert()
            
            isOccupied = None
            #mierzenie odleglosci
            if DIST_ENABLED==1:
                isOccupied = distance.isOccupied(DIST_MAX)
                #print(distance.measure())
                occupyStatus = newStatus if isOccupied == None else ("parked" if isOccupied else "empty")
                #print("oc-status: %s -isOc: %s" %(str(occupyStatus), str(isOccupied)))
                newStatus = occupyStatus if newStatus != occupyStatus else newStatus
                item.setLastStatus(newStatus);
                
            isSame = False
            #for i in range(len(status_table)):
                #if status == status_table[i]:
                #    isSame = True
            
            #if not isSame:
            #    newStatus = status_table[2]
            
            #print('same:',isSame)
            status_table.clear()
                    
            
            if item.id != None and (status != newStatus or position != newPosition):
            #if item.id != None and not isSame:
                every1min = time.time()
                status = newStatus
                position = newPosition
                
                #print('@@@', item.isVisible(), item.getMarker(101).visible if item.getMarker(101) != None else ' - ')
                
                print('####item', item.name, status)
                print(position, item.id, item.urlStatus())
                post_r = None
                if item.name == 'gate':
                    post_r = r.post("gate/" + str(item.id)
                   +"/"+item.urlStatus() + "/" + str(position))
                if item.name == 'vehicle':
                    #print('####veh-id', item.vehicleId)
                    post_r = r.post("vehicle/" + str(item.id)
                   +"/" + str(item.vehicleId) +"/"+item.urlStatus() + "/" + str(position))
                #if post_r != None:
                #    print(post_r)
            
            #alert?
            if item.urlStatus() == 'down':
                alert.setAlert()
            
    #fps update
    fps.update()
    fps.stop()
    
    if frame_counter > fps.fps():
        frame_counter = 0
        #print('hide')
        hideAllMarkers()  #ide all markers
        #hideAllMarkers()  #ide all markers
            
    #import json
    #every 5 mins
    if ((time.time() - every5min) / 10 > 1):
        print(str(item.getControlMarker().id) + ':' + str(item.id) + ':' + str(device.getTemperature()))
        
        every5min = time.time()
        jd = device.getJsonData(str(item.getControlMarker().id))
        post_r = r.post("device/" + str(device.getSerial()), jd)
        #print('post res:', post_r)
            
    
    #print fps
    i=1
    cv2.putText(frame, "FPS: {:.2f}".format(fps.fps()), (10, H - ((i * 20) + 20)),
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    #resize output
    if not cli:
        frame1 = frame #cv2.resize(frame, (int(W/2), int(H/2)))
        cv2.imshow("Frame-res", frame1)
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

   
# if we are using a webcam, release the pointer
if not fromFile and not args.get("video", False):
    vs.stop()
# otherwise, release the file pointer
else:
    vs.release()
    
# When everything done, release the capture
#cap.release()
#out.release()
cv2.destroyAllWindows()

del alert


