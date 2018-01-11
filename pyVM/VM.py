import sys
import numpy as np
import hashlib
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time

from receive import receive
from settings import settings_fromRTDS, NumData, IP_send, IP_receive, Port_send, Port_receive, IP_broker, dcssim

msgs_from_dcs = []


def on_message(client, userdata, message):
    print("Following message received: ", str(message.payload.decode("utf-8")), ": about ", "V? = ", message.topic[-2:])
    tup = [message.topic[-2:], str(message.payload.decode("utf-8"))]
    msgs_from_dcs.append(tup)


def runVM():

    ldata = np.array([0.95, 0.23]) # offline TEST
    #ldata = receive(IP_receive, Port_receive, NumData)

    print("Values received from RTDS (or fake ones): ", ldata)

    if len(settings_fromRTDS) != NumData or len(settings_fromRTDS) != NumData:
        print("RPI2: Setting does not compatible with incoming RTDS data! STOP writing to DB!")
        sys.exit()

    ### makes HASH1 from DATA
    h1 = hashlib.sha256(ldata[0]).hexdigest()
    h2 = hashlib.sha256(ldata[1]).hexdigest()
    hash1 = np.array([h1,h2])

    ### sends HASH1 to DCS1 via MQTT topic
    vm = mqttcli.Client()
    vm.on_message = on_message

    vm.connect(IP_broker[0]) # connect to broker at DCS1
    #vm.publish("VM/DCS/VM", payload=hash1[1]) - solution with .client
    msgs_to_dcs = [("VM/DCS/VM/V1", hash1[0]), ("VM/DCS/VM/V2", hash1[1])] # solution with .publish and multiple messages
    publish.multiple(msgs_to_dcs, hostname=IP_broker[0])

    ### receives SIGN from DCS1 via MQTT topic
    vm.loop_start()
    vm.subscribe([("VM/VM/DCS/V1",0), ("VM/VM/DCS/V2",0)])

    if dcssim==True: # test certificates from DCS agent
        testdcs = mqttcli.Client()
        testdcs.connect(IP_broker[0]) # connect to broker at DCS1 (self)
        testdcs.publish("VM/VM/DCS/V1", "signV1 from DCS1")
        testdcs.publish("VM/VM/DCS/V2", "signV2 from DCS1")

    time.sleep(3)  # max waiting time for DCS agent response
    vm.loop_stop()

    ### sends DATAs and SIGNs via LTE, MQTT to DSO (data + signature) + ts
    ts = time.time()
    # list of ['V?', value],'signV?', ts]x2
    msgs_to_dso = [("LTE/DSO/VM/V1/data", ldata[0]),            # data value
                   ("LTE/DSO/VM/V1/sign", msgs_from_dcs[0][1]), # signature
                   ("LTE/DSO/VM/V1/ts", ts),                    # timestanp
                   ("LTE/DSO/VM/V2/data", ldata[1]),
                   ("LTE/DSO/VM/V2/sign", msgs_from_dcs[1][1]),
                   ("LTE/DSO/VM/V2/ts", ts)]

    vm.reinitialise()
    vm.connect(IP_broker[1])
    publish.multiple(msgs_to_dso, hostname=IP_broker[1])
    print("published via LTE topic...")

runVM()
