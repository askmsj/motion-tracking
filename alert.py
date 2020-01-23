import RPi.GPIO as GPIO
import time
from threading import Thread 

class Alert():
    
    GPIO.setwarnings(False)

    GPIO.setmode(GPIO.BCM)

    LED_PIN = None

    def __init__(self, LED_PIN):
            Thread.__init__(self)
            self.LED_PIN = LED_PIN

            GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)

    def a_thread(self):
        print('gpio start')
        GPIO.output(self.LED_PIN, False)
        time.sleep(2)
        GPIO.output(self.LED_PIN, True)
        print('gpio end')

    def alert(self):
        at = Thread(target=self.a_thread)
        at.start()
        print('gpio clean')
        GPIO.cleanup()
    
