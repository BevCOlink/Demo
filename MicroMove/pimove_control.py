#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pipython import GCSDevice
import time,threading
PI_ID="0118045977"

class Pi(object):
    def __init__(self,device_code):
        self.gcs = GCSDevice('E-727')
        self.device_code=device_code
        self.gcs.ConnectUSB(self.device_code)
        self.gcs.SVO(u'1', 1)
        self.gcs.SVO(u'2', 1)
        self.gcs.SVO(u'3', 1)

    def getposition(self):
        posi = self.gcs.qPOS()
        return posi
    def position_read_x(self):
        aa = self.gcs.qPOS()
        return aa['1']
    def position_read_y(self):
        aa = self.gcs.qPOS()
        return aa['2']
    def position_read_z(self):
        aa = self.gcs.qPOS()
        return aa['3']

    def position_move(self,length):
        self.gcs.MOV(length)

    def position_move_x(self,length):       #length unit is um
        self.gcs.MOV(u'1', length)

    def position_move_y(self,length):       #length unit is um
        self.gcs.MOV(u'2', length)

    def position_move_z(self,length):       #length unit is um
        self.gcs.MOV(u'3', length)


    def r_position_move_x(self,length):       #length unit is um
        self.gcs.MVR(u'1', length)

    def r_position_move_y(self,length):       #length unit is um
        self.gcs.MVR(u'2', length)

    def r_position_move_z(self,length):       #length unit is um
        self.gcs.MVR(u'3', length)

    def close(self):
        self.gcs.close()

    def connect(self):
        self.gcs.ConnectUSB(self.device_code)

    def read_velocicty(self):
        v=self.gcs.qVEL()
        print(v)
        v=self.gcs.qJOG()
        print(v)

if __name__ == '__main__':
    PI=Pi(PI_ID)
    z=PI.position_read_z()
    print(z)
    PI.read_velocicty()