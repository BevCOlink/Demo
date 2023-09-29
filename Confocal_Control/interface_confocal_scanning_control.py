#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: interface_confocal_scanning_control.py
@time: 2022/4/15/0015 11:32:49
@desc:
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QStatusBar,QMenuBar
import sys,os
import pyqtgraph as pg
import numpy as np
import LableStyle, ButtonStyle
import ctypes


#若导入错误ButtonStyle，删除.idea文件重新设置即可

position_dic={'x position':[50,50],'y position':[50,50],'z position':[50,50],'x step':[0.2,2],'y step':[0.2,2],'z step':[0.2,2],'x range':[10,50],'y range':[10,50],'z range':[10,50]}

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None, QtCore.Qt.Widget)
        self.counter_poltting = QtCore.QTimer()  # 计时器
        self.counter_poltting.setTimerType(QtCore.Qt.PreciseTimer)

        self.image_poltting = QtCore.QTimer()  # 计时器
        self.image_poltting.setTimerType(QtCore.Qt.PreciseTimer)
        self.setupUi()
        path = os.getcwd()
        version = path.split('\\')[-1].split('-')[-1]
        self.setWindowTitle('Confocal Scan '+version)
        self.setWindowIcon(QtGui.QIcon(QtCore.QDir.currentPath()+'/ico/interface.ico'))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

        name = '# step:0.2 range:10'
        self.position_comboBox.addItem(name)
        name='# step:2 range 50'
        self.position_comboBox.addItem(name)


    def setupUi(self):
        self.resize(800, 600)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setWindowTitle('PI Scanning')
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.top_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.top_widget.setLayout(self.top_layout)  # 设置左侧部件布局为网格
        self.top_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.para_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.para_widget.setObjectName('para_widget')
        self.par_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.para_widget.setLayout(self.par_layout)  # 设置左侧部件布局为网格
        self.par_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.save_load_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.save_load_widget.setObjectName('save_load_widget')
        self.save_load_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.save_load_widget.setLayout(self.save_load_layout)  # 设置左侧部件布局为网格
        self.save_load_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.pi_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.pi_widget.setObjectName('pi_widget')
        self.pi_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.pi_widget.setLayout(self.pi_layout)  # 设置左侧部件布局为网格
        self.pi_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.lock_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.lock_widget.setObjectName('lock_widget')
        self.lock_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.lock_widget.setLayout(self.lock_layout)  # 设置左侧部件布局为网格
        self.lock_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.button_widget.setObjectName('button_widget')
        self.button_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.button_widget.setLayout(self.button_layout)  # 设置左侧部件布局为网格

        self.image_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.image_widget.setObjectName('image_widget')
        self.image_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.image_widget.setLayout(self.image_layout)  # 设置左侧部件布局为网格

        self.count_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.count_widget.setObjectName('count_widget')
        self.count_layout = QtWidgets.QGridLayout()
        self.count_widget.setLayout(self.count_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.para_widget, 0, 0, 3, 5)
        self.main_layout.addWidget(self.save_load_widget, 0, 5, 3, 5)
        self.main_layout.addWidget(self.pi_widget, 3, 0, 10, 10)
        self.main_layout.addWidget(self.lock_widget, 13, 0, 5, 10)
        self.main_layout.addWidget(self.button_widget, 18, 0, 2, 10)

        self.main_layout.addWidget(self.image_widget, 0, 10, 15, 20)
        self.main_layout.addWidget(self.count_widget, 15, 10, 5, 20)
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件,必须设置

        self._menu_bar_setup()
        self._piWindow()
        self._lockWindow()
        self._imageWindow()
        self._countWindow()
        self._paraWindow()
        self._buttonWindow()
        self._save_loadWindow()


        ##########功能设置####################
        self._connect_function()

    def _menu_bar_setup(self):

        self.statusbar=QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('运行')

        self.menubar=QMenuBar()
        self.setMenuBar(self.menubar)
        self.menubar.installEventFilter(self)
        self.function_menu=self.menubar.addMenu('Function')
        self.function_menu.addSeparator()


        self.spin_control_action = QAction('spin control', self)
        self.function_menu.addAction(self.spin_control_action)
        self.find_spots_action = QAction('find spots', self)
        self.function_menu.addAction(self.find_spots_action)
        self.user_defined_spincontrol_action = QAction('user_defined spin-control', self)
        self.function_menu.addAction(self.user_defined_spincontrol_action)

    # https://blog.csdn.net/seniorwizard/article/details/110851057
    def eventFilter(self,watched,event):
        if(watched == self.menubar and event.type() == event.MouseMove):
            return True
        return super(MainWindow,self).eventFilter(watched,event)

    def _save_loadWindow(self):
        ###################按钮##########################
        self.save_scan_button = QtWidgets.QPushButton('Save Scan')
        self.save_scan_button.setFixedSize(80, 60)
        # self.save_scan_button.setMouseTracking(True)
        self.save_scan_button.setCheckable(True)
        self.save_scan_button.setChecked(False)
        self.save_scan_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.load_scan_button = QtWidgets.QPushButton('Load Scan')
        self.load_scan_button.setFixedSize(80, 60)
        # self.load_scan_button.setMouseTracking(True)
        self.load_scan_button.setCheckable(True)
        self.load_scan_button.setChecked(False)
        self.load_scan_button.setStyleSheet(ButtonStyle.style_tab_button)
        ###############################################
        self.save_load_layout.addWidget(self.save_scan_button, 0, 0, 2, 2)
        self.save_load_layout.addWidget(self.load_scan_button, 0, 2, 2, 2)

        ####################图层格式#########################
        self.save_load_widget.setStyleSheet('''
                                                    QWidget#save_load_widget{
                                                        color:#232C51;
                                                        background:gray;
                                                        border-top:1px solid darkGray;
                                                        border-bottom:1px solid darkGray;
                                                        border-right:1px solid darkGray;
                                                        border-top-right-radius:10px;
                                                        border-bottom-right-radius:10px;
                                                    }
                                                    QLabel#right_lable{
                                                        color:red;
                                                        font-size:20px;
                                                        font-weight:700;
                                                        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                                                    }
                                                ''')

    def _paraWindow(self):
        ####################标签#########################
        self.DAQ_label = QtWidgets.QLabel("DAQ")
        self.DAQ_label.setStyleSheet(LableStyle.lable_tex_succeed)
        self.PI_label = QtWidgets.QLabel("PI")
        self.PI_label.setStyleSheet(LableStyle.lable_tex_succeed)

        ####################编辑栏#########################
        self.DAQ_edit = QtWidgets.QLineEdit()
        self.DAQ_edit.setFixedSize(100, 20)
        self.PI_edit = QtWidgets.QLineEdit()
        self.PI_edit.setFixedSize(100, 20)

        self.par_layout.addWidget(self.DAQ_label, 0, 0, 2, 2)
        self.par_layout.addWidget(self.PI_label, 2, 0, 2, 2)
        self.par_layout.addWidget(self.DAQ_edit, 0, 2, 2, 2)
        self.par_layout.addWidget(self.PI_edit, 2, 2, 2, 2)

        ####################图层格式#########################
        self.para_widget.setStyleSheet('''
                                                        QWidget#para_widget{
                                                        color:#232C51;
                                                        background:gray;
                                                        border-top:1px solid darkGray;
                                                        border-bottom:1px solid darkGray;
                                                        border-left:1px solid darkGray;
                                                        border-top-left-radius:10px;
                                                        border-bottom-left-radius:10px;
                                                    }''')

    def _piWindow(self):
        ####################标签#########################
        self.Scan_label = QtWidgets.QLabel("Scan")
        self.Scan_label.setStyleSheet(LableStyle.lable_subtitle_2)

        self.Current_Position_label = QtWidgets.QLabel("Curr Position")
        self.Current_Position_label.setStyleSheet(LableStyle.lable_subtitle_2)
        self.Move_Position_label = QtWidgets.QLabel("Mov Position")
        self.Move_Position_label.setStyleSheet(LableStyle.lable_subtitle_2)
        self.Functional_label = QtWidgets.QLabel("Function Zone")
        self.Functional_label.setStyleSheet(LableStyle.lable_subtitle_2)

        self.x_step_label = QtWidgets.QLabel("x step")
        self.y_step_label = QtWidgets.QLabel("y step")
        self.z_step_label = QtWidgets.QLabel("z step")
        self.x_range_label = QtWidgets.QLabel("x range")
        self.y_range_label = QtWidgets.QLabel("y range")
        self.z_range_label = QtWidgets.QLabel("z range")

        self.x_curr_position_label = QtWidgets.QLabel("x")
        self.x_curr_position_label.setStyleSheet(LableStyle.lable_box3)
        self.y_curr_position_label = QtWidgets.QLabel("y")
        self.y_curr_position_label.setStyleSheet(LableStyle.lable_box3)
        self.z_curr_position_label = QtWidgets.QLabel("z")
        self.z_curr_position_label.setStyleSheet(LableStyle.lable_box3)



        ####################复选框#########################
        self.x_position_checkbox = QtWidgets.QCheckBox('x position')
        self.y_position_checkbox = QtWidgets.QCheckBox('y position')
        self.z_position_checkbox = QtWidgets.QCheckBox('z position')
        ####################按钮#########################
        self.start_scan_button = QtWidgets.QPushButton('Start')
        self.start_scan_button.setFixedSize(80, 60)
        # self.start_scan_button.setMouseTracking(True)
        self.start_scan_button.setCheckable(True)
        self.start_scan_button.setChecked(False)
        self.start_scan_button.setStyleSheet(ButtonStyle.conected)

        self.load_position_button = QtWidgets.QPushButton('Load')
        self.load_position_button.setFixedSize(50, 30)
        # self.load_position_button.setMouseTracking(True)
        self.load_position_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.load_z_position_button = QtWidgets.QPushButton('Load z')
        self.load_z_position_button.setFixedSize(50, 30)
        # self.load_z_position_button.setMouseTracking(True)
        self.load_z_position_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.general_setting_button = QtWidgets.QPushButton('general setting')
        self.general_setting_button.setFixedSize(80, 60)
        # self.Point_lock_button.setMouseTracking(True)
        self.general_setting_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.save_position_combobox_button = QtWidgets.QPushButton('save')
        self.save_position_combobox_button.setFixedSize(50, 30)
        self.save_position_combobox_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.load_position_combobox_button = QtWidgets.QPushButton('load')
        self.load_position_combobox_button.setFixedSize(50, 30)
        self.load_position_combobox_button.setStyleSheet(ButtonStyle.style_tab_button)


        ####################数值框#########################
        # self.counter_value_box = pg.SpinBox(value=50.0, suffix='um',
        #                                  dec=True,
        #                                  step=1.0, minStep=0.01,
        #                                  bounds=[0, 100])


        self.x_position_Box = pg.SpinBox(value=50.0, suffix='um',
                                         dec=True,
                                         step=1.0, minStep=0.01,
                                         bounds=[0, 100])
        self.x_position_Box.setFixedSize(100, 30)
        self.y_position_Box = pg.SpinBox(value=50.0, suffix='um',
                                         dec=True,
                                         step=1.0, minStep=0.01,
                                         bounds=[0, 100])
        self.y_position_Box.setFixedSize(100, 30)
        self.z_position_Box = pg.SpinBox(value=50.0, suffix='um',
                                         dec=True,
                                         step=1.0, minStep=0.01,
                                         bounds=[0, 100])
        self.z_position_Box.setFixedSize(100, 30)

        self.x_step_Box = pg.SpinBox(value=2.0, suffix='um',
                                     dec=True,
                                     step=0.02, minStep=0.01,
                                     bounds=[0, 100])
        self.x_step_Box.setFixedSize(100, 30)
        self.y_step_Box = pg.SpinBox(value=2.0, suffix='um',
                                     dec=True,
                                     step=0.02, minStep=0.01,
                                     bounds=[0, 100])
        self.y_step_Box.setFixedSize(100, 30)
        self.z_step_Box = pg.SpinBox(value=2.0, suffix='um',
                                     dec=True,
                                     step=0.02, minStep=0.01,
                                     bounds=[0, 100])
        self.z_step_Box.setFixedSize(100, 30)

        self.x_range_Box = pg.SpinBox(value=50.0, suffix='um',
                                      dec=True,
                                      step=1.0, minStep=0.01,
                                      bounds=[0, 100])
        self.x_range_Box.setFixedSize(100, 30)
        self.y_range_Box = pg.SpinBox(value=50.0, suffix='um',
                                      dec=True,
                                      step=1.0, minStep=0.01,
                                      bounds=[0, 100])
        self.y_range_Box.setFixedSize(100, 30)
        self.z_range_Box = pg.SpinBox(value=50.0, suffix='um',
                                      dec=True,
                                      step=1.0, minStep=0.01,
                                      bounds=[0, 100])
        self.z_range_Box.setFixedSize(100, 30)

        self.x_psoition_adjust_Box = pg.SpinBox(suffix='um',
                                                dec=False,
                                                step=0.001, minStep=0.001,
                                                bounds=[0, 100])
        self.x_psoition_adjust_Box.setFixedSize(100, 30)
        self.y_psoition_adjust_Box = pg.SpinBox(suffix='um',
                                                dec=False,
                                                step=0.001, minStep=0.001,
                                                bounds=[0, 100])
        self.y_psoition_adjust_Box.setFixedSize(100, 30)
        self.z_psoition_adjust_Box = pg.SpinBox(suffix='um',
                                                dec=False,
                                                step=0.01, minStep=0.01,
                                                bounds=[0, 100])
        self.z_psoition_adjust_Box.setFixedSize(100, 30)




        ######################combobox#######################
        self.position_comboBox=QtWidgets.QComboBox()
        self.position_comboBox.setFixedSize(140,30)

        self.scale_comboBox = QtWidgets.QComboBox()
        self.scale_comboBox.setFixedSize(60, 30)
        self.scale_comboBox.addItems(['x0.001', 'x0.01', 'x0.1'])
        #############################################
        self.pi_layout.addWidget(self.Scan_label, 0, 5, 1, 2)

        self.pi_layout.addWidget(self.x_position_checkbox, 1, 0, 1, 4)
        self.pi_layout.addWidget(self.y_position_checkbox, 1, 4, 1, 4)
        self.pi_layout.addWidget(self.z_position_checkbox, 1, 8, 1, 4)

        self.pi_layout.addWidget(self.x_position_Box, 2, 0, 1, 4)
        self.pi_layout.addWidget(self.y_position_Box, 2, 4, 1, 4)
        self.pi_layout.addWidget(self.z_position_Box, 2, 8, 1, 4)

        self.pi_layout.addWidget(self.x_step_label, 3, 0, 1, 4)
        self.pi_layout.addWidget(self.y_step_label, 3, 4, 1, 4)
        self.pi_layout.addWidget(self.z_step_label, 3, 8, 1, 4)

        self.pi_layout.addWidget(self.x_step_Box, 4, 0, 1, 4)
        self.pi_layout.addWidget(self.y_step_Box, 4, 4, 1, 4)
        self.pi_layout.addWidget(self.z_step_Box, 4, 8, 1, 4)

        self.pi_layout.addWidget(self.x_range_label, 5, 0, 1, 4)
        self.pi_layout.addWidget(self.y_range_label, 5, 4, 1, 4)
        self.pi_layout.addWidget(self.z_range_label, 5, 8, 1, 4)

        self.pi_layout.addWidget(self.x_range_Box, 6, 0, 1, 4)
        self.pi_layout.addWidget(self.y_range_Box, 6, 4, 1, 4)
        self.pi_layout.addWidget(self.z_range_Box, 6, 8, 1, 4)

        self.pi_layout.addWidget(self.Current_Position_label, 7, 1, 1, 4)
        self.pi_layout.addWidget(self.Functional_label, 7, 7, 1, 4)

        self.pi_layout.addWidget(self.start_scan_button, 8, 7, 2, 4)

        self.pi_layout.addWidget(self.position_comboBox,10,7,2,4)
        self.pi_layout.addWidget(self.save_position_combobox_button, 12, 7, 1, 2)
        self.pi_layout.addWidget(self.load_position_combobox_button, 12, 9, 1, 2)


        self.pi_layout.addWidget(self.x_curr_position_label, 8, 0, 1, 1)
        self.pi_layout.addWidget(self.y_curr_position_label, 9, 0, 1, 1)
        self.pi_layout.addWidget(self.z_curr_position_label, 10, 0, 1, 1)
        self.pi_layout.addWidget(self.x_psoition_adjust_Box, 8, 1, 1, 4)
        self.pi_layout.addWidget(self.y_psoition_adjust_Box, 9, 1, 1, 4)
        self.pi_layout.addWidget(self.z_psoition_adjust_Box, 10, 1, 1, 4)
        self.pi_layout.addWidget(self.scale_comboBox, 12, 4, 1, 2)
        self.pi_layout.addWidget(self.load_position_button, 12, 0, 1, 2)
        self.pi_layout.addWidget(self.load_z_position_button, 12, 2, 1, 2)


        #####################################################
        self.pi_widget.setStyleSheet('''
                                                                QWidget#pi_widget{
                                                                color:#232C51;
                                                                background:gray;
                                                                border-top:1px solid darkGray;
                                                                border-bottom:1px solid darkGray;
                                                                border-left:1px solid darkGray;
                                                                border-top-left-radius:10px;
                                                                border-bottom-left-radius:10px;
                                                            }''')

    def _lockWindow(self):
        ###################label######################
        self.Lock_label = QtWidgets.QLabel("Point Lock")
        self.Lock_label.setStyleSheet(LableStyle.lable_subtitle_2)

        self.lock_uprate_label = QtWidgets.QLabel('uprate')
        self.lock_uprate_label.setStyleSheet(LableStyle.lable_box3)
        self.lock_downrate_label = QtWidgets.QLabel('downrate')
        self.lock_downrate_label.setStyleSheet(LableStyle.lable_box3)
        self.lock_step_label = QtWidgets.QLabel('step')
        self.lock_step_label.setStyleSheet(LableStyle.lable_box3)

        ################box###########################
        self.lock_uprate_box = pg.SpinBox(value=1.06,
                                          dec=False,
                                          decimals=3,
                                          step=0.01, minStep=0.01,
                                          bounds=[1, 10])
        self.lock_uprate_box.setFixedSize(80, 30)

        self.lock_downrate_box = pg.SpinBox(value=0.9,
                                            dec=False,
                                            decimals=3,
                                            step=0.01, minStep=0.01,
                                            bounds=[0, 1])
        self.lock_downrate_box.setFixedSize(80, 30)

        self.lock_step_box = pg.SpinBox(value=0.03, suffix='um',
                                        dec=False,
                                        decimals=3,
                                        step=0.01, minStep=0.01,
                                        bounds=[0, 1])
        self.lock_step_box.setFixedSize(80, 30)
        ###################button#######################
        self.Point_lock_button = QtWidgets.QPushButton('Start Lock')
        self.Point_lock_button.setFixedSize(80, 40)
        self.Point_lock_button.setCheckable(True)
        self.Point_lock_button.setChecked(False)
        self.Point_lock_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.force_lock_button = QtWidgets.QPushButton('Force Lock')
        self.force_lock_button.setFixedSize(80, 40)
        self.force_lock_button.setStyleSheet(ButtonStyle.style_tab_button)
        ####################textbrowser##################
        self.Text_browser=QtWidgets.QTextBrowser()
        self.Text_browser.setFixedSize(170, 170)

        self.lock_layout.addWidget(self.Lock_label, 0, 3, 1, 3)
        self.lock_layout.addWidget(self.lock_uprate_label, 1, 0, 1, 2)
        self.lock_layout.addWidget(self.lock_downrate_label, 2, 0, 1, 2)
        self.lock_layout.addWidget(self.lock_step_label, 3, 0, 1, 2)

        self.lock_layout.addWidget(self.lock_uprate_box, 1, 2, 1, 2)
        self.lock_layout.addWidget(self.lock_downrate_box, 2, 2, 1, 2)
        self.lock_layout.addWidget(self.lock_step_box, 3, 2, 1, 2)
        self.lock_layout.addWidget(self.force_lock_button,4,0,1,2)
        self.lock_layout.addWidget(self.Point_lock_button,4,2,1,2)

        self.lock_layout.addWidget(self.Text_browser,1,4,4,2)

        self.lock_widget.setStyleSheet('''
                                                                                QWidget#lock_widget{
                                                                                color:#232C51;
                                                                                background:gray;
                                                                                border-top:1px solid darkGray;
                                                                                border-bottom:1px solid darkGray;
                                                                                border-left:1px solid darkGray;
                                                                                border-top-left-radius:10px;
                                                                                border-bottom-left-radius:10px;
                                                                            }''')

    def _buttonWindow(self):
        ###################按钮########################
        self.pause_button = QtWidgets.QPushButton('暂停')
        self.pause_button.setFixedSize(100, 50)
        self.pause_button.setStyleSheet(ButtonStyle.style_quit)

        self.active_button = QtWidgets.QPushButton('启动')
        self.active_button.setFixedSize(100, 50)
        self.active_button.setStyleSheet(ButtonStyle.style_quit)

        self.exit_button = QtWidgets.QPushButton('退出')
        self.exit_button.setFixedSize(100, 50)
        self.exit_button.setStyleSheet(ButtonStyle.style_quit)

        #############################################
        self.button_layout.addWidget(self.pause_button, 0, 0)
        self.button_layout.addWidget(self.active_button, 0, 1)
        self.button_layout.addWidget(self.exit_button, 0, 2)

        #####################################################
        self.button_widget.setStyleSheet('''
                                                                        QWidget#button_widget{
                                                                        color:#232C51;
                                                                        background:gray;
                                                                        border-top:1px solid darkGray;
                                                                        border-bottom:1px solid darkGray;
                                                                        border-left:1px solid darkGray;
                                                                        border-top-left-radius:10px;
                                                                        border-bottom-left-radius:10px;
                                                                    }''')

    def _imageWindow(self):
        self.image = pg.ImageView(view=pg.PlotItem())  # 绘制窗口是个widget
        self.colors = [(139, 0, 255), (0, 0, 255),(0, 127, 255),(0, 255, 0),(255, 255, 0), (255, 165, 0),(255, 0, 0)]
        self.color_map = pg.ColorMap(pos=np.linspace(0.0, 1.0, 7), color=self.colors)  # 将三种颜色作为节点，平滑过渡
        self.image.setColorMap(self.color_map)
        self.image.vLine = pg.InfiniteLine(pos=0, angle=90, movable=True)
        self.image.hLine = pg.InfiniteLine(pos=0, angle=0, movable=True)

        self.image.addItem(self.image.vLine, ignoreBounds=True)
        self.image.addItem(self.image.hLine, ignoreBounds=True)
        self.image.view.invertY(b=False)
        self.image.view.invertX(b=True)
        self.image.setFixedSize(750, 600)

        #############checkbox###############
        self.autorange_checkbox = QtWidgets.QCheckBox('Auto range')
        #############label##################
        self.image_time_label = QtWidgets.QLabel("image int-time")
        #############box####################
        self.image_time_Box = pg.SpinBox(value=10.0, suffix='ms',
                                         dec=True,
                                         step=10, minStep=0.01)
        self.image_time_Box.setFixedSize(80, 20)

        self.image_layout.addWidget(self.image, 0, 0, 10, 10)

        self.image_layout.addWidget(self.image_time_label,10,1,1,1)
        self.image_layout.addWidget(self.image_time_Box, 10, 2, 1, 1)

        self.image_layout.addWidget(self.autorange_checkbox, 10, 8, 1,1)

        self.image_widget.setStyleSheet('''
                                            QWidget#image_widget{
                                                color:#232C51;
                                                background:gray;
                                                border-top:1px solid darkGray;
                                                border-bottom:1px solid darkGray;
                                                border-right:1px solid darkGray;
                                                border-top-right-radius:10px;
                                                border-bottom-right-radius:10px;
                                            }
                                            QLabel#right_lable{
                                                color:red;
                                                font-size:20px;
                                                font-weight:700;
                                                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                                            }
                                        ''')


    def _countWindow(self):
        ###################标签########################
        self.mean_count_lable = QtWidgets.QLabel('mean counts')
        self.count_record_lable = QtWidgets.QLabel('record counts')
        self.count_int_lable = QtWidgets.QLabel('count int-time')

        ###################编辑栏########################
        self.mean_count_edit = QtWidgets.QLineEdit()
        self.mean_count_edit.setFixedSize(80, 20)
        ####################数值框#########################
        self.count_int_Box = pg.SpinBox(value=100.0, suffix='ms',
                                        dec=True,
                                        step=10, minStep=0.01)
        self.count_int_Box.setFixedSize(80, 20)

        ###################按钮########################
        self.clear_count_button = QtWidgets.QPushButton('Clear')
        self.clear_count_button.setFixedSize(70, 20)
        self.record_count_button = QtWidgets.QPushButton('Record')
        self.record_count_button.setFixedSize(70, 20)
        self.save_count_button = QtWidgets.QPushButton('Save')
        self.save_count_button.setFixedSize(70, 20)

        ###################绘图########################
        self.countPlot = pg.PlotWidget()  # 绘制窗口是个widget
        self.countPlot.setFixedSize(750, 200)
        self.countPlot.plotItem.showGrid(y=True, x=True, alpha=0.5)
        self.countPlot.setLabel('left', 'Counts')
        self.countPlot.setLabel('bottom', 'Time', units='s')
        self.curve = self.countPlot.plot(pen=(255, 0, 0))  # 绘图的线
        self.curve_average = self.countPlot.plot(pen=(0, 255, 0))

        #############################################
        self.count_layout.addWidget(self.countPlot, 0, 0, 1, 10)

        self.count_layout.addWidget(self.mean_count_lable, 1, 0)
        self.count_layout.addWidget(self.mean_count_edit, 1, 1)
        self.count_layout.addWidget(self.count_int_lable, 1, 3)
        self.count_layout.addWidget(self.count_int_Box, 1, 4)
        self.count_layout.addWidget(self.count_record_lable, 1, 6)
        self.count_layout.addWidget(self.clear_count_button, 1, 7)
        self.count_layout.addWidget(self.record_count_button, 1, 8)
        self.count_layout.addWidget(self.save_count_button, 1, 9)

        #############################################
        self.count_widget.setStyleSheet('''
                                                    QWidget#count_widget{
                                                        color:#232C51;
                                                        background:gray;
                                                        border-top:1px solid darkGray;
                                                        border-bottom:1px solid darkGray;
                                                        border-right:1px solid darkGray;
                                                        border-top-right-radius:10px;
                                                        border-bottom-right-radius:10px;
                                                    }
                                                    QLabel#right_lable{
                                                        color:red;
                                                        font-size:20px;
                                                        font-weight:700;
                                                        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                                                    }
                                                ''')

        ####################################################

    def ui_close(self):
        self.close()

    def _change_scale_function(self):
        if self.scale_comboBox.currentText()=='x0.001':
            self.x_psoition_adjust_Box.setSingleStep(0.001)
            self.y_psoition_adjust_Box.setSingleStep(0.001)
            self.z_psoition_adjust_Box.setSingleStep(0.001)
        elif self.scale_comboBox.currentText()=='x0.01':
            self.x_psoition_adjust_Box.setSingleStep(0.01)
            self.y_psoition_adjust_Box.setSingleStep(0.01)
            self.z_psoition_adjust_Box.setSingleStep(0.01)
        elif self.scale_comboBox.currentText()=='x0.1':
            self.x_psoition_adjust_Box.setSingleStep(0.1)
            self.y_psoition_adjust_Box.setSingleStep(0.1)
            self.z_psoition_adjust_Box.setSingleStep(0.1)

    def _connect_function(self):
        self.save_position_combobox_button.clicked.connect(self._save_position_combobox_function)
        self.load_position_combobox_button.clicked.connect(self._load_position_combobox_function)
        self.scale_comboBox.currentTextChanged.connect(self._change_scale_function)
    def _save_position_combobox_function(self):
        global position_dic
        name=input('请输入描述：')
        self.position_comboBox.addItem(name)
        position_dic['x position'].append(self.x_position_Box.value())
        position_dic['y position'].append(self.y_position_Box.value())
        position_dic['z position'].append(self.z_position_Box.value())
        position_dic['x step'].append(self.x_step_Box.value())
        position_dic['y step'].append(self.y_step_Box.value())
        position_dic['z step'].append(self.z_step_Box.value())
        position_dic['x range'].append(self.x_range_Box.value())
        position_dic['y range'].append(self.y_range_Box.value())
        position_dic['z range'].append(self.z_range_Box.value())

    def _load_position_combobox_function(self):
        global position_dic
        i=self.position_comboBox.currentIndex()
        self.x_position_Box.setValue(position_dic['x position'][i])
        self.y_position_Box.setValue(position_dic['y position'][i])
        self.z_position_Box.setValue(position_dic['z position'][i])
        self.x_step_Box.setValue(position_dic['x step'][i])
        self.y_step_Box.setValue(position_dic['y step'][i])
        self.z_step_Box.setValue(position_dic['z step'][i])
        self.x_range_Box.setValue(position_dic['x range'][i])
        self.y_range_Box.setValue(position_dic['y range'][i])
        self.z_range_Box.setValue(position_dic['z range'][i])
    # def test(self):
    #     print(gui_main.start_scan_button.isChecked())
    #     # gui_main.start_scan_button.toggle()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui_main = MainWindow()
    # gui_main.start_scan_button.clicked.connect(gui_main.test)
    gui_main.show()
    sys.exit(app.exec_())

