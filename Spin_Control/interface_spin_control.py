#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: interface_spin_control.py
@time: 2021/12/10 16:06
@desc:
'''
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction
from pyqtgraph.dockarea import *
import ButtonStyle
import numpy as np
import os,ctypes

class spin_control_MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None, QtCore.Qt.Widget)
        self.setWindowTitle('Spin Control')
        self.setFixedSize(2000, 1600)
        self.menu()
        self.Dock_Window()
        self.general_Winodw()
        self.control_sign='None' #是否测量OMDR
        self.setWindowIcon(QtGui.QIcon(QtCore.QDir.currentPath() + '/ico/spin_control.ico'))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self._connect_function()

    def _connect_function(self):
        self.c_lock_checkbox.clicked.connect(self._c_lock_action)
        self.scan_lock_checkbox.clicked.connect(self._scan_lock_action)

        self.thread_mode_checkbox.clicked.connect(self._thread_lock_mode_action)
        self.time_mode_checkbox.clicked.connect(self._time_lock_mode_action)

    def _c_lock_action(self):
        self.scan_lock_checkbox.setChecked(False)

    def _scan_lock_action(self):
        self.c_lock_checkbox.setChecked(False)

    def _thread_lock_mode_action(self):
        self.time_mode_checkbox.setChecked(False)

    def _time_lock_mode_action(self):
        self.thread_mode_checkbox.setChecked(False)

    def menu(self):
        # self.statusBar()
        self.menu=self.menuBar()
        self.opt_menu=self.menu.addMenu('Option')
        self.opt_menu.addSeparator()
        self.tool_menu = self.menu.addMenu('Tools')
        self.tool_menu.addSeparator()

        self.ODMR_action=QAction('ODMR',self)
        self.ODMR_action.triggered.connect(self.ODMR_layout_action)
        self.opt_menu.addAction(self.ODMR_action)

        self.Rabi_action = QAction('Rabi', self)
        self.Rabi_action.triggered.connect(self.Rabi_layout_action)
        self.opt_menu.addAction(self.Rabi_action)

        self.NRabi_action = QAction('NRabi', self)
        self.NRabi_action.triggered.connect(self.NRabi_layout_action)
        self.opt_menu.addAction(self.NRabi_action)

        self.Hahn_action = QAction('Hahn', self)
        self.Hahn_action.triggered.connect(self.Hahn_layout_action)
        self.opt_menu.addAction(self.Hahn_action)

        self.Ramsey_action = QAction('Ramsey', self)
        self.Ramsey_action.triggered.connect(self.Ramsey_layout_action)
        self.opt_menu.addAction(self.Ramsey_action)

        self.T1_action = QAction('T1', self)
        self.T1_action.triggered.connect(self.T1_layout_action)
        self.opt_menu.addAction(self.T1_action)

        self.nuRabi_action = QAction('nuRabi', self)
        self.nuRabi_action.triggered.connect(self.nuRabi_layout_action)
        self.opt_menu.addAction(self.nuRabi_action)

        self.ODNMR_action = QAction('ODNMR', self)
        self.ODNMR_action.triggered.connect(self.ODNMR_layout_action)
        self.opt_menu.addAction(self.ODNMR_action)

        # self.user_defiend_action = QAction('user_defined', self)
        # self.user_defiend_action.triggered.connect(self.user_defiend_action_action)
        # self.opt_menu.addAction(self.user_defiend_action)

        self.show_list_action = QAction('Show List', self)
        self.tool_menu.addAction(self.show_list_action)

    def Dock_Window(self):
        self.main_area = DockArea()
        self.setCentralWidget(self.main_area)
        #####整体框架,所有测量中这些变量名称保持一致！！！
        self.para_dock_widget=pg.LayoutWidget()
        self.para_dock_layout=Dock('parameters',size=(100,300),widget=self.para_dock_widget)
        self.para_dock_layout.setOrientation(o='horizontal',force=True)

        #############tab##########################
        self.c_pointlock_dock_widget = pg.LayoutWidget()
        self.scan_pointlock_dock_widget = pg.LayoutWidget()

        self.function_dock_widget = QtWidgets.QTabWidget()
        self.function_dock_layout = Dock('state', size=(100, 200), widget=self.function_dock_widget)
        self.function_dock_widget.addTab(self.c_pointlock_dock_widget, u'point lock')
        self.function_dock_widget.addTab(self.scan_pointlock_dock_widget, u'scan point lock')


        self.button_dock_widegt = pg.LayoutWidget()
        self.button_dock_layout = Dock('button', size=(100, 100), widget=self.button_dock_widegt)
        self.button_dock_layout.setOrientation(o='horizontal',force=True)

        self.plot_all_dock_layout = Dock('', size=(3000, 300))

    def layout_Window(self):
        self.main_area = DockArea()
        self.setCentralWidget(self.main_area)
        #####整体框架,所有测量中这些变量名称保持一致！！！
        self.para_dock_widget=pg.LayoutWidget()
        self.para_dock_layout=Dock('parameters',size=(100,300),widget=self.para_dock_widget)
        self.para_dock_layout.setOrientation(o='horizontal',force=True)

        self.plot_all_dock_layout = Dock('', size=(3000, 300))

        self.main_area.addDock(self.para_dock_layout, 'left')
        self.main_area.addDock(self.function_dock_layout, 'bottom', self.para_dock_layout)
        self.main_area.addDock(self.button_dock_layout, 'bottom', self.function_dock_layout)
        self.main_area.addDock(self.plot_all_dock_layout, 'right')

    #每次都不变的layout
    def general_Winodw(self):
        ###################label######################
        self.lock_uprate_label=QtWidgets.QLabel('uprate')
        self.lock_downrate_label=QtWidgets.QLabel('downrate')
        self.lock_step_label=QtWidgets.QLabel('step')
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

        #######state window
        #############################################################
        self.Text_Edit = QtWidgets.QTextBrowser()
        self.Text_Edit.setFixedSize(150, 200)


        ######################checkbox########################
        # self._group = QtWidgets.QButtonGroup()
        self.c_lock_checkbox = QtWidgets.QCheckBox('continue')
        self.scan_lock_checkbox = QtWidgets.QCheckBox('scan')
        # self._group.addButton(self.c_lock_checkbox)
        # self._group.addButton(self.scan_lock_checkbox)
        # self._group.setExclusive(True)

        self.c_pointlock_dock_widget.addWidget(self.lock_uprate_label, 0, 0, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_downrate_label, 1, 0, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_step_label, 2, 0, 1, 2)

        self.c_pointlock_dock_widget.addWidget(self.lock_uprate_box, 0, 2, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_downrate_box, 1, 2, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_step_box, 2, 2, 1, 2)

        self.c_pointlock_dock_widget.addWidget(self.c_lock_checkbox, 3, 0, 1, 1)
        self.c_pointlock_dock_widget.addWidget(self.scan_lock_checkbox, 3, 2, 1, 1)

        self.c_pointlock_dock_widget.addWidget(self.Text_Edit,0,4,4,3)

        #####scan_point_lock_window

        ###################label######################
        self.scan_lock_range_label = QtWidgets.QLabel('x/y range')
        self.scan_lock_step_label = QtWidgets.QLabel('x/y step')
        self.scan_lock_time_label = QtWidgets.QLabel('lock interval')
        ################box###########################
        self.scan_lock_range_box = pg.SpinBox(value=1,suffix='um',
                                          dec=False,
                                          decimals=6)
        self.scan_lock_range_box.setFixedSize(80, 30)

        self.scan_lock_step_box = pg.SpinBox(value=0.05, suffix='um',
                                              dec=False,
                                              decimals=6)
        self.scan_lock_step_box.setFixedSize(80, 30)

        self.scan_lock_time_box = pg.SpinBox(value=30, suffix='min',
                                             dec=False,
                                             decimals=6)
        self.scan_lock_time_box.setFixedSize(80, 30)
        ######################checkbox########################
        self.thread_mode_checkbox = QtWidgets.QCheckBox('thresh mode')
        self.thread_mode_checkbox.setChecked(True)
        self.time_mode_checkbox = QtWidgets.QCheckBox('time mode')

        self.scan_lock_image=pg.ImageView()
        self.scan_lock_image.resize(200,200)
        self.colors = [(139, 0, 255), (0, 0, 255), (0, 127, 255), (0, 255, 0), (255, 255, 0), (255, 165, 0),
                       (255, 0, 0)]
        self.color_map = pg.ColorMap(pos=np.linspace(0.0, 1.0, 7), color=self.colors)  # 将三种颜色作为节点，平滑过渡
        self.scan_lock_image.setColorMap(self.color_map)
        self.scan_lock_image.view.invertY(b=False)
        self.scan_lock_image.view.invertX(b=False)
        self.scan_lock_image.getHistogramWidget().setVisible(False)
        self.scan_lock_image.ui.menuBtn.setVisible(False)
        self.scan_lock_image.ui.roiBtn.setVisible(False)

        data = np.array([[1,2,3],[4,5,6],[7,8,9]])
        self.scan_lock_image.setImage(data)

        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_range_label,0,0,1,2)
        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_range_box,1,0,1,2)
        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_step_label,2,0,1,2)
        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_step_box,3,0,1,2)
        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_time_label, 4, 0, 1, 2)
        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_time_box, 5, 0, 1, 2)
        self.scan_pointlock_dock_widget.addWidget(self.thread_mode_checkbox, 6, 0, 1, 2)
        self.scan_pointlock_dock_widget.addWidget(self.time_mode_checkbox, 7, 0, 1, 2)


        self.scan_pointlock_dock_widget.addWidget(self.scan_lock_image,0,2,8,8)

        #####function_window
        ######################button#######################
        c = 60
        self.save_button = QtWidgets.QPushButton('Save')
        self.save_button.setFixedSize(c, 40)
        self.save_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.setFixedSize(c, 40)
        self.start_button.setCheckable(True)
        self.start_button.setChecked(False)
        self.start_button.setStyleSheet(ButtonStyle.conected)

        self.exit_button = QtWidgets.QPushButton('Exit')
        self.exit_button.setFixedSize(c, 40)
        self.exit_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.pause_button = QtWidgets.QPushButton('Pause')
        self.pause_button.setFixedSize(c, 40)
        self.pause_button.setCheckable(True)
        self.pause_button.setChecked(False)
        self.pause_button.setStyleSheet(ButtonStyle.conected)

        #############添加##########################
        self.button_dock_widegt.addWidget(self.save_button, 0, 2, 1, 1)
        self.button_dock_widegt.addWidget(self.start_button, 0, 6, 1, 1)
        self.button_dock_widegt.addWidget(self.pause_button, 0, 4, 1, 1)
        self.button_dock_widegt.addWidget(self.exit_button, 0, 0, 1, 1)


        # self.main_area.addDock(self.button_dock_layout, 'bottom')

    def ODMR_Window(self):
        #####para_window
        ###############label##################
        self.Freq_start_label=QtGui.QLabel('start frequency')
        self.Fre_stop_label = QtGui.QLabel('stop frequency')
        self.Fre_step_label = QtGui.QLabel('frequency step')

        self.MW_model_label = QtGui.QLabel('MW model')
        self.MW_Power_label = QtGui.QLabel('MW Power')

        self.cyc_label=QtGui.QLabel('cyc')

        ##############box######################
        self.Freq_start_box=pg.SpinBox(value=1300, suffix='MHz',
                                      dec=False,
                                      decimals=9,
                                      step=0.1, minStep=0.01,
                                      bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.Fre_stop_box = pg.SpinBox(value=1400, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Fre_stop_box.setFixedSize(100, 30)

        self.Fre_step_box = pg.SpinBox(value=1, suffix='MHz',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01,
                                       bounds=[0,50])
        self.Fre_step_box.setFixedSize(100, 30)


        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=1, minStep=0.01,
                                       bounds=[-60, -10])
        self.MW_Power_box.setFixedSize(100, 30)

        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Agilent', 'Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(100, 20)

        #####plot_window
        ######################plot_window#######################
        self.plot_1_dock_widget = pg.PlotWidget(title='single')
        self.plot_1_dock_widget.setLabel('left', 'Counts')
        self.plot_1_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_1_curve = self.plot_1_dock_widget.plot(pen=(255, 0, 0))

        self.plot_all_dock_widget = pg.PlotWidget(title='integration')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))


        #############添加##########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_label, 1, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 0, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 1, 2, 1, 2)

        self.para_dock_widget.addWidget(self.Freq_start_label, 2, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_stop_label, 3, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_step_label, 4, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Freq_start_box, 2, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_stop_box, 3, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_step_box, 4, 2, 1, 2)

        self.para_dock_widget.addWidget(self.cyc_label, 5, 0, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 5, 2, 1, 2)

        self.plot_all_dock_layout.addWidget(self.plot_1_dock_widget,0,0,4,6)
        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget,4,0,4,6)

    def Rabi_Window(self):
        ###############label##################
        self.MW_model_label = QtGui.QLabel('MW model')
        self.rabi_Freq_label = QtGui.QLabel('Rabi frequency')
        self.rabi_MW_Power_label = QtGui.QLabel('MW Power')

        self.rabi_detecting_time_label = QtGui.QLabel('Detecting time')
        self.rabi_start_label = QtGui.QLabel('Start')
        self.rabi_stop_label = QtGui.QLabel('Stop')
        self.rabi_points_label = QtGui.QLabel('Points')
        self.rabi_cyc_label = QtGui.QLabel('cyc')

        #############radio######################
        self.rabi_pumping_time_checkbox = QtWidgets.QCheckBox('Pumping time')

        ##############box######################
        self.Freq_start_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                        dec=False,
                                        decimals=4,
                                        step=0.1, minStep=0.01,
                                        bounds=[-60, 0])
        self.MW_Power_box.setFixedSize(100, 30)

        self.rabi_pumping_time_box = pg.SpinBox(value=3, suffix='us',
                                            dec=False,
                                            decimals=4)
        self.rabi_pumping_time_box.setFixedSize(100, 30)

        self.rabi_detecting_time_box = pg.SpinBox(value=550, suffix='ns',
                                                dec=False,
                                                decimals=4)
        self.rabi_detecting_time_box.setFixedSize(100, 30)

        self.rabi_start_time_box = pg.SpinBox(value=20, suffix='ns',
                                                  dec=False,
                                                  decimals=4)
        self.rabi_start_time_box.setFixedSize(100, 30)

        self.rabi_stop_time_box = pg.SpinBox(value=1020, suffix='ns',
                                              dec=False,
                                              decimals=4)
        self.rabi_stop_time_box.setFixedSize(100, 30)

        self.rabi_points_box = pg.SpinBox(value=80,
                                             dec=False,
                                             decimals=4)
        self.rabi_points_box.setFixedSize(100, 30)


        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Agilent', 'Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(100, 20)

        #####plot_window
        ######################plot_window#######################
        self.plot_all_dock_widget = pg.PlotWidget(title='Rabi')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))

        ############################添加#########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 0, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_Freq_label, 1, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Freq_start_box, 2, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_MW_Power_label, 1, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 2, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_pumping_time_checkbox, 3, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_pumping_time_box, 4, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_detecting_time_label, 3, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_detecting_time_box, 4, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_start_label, 5, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_start_time_box, 6, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_stop_label, 5, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_stop_time_box, 6, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_points_label, 7, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_points_box, 8, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_cyc_label, 7, 2, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 8, 2, 1, 2)

        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def NRabi_Window(self):
        ###############label##################
        self.MW_model_label = QtGui.QLabel('MW model')
        self.rabi_Freq_label = QtGui.QLabel('MW Rabi frequency')
        self.rabi_Freq_label_RF = QtGui.QLabel('RF frequency')
        self.rabi_MW_Power_label = QtGui.QLabel('MW Power')
        self.rabi_RF_Power_label = QtGui.QLabel('RF Power')
        self.rabi_MW_Length_label = QtGui.QLabel('MW Pi')

        self.rabi_detecting_time_label = QtGui.QLabel('Detecting time')
        self.rabi_start_label = QtGui.QLabel('Start')
        self.rabi_stop_label = QtGui.QLabel('Stop')
        self.rabi_points_label = QtGui.QLabel('Points')
        self.rabi_cyc_label = QtGui.QLabel('cyc')

        #############radio######################
        self.rabi_pumping_time_checkbox = QtWidgets.QCheckBox('Pumping time')

        ##############box######################
        self.MW_Freq_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.MW_Freq_box.setFixedSize(100, 30)

        self.Freq_start_box = pg.SpinBox(value=9, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                        dec=False,
                                        decimals=4,
                                        step=0.1, minStep=0.01,
                                        bounds=[-60, 0])
        self.MW_Power_box.setFixedSize(100, 30)

        self.RF_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01,
                                       bounds=[-60, 0])
        self.RF_Power_box.setFixedSize(100, 30)

        self.rabi_pumping_time_box = pg.SpinBox(value=3, suffix='us',
                                            dec=False,
                                            decimals=4)
        self.rabi_pumping_time_box.setFixedSize(100, 30)

        self.rabi_MW_Length_box = pg.SpinBox(value=1.0, suffix='us',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01)
        self.rabi_MW_Length_box.setFixedSize(100, 30)

        self.rabi_detecting_time_box = pg.SpinBox(value=550, suffix='ns',
                                                dec=False,
                                                decimals=4)
        self.rabi_detecting_time_box.setFixedSize(100, 30)

        self.rabi_start_time_box = pg.SpinBox(value=20, suffix='ns',
                                                  dec=False,
                                                  decimals=4)
        self.rabi_start_time_box.setFixedSize(100, 30)

        self.rabi_stop_time_box = pg.SpinBox(value=1020, suffix='ns',
                                              dec=False,
                                              decimals=4)
        self.rabi_stop_time_box.setFixedSize(100, 30)

        self.rabi_points_box = pg.SpinBox(value=80,
                                             dec=False,
                                             decimals=4)
        self.rabi_points_box.setFixedSize(100, 30)


        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(100, 20)

        #####plot_window
        ######################plot_window#######################
        self.plot_all_dock_widget = pg.PlotWidget(title='NRabi')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))

        ############################添加#########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 0, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_Freq_label, 1, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Freq_box, 2, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_MW_Power_label, 1, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 2, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_MW_Length_label, 3, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_MW_Length_box, 4, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_Freq_label_RF, 5, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Freq_start_box, 6, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_RF_Power_label, 5, 2, 1, 2)
        self.para_dock_widget.addWidget(self.RF_Power_box, 6, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_pumping_time_checkbox, 7, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_pumping_time_box, 8, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_detecting_time_label, 7, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_detecting_time_box, 8, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_start_label, 9, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_start_time_box, 10, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_stop_label, 9, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_stop_time_box, 10, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_points_label, 11, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_points_box, 12, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_cyc_label, 11, 2, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 12, 2, 1, 2)

        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def Hahn_Window(self):
        ###############label##################
        self.MW_model_label = QtGui.QLabel('MW model')
        self.hahn_pi_label = QtGui.QLabel('MW PI Pulse')
        self.hahn_Freq_label = QtGui.QLabel('Hahn frequency')
        self.hahn_MW_Power_label = QtGui.QLabel('MW Power')


        self.hahn_detecting_time_label = QtGui.QLabel('Detecting time')
        self.hahn_start_label = QtGui.QLabel('Start')
        self.hahn_stop_label = QtGui.QLabel('Stop')
        self.hahn_points_label = QtGui.QLabel('Points')
        self.hahn_cyc_label = QtGui.QLabel('cyc')

        ##############box######################
        self.hahn_pi_box = pg.SpinBox(value=1, suffix='us')
        self.hahn_pi_box.setFixedSize(100, 30)

        self.Freq_start_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                        dec=False,
                                        decimals=4,
                                        step=0.1, minStep=0.01,
                                        bounds=[-60, 0])
        self.MW_Power_box.setFixedSize(100, 30)

        self.hahn_pumping_time_box = pg.SpinBox(value=3, suffix='us',
                                            dec=False,
                                            decimals=4)
        self.hahn_pumping_time_box.setFixedSize(100, 30)

        self.hahn_detecting_time_box = pg.SpinBox(value=550, suffix='ns',
                                                dec=False,
                                                decimals=4)
        self.hahn_detecting_time_box.setFixedSize(100, 30)

        self.hahn_start_time_box = pg.SpinBox(value=0.02, suffix='us',
                                                  dec=False,
                                                  decimals=4)
        self.hahn_start_time_box.setFixedSize(100, 30)

        self.hahn_stop_time_box = pg.SpinBox(value=30.02, suffix='us',
                                              dec=False,
                                              decimals=4)
        self.hahn_stop_time_box.setFixedSize(100, 30)

        self.hahn_points_box = pg.SpinBox(value=80,
                                             dec=False,
                                             decimals=4)
        self.hahn_points_box.setFixedSize(100, 30)


        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Agilent', 'Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(80, 20)
        ############checkbox###########################
        self.hahn_pumping_time_checkbox = QtWidgets.QCheckBox('Pumping time')
        self.ref_checkbox = QtWidgets.QCheckBox('Ref')

        #####plot_window
        ######################plot_window#######################
        self.plot_all_dock_widget = pg.PlotWidget(title='Hahn')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))

        ############################添加#########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 1, 0, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_pi_label, 0, 2, 1, 2)
        self.para_dock_widget.addWidget(self.hahn_pi_box, 1, 2, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_Freq_label, 2, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Freq_start_box, 3, 0, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_MW_Power_label, 2, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 3, 2, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_pumping_time_checkbox, 4, 0, 1, 2)
        self.para_dock_widget.addWidget(self.hahn_pumping_time_box, 5, 0, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_detecting_time_label, 4, 2, 1, 2)
        self.para_dock_widget.addWidget(self.hahn_detecting_time_box, 5, 2, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_start_label, 6, 0, 1, 2)
        self.para_dock_widget.addWidget(self.hahn_start_time_box, 7, 0, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_stop_label, 6, 2, 1, 2)
        self.para_dock_widget.addWidget(self.hahn_stop_time_box, 7, 2, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_points_label, 8, 0, 1, 2)
        self.para_dock_widget.addWidget(self.hahn_points_box, 9, 0, 1, 2)

        self.para_dock_widget.addWidget(self.hahn_cyc_label, 8, 2, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 9, 2, 1, 1)

        self.para_dock_widget.addWidget(self.ref_checkbox,9,3,1,1)



        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def Ramsey_Window(self):
        ###############label##################
        self.MW_model_label = QtGui.QLabel('MW model')
        self.Ramsey_pi2_label = QtGui.QLabel('MW PI/2 Pulse')
        self.Ramsey_Freq_label = QtGui.QLabel('Hahn frequency')
        self.Ramsey_MW_Power_label = QtGui.QLabel('MW Power')

        self.Ramsey_detecting_time_label = QtGui.QLabel('Detecting time')
        self.Ramsey_start_label = QtGui.QLabel('Start')
        self.Ramsey_stop_label = QtGui.QLabel('Stop')
        self.Ramsey_points_label = QtGui.QLabel('Points')
        self.Ramsey_cyc_label = QtGui.QLabel('cyc')

        ##############box######################
        self.Ramsey_pi2_box = pg.SpinBox(value=1, suffix='us')
        self.Ramsey_pi2_box.setFixedSize(100, 30)

        self.Freq_start_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                        dec=False,
                                        decimals=4,
                                        step=0.1, minStep=0.01,
                                        bounds=[-60, 0])
        self.MW_Power_box.setFixedSize(100, 30)

        self.Ramsey_pumping_time_box = pg.SpinBox(value=3, suffix='us',
                                            dec=False,
                                            decimals=4)
        self.Ramsey_pumping_time_box.setFixedSize(100, 30)

        self.Ramsey_detecting_time_box = pg.SpinBox(value=550, suffix='ns',
                                                dec=False,
                                                decimals=4)
        self.Ramsey_detecting_time_box.setFixedSize(100, 30)

        self.Ramsey_start_time_box = pg.SpinBox(value=0.02, suffix='us',
                                                  dec=False,
                                                  decimals=4)
        self.Ramsey_start_time_box.setFixedSize(100, 30)

        self.Ramsey_stop_time_box = pg.SpinBox(value=30.02, suffix='us',
                                              dec=False,
                                              decimals=4)
        self.Ramsey_stop_time_box.setFixedSize(100, 30)

        self.Ramsey_points_box = pg.SpinBox(value=80,
                                             dec=False,
                                             decimals=4)
        self.Ramsey_points_box.setFixedSize(100, 30)


        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Agilent', 'Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(80, 20)
        ############checkbox###########################
        self.Ramsey_pumping_time_checkbox = QtWidgets.QCheckBox('Pumping time')
        self.ref_checkbox = QtWidgets.QCheckBox('Ref')

        #####plot_window
        ######################plot_window#######################
        self.plot_all_dock_widget = pg.PlotWidget(title='Ramsey')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))

        ############################添加#########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 1, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_pi2_label, 0, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Ramsey_pi2_box, 1, 2, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_Freq_label, 2, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Freq_start_box, 3, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_MW_Power_label, 2, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 3, 2, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_pumping_time_checkbox, 4, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Ramsey_pumping_time_box, 5, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_detecting_time_label, 4, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Ramsey_detecting_time_box, 5, 2, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_start_label, 6, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Ramsey_start_time_box, 7, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_stop_label, 6, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Ramsey_stop_time_box, 7, 2, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_points_label, 8, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Ramsey_points_box, 9, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Ramsey_cyc_label, 8, 2, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 9, 2, 1, 1)

        # self.para_dock_widget.addWidget(self.ref_checkbox,9,3,1,1)


        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def T1_Window(self):
        ###############label##################
        self.MW_model_label = QtGui.QLabel('MW model')
        self.T1_pi_label = QtGui.QLabel('MW PI Pulse')
        self.T1_Freq_label = QtGui.QLabel('T1 frequency')
        self.T1_MW_Power_label = QtGui.QLabel('MW Power')


        self.T1_detecting_time_label = QtGui.QLabel('Detecting time')
        self.T1_start_label = QtGui.QLabel('Start')
        self.T1_stop_label = QtGui.QLabel('Stop')
        self.T1_points_label = QtGui.QLabel('Points')
        self.T1_cyc_label = QtGui.QLabel('cyc')

        ##############box######################
        self.T1_pi_box = pg.SpinBox(value=1, suffix='us')
        self.T1_pi_box.setFixedSize(100, 30)

        self.Freq_start_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01,
                                       bounds=[-60, 0])
        self.MW_Power_box.setFixedSize(100, 30)

        self.T1_pumping_time_box = pg.SpinBox(value=3, suffix='us',
                                                dec=False,
                                                decimals=4)
        self.T1_pumping_time_box.setFixedSize(100, 30)

        self.T1_detecting_time_box = pg.SpinBox(value=550, suffix='ns',
                                                  dec=False,
                                                  decimals=4)
        self.T1_detecting_time_box.setFixedSize(100, 30)

        self.T1_start_time_box = pg.SpinBox(value=0.02, suffix='us',
                                              dec=False,
                                              decimals=4)
        self.T1_start_time_box.setFixedSize(100, 30)

        self.T1_stop_time_box = pg.SpinBox(value=300.02, suffix='us',
                                             dec=False,
                                             decimals=4)
        self.T1_stop_time_box.setFixedSize(100, 30)

        self.T1_points_box = pg.SpinBox(value=80,
                                          dec=False,
                                          decimals=4)
        self.T1_points_box.setFixedSize(100, 30)

        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Agilent', 'Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(80, 20)
        ############checkbox###########################
        self.T1_pumping_time_checkbox =  QtWidgets.QCheckBox('Pumping time')
        self.ref_checkbox = QtWidgets.QCheckBox('Ref')

        #####plot_window
        ######################plot_window#######################
        self.plot_all_dock_widget = pg.PlotWidget(title='T1')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))


        ############################添加#########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 1, 0, 1, 2)

        self.para_dock_widget.addWidget(self.T1_pi_label, 0, 2, 1, 2)
        self.para_dock_widget.addWidget(self.T1_pi_box, 1, 2, 1, 2)

        self.para_dock_widget.addWidget(self.T1_Freq_label, 2, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Freq_start_box, 3, 0, 1, 2)

        self.para_dock_widget.addWidget(self.T1_MW_Power_label, 2, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 3, 2, 1, 2)

        self.para_dock_widget.addWidget(self.T1_pumping_time_checkbox, 4, 0, 1, 2)
        self.para_dock_widget.addWidget(self.T1_pumping_time_box, 5, 0, 1, 2)

        self.para_dock_widget.addWidget(self.T1_detecting_time_label, 4, 2, 1, 2)
        self.para_dock_widget.addWidget(self.T1_detecting_time_box, 5, 2, 1, 2)

        self.para_dock_widget.addWidget(self.T1_start_label, 6, 0, 1, 2)
        self.para_dock_widget.addWidget(self.T1_start_time_box, 7, 0, 1, 2)

        self.para_dock_widget.addWidget(self.T1_stop_label, 6, 2, 1, 2)
        self.para_dock_widget.addWidget(self.T1_stop_time_box, 7, 2, 1, 2)

        self.para_dock_widget.addWidget(self.T1_points_label, 8, 0, 1, 2)
        self.para_dock_widget.addWidget(self.T1_points_box, 9, 0, 1, 2)

        self.para_dock_widget.addWidget(self.T1_cyc_label, 8, 2, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 9, 2, 1, 1)

        self.para_dock_widget.addWidget(self.ref_checkbox, 9, 3, 1, 1)

        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def nuRabi_Window(self):
        ###############label##################
        self.MW_model_label = QtGui.QLabel('MW model')
        self.rabi_MW_Freq_label = QtGui.QLabel('MW Rabi Frequency')
        self.rabi_MW_Power_label = QtGui.QLabel('MW Power')
        self.rabi_MW_Length_label = QtGui.QLabel('MW Pi Pulse Length')
        self.radio_Freq_label = QtGui.QLabel('Radio Frequency')
        self.radio_Power = QtGui.QLabel('Radio Power')

        self.rabi_detecting_time_label = QtGui.QLabel('Detecting time')
        self.rabi_start_label = QtGui.QLabel('Start')
        self.rabi_stop_label = QtGui.QLabel('Stop')
        self.rabi_points_label = QtGui.QLabel('Points')
        self.rabi_cyc_label = QtGui.QLabel('cyc')

        #############radio######################
        self.rabi_pumping_time_checkbox = QtWidgets.QCheckBox('Pumping time')

        ##############box######################
        self.Freq_start_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                        dec=False,
                                        decimals=4,
                                        step=0.1, minStep=0.01,
                                        bounds=[-60, 0])
        self.MW_Power_box.setFixedSize(100, 30)

        self.MW_Length_box = pg.SpinBox(value=1.0, suffix='us',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01)
        self.MW_Length_box.setFixedSize(100, 30)

        self.radio_Freq_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.radio_Freq_box.setFixedSize(100, 30)

        self.radio_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01,
                                       bounds=[-60, 0])
        self.radio_Power_box.setFixedSize(100, 30)

        self.rabi_pumping_time_box = pg.SpinBox(value=3, suffix='us',
                                            dec=False,
                                            decimals=4)
        self.rabi_pumping_time_box.setFixedSize(100, 30)

        self.rabi_detecting_time_box = pg.SpinBox(value=550, suffix='ns',
                                                dec=False,
                                                decimals=4)
        self.rabi_detecting_time_box.setFixedSize(100, 30)

        self.rabi_start_time_box = pg.SpinBox(value=20, suffix='ns',
                                                  dec=False,
                                                  decimals=4)
        self.rabi_start_time_box.setFixedSize(100, 30)

        self.rabi_stop_time_box = pg.SpinBox(value=1020, suffix='ns',
                                              dec=False,
                                              decimals=4)
        self.rabi_stop_time_box.setFixedSize(100, 30)

        self.rabi_points_box = pg.SpinBox(value=80,
                                             dec=False,
                                             decimals=4)
        self.rabi_points_box.setFixedSize(100, 30)


        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Zurich'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(100, 20)

        #####plot_window
        ######################plot_window#######################
        self.plot_all_dock_widget = pg.PlotWidget(title='nuRabi')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))

        ############################添加#########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 0, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_MW_Freq_label, 1, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Freq_start_box, 2, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_MW_Power_label, 1, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 2, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_MW_Length_label, 3, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Length_box, 4, 0, 1, 2)

        self.para_dock_widget.addWidget(self.radio_Freq_label, 5, 0, 1, 2)
        self.para_dock_widget.addWidget(self.radio_Freq_box, 6, 0, 1, 2)
        self.para_dock_widget.addWidget(self.radio_Power, 5, 2, 1, 2)
        self.para_dock_widget.addWidget(self.radio_Power_box, 6, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_pumping_time_checkbox, 7, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_pumping_time_box, 8, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_detecting_time_label, 7, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_detecting_time_box, 8, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_start_label, 9, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_start_time_box, 10, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_stop_label, 9, 2, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_stop_time_box, 10, 2, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_points_label, 11, 0, 1, 2)
        self.para_dock_widget.addWidget(self.rabi_points_box, 12, 0, 1, 2)

        self.para_dock_widget.addWidget(self.rabi_cyc_label, 11, 2, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 12, 2, 1, 2)

        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def ODNMR_Window(self):
        #####para_window
        ###############label##################
        self.Freq_start_label=QtGui.QLabel('start frequency')
        self.Fre_stop_label = QtGui.QLabel('stop frequency')
        self.Fre_step_label = QtGui.QLabel('frequency step')

        self.MW_model_label = QtGui.QLabel('MW model')
        self.MW_Power_label = QtGui.QLabel('MW Power')
        self.MW_Freq_label = QtGui.QLabel('MW Frequency')
        self.RF_Power_label = QtGui.QLabel('RF Power')

        self.MW_len_label = QtGui.QLabel('MW Length')
        self.RF_len_label = QtGui.QLabel('RF Length')

        self.cyc_label=QtGui.QLabel('cyc')

        ##############box######################
        self.Freq_start_box=pg.SpinBox(value=8, suffix='MHz',
                                      dec=False,
                                      decimals=9,
                                      step=0.1, minStep=0.01,
                                      bounds=[0, 2000])
        self.Freq_start_box.setFixedSize(100, 30)

        self.Fre_stop_box = pg.SpinBox(value=12, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.Fre_stop_box.setFixedSize(100, 30)

        self.Fre_step_box = pg.SpinBox(value=1, suffix='MHz',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01,
                                       bounds=[0,50])
        self.Fre_step_box.setFixedSize(100, 30)

        self.MW_Freq_box = pg.SpinBox(value=1300, suffix='MHz',
                                         dec=False,
                                         decimals=9,
                                         step=0.1, minStep=0.01,
                                         bounds=[0, 2000])
        self.MW_Freq_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=1, minStep=0.01,
                                       bounds=[-60, -10])
        self.MW_Power_box.setFixedSize(100, 30)

        self.RF_Power_box = pg.SpinBox(value=-30, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=1, minStep=0.01,
                                       bounds=[-60, -10])
        self.RF_Power_box.setFixedSize(100, 30)

        self.MW_len_box = pg.SpinBox(value=0.2, suffix='us',
                                       dec=False,
                                       decimals=4,
                                       step=1, minStep=0.01,
                                       bounds=[0, 1000])
        self.MW_len_box.setFixedSize(100, 30)

        self.RF_len_box = pg.SpinBox(value=1.0, suffix='us',
                                     dec=False,
                                     decimals=4,
                                     step=1, minStep=0.01,
                                     bounds=[0, 1000])
        self.RF_len_box.setFixedSize(100, 30)

        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Mini'])

        ###################lineedit###################
        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(100, 20)

        #####plot_window
        ######################plot_window#######################
        self.plot_1_dock_widget = pg.PlotWidget(title='single')
        self.plot_1_dock_widget.setLabel('left', 'Counts')
        self.plot_1_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_1_curve = self.plot_1_dock_widget.plot(pen=(255, 0, 0))

        self.plot_all_dock_widget = pg.PlotWidget(title='integration')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))


        #############添加##########################
        self.para_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_label, 1, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_model_comboBox, 0, 2, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Power_box, 1, 2, 1, 2)

        self.para_dock_widget.addWidget(self.MW_Freq_label, 2, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_Freq_box, 2, 2, 1, 2)
        self.para_dock_widget.addWidget(self.RF_Power_label, 3, 0, 1, 2)
        self.para_dock_widget.addWidget(self.RF_Power_box, 3, 2, 1, 2)

        self.para_dock_widget.addWidget(self.Freq_start_label, 4, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_stop_label, 5, 0, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_step_label, 6, 0, 1, 2)

        self.para_dock_widget.addWidget(self.Freq_start_box, 4, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_stop_box, 5, 2, 1, 2)
        self.para_dock_widget.addWidget(self.Fre_step_box, 6, 2, 1, 2)

        self.para_dock_widget.addWidget(self.MW_len_label, 7, 0, 1, 2)
        self.para_dock_widget.addWidget(self.MW_len_box, 7, 2, 1, 2)
        self.para_dock_widget.addWidget(self.RF_len_label, 8, 0, 1, 2)
        self.para_dock_widget.addWidget(self.RF_len_box, 8, 2, 1, 2)

        self.para_dock_widget.addWidget(self.cyc_label, 9, 0, 1, 2)
        self.para_dock_widget.addWidget(self.cyc_edit, 9, 2, 1, 2)

        self.plot_all_dock_layout.addWidget(self.plot_1_dock_widget,0,0,4,6)
        self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget,4,0,4,6)

    #使用layout布局方式
    # def user_defined_Window(self):
    #     self.v_layout = QtWidgets.QVBoxLayout()
    #     self.h_layout = QtWidgets.QHBoxLayout()
    #
    #     self.task_label = QtWidgets.QLabel('Task')
    #     self.task_combbox = QtWidgets.QComboBox()
    #     self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
    #     self.sizePolicy.setHorizontalStretch(1)
    #     self.sizePolicy.setVerticalStretch(0)
    #     self.task_combbox.setSizePolicy(self.sizePolicy)
    #
    #     self.save_task_button = QtWidgets.QPushButton('Save')
    #     self.load_tas_button = QtWidgets.QPushButton('Load')
    #     self.text_edit = QtWidgets.QPlainTextEdit()
    #
    #     self.h_layout.addWidget(self.task_label)
    #     self.h_layout.addWidget(self.task_combbox)
    #     self.h_layout.addWidget(self.save_task_button)
    #     self.h_layout.addWidget(self.load_tas_button)
    #     self.v_layout.addLayout(self.h_layout)
    #     self.v_layout.addWidget(self.text_edit)
    #
    #     self.task_widget = QtWidgets.QWidget()
    #     self.task_widget.setLayout(self.v_layout)
    #     self.para_dock_layout.addWidget(self.task_widget)
    #
    #     #####plot_window
    #     ######################plot_window#######################
    #     self.plot_all_dock_widget = pg.PlotWidget(title='Ramsey')
    #     self.plot_all_dock_widget.setLabel('left', 'Counts')
    #     self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
    #     self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))
    #
    #     self.plot_all_dock_layout.addWidget(self.plot_all_dock_widget)

    def _layout_delete(self):
        self.main_area.deleteLater()
        self.para_dock_widget.deleteLater()
        self.plot_all_dock_layout.deleteLater()


    def ODMR_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.ODMR_Window()
        self.control_sign = 'ODMR'
        self._Load_last_para()

    def Rabi_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.Rabi_Window()
        self.control_sign = 'Rabi'
        self._Load_last_para()

    def NRabi_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.NRabi_Window()
        self.control_sign = 'NRabi'
        self._Load_last_para()

    def Hahn_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.Hahn_Window()
        self.control_sign = 'Hahn'
        self._Load_last_para()

    def Ramsey_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.Ramsey_Window()
        self.control_sign = 'Ramsey'
        self._Load_last_para()

    def T1_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.T1_Window()
        self.control_sign = 'T1'
        self._Load_last_para()

    def nuRabi_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.nuRabi_Window()
        self.control_sign = 'nuRabi'
        self._Load_last_para()

    def ODNMR_layout_action(self):
        self._Save_last_para()
        # 删除上一次的界面，为新界面的添加做准备
        self._layout_delete()
        self.layout_Window()
        self.ODNMR_Window()
        self.control_sign = 'ODNMR'
        self._Load_last_para()

    # def user_defiend_action_action(self):
    #     self._Save_last_para()
    #     self._layout_delete()
    #     self.layout_Window()
    #     self.user_defined_Window()
    #     self.control_sign = 'User_defined'


    def _Save_last_para(self):
        if self.control_sign == 'ODMR':
            last_ODMR_para = {'MW Power':self.MW_Power_box.value(),
                              'Start F':self.Freq_start_box.value(),
                              'Stop F':self.Fre_stop_box.value(),
                              'Step F':self.Fre_step_box.value(),
                              'Lock uprate':self.lock_uprate_box.value(),
                              'Lock downrate':self.lock_downrate_box.value(),
                              'Lock step':self.lock_step_box.value(),
                              'Lock scan step':self.scan_lock_step_box.value(),
                              'Lock scan range':self.scan_lock_range_box.value(),
                              'Lock scan interval':self.scan_lock_time_box.value(),
                              'MW type':self.MW_model_comboBox.currentIndex(),
                         }
            np.save(os.getcwd() + '\\history_data\\last_ODMR_para.npy', last_ODMR_para)
            print('last ODMR paras saved')
        elif self.control_sign == 'Rabi':
            last_Rabi_para = {'Rabi Freq': self.Freq_start_box.value(),
                              'MW Power': self.MW_Power_box.value(),
                              'Pumping time': self.rabi_pumping_time_box.value(),
                              'Detecting time': self.rabi_detecting_time_box.value(),
                              'Start time': self.rabi_start_time_box.value(),
                              'Stop time': self.rabi_stop_time_box.value(),
                              'Points': self.rabi_points_box.value(),
                              'Lock uprate': self.lock_uprate_box.value(),
                              'Lock downrate': self.lock_downrate_box.value(),
                              'Lock step': self.lock_step_box.value(),
                              'Lock scan step': self.scan_lock_step_box.value(),
                              'Lock scan range': self.scan_lock_range_box.value(),
                              'Lock scan interval': self.scan_lock_time_box.value(),
                              'MW type': self.MW_model_comboBox.currentIndex(),
                         }
            np.save(os.getcwd() + '\\history_data\\last_Rabi_para.npy', last_Rabi_para)
            print('last Rabi paras saved')
        elif self.control_sign == 'NRabi':
            last_NRabi_para = {'MW Rabi Freq': self.MW_Freq_box.value(),
                                  'MW Power': self.MW_Power_box.value(),
                                  'MW Pi Pulse Length': self.rabi_MW_Length_box.value(),
                                  'Radio Frequency': self.Freq_start_box.value(),
                                  'Radio Power': self.RF_Power_box.value(),
                                  'Pumping time': self.rabi_pumping_time_box.value(),
                                  'Detecting time': self.rabi_detecting_time_box.value(),
                                  'Start time': self.rabi_start_time_box.value(),
                                  'Stop time': self.rabi_stop_time_box.value(),
                                  'Points': self.rabi_points_box.value(),
                                  'Lock uprate': self.lock_uprate_box.value(),
                                  'Lock downrate': self.lock_downrate_box.value(),
                                  'Lock step': self.lock_step_box.value(),
                                  'Lock scan step': self.scan_lock_step_box.value(),
                                  'Lock scan range': self.scan_lock_range_box.value(),
                                  'Lock scan interval': self.scan_lock_time_box.value(),
                                  'MW type': self.MW_model_comboBox.currentIndex(),
                             }
            np.save(os.getcwd() + '\\history_data\\last_NRabi_para.npy', last_NRabi_para)
            print('last NRabi paras saved')
        elif self.control_sign == 'Hahn':
            last_Hahn_para = {'Pi pulse':self.hahn_pi_box.value(),
                              'Hahn Freq': self.Freq_start_box.value(),
                              'MW Power': self.MW_Power_box.value(),
                              'Pumping time': self.hahn_pumping_time_box.value(),
                              'Detecting time': self.hahn_detecting_time_box.value(),
                              'Start time': self.hahn_start_time_box.value(),
                              'Stop time': self.hahn_stop_time_box.value(),
                              'Points': self.hahn_points_box.value(),
                              'Lock uprate': self.lock_uprate_box.value(),
                              'Lock downrate': self.lock_downrate_box.value(),
                              'Lock step': self.lock_step_box.value(),
                              'Lock scan step': self.scan_lock_step_box.value(),
                              'Lock scan range': self.scan_lock_range_box.value(),
                              'Lock scan interval': self.scan_lock_time_box.value(),
                              'MW type': self.MW_model_comboBox.currentIndex(),
                         }
            np.save(os.getcwd() + '\\history_data\\last_Hahn_para.npy', last_Hahn_para)
            print('last Hahn paras saved')
        elif self.control_sign == 'Ramsey':
            last_Ramsey_para = {'Pi/2 pulse':self.Ramsey_pi2_box.value(),
                              'Ramsey Freq': self.Freq_start_box.value(),
                              'MW Power': self.MW_Power_box.value(),
                              'Pumping time': self.Ramsey_pumping_time_box.value(),
                              'Detecting time': self.Ramsey_detecting_time_box.value(),
                              'Start time': self.Ramsey_start_time_box.value(),
                              'Stop time': self.Ramsey_stop_time_box.value(),
                              'Points': self.Ramsey_points_box.value(),
                              'Lock uprate': self.lock_uprate_box.value(),
                              'Lock downrate': self.lock_downrate_box.value(),
                              'Lock step': self.lock_step_box.value(),
                                'Lock scan step': self.scan_lock_step_box.value(),
                                'Lock scan range': self.scan_lock_range_box.value(),
                                'Lock scan interval': self.scan_lock_time_box.value(),
                              'MW type': self.MW_model_comboBox.currentIndex(),
                         }
            np.save(os.getcwd() + '\\history_data\\last_Ramsey_para.npy', last_Ramsey_para)
            print('last Ramsey paras saved')
        elif self.control_sign == 'T1':
            last_T1_para = {'Pi pulse':self.T1_pi_box.value(),
                              'T1 Freq': self.Freq_start_box.value(),
                              'MW Power': self.MW_Power_box.value(),
                              'Pumping time': self.T1_pumping_time_box.value(),
                              'Detecting time': self.T1_detecting_time_box.value(),
                              'Start time': self.T1_start_time_box.value(),
                              'Stop time': self.T1_stop_time_box.value(),
                              'Points': self.T1_points_box.value(),
                              'Lock uprate': self.lock_uprate_box.value(),
                              'Lock downrate': self.lock_downrate_box.value(),
                              'Lock step': self.lock_step_box.value(),
                            'Lock scan step': self.scan_lock_step_box.value(),
                            'Lock scan range': self.scan_lock_range_box.value(),
                            'Lock scan interval': self.scan_lock_time_box.value(),
                              'MW type': self.MW_model_comboBox.currentIndex(),
                         }
            np.save(os.getcwd() + '\\history_data\\last_T1_para.npy', last_T1_para)
            print('last Hahn paras saved')
        elif self.control_sign == 'nuRabi':
            last_nuRabi_para = {'MW Rabi Freq': self.Freq_start_box.value(),
                                  'MW Power': self.MW_Power_box.value(),
                                  'MW Pi Pulse Length': self.MW_Length_box.value(),
                                  'Radio Frequency': self.radio_Freq_box.value(),
                                  'Radio Power': self.radio_Power_box.value(),
                                  'Pumping time': self.rabi_pumping_time_box.value(),
                                  'Detecting time': self.rabi_detecting_time_box.value(),
                                  'Start time': self.rabi_start_time_box.value(),
                                  'Stop time': self.rabi_stop_time_box.value(),
                                  'Points': self.rabi_points_box.value(),
                                  'Lock uprate': self.lock_uprate_box.value(),
                                  'Lock downrate': self.lock_downrate_box.value(),
                                  'Lock step': self.lock_step_box.value(),
                                  'Lock scan step': self.scan_lock_step_box.value(),
                                  'Lock scan range': self.scan_lock_range_box.value(),
                                  'Lock scan interval': self.scan_lock_time_box.value(),
                                  'MW type': self.MW_model_comboBox.currentIndex(),
                             }
            np.save(os.getcwd() + '\\history_data\\last_nuRabi_para.npy', last_nuRabi_para)
            print('last nuRabi paras saved')
        elif self.control_sign == 'ODNMR':
            last_ODNMR_para = {'MW Power':self.MW_Power_box.value(),
                              'MW F':self.MW_Freq_box.value(),
                              'RF Power':self.RF_Power_box.value(),
                              'Start F':self.Freq_start_box.value(),
                              'Stop F':self.Fre_stop_box.value(),
                              'Step F':self.Fre_step_box.value(),
                              'Lock uprate':self.lock_uprate_box.value(),
                              'Lock downrate':self.lock_downrate_box.value(),
                              'Lock step':self.lock_step_box.value(),
                              'Lock scan step':self.scan_lock_step_box.value(),
                              'Lock scan range':self.scan_lock_range_box.value(),
                              'Lock scan interval':self.scan_lock_time_box.value(),
                              'MW type':self.MW_model_comboBox.currentIndex(),
                         }
            np.save(os.getcwd() + '\\history_data\\last_ODNMR_para.npy', last_ODNMR_para)
            print('last ODNMR paras saved')
        else:
            print('no last para data saved')


    def _Load_last_para(self):
        try:
            if self.control_sign == 'ODMR':
                last_data = np.load(os.getcwd()+'\\history_data\\last_ODMR_para.npy', allow_pickle=True).item()
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.Freq_start_box.setValue(last_data['Start F'])
                self.Fre_stop_box.setValue(last_data['Stop F'])
                self.Fre_step_box.setValue(last_data['Step F'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('ODMR last para loaded')
            elif self.control_sign == 'Rabi':
                last_data = np.load(os.getcwd() + '\\history_data\\last_Rabi_para.npy', allow_pickle=True).item()
                self.Freq_start_box.setValue(last_data['Rabi Freq'])
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.rabi_pumping_time_box.setValue(last_data['Pumping time'])
                self.rabi_detecting_time_box.setValue(last_data['Detecting time'])
                self.rabi_start_time_box.setValue(last_data['Start time'])
                self.rabi_stop_time_box.setValue(last_data['Stop time'])
                self.rabi_points_box.setValue(last_data['Points'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('Rabi last para loaded')
            elif self.control_sign == 'NRabi':
                last_data = np.load(os.getcwd() + '\\history_data\\last_NRabi_para.npy', allow_pickle=True).item()
                self.MW_Freq_box.setValue(last_data['MW Rabi Freq'])
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.rabi_MW_Length_box.setValue(last_data['MW Pi Pulse Length'])
                self.Freq_start_box.setValue(last_data['Radio Frequency'])
                self.RF_Power_box.setValue(last_data['Radio Power'])
                self.rabi_pumping_time_box.setValue(last_data['Pumping time'])
                self.rabi_detecting_time_box.setValue(last_data['Detecting time'])
                self.rabi_start_time_box.setValue(last_data['Start time'])
                self.rabi_stop_time_box.setValue(last_data['Stop time'])
                self.rabi_points_box.setValue(last_data['Points'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('NRabi last para loaded')
            elif self.control_sign == 'Hahn':
                last_data = np.load(os.getcwd() + '\\history_data\\last_Hahn_para.npy', allow_pickle=True).item()
                self.hahn_pi_box.setValue(last_data['Pi pulse'])
                self.Freq_start_box.setValue(last_data['Hahn Freq'])
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.hahn_pumping_time_box.setValue(last_data['Pumping time'])
                self.hahn_detecting_time_box.setValue(last_data['Detecting time'])
                self.hahn_start_time_box.setValue(last_data['Start time'])
                self.hahn_stop_time_box.setValue(last_data['Stop time'])
                self.hahn_points_box.setValue(last_data['Points'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('Hahn last para loaded')
            elif self.control_sign == 'Ramsey':
                last_data = np.load(os.getcwd() + '\\history_data\\last_Ramsey_para.npy', allow_pickle=True).item()
                self.Ramsey_pi2_box.setValue(last_data['Pi/2 pulse'])
                self.Freq_start_box.setValue(last_data['Ramsey Freq'])
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.Ramsey_pumping_time_box.setValue(last_data['Pumping time'])
                self.Ramsey_detecting_time_box.setValue(last_data['Detecting time'])
                self.Ramsey_start_time_box.setValue(last_data['Start time'])
                self.Ramsey_stop_time_box.setValue(last_data['Stop time'])
                self.Ramsey_points_box.setValue(last_data['Points'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('Ramsey last para loaded')
            elif self.control_sign == 'T1':
                last_data = np.load(os.getcwd() + '\\history_data\\last_T1_para.npy', allow_pickle=True).item()
                self.T1_pi_box.setValue(last_data['Pi pulse'])
                self.Freq_start_box.setValue(last_data['T1 Freq'])
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.T1_pumping_time_box.setValue(last_data['Pumping time'])
                self.T1_detecting_time_box.setValue(last_data['Detecting time'])
                self.T1_start_time_box.setValue(last_data['Start time'])
                self.T1_stop_time_box.setValue(last_data['Stop time'])
                self.T1_points_box.setValue(last_data['Points'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('T1 last para loaded')
            elif self.control_sign == 'nuRabi':
                last_data = np.load(os.getcwd() + '\\history_data\\last_nuRabi_para.npy', allow_pickle=True).item()
                self.Freq_start_box.setValue(last_data['MW Rabi Freq'])
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.MW_Length_box.setValue(last_data['MW Pi Pulse Length'])
                self.radio_Freq_box.setValue(last_data['Radio Frequency'])
                self.radio_Power_box.setValue(last_data['Radio Power'])
                self.rabi_pumping_time_box.setValue(last_data['Pumping time'])
                self.rabi_detecting_time_box.setValue(last_data['Detecting time'])
                self.rabi_start_time_box.setValue(last_data['Start time'])
                self.rabi_stop_time_box.setValue(last_data['Stop time'])
                self.rabi_points_box.setValue(last_data['Points'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('nuRabi last para loaded')
            elif self.control_sign == 'ODNMR':
                last_data = np.load(os.getcwd()+'\\history_data\\last_ODNMR_para.npy', allow_pickle=True).item()
                self.MW_Power_box.setValue(last_data['MW Power'])
                self.MW_Freq_box.setValue(last_data['MW F'])
                self.RF_Power_box.setValue(last_data['RF Power'])
                self.Freq_start_box.setValue(last_data['Start F'])
                self.Fre_stop_box.setValue(last_data['Stop F'])
                self.Fre_step_box.setValue(last_data['Step F'])
                self.lock_uprate_box.setValue(last_data['Lock uprate'])
                self.lock_downrate_box.setValue(last_data['Lock downrate'])
                self.lock_step_box.setValue(last_data['Lock step'])
                self.scan_lock_step_box.setValue(last_data['Lock scan step'])
                self.scan_lock_range_box.setValue(last_data['Lock scan range'])
                self.scan_lock_time_box.setValue(last_data['Lock scan interval'])
                self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
                print('ODNMR last para loaded')

        except:
            print('last data is not exist')

    def ui_close(self):
        self._Save_last_para()
        self.close()


if __name__ == '__main__':
    app = QtGui.QApplication([])
    # win = QtGui.QMainWindow()
    from pyqtgraph import exporters

    aa = spin_control_MainWindow()

    # ex_all = exporters.ImageExporter(aa.scene())
    # ex_all.export(fileName='D:/test.jpg')
    aa.show()
    app.exec_()
