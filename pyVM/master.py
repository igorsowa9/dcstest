#from RPI1.RPI1 import rpi1
import rpi2fromRTDS, rpi2toRTDS

rpi2fromRTDS() # read measurements from RTDS -> write measurements to DB

#time.sleep(1)

#rpi1() # update cases, measurements/constraints, calculate opf -> write to DB

#time.sleep(1)

#rpi2toRTDS() # take net control and send to RTDS
