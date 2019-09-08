import os

def getConfig():
    out = {}
    try:
        #print(os.getcwd())        
        with open('config', 'r') as tFile:
            for line in tFile:
                #print(line,line.startswith('#'))
                if not line.startswith('#'):
                    argval = line.rstrip('\n').split("=")
                    arg = argval[0]
                    val = argval[1]
                    out[arg] = val
        
        return out

    except:
        return {}

    return {}


def getTemperature():
    try:
        tFile = open('/sys/class/thermal/thermal_zone0/temp', 'r')
        temp = float(tFile.read())
        tFile.close()
        return temp/1000

    except:
        tFile.close()

    return None   


def getVolts():
    f = os.popen('/opt/vc/bin/vcgencmd measure_volts').read()
    #f = os.system("/opt/vc/bin/vcgencmd measure_volts")
    out = f.split('=')[1].replace('V','')
    return out

def getThrottled():
#    1110000000000000010
#    |||             |||_ under-voltage
#    |||             ||_ currently throttled
#    |||             |_ arm frequency capped
#    |||_ under-voltage has occurred since last reboot!!
#    ||_ throttling has occurred since last reboot
#    |_ arm frequency capped has occurred since last reboot!!
  
    MESSAGES = {
        0: 'Under-voltage!',
        1: 'ARM frequency capped!',
        2: 'Currently throttled!',
        3: 'Soft temperature limit ON',
        16: 'Under-voltage has occurred since last reboot.',
        17: 'Throttling has occurred since last reboot.',
        18: 'ARM frequency capped has occurred since last reboot.',
        19: 'Soft temperature limit has occurred since last reboot.',
    }
    
    f = os.popen('/opt/vc/bin/vcgencmd get_throttled').read()
    throttled_binary = bin(int(f.split('=')[1], 0))
    #print(throttled_binary)

    warnings = 0
    for position, message in MESSAGES.items():
        if len(throttled_binary) > position and throttled_binary[0 - position - 1] == '1':
            print(message)
            warnings += 1
    
    return f

def getSerial():
    res = None
    try:
        tFile = open('/proc/cpuinfo', 'r')
        for line in tFile:
            if line[0:6]=='Serial':
                res = line[10:26]
                
        tFile.close()
        return res

    except:
        tFile.close()

    return res


def getJsonData(gateId):
    out = dict(gateId=gateId)
    out['temp'] = getTemperature()
    out['volts'] = getVolts()
    out['throttled'] = getThrottled()
    
    return out

def main():
    #print(bin(0x80008))
    print(getVolts())
    
    
if __name__ == "__main__":
    main()

