import sys
import numpy as np
import hashlib
import paho.mqtt.client as mqttcli
import paho.mqtt.publish as publish
import time
import struct

from receive import receive
from settings import settings_fromRTDS, NumData, IP_send, IP_receive, Port_send, Port_receive, IP_broker, dcssim, DSO_control
from pypower.api import ppoption, runpf, printpf, runopf
from runopf_no_printpf import runopf as runopf2
from case33bw_dcs import case33bw_dcs
from send import send
import bitstring

msgs_from_vm = {}


def on_message(client, userdata, message):
    #print("Following message received: ", str(message.payload.decode("utf-8")), ": full topic: ", message.topic)
    tup = {message.topic : str(message.payload.decode("utf-8"))}
    msgs_from_vm.update(tup)


def on_message_countermeasure(client, userdata, message):
    print("Possible countermeasure message received: ", str(message.payload.decode("utf-8")), ": about ", "V? = ", message.topic[-2:])

    if int(message.payload.decode("utf-8")) == 1:
        print("Blocking procedure of ", message.topic[-2:], ". Message published for BRGW")
        publish.single("DSO/BRGW/COUNTERMEASURE/" + str(message.topic[-2:]), "1")


def runDSO():

    if False:

        num_str = str(bitstring.BitArray(float=1.2323, length=32))
        float_back = struct.unpack('!f', bytes.fromhex(num_str[2:]))[0]

        f1 = bitstring.BitArray(float=4.265, length=32)
        print(f1.hex)

        Pload10 = 4.265
        Qload10 = 2.132
        V10pu = 0.8754

        ppc = case33bw_dcs()
        ppc["bus"][9][2] = Pload10
        ppc["bus"][9][3] = Qload10

        r = runopf2(ppc)

        print(r["gen"][:, 0:3])

        Pset5 = round(r["gen"][1, 1], 4)
        if Pset5 == 0: Pset5 = 0.0001
        Qset5 = round(r["gen"][1, 2], 4)
        Pset7 = round(r["gen"][2, 1], 4)
        if Pset7 == 0: Pset7 = 0.0001
        Qset7 = round(r["gen"][2, 2], 4)
        Pset9 = round(r["gen"][3, 1], 4)
        if Pset9 == 0: Pset9 = 0.0001
        Qset9 = round(r["gen"][3, 2], 4)

        Pset8fl = round(r["gen"][4, 1], 4)
        Qset8fl = round(r["gen"][4, 2], 4)

        data_to_RTDS = [Pset5, Qset5, Pset7, Qset7, Pset9, Qset9, Pset8fl, Qset8fl]
        print(data_to_RTDS)
        send(data_to_RTDS, IP_send, Port_send)

        sys.exit()


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
    data = np.array([str(msgs_from_vm['LTE/DSO/VM/V1/data']), str(msgs_from_vm['LTE/DSO/VM/V2/data'])])
    h1 = hashlib.sha256(data[0].encode('utf8')).hexdigest()
    h2 = hashlib.sha256(data[1].encode('utf8')).hexdigest()
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
    if DSO_control==True:

        #data received from measurements, also might be compromised

        print(data[0])
        print(data[0][22:30])

        Pload10 = round(float(struct.unpack('!f', bytes.fromhex(data[0][2:10]))[0]),4)
        Qload10 = round(float(struct.unpack('!f', bytes.fromhex(data[0][12:20]))[0]),4)
        V10pu = round(float(struct.unpack('!f', bytes.fromhex(data[0][22:30]))[0]),4)

        Pload5 = round(float(struct.unpack('!f', bytes.fromhex(data[1][2:10]))[0]),4)
        Qload5 = round(float(struct.unpack('!f', bytes.fromhex(data[1][12:20]))[0]),4)
        V5pu = round(float(struct.unpack('!f', bytes.fromhex(data[1][22:30]))[0]),4)

        ppc = case33bw_dcs() # static data of topology and rest of the loads etc.

        ppc["bus"][9][2] = Pload10 # update of the ppc according to measurements
        ppc["bus"][9][3] = Qload10
        ppc["bus"][4][2] = Pload5
        ppc["bus"][4][3] = Qload5

        r = runopf2(ppc) # opf according to new states (i.e. measurements, possibly compromised)

        Pset5 = round(r["gen"][1, 1], 4)
        if Pset5 == 0: Pset5 = 0.0001
        Qset5 = round(r["gen"][1, 2], 4)
        Pset7 = round(r["gen"][2, 1], 4)
        if Pset7 == 0: Pset7 = 0.0001
        Qset7 = round(r["gen"][2, 2], 4)
        Pset9 = round(r["gen"][3, 1], 4)
        if Pset9 == 0: Pset9 = 0.0001
        Qset9 = round(r["gen"][3, 2], 4)

        Pset8fl = round(r["gen"][4, 1], 4)
        Qset8fl = round(r["gen"][4, 2], 4)

        data_to_RTDS = [Pset5, Qset5, Pset7, Qset7, Pset9, Qset9, Pset8fl, Qset8fl]
        send(data_to_RTDS, IP_send, Port_send)


runDSO()
