import RPi.GPIO as GPIO
import time
import threading # as Thread

class Alert(threading.Thread):
    
    PIN = None
    active = False
    busy = False

    def __init__(self, PIN): #self, LED_PIN):
        #super(Alert, self).__init__()
        threading.Thread.__init__(self)
         
        self.PIN = int(PIN)

        GPIO.setup(self.PIN, GPIO.OUT, initial=GPIO.HIGH)
        
        self.active = False
        
        #self.start()
        #print('__init__', self.active)
        
        
    # thread fn
    def alert_on(): #( name, delay):
        GPIO.output(self.LED_PIN, False)
        time.sleep(2)
        print('t-a-on')

    def run(self):
        #print ("Starting ", self.isAlive())
        while True: #self.active:
            if self.busy and self.active:
                self.alertOn()          
            
        #print ("Exiting ") # + self.name
    
    def setAlert(self):
        self.busy = True
        self.active = True
            
    def __del__(self):
        GPIO.cleanup()
        
    def alertOn(self):
        self.busy = True
        #print('switch-on')
        time.sleep(0.01)
        GPIO.output(self.PIN, False)
        time.sleep(3)
        GPIO.output(self.PIN, True)
        self.busy = False
        self.active = False
        #print('switch-off')
        
    def alertOff(self):
        #print('alert-off')
        GPIO.output(self.PIN, True)
        self.alert = False
        self.busy = False
        
    
if __name__ == "__main1__":
    
    print("qq")
    thread1 = Alert(4)
    thread1.start()
    
    while True:
        name = input("Ent:")
        print(name, name == "1")
        if name == "1":
            #thread1.active = True
            thread1.setAlert()
        if name == "2":
            thread1.active = False
        if name == "q":
            thread1.active = False
            break;
            thread1.exit()
            
        #thread1.offAlert()
        print('www')
        #thread1.active = False
    #thread1.start()
    #thread1.exit()
    #alert = Alert(4)
    #Alert.alertOn()
    #time.sleep(2)
    print('dd')
    #GPIO.cleanup()
    #alert.alertOn()
    #time.sleep(0.01)
    #alert.alertOff()
    del thread1
    #GPIO.cleanup()