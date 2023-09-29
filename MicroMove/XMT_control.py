#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: XMT_control.py
@time: 2022/7/8 16:16
@desc: 芯明天位移台控制
'''

import serial,time
import numpy as np

class XMT(object):
    def __init__(self,COM):
        self.COM = COM
        self.XMT_serial = serial.Serial(self.COM, baudrate=115200, bytesize=8, stopbits=1, parity='N', xonxoff=True,
                                   timeout=0.01)
        if self.XMT_serial.is_open:
            print('XMT connection succeeded')
        else:
            print('XMT connection failed')

    def _num_to_byte(self, position):
        kk=np.zeros(4,dtype=np.uint16)
        if position<0:
            position*=-1
            a = int(position)
            kk[0] = a/256 +0x80
            kk[1] = a%256
            a=int((position - a)*10000)
            kk[2] = a/256
            kk[3] = a%256
        else:
            a = int(position)
            kk[0] = a / 256
            kk[1] = a % 256
            a = int((position - a + 0.000001) * 10000)
            kk[2] = a / 256
            kk[3] = a % 256
        return kk

    def _byte_to_num(self,bytes):
        if (bytes[0]&0x80):
            temp= bytes[0]-0x80
            d=temp*256+bytes[1]+(bytes[2]*256+bytes[3])*0.0001
            d*=(-1)
        else:
            d = bytes[0]*256+bytes[1]+(bytes[2]*256+bytes[3])*0.0001

        return d

    def _oct2hex(self,list):
        com = []
        for i in list:
            com.append(int(hex(i),16))

        return com

    def _XOR8_check(self,com):
        check = 0
        for i in com:
            check = check^i
        com = np.append(com,check)
        com = self._oct2hex(com)
        return com

    def _SVO(self,axis:int,sign:int):
        com = np.array([0xaa, 0x01, 0x08, 0x12, 0x00, 0x01, 0x00], dtype=np.uint16)
        # com = np.append(com,[axis,sign])
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))

    #-----------------------#

    def getposition(self):
        com = np.array([0xaa, 0x01, 0x06, 0x33, 0x00], dtype=np.uint16)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))
        pos = self.XMT_serial.readall()
        x=self._byte_to_num(pos[-13:-9])
        y=self._byte_to_num(pos[-9:-5])
        z=self._byte_to_num(pos[-5:-1])
        return {'1':x,'2':y,'3':z}

    def position_read_x(self):
        com = np.array([0xaa, 0x01, 0x07, 0x06, 0x00,0x00],dtype=np.uint16)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))
        pos = self.XMT_serial.readall()[-5:-1]
        pos = self._byte_to_num(pos)
        return pos

    def position_read_y(self):
        com = np.array([0xaa, 0x01, 0x07, 0x06, 0x00,0x01],dtype=np.uint16)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))
        pos = self.XMT_serial.readall()[-5:-1]
        pos = self._byte_to_num(pos)
        return pos

    def position_read_z(self):
        com = np.array([0xaa, 0x01, 0x07, 0x06, 0x00,0x02],dtype=np.uint16)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))
        pos = self.XMT_serial.readall()[-5:-1]
        pos = self._byte_to_num(pos)
        return pos

    def position_move_x(self,position):
        curr_pos=0
        com = np.array([0xaa, 0x01, 0x0b, 0x01, 0x00, 0x00],dtype=np.uint16)
        hex_position = self._num_to_byte(position)
        com = np.append(com,hex_position)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))
        # while abs(curr_pos - position) > 0.01:
        #     curr_pos =

    def position_move_y(self,position):
        com = np.array([0xaa, 0x01, 0x0b, 0x01, 0x00, 0x01],dtype=np.uint16)
        hex_position = self._num_to_byte(position)
        com = np.append(com,hex_position)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))

    def position_move_z(self,position):
        com = np.array([0xaa, 0x01, 0x0b, 0x01, 0x00, 0x02],dtype=np.uint16)
        hex_position = self._num_to_byte(position)
        com = np.append(com,hex_position)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))

    def position_move(self,position):
        com = np.array([0xaa, 0x01, 0x12, 0x03, 0x00],dtype=np.uint16)
        for i in position.values():
            hex_position = self._num_to_byte(i)
            com = np.append(com,hex_position)
        com = self._XOR8_check(com)
        self.XMT_serial.write(bytearray(com))

    def r_position_move_x(self,length):
        curr_pos = self.position_read_x()
        pos = curr_pos+length
        self.position_move_x(pos)

    def r_position_move_y(self,length):
        curr_pos = self.position_read_y()
        pos = curr_pos+length
        self.position_move_y(pos)

    def r_position_move_z(self,length):
        curr_pos = self.position_read_z()
        pos = curr_pos+length
        self.position_move_z(pos)

    def close(self):
        self.XMT_serial.close()

    def connect(self):
        self.XMT_serial = serial.Serial(self.COM, baudrate=115200, bytesize=8, stopbits=1, parity='N', xonxoff=True,
                                        timeout=0.01)
        if self.XMT_serial.is_open:
            print('XMT connection succeeded')
        else:
            print('XMT connection failed')


if __name__ == '__main__':
    COM = 'COM3'
    PI=XMT(COM)
    # PI.position_move_y(15)
    PI.position_move([20,20,30])
    time.sleep(1)
    PI.close()
    PI.connect()
    # PI.position_read_x()
    x = PI.position_read_x()
    print(x)
    # PI.r_position_move_x(-10)
    # x=PI.position_read_x()
    # print(x)
    # PI._SVO(0,0)
    # PI.getposition()
    # x=PI.num_to_byte(20)
    # print(hex(int(x[3])).upper())