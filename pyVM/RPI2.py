import socket
import sys
import os
import struct
from datetime import datetime, timedelta
import time
import numpy as np
from pprint import pprint as pp
import platform

# import own RPI2 scripts
from RPI2.tofloat import tofloat
from RPI2.send import send
from RPI2.receive import receive
from RPI2.settings import settings_fromRTDS, settings_toRTDS, NumData, default_accuracy, dbname
from RPI2.settings import IP_send, IP_receive, Port_send, Port_receive

# adding python path at runtime - common RPI1 and RPI2 scripts
# sys.path.append('/home/pi/git_SAU/SAU/control/IS/sau_pc')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sql_queries import sqlquery_measurement_write, sqlquery_control_read
from load_db import db_connection


def rpi2fromRTDS():

    ################################
    # Should run max. every X sec as cronjob #
    ################################

    #### TEST query??? ####
    if False: # select
        conn = db_connection(dbname)
        cursor = conn.cursor()

        now = datetime.now()
        minute = timedelta(hours=1)
        query = sqlquery_control_read(str(4),str(0),str(2),str(now)) #nodeid, resource_id, control_type, time

        cursor.execute(query)
        r = cursor.fetchall()
        conn.close()
        pp(r)
        sys.exit()

    if str(platform.machine()) == 'x86_64':
        ldata = np.array([0.95, 0, 0.9, -0.9, 0.94, 0, 0.85, -0.85, 0.98, 0, 0.97, -0.97,
                          1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]) # offline TEST
    else:
        # downloads measurements from the devices (from RTDS)
        ldata = receive(IP_receive, Port_receive, NumData)

    print("Values received from RTDS (or fake ones): ", ldata)

    if len(settings_fromRTDS) != NumData or len(settings_fromRTDS) != NumData:
        print("RPI2: Setting does not compatible with incoming RTDS data! STOP writing to DB!")
        sys.exit()
    sys.exit()

    SQLtext_measurements = ""
    current_time = datetime.now()
    for i in range(0,NumData):
        measurementvalue = ldata[i]
        s = settings_fromRTDS[i]
        mtype = int(settings_fromRTDS[i][1])
        phaseid = settings_fromRTDS[i][2]
        nodeid = int(settings_fromRTDS[i][3])
        SQLtext_measurements += sqlquery_measurement_write(str(mtype),
                                                           str(phaseid),
                                                           str(nodeid),
                                                           str(current_time),
                                                           str(measurementvalue),
                                                           str(default_accuracy))
        SQLtext_measurements += " "

    # writes measurements to the DB
    conn = db_connection(dbname)
    cursor = conn.cursor()

    try:
        cursor.execute(SQLtext_measurements)
        conn.commit()
        print("RPI2: ...trying to write measurements in DB...")
    except psycopg2.OperationalError as e:
        print('RPI2: Unable to execute query!\n{0}').format(e)
        sys.exit(1)
    finally:
        print('RPI2: Measurements written in DB, closing the connection.')
        conn.close()


def rpi2toRTDS():

    ##################################################################
    ##### Sending controls to RTDS ##########################

    now = datetime.now()
    data_to_RTDS = []
    conn = db_connection(dbname)
    cursor = conn.cursor()
    # minute = timedelta(hours=1)
    for i in range(0, len(settings_toRTDS)):
        nodeid = settings_toRTDS[i][1]
        resourceid = settings_toRTDS[i][2]
        controltype = settings_toRTDS[i][3]
        query = sqlquery_control_read(str(nodeid), str(resourceid), str(controltype), str(now), str(1))
        cursor.execute(query)
        r = cursor.fetchall()
        data_to_RTDS.append(float(r[0][2]))

    conn.close()

    #data_test = [0.9, -0.2, 0.7, 0.5, 1.0, 0.9, -0.96, -0.6]
    send(data_to_RTDS, IP_send, Port_send)
    #print("RPI2: Successfully sent! Control values sent to RTDS: ", data_to_RTDS)
