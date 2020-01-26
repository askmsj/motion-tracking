import RPi.GPIO as GPIO
import time
import math


class Distance():
    
    PIN_TRIG = None
    PIN_ECHO = None

    def __init__(self, pin_trig, pin_echo):
        self.PIN_TRIG = int(pin_trig)
        self.PIN_ECHO = int(pin_echo)
     
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        GPIO.setup(self.PIN_TRIG, GPIO.OUT)
      
    def __del__(self):
        GPIO.cleanup((self.PIN_ECHO, self.PIN_TRIG))
    
    def measure(self):
        try:
        #clean
            GPIO.output(self.PIN_TRIG, GPIO.LOW)
            time.sleep(0.01)
        
            GPIO.output(self.PIN_TRIG, True)
            time.sleep(0.00001)
            GPIO.output(self.PIN_TRIG, False)
        
            sT = eT = time.time()
            #eT = time.time()
        
            echos_counter = 1
            while GPIO.input(self.PIN_ECHO) == 0:
                if echos_counter < 1000:
                    sT = time.time()
                    echos_counter += 1
                else:
                    return None
                #raise SystemError("Echo pulse was not received")
        
            while GPIO.input(self.PIN_ECHO) == 1:
                eT = time.time()
        
        #time elapsed
            te = eT - sT
        #temperature
            T = 20
        #speed of sound in air for given T
            s_of_s = 331.3 * math.sqrt(1 + (T / 273.15))
        
            distance = (te * s_of_s * 100) / 2  # t*v / 2 tam i z powrotem
               
            return distance
        
        except:
            return None
        #print('odległość: %.lf cm' %distance)
        #time.sleep(1)
    
    def isOccupied(self, max_distance):
        dist = self.measure()
        if dist == None or max_distance <= 0:
            return None
        if self.measure() < max_distance:
            return True
        return False

if __name__ == "__main__":
    #GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    dist = Distance(21,20)
    #del dist
    while True:
        distance = dist.measure()
        print('odległość: %.lf cm' %distance)
        time.sleep(1)
        
    print('del')    
    del dist
