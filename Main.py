#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: Main.py
@time: 2021/6/28/0028 15:49
@desc:
'''
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys
from counter import Counter
from pimove_control import Pi
import point_lock
from SpinCore import spincore
from main_operator import Main_Operator
from confocal_ccanning_control import Confocal_Control
from spin_control import Spin_Control

from spot_finder_control import Spots_Finder_Control
from user_defined_control import User_defined_Control
from XMT_control import XMT


PI = 'PI'
MW_Source = 'Mini' #Agilent, Mini
PI_ID="0118069721" #COM5  0118003812  0118045977

Device_str = "Dev1/ctr2"
TriggerGate = "PFI9"


if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)

    if PI == 'PI':
        PI = Pi(PI_ID)
    elif PI == 'XMT':
        PI = XMT(PI_ID)
    counter=Counter(Device_str=Device_str,TriggerGate=TriggerGate,counter_update_time=100)
    sc = spincore()
    operator = Main_Operator(counter=counter, spincore=sc)
    Point_Lock = point_lock.Lock(Pi=PI)
    spot_finder_control = Spots_Finder_Control()
    gui_main = Confocal_Control(operator=operator,sc=sc,PI=PI,counter=counter,point_lock=Point_Lock,find_spots=spot_finder_control)
    spot_finder_control.confcocal_control = gui_main
    gui_main.PI_device = PI_ID
    Point_Lock.text_browser = gui_main.Text_browser
    if MW_Source == 'Agilent':
        from MW_Agilent import MW_generater
        MW = MW_generater()
    elif MW_Source == 'Mini':
        from MW_Mini_2 import mini_MW_generater
        MW = mini_MW_generater()
    elif MW_Source == 'Zurich':
        from AWG_Zurich_test import MW_generater
        MW = MW_generater()
    Spin_control=Spin_Control(gui_main=gui_main,MW_generater=MW,spincore=sc,operator=operator,counter=counter,point_lock=Point_Lock)
    User_defined_Spin_control = User_defined_Control(gui_main=gui_main,MW_generater=MW,spincore=sc,operator=operator,counter=counter,point_lock=Point_Lock)
    gui_main.Spin_control = Spin_control
    gui_main.user_defined_spin_control = User_defined_Spin_control
    gui_main.DAQ_edit.setText(Device_str)
    gui_main.PI_edit.setText(PI_ID)

    gui_main.show()

    sys.exit(app.exec_())