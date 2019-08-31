
def getTemperature():
    
    try:
        tFile = open('/sys/class/thermal/thermal_zone0/temp', 'r')
        temp = float(tFile.read())
        tFile.close()
        return temp/1000

    except:
        tFile.close()

    return None   

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
