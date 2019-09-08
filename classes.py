#class marker   one cam version
class Marker(object):
    # 2 cam - info
    #id 1-10 means % of state with relation to init state (closed, parked)
    id = None
    visible = False
    item = None
    x_current = 0
    y_current = 0
    x_last = 0
    y_last = 0
    min_move_px = 8
    y_min = 0       # min when max opened
    y_max = 0
    def __init__(self, id, ):
        self.id = id

    def setItem(self, item):
        self.item = item

    def setCoords(self, coords):
        #detekcja jako zmiana tylko jeśli przesuniecie wzgledem poprzedniego wieksze niż 4px?
        if abs(coords[1] - self.x_last) > self.min_move_px:
            self.x_last = coords[0] if self.x_current == 0  else self.x_current
            self.y_last = coords[1] if self.y_current == 0 else self.y_current
            self.x_current = coords[0]
            self.y_current = coords[1]
            
        self.visible = True

    def getY(self):
        return self.y_current

    def isMovingUp(self):
        if self.isMoving() and self.y_current < self.y_last:
            return True
        else:
            return False

    def isMovingDown(self):
        #if self.item.name == 'gate':
        #    return True if self.isMoving() and self.y_current > self.y_last else False
        #else:
            return True if self.isMoving() and self.y_current > self.y_last else False

    def isMoving(self):
        return abs(self.y_current - self.y_last) > 3 #or abs(self.x_current - self.x_last) > 1

    def isMovingRight(self):
        return True if self.isMoving() and self.x_current > self.x_last else False

    def isMovingLeft(self):
        return True if self.isMoving() and self.x_current < self.x_last else False
    
    def getPositionPercent(self):
        print(CONST_HEIGHT, self.y_current, self.y_current / CONST_HEIGHT) 
        return self.y_current / CONST_HEIGHT
        
    def update(self):
        self.x_last=self.x_last
        #self.visible = False
        #self.x_last = self.x_current
        #self.y_last = self.y_current

    def setVisible(self, isVisible):
        self.visible = isVisible
        #print("The shark is being awesome.")



#class object (gate/vehicle/testpoint)
class Item:
    name = None
    id = None #item id (gate/vehicle)
    vehicleId = None
    #two cams - test marker
    controlMarker = None
    
    #one cam version item boundary (pixels)
    bottom = None      #bottom position for reference marker
    top = None

    visible = None
    markers = []
    last_status = None
    rtl = False #true if leaving is the same as closing
            #false if logic is changed
    
    def __init__(self, name):
        self.name = name
        #if name == 'gate':
        setupMarkers(self)
        #self.markers = setupMarkers(self)

    
    def setConstants(self, top, bottom):
        self.top = top
        self.bottom = bottom

    def setControlMarker(self, marker):
        marker.setVisible(True)
        self.controlMarker = marker
        self.id = marker.id - 50 if self.name == 'gate' else marker.id - 70
        

    def getControlMarker(self):
        return self.controlMarker
              
    def setMarkers(self, markerList):
        self.markers = markerList

    def addMarker(self, marker):
        self.markers.append(marker)

    def getMarker(self, id):
        for x in self.markers:
            if x.id == id:
                return x
        return None

    def getMarkers(self):
        return self.markers
    def getMarkersIds(self):
        res = []
        for i in range(len(self.markers)):
            res.append(self.markers[i].id)
        return res

    def isMoving(self):
        for x in self.markers:
            if x.visible and x.isMoving():
                return True
        return False

    #dla gate 
    def isOpening(self):
        for x in self.markers:
            if x.visible and x.isMovingUp():
                return True
        return False

    def isClosing(self):
        for x in self.markers:
            if x.visible and x.isMovingDown():
                return True
        return False

    def isOpened(self):
        
        #sprawdzamy na podstawie markera (1) i markera kontrolnego
        marker1 = self.getMarker(1)
        
        return marker1 != None and marker1.visible and not self.isMoving()
        #return not self.isMoving() and self.getMarker(1).getY() < self.top

    def isClosed(self):
        #sprawdzamy na podstawie markera (10) i markera kontrolnego
        marker10 = self.getMarker(10)
        return marker10 != None and marker10.visible and not self.isMoving()
    
    #dla vehicle kamera nad pojazdem
    def isLeaving(self):
        for x in self.markers:
            if (self.rtl == False and x.visible and x.isMovingDown()) or (self.rtl == True and x.visible and x.isMovingUp()):
                return True
        return False

    def isEntering(self):
        for x in self.markers:
            if (self.rtl == False and x.visible and x.isMovingUp()) or (self.rtl == True and x.visible and x.isMovingDown()):
                return True
        return False

    def isVisible(self):
        #return self.visible
        for x in self.markers:
            if x.visible:
                return True
        return False
    
    def isParked(self):
        return self.isVisible() == True and self.isMoving() == False

    def isEmpty(self):
        return self.controlMarker.visible == True and self.isVisible() == False

    lastMarker = None
    def getPositionPercent(self):
        if self.name == 'gate':
            #isopening - marker ref to ten z mnijszym id
            #isclosing - marker ref to ten z większym id
            min = 1000
            refMarker = self.lastMarker
            for x in self.markers:
                #print('markerid:' + str(x.id))
                if x.visible == True:
                    refMarker = x
                    #if self.isOpening() or self.isEntering():
                    #    if refMarker == None:
                    #        refMarker = x
                    #    else:
                    #        refMarker = x if x.id < refMarker.id else refMarker
                    #elif self.isClosing() or self.isLeaving():
                    #    if refMarker == None:
                    #        refMarker = x
                    #    else:
                    #        refMarker = x if x.id > refMarker.id else refMarker
                    #else:
                    #    refMarker = x

            self.lastMarker = refMarker        
            return refMarker.id if refMarker != None else -1
        elif self.name == 'vehicle':
            return 1 if self.status() == 'parked' else (10 if self.status() == 'emoty' else 5)
                
        
        #print(CONST_HEIGHT, self.y_current, self.y_current / CONST_HEIGHT) 
        #return self.y_current / CONST_HEIGHT
    
    def status(self):
        #print(len(self.markers))
        status = self.last_status
        #print('s1:' + str(status))
        if self.isMoving():
            if self.name == 'gate':
                if self.isClosing():
                    status = 'closing'
                if self.isOpening():
                    status = 'opening'
            if self.name == 'vehicle':
                if self.isLeaving():
                    status = 'leaving'
                if self.isEntering():
                    status = 'entering'
        else:
            if self.name == 'gate':
                #status = 'hold'
                #print(self.isOpened(), self.isClosed(),status)
                if self.isOpened():
                    status = 'opened'
                elif self.isClosed():
                    status = 'closed'
                elif self.isVisible():
                    status = 'hold'
                
            if self.name == 'vehicle':
                #status = 'null'
                if self.isParked():
                    status = 'parked'
                elif self.isEmpty():
                    status = 'empty'
                 
        #print('s1:' + str(self.last_status) + ' ' + str(status))
        self.last_status = status
        return status

    def urlStatus(self):
        if self.name == 'gate':
            if self.status() == "closing":
                return 'down'
            elif self.status() == "opening":
                return 'up'
            else:
                return 'null' #hold
        elif self.name == 'vehicle':
            if self.status() == 'leaving':
                return 'down'
            elif self.status() == 'entering':
                return 'up'
            else:
                return 'null' # empty
            


def setupMarkers(item):
    for i in range(1,11):
        m = Marker(i)
        item.addMarker(m)
    
