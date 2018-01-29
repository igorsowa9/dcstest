import sys
import numpy as np
import hashlib
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time
import bitstring
import struct

from receive import receive
from settings import settings_fromRTDS, NumData, IP_send, IP_receive, Port_send, Port_receive, IP_broker, dcssim, wait_dcs, attack

msgs_from_dcs = []

def on_message(client, userdata, message):
    #print("Following message received: ", str(message.payload.decode("utf-8")), ": about ", "V? = ", message.topic[-2:])
    tup = [message.topic[-2:], str(message.payload.decode("utf-8"))]
    msgs_from_dcs.append(tup)


def runVM():

    ldata = np.array([4.111, 2.111, 1.01, 0.661, 0.331, 1.02]) # offline TEST
    #ldata = receive(IP_receive, Port_receive, NumData)

    #num_str = str(bitstring.BitArray(float=1.2323, length=32))
    #float_back = struct.unpack('!f', bytes.fromhex(num_str[2:]))[0]

    print("1... Values received from RTDS (or fake ones): ", ldata)

    if len(settings_fromRTDS) != NumData or len(settings_fromRTDS) != NumData:
        print("VM: Setting does not compatible with incoming RTDS data! STOP!")
        sys.exit()

    ### makes HASH1 from DATA
    ldata1 = ldata[:3]
    ldata2 = ldata[3:]

    lstr1 = ""
    lstr2 = ""

    for l in ldata1:
        lb = bitstring.BitArray(float=l, length=32)
        ls = str(lb)
        lstr1 = lstr1 + ls

    for l in ldata2:
        lb = bitstring.BitArray(float=l, length=32)
        ls = str(lb)
        lstr2 = lstr2 + ls

    h1 = hashlib.sha256(lstr1.encode('utf8')).hexdigest() # V1, P,Q,V
    h2 = hashlib.sha256(lstr2.encode('utf8')).hexdigest() # V2, P,Q,V

    hash1 = np.array([h1,h2])
    data1 = np.array([lstr1,lstr2])

    ### sends HASH1 to DCS1 via MQTT topic
    vm = mqttcli.Client()
    vm.on_message = on_message

    vm.connect(IP_broker[0]) # connect to broker at DCS1
    #vm.publish("VM/DCS/VM", payload=hash1[1]) - solution with .client
    msgs_to_dcs = [("VM/DCS/VM/V1", hash1[0]), ("VM/DCS/VM/V2", hash1[1])] # solution with .publish and multiple messages
    publish.multiple(msgs_to_dcs, hostname=IP_broker[0])

    ### receives SIGN from DCS1 via MQTT topic
    vm.loop_start()
    vm.subscribe([("VM/VM/DCS/V1",0),
                  ("VM/VM/DCS/V2",0)])

    if dcssim==True: # test certificates from DCS agent
        testdcs = mqttcli.Client()
        testdcs.connect(IP_broker[0]) # connect to broker at DCS1 (self)
        testdcs.publish("VM/VM/DCS/V1", "signV1 from DCS1")
        testdcs.publish("VM/VM/DCS/V2", "signV2 from DCS1")

    time.sleep(wait_dcs)  # max waiting time for DCS agent response
    vm.loop_stop()
    print("2... VM: Communication with DCS done.")

    ### sends DATAs and SIGNs via LTE, MQTT to DSO (data + signature) + ts
    ts = time.time()
    # list of ['V?', value],'signV?', ts]x2
    msgs_to_dso = [("LTE/DSO/VM/V1/data", data1[0]),            # data value
                   ("LTE/DSO/VM/V1/sign", msgs_from_dcs[0][1]), # signature
                   ("LTE/DSO/VM/V1/ts", ts),                    # timestanp
                   ("LTE/DSO/VM/V2/data", data1[1]),
                   ("LTE/DSO/VM/V2/sign", msgs_from_dcs[1][1]),
                   ("LTE/DSO/VM/V2/ts", ts)]
    print(msgs_to_dso)

    if attack == True:
        # HERE "THE ATTACK", for example... Qload10 0.001 injection instead of 2.111
        inj_str = str(bitstring.BitArray(float=0.001, length=32))
        mod = msgs_to_dso[0][1][0:10] + inj_str + msgs_to_dso[0][1][20:30]
        msgs_to_dso[0] = ("LTE/DSO/VM/V1/data", mod)
        print("\tAttack performed on Qload10, message modified: ", msgs_to_dso)

    # change connection to DSO, instead of DCS
    vm.reinitialise()
    vm.connect(IP_broker[1])
    publish.multiple(msgs_to_dso, hostname=IP_broker[1])
    print("3... Multiple message (above) published via LTE topic.")
