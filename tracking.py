#test
import numpy as np
import cv2
import cv2.aruco as aruco
#from pprint import pprint

#import random as rng
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
#import msvcrt

from classes import Marker
from classes import Item
import url_requests as r
import device_info as device


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

cli = False#args.get("show")
fromFile = False 

#const
#gateid - id bramy zakres 51-69 - id id 1 do 19
#miejsca postojowego bramy (71-99) - id od 1 do 29
#CONST_GATE_ID = None

config_data = device.getConfig()
r.baseURL = config_data['destination'] if 'destination' in config_data.keys() else ""
print(config_data)


#video resolution
CONST_WIDTH = 640#1280#640#1280#640#1920#1280
CONST_HEIGHT = 480#720#480#720#480#1080#720

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
    item = Item('vehicle')
    mv = args.get("vehiclemarker") if args.get("vehiclemarker") != None else config_data['vehicle_id']
    item.setControlMarker(Marker(int(mv)))
elif args.get("gatemarker") != None or 'gate_id' in config_data.keys():
    item = Item('gate')
    mg = args.get("gatemarker") if args.get("gatemarker") != None else config_data['gate_id']
    item.setControlMarker(Marker(int(args.get("gatemarker"))))
else:
    item = Item('gate') #default mode - read from marker

print(item.name)
#quit()

allMarkers = item.getMarkers()

#tak zeby przelecialo update dla all markers przy okazji szukania
def findMarkerInAllMarkers(id):
    _res = None;
    for _m in allMarkers:
        _m.update()
        if _m.id == id:
            _res = _m
    return _res

def hideAllMarkers():
    for _m in allMarkers:
        _m.setVisible(False)

    _cm = item.getControlMarker()
    if _cm != None:
        _cm.setVisible(False)

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
CONST_F_SKIP_QTY = 1 # skip frames -> run detection every f_skip_qty frame

#object status and position
status = None
position = None


fps = None
fps = FPS().start()
# loop over frames from the video stream
while True:
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) or fromFile else frame

    f_counter = f_counter + 1
    
    # check to see if we have reached the end of the stream
    if frame is None:
        break

    # resize the frame (so we can process it faster) and grab the
    #frame = imutils.resize(frame, width=640)
    (H, W, L) = frame.shape#[:2]
    #frame = cv2.flip(frame, -1)
    #frame = imutils.rotate_bound(frame, -90)
    
        
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
    
    
    #arcuo part - skip frames
    ids = []
    corners = []
    if f_counter >= CONST_F_SKIP_QTY:
        corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        frame = aruco.drawDetectedMarkers(frame, corners, ids)
        f_counter = 0
       
        #analiza odczytanych markerow
        #markery 0-10 level bramy lub pojazdu
        
        if not ids is None and len(ids) > 0:
            hideAllMarkers()  #ide all markers
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
                    item.visible = True

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
                    _marker.setVisible(True)
                    _marker.setCoords(corners[m][0][0])
                        
                

        #statuses
        newStatus = item.status()
        newPosition = item.getPositionPercent()
        if item.id != None and (status != newStatus or position != newPosition):
            every1min = time.time()
            status = newStatus
            position = newPosition
            print('####item', item.name, status)
            print(position, item.id, item.urlStatus() )
            if item.name == 'gate':
                r.post("gate/" + str(item.id)
               +"/"+item.urlStatus() + "/" + str(position))
            if item.name == 'vehicle':
                print('####veh-id', item.vehicleId)
                r.post("vehicle/" + str(item.id)
               +"/" + str(item.vehicleId) +"/"+item.urlStatus() + "/" + str(position))
    
    
    #fps update
    fps.update()
    fps.stop()
    
    import json
    #every 5 mins
    if ((time.time() - every5min) / 15 > 1):
        print(str(item.getControlMarker().id) + ':' + str(item.id) + ':' + str(device.getTemperature()))
        
        every5min = time.time()
        jd = device.getJsonData(str(item.getControlMarker().id))
        r.post("device/" + str(device.getSerial()), jd)
    
    
    #print fps
    i=1
    cv2.putText(frame, "FPS: {:.2f}".format(fps.fps()), (10, H - ((i * 20) + 20)),
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    #resize output
    if not cli:
        frame1 = cv2.resize(frame, (int(W/2), int(H/2)))
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
