import sys
import numpy as np
import hashlib
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time
import struct

from receive import receive
from settings import settings_fromRTDS, NumData, IP_send, IP_receive, Port_send, Port_receive, IP_broker, \
    dcssim, DSO_control, wait_lte, wait_dcs, results, attack
from pypower.api import ppoption, runpf, printpf, runopf, rundcopf, case9
from pypower.api import *
from case33bw_dcs2 import case33bw_dcs2
from send import send
import bitstring

#from runopf_no_printpf import runopf as runopf2
#from opf_setup_edit import opf_setup
#from opf_edit import opf as opf_setup
#from runopf_edit import runopf

#ppc = case33bw_dcs2()
ppc = case9Q()
r = runopf(ppc)

print(r["f"])