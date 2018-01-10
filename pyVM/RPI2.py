import socket
import sys
import os
import struct
from datetime import datetime, timedelta
import time
import numpy as np
from pprint import pprint as pp
import platform

from tofloat import tofloat
from send import send
from receive import receive
from settings import settings_fromRTDS, NumData, IP_send, IP_receive, Port_send, Port_receive

def VMfromRTDS():

    #ldata = np.array([0.95, 0]) # offline TEST
    ldata = receive(IP_receive, Port_receive, NumData)

    print("Values received from RTDS (or fake ones): ", ldata)

    if len(settings_fromRTDS) != NumData or len(settings_fromRTDS) != NumData:
        print("RPI2: Setting does not compatible with incoming RTDS data! STOP writing to DB!")
        sys.exit()

    # makes HASH1 from DATA
    # sends HASH1 to DCS1 via MQTT topic
    # receives SIGN from DCS1 via MQTT topic
    # sends SIGN and DATA via LTE, MQTT to DSO

VMfromRTDS()