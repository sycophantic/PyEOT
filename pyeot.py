#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyEOT End-of-Train Device Decoder
Copyright (c) 2018 Eric Reuter
Copyright (c) 2019 Daniel J. Grinkevich

This source file is subject of the GNU general public license

history:    2018-08-09 Initial Version
            2019-03-05 Forked

purpose:    Receives demodulated FFSK bitstream from GNU Radio, indentifes
            potential packets, and passes them to decoder classes for
            parsing and verification.  Finally human-readable data are printed
            to stdout.

            Requires eot_decoder.py and helpers.py
"""

import datetime
import collections
from eot_decoder import EOT_decode
import zmq
import csv

# Socket to talk to server
context = zmq.Context()
sock = context.socket(zmq.SUB)

# create fixed length queue
queue = collections.deque(maxlen=256)


def printEOT(EOT):
    localtime = str(datetime.datetime.now().
                    strftime('%Y-%m-%d %H:%M:%S.%f'))[:-3]
    eotout = {
        "time": localtime,
        "raw_packet": EOT.get_packet(),
        "unit_addr": EOT.unit_addr,
        "pressure": EOT.pressure,
        "motion": EOT.motion,
        "mkr_light": EOT.mkr_light,
        "turbine": EOT.turbine,
        "batt_cond_text": EOT.batt_cond_text,
        "batt_charge": EOT.batt_charge,
        "arm_status": EOT.arm_status
         }
    
    print("")
    print("EOT {}".format(localtime))
    #   print(EOT.get_packet())
    print("---------------------")
    print("Unit Address:   {}".format(eotout['unit_addr']))
    print("Pressure:       {} psig".format(eotout['pressure']))
    print("Motion:         {}".format(eotout['motion']))
    print("Marker Light:   {}".format(eotout['mkr_light']))
    print("Turbine:        {}".format(eotout['turbine']))
    print("Battery Cond:   {}".format(eotout['batt_cond_text']))
    print("Battery Charge: {}".format(eotout['batt_charge']))
    print("Arm Status:     {}".format(eotout['arm_status']))

    f = open('out.csv','a') #store captured data in out.csv
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(eotout.values())
    f.close()

def main():
    #  Connect to GNU Radio and subscribe to stream
    sock.connect("tcp://localhost:5555")
    sock.setsockopt(zmq.SUBSCRIBE, b'')
    print("PyEOT Running. Data will be stored in out.csv.")
    while True:
        newData = sock.recv()  # get whatever data are available
        for byte in newData:
            queue.append(str(byte))  # append each new symbol to deque

            buffer = ''  # clear buffer
            for bit in queue:  # move deque contents into buffer
                buffer += bit

            if (buffer.find('10101011100010010') == 0):  # look for frame sync
                EOT = EOT_decode(buffer[6:])  # first 6 bits are bit sync
                if (EOT.valid):
                    printEOT(EOT)

main()
