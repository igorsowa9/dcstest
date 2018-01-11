import sys
import numpy as np
import hashlib
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time

from receive import receive
from settings import settings_fromRTDS, NumData, IP_send, IP_receive, Port_send, Port_receive, IP_broker, dcssim

msgs_from_vm = {}


def on_message(client, userdata, message):
    print("Following message received: ", str(message.payload.decode("utf-8")), ": full topic: ", message.topic)

    tup = {message.topic : str(message.payload.decode("utf-8"))}
    msgs_from_vm.update(tup)


def on_message_countermeasure(client, userdata, message):
    print("Possible countermeasure message received: ", str(message.payload.decode("utf-8")), ": about ", "V? = ", message.topic[-2:])

    if int(message.payload.decode("utf-8")) == 1:
        print("Blocking procedure of ", message.topic[-2:], ". Message published for BRGW")
        publish.single("DSO/BRGW/COUNTERMEASURE/" + str(message.topic[-2:]), "1")


def runDSO():
    pass

    ### receive signature and data from VM
    dso = mqttcli.Client()
    dso.on_message = on_message
    dso.connect(IP_broker[1])  # connect to broker at DCS1 (self)
    dso.loop_start()
    dso.subscribe([("LTE/DSO/VM/V1/data", 0),
                   ("LTE/DSO/VM/V1/sign", 0),
                   ("LTE/DSO/VM/V1/ts", 0),
                   ("LTE/DSO/VM/V2/data", 0),
                   ("LTE/DSO/VM/V2/sign", 0),
                   ("LTE/DSO/VM/V2/ts", 0),])
    print("...waiting for data via LTE...")
    # publish from swh else
    time.sleep(6)
    dso.loop_stop()
    print("...no more waiting... received: ", msgs_from_vm)
    if msgs_from_vm=={}:
        print("no data via LTE received. STOP")
        sys.exit()

    ### hash the data
    data = np.array([float(msgs_from_vm['LTE/DSO/VM/V1/data']), float(msgs_from_vm['LTE/DSO/VM/V2/data'])])
    h1 = hashlib.sha256(data[0]).hexdigest()
    h2 = hashlib.sha256(data[1]).hexdigest()
    hash2 = np.array([h1, h2])

    ### send the hashed data + signatures
    dso.reinitialise()
    dso.on_message = on_message_countermeasure
    dso.connect(IP_broker[2])
    msgs_to_dcs = [("DSO/DCS/DSO/V1/hash", hash2[0]),
                   ("DSO/DCS/DSO/V1/sign", msgs_from_vm['LTE/DSO/VM/V1/sign']),
                   ("DSO/DCS/DSO/V2/hash", hash2[1]),
                   ("DSO/DCS/DSO/V2/sign", msgs_from_vm['LTE/DSO/VM/V2/sign'])]
    publish.multiple(msgs_to_dcs, hostname=IP_broker[2])

    ### receives response from DCS2
    dso.loop_start()
    dso.subscribe([("DSO/DSO/DCS/V1", 0),
                   ("DSO/DSO/DCS/V2", 0)])

    if dcssim == True:  # test certificates from DCS agent
        testdcs = mqttcli.Client()
        testdcs.connect(IP_broker[2])  # connect to broker at DCS1 (self)
        testdcs.publish("DSO/DSO/DCS/V1", "1")
        testdcs.publish("DSO/DSO/DCS/V2", "0")

    time.sleep(3)  # max waiting time for DCS2 response
    dso.loop_stop()

    # DSO sends the block traffic command if necessary - via on_message_countermeasure()


runDSO()
