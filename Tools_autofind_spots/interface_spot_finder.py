#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: interface_find_spots.py
@time: 2022/4/16/0016 11:29:03
@desc:
'''
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from pyqtgraph.dockarea import *
import sys
import pyqtgraph as pg
import os,ctypes
import numpy as np
import LableStyle, ButtonStyle
from PyQt5.QtWidgets import QAction,QStatusBar,QMenuBar
from PyQt5.QtGui import QPixmap
from PIL import Image

class Spot_Finder_MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None, QtCore.Qt.Widget)
        self._setup_layout()
        self._setupWinodw()
        self.setWindowTitle('Spots Finder')
        self._Load_last_para()
        # self._function_connect()
        self.setWindowIcon(QtGui.QIcon(QtCore.QDir.currentPath() + '/ico/auto_find_spots.ico'))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def _setup_layout(self):
        self.resize(1500, 400)
        self.main_area = DockArea()

        self.para_dock_widget = pg.LayoutWidget()
        self.mode_dock_widget = pg.LayoutWidget()
        self.advanced_para_dock_widget = pg.LayoutWidget()


        self.para_tab_widget = QtWidgets.QTabWidget()
        self.para_tab_widget.addTab(self.para_dock_widget,u'scan para')
        self.para_tab_widget.addTab(self.mode_dock_widget, u'scan mode')
        self.para_tab_widget.addTab(self.advanced_para_dock_widget, u'advanced para')
        self.para_tab_layout = Dock('scanning parameters', size=(60, 200), widget=self.para_tab_widget)


        self.setting_z_dock_widget = pg.LayoutWidget()
        self.setting_z_dock_layout = Dock('setting z para', size=(35, 100), widget=self.setting_z_dock_widget)

        self.setting_xy_dock_widget = pg.LayoutWidget()
        self.setting_xy_dock_layout = Dock('setting xy para', size=(35, 100), widget=self.setting_xy_dock_widget)

        self.setting_path_dock_widget = pg.LayoutWidget()
        self.setting_path_dock_layout = Dock('setting path', size=(60, 200), widget=self.setting_path_dock_widget)

        self.optimal_dock_widget = pg.LayoutWidget()
        self.optimal_dock_layout = Dock('optimal para', size=(60, 100), widget=self.optimal_dock_widget)

        self.button_dock_widget = pg.LayoutWidget()
        self.button_dock_layout = Dock('button', size=(60, 100), widget=self.button_dock_widget)

        self.position_dock_widget = pg.LayoutWidget()
        self.position_dock_layout = Dock('PI position', size=(600, 50), widget=self.position_dock_widget)

        self.image_dock_widget = pg.LayoutWidget()
        self.image_dock_layout = Dock('image show', size=(800, 450), widget=self.image_dock_widget)

        self.MW_dock_widget = pg.LayoutWidget()
        self.MW_dock_layout = Dock('MW', size=(100, 200), widget=self.MW_dock_widget)

        self.lock_dock_widget = pg.LayoutWidget()
        self.lock_dock_layout = Dock('lock', size=(100, 300), widget=self.lock_dock_widget)

        self.spin_dock_widget = pg.LayoutWidget()
        self.spin_dock_layout = Dock('spin control', size=(1200, 500), widget=self.spin_dock_widget)

        self.main_area.addDock(self.para_tab_layout, 'left')
        self.main_area.addDock(self.setting_z_dock_layout, 'bottom', self.para_tab_layout)
        self.main_area.addDock(self.setting_xy_dock_layout, 'right', self.setting_z_dock_layout)
        self.main_area.addDock(self.setting_path_dock_layout, 'bottom')
        self.main_area.addDock(self.optimal_dock_layout, 'bottom',self.setting_path_dock_layout)
        self.main_area.addDock(self.button_dock_layout, 'bottom',self.optimal_dock_layout)
        self.main_area.addDock(self.position_dock_layout, 'right')
        self.main_area.addDock(self.image_dock_layout, 'bottom', self.position_dock_layout)
        self.main_area.addDock(self.MW_dock_layout,'right')
        self.main_area.addDock(self.lock_dock_layout, 'bottom',self.MW_dock_layout)
        self.main_area.addDock(self.spin_dock_layout, 'right')
        self.setCentralWidget(self.main_area)


    def _setupWinodw(self):
        self._para_Window()
        self._scan_mode_Winodw()
        self._advanced_para_Window()
        self._setting_z_Window()
        self._setting_xy_Window()
        self._setting_path_Window()
        self._optimal_Window()
        self._button_Window()
        self._position_Window()
        self._image_Window()
        self._lock_Window()
        self._MW_Window()
        self._spin_Window()


    def _para_Window(self):
        #################label#####################
        self.scan_start_x_label = QtWidgets.QLabel('Scan Start x')
        self.scan_stop_x_label = QtWidgets.QLabel('Scan Stop x')
        self.scan_start_y_label = QtWidgets.QLabel('Scan Start y')
        self.scan_stop_y_label = QtWidgets.QLabel('Scan Stop y')
        self.scan_position_z_label = QtWidgets.QLabel('Scan Position z')
        self.scan_stop_z_label = QtWidgets.QLabel('Scan Stop z')
        self.scan_range_x_label= QtWidgets.QLabel('Scan Range x')
        self.scan_range_y_label = QtWidgets.QLabel('Scan Range y')
        self.scan_range_z_label = QtWidgets.QLabel('Scan Range z')
        self.scan_step_x_label = QtWidgets.QLabel('Scan Step x')
        self.scan_step_y_label = QtWidgets.QLabel('Scan Step y')
        self.scan_step_z_label = QtWidgets.QLabel('Scan Step z')


        ##################spinbox###################
        L = 80
        W = 20
        self.scan_start_x_box = pg.SpinBox(value=0, suffix='um',
                                             dec=True,
                                             bounds=[0, 100])
        self.scan_start_x_box.setFixedSize(L, W)

        self.scan_stop_x_box = pg.SpinBox(value=100, suffix='um',
                                         dec=True,
                                        bounds=[0, 100])
        self.scan_stop_x_box.setFixedSize(L, W)

        self.scan_start_y_box = pg.SpinBox(value=0, suffix='um',
                                           dec=True,
                                           bounds=[0, 100])
        self.scan_start_y_box.setFixedSize(L, W)

        self.scan_stop_y_box = pg.SpinBox(value=100, suffix='um',
                                          dec=True,
                                          bounds=[0, 100])
        self.scan_stop_y_box.setFixedSize(L, W)

        self.scan_position_z_box = pg.SpinBox(value=50, suffix='um',
                                           dec=True,
                                           bounds=[0, 100])
        self.scan_position_z_box.setFixedSize(L, W)

        self.scan_stop_z_box = pg.SpinBox(value=100, suffix='um',
                                          dec=True,
                                          bounds=[0, 100])
        self.scan_stop_z_box.setFixedSize(L, W)


        self.scan_range_x_box = pg.SpinBox(value=20, suffix='um',
                                           dec=True,
                                           bounds=[0, 100])
        self.scan_range_x_box.setFixedSize(L, W)

        self.scan_range_y_box = pg.SpinBox(value=20, suffix='um',
                                           dec=True,
                                           bounds=[0, 100])
        self.scan_range_y_box.setFixedSize(L, W)

        self.scan_range_z_box = pg.SpinBox(value=100, suffix='um',
                                           dec=True,
                                           bounds=[0, 100])
        self.scan_range_z_box.setFixedSize(L, W)

        self.scan_step_x_box = pg.SpinBox(value=0.2, suffix='um',
                                          dec=True,
                                          bounds=[0, 100])
        self.scan_step_x_box.setFixedSize(L, W)

        self.scan_step_y_box = pg.SpinBox(value=0.2, suffix='um',
                                          dec=True,
                                          bounds=[0, 100])
        self.scan_step_y_box.setFixedSize(L, W)

        self.scan_step_z_box = pg.SpinBox(value=1, suffix='um',
                                          dec=True,
                                          bounds=[0, 100])
        self.scan_step_z_box.setFixedSize(L, W)
        #######################添加######################

        self.para_dock_widget.addWidget(self.scan_start_x_label,0,0,1,1)
        self.para_dock_widget.addWidget(self.scan_start_y_label, 0, 1, 1, 1)
        self.para_dock_widget.addWidget(self.scan_position_z_label, 0, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_start_x_box, 1, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_start_y_box, 1, 1, 1, 1)
        self.para_dock_widget.addWidget(self.scan_position_z_box, 1, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_stop_x_label, 2, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_stop_y_label, 2, 1, 1, 1)
        # self.para_dock_widget.addWidget(self.scan_stop_z_label, 2, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_stop_x_box, 3, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_stop_y_box, 3, 1, 1, 1)
        # self.para_dock_widget.addWidget(self.scan_stop_z_box, 3, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_range_x_label, 4, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_range_y_label, 4, 1, 1, 1)
        self.para_dock_widget.addWidget(self.scan_range_z_label, 4, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_range_x_box, 5, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_range_y_box, 5, 1, 1, 1)
        self.para_dock_widget.addWidget(self.scan_range_z_box, 5, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_step_x_label, 6, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_step_y_label, 6, 1, 1, 1)
        self.para_dock_widget.addWidget(self.scan_step_z_label, 6, 2, 1, 1)

        self.para_dock_widget.addWidget(self.scan_step_x_box, 7, 0, 1, 1)
        self.para_dock_widget.addWidget(self.scan_step_y_box, 7, 1, 1, 1)
        self.para_dock_widget.addWidget(self.scan_step_z_box, 7, 2, 1, 1)



    def _scan_mode_Winodw(self):
        #################label#####################
        self.z_bias_label = QtWidgets.QLabel('Z bias')
        self.z_step_label = QtWidgets.QLabel('Z step')
        self.z_start_label = QtWidgets.QLabel('Z start')
        self.z_stop_label = QtWidgets.QLabel('Z stop')

        #################radio_button##############
        self.s_z_mode_radio_button = QtWidgets.QRadioButton('Single z')
        self.s_z_mode_radio_button.setChecked(True)
        self.m_z_mode_radio_button = QtWidgets.QRadioButton('Multiple z')
        self.e_z_mode_radio_button = QtWidgets.QRadioButton('Every z')
        ##################spinbox###################
        self.z_bias_box = pg.SpinBox(value=3.5,suffix='um',
                                            dec=True)
        self.z_bias_box.setFixedSize(120, 30)

        self.z_step_box = pg.SpinBox(value=2,suffix='um',
                                     dec=True)
        self.z_step_box.setFixedSize(120, 30)

        self.z_start_box = pg.SpinBox(value=0,suffix='um',
                                              dec=True)
        self.z_start_box.setFixedSize(120, 30)

        self.z_stop_box = pg.SpinBox(value=100, suffix='um',
                                      dec=True)
        self.z_stop_box.setFixedSize(120, 30)
        #######################添加######################

        self.mode_dock_widget.addWidget(self.s_z_mode_radio_button, 0, 0, 1, 1)
        self.mode_dock_widget.addWidget(self.e_z_mode_radio_button, 0, 1, 1, 1)
        self.mode_dock_widget.addWidget(self.m_z_mode_radio_button, 0, 2, 1, 1)

        self.mode_dock_widget.addWidget(self.z_bias_label, 1, 0, 1, 2)
        self.mode_dock_widget.addWidget(self.z_step_label, 1, 2, 1, 2)

        self.mode_dock_widget.addWidget(self.z_bias_box, 2, 0, 1, 2)
        self.mode_dock_widget.addWidget(self.z_step_box, 2, 2, 1, 2)

        self.mode_dock_widget.addWidget(self.z_start_label, 3, 0, 1, 2)
        self.mode_dock_widget.addWidget(self.z_stop_label, 3, 2, 1, 2)

        self.mode_dock_widget.addWidget(self.z_start_box, 4, 0, 1, 2)
        self.mode_dock_widget.addWidget(self.z_stop_box, 4, 2, 1, 2)

    def _advanced_para_Window(self):
        #################label#####################
        self.numP_min_xy_label = QtWidgets.QLabel('numP min xy')
        self.numP_max_xy_label = QtWidgets.QLabel('numP max xy')
        self.numP_min_z_label = QtWidgets.QLabel('num P min z')

        ##################spinbox###################
        self.numP_min_xy_box = pg.SpinBox(value=100,
                                            dec=True)
        self.numP_min_xy_box.setFixedSize(120, 30)

        self.numP_max_xy_box = pg.SpinBox(value=500,
                                              dec=True)
        self.numP_max_xy_box.setFixedSize(120, 30)

        self.numP_min_z_box = pg.SpinBox(value=5000,
                                          dec=True)
        self.numP_min_z_box.setFixedSize(120, 30)

        #######################添加######################

        self.advanced_para_dock_widget.addWidget(self.numP_min_xy_label, 0, 0, 1, 2)
        self.advanced_para_dock_widget.addWidget(self.numP_max_xy_label, 0, 2, 1, 2)

        self.advanced_para_dock_widget.addWidget(self.numP_min_xy_box, 1, 0, 1, 2)
        self.advanced_para_dock_widget.addWidget(self.numP_max_xy_box, 1, 2, 1, 2)

        self.advanced_para_dock_widget.addWidget(self.numP_min_z_label, 2, 0, 1, 2)

        self.advanced_para_dock_widget.addWidget(self.numP_min_z_box, 3, 0, 1, 2)


    def _setting_z_Window(self):
        #################label#####################
        self.gray_thresh_z_label = QtWidgets.QLabel('Gray T(z)')
        self.color_bar_max_z_label = QtWidgets.QLabel('CB Max(z)')

        ##################spinbox###################
        self.gray_thresh_z_box = pg.SpinBox(value=175,
                                          dec=True)
        self.gray_thresh_z_box.setFixedSize(50, 20)

        self.color_bar_max_z_box = pg.SpinBox(value=11,
                                            dec=True)
        self.color_bar_max_z_box.setFixedSize(50, 20)
        #######################添加######################

        self.setting_z_dock_widget.addWidget(self.gray_thresh_z_label, 0, 0, 1, 1)
        self.setting_z_dock_widget.addWidget(self.gray_thresh_z_box, 0, 1, 1, 1)

        self.setting_z_dock_widget.addWidget(self.color_bar_max_z_label, 1, 0, 1, 1)
        self.setting_z_dock_widget.addWidget(self.color_bar_max_z_box, 1, 1, 1, 1)

    def _setting_xy_Window(self):
        #################label#####################
        self.gray_thresh_label = QtWidgets.QLabel('Gray T(xy)')
        self.color_bar_max_label = QtWidgets.QLabel('CB Max(xy)')

        ##################spinbox###################
        self.gray_thresh_box = pg.SpinBox(value=115,
                                             dec=True)
        self.gray_thresh_box.setFixedSize(50, 20)

        self.color_bar_max_box = pg.SpinBox(value=18,
                                                dec=True)
        self.color_bar_max_box.setFixedSize(50, 20)

        #######################添加######################

        self.setting_xy_dock_widget.addWidget(self.gray_thresh_label, 0, 0, 1, 1)
        self.setting_xy_dock_widget.addWidget(self.gray_thresh_box, 0, 1, 1, 1)

        self.setting_xy_dock_widget.addWidget(self.color_bar_max_label, 1, 0, 1, 1)
        self.setting_xy_dock_widget.addWidget(self.color_bar_max_box, 1, 1, 1, 1)



    def _setting_path_Window(self):
        #################label#####################
        self.data_path_label = QtWidgets.QLabel('Data Path')
        self.data_name_label = QtWidgets.QLabel('Data Name')
        #################lineedit##############################
        self.data_path_edit = QtWidgets.QLineEdit('D:/')
        self.data_path_edit.setFixedSize(130, 30)
        self.data_name_edit = QtWidgets.QLineEdit('20220419')
        self.data_name_edit.setFixedSize(190, 30)
        ###################button##########################
        self.select_path_button = QtWidgets.QPushButton('Select')
        self.select_path_button.setFixedSize(50, 30)
        self.select_path_button.setStyleSheet(ButtonStyle.style_tab_button)
        ##################add##############################

        self.setting_path_dock_widget.addWidget(self.data_path_label, 0, 0, 1, 1)
        self.setting_path_dock_widget.addWidget(self.data_path_edit, 0, 1, 1, 3)
        self.setting_path_dock_widget.addWidget(self.select_path_button, 0, 4, 1, 2)

        self.setting_path_dock_widget.addWidget(self.data_name_label, 1, 0, 1, 1)
        self.setting_path_dock_widget.addWidget(self.data_name_edit, 1, 1, 1, 4)
    def _optimal_Window(self):
        #################label#####################
        self.opt_path_label = QtWidgets.QLabel('Path')
        #################lineedit##############################
        self.opt_path_edit = QtWidgets.QLineEdit()
        self.opt_path_edit.setFixedSize(130, 30)
        ###################button##########################
        self.select_txt_button = QtWidgets.QPushButton('select')
        self.select_txt_button.setFixedSize(50, 30)
        self.select_txt_button.setStyleSheet(ButtonStyle.style_tab_button)

        self.refresh_txt_button = QtWidgets.QPushButton('refresh')
        self.refresh_txt_button.setFixedSize(50, 30)
        self.refresh_txt_button.setStyleSheet(ButtonStyle.style_tab_button)
        ##################add##############################
        self.optimal_dock_widget.addWidget(self.opt_path_label, 0, 0, 1, 1)
        self.optimal_dock_widget.addWidget(self.opt_path_edit, 0, 1, 1, 3)

        self.optimal_dock_widget.addWidget(self.select_txt_button, 0, 4, 1, 1)
        self.optimal_dock_widget.addWidget(self.refresh_txt_button, 0, 5, 1, 1)

    def _button_Window(self):
        ###################button##########################
        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.setFixedSize(100, 50)
        self.start_button.setCheckable(True)
        self.start_button.setChecked(False)
        self.start_button.setStyleSheet(ButtonStyle.style_button_highlight)

        self.exit_button = QtWidgets.QPushButton('Exit')
        self.exit_button.setFixedSize(100, 50)
        self.exit_button.setStyleSheet(ButtonStyle.style_quit)

        #######################添加######################

        self.button_dock_widget.addWidget(self.exit_button, 0, 1, 1, 2)
        self.button_dock_widget.addWidget(self.start_button, 0, 3, 1, 2)

    def _position_Window(self):
        #################label#####################
        self.x_position_label = QtWidgets.QLabel('X position')
        self.y_position_label = QtWidgets.QLabel('Y position')
        self.point_num_label = QtWidgets.QLabel('Point num')
        self.z_position_label = QtWidgets.QLabel('Z position')

        ##################spinbox###################
        self.x_position_box = pg.SpinBox(value=0,suffix='nm',
                                         dec=True)
        self.x_position_box.setFixedSize(90, 30)
        self.x_position_box.setEnabled(False)

        self.y_position_box = pg.SpinBox(value=0,suffix='nm',
                                         dec=True)
        self.y_position_box.setFixedSize(90, 30)
        self.y_position_box.setEnabled(False)

        self.point_num_box = pg.SpinBox(value=0,
                                         dec=True)
        self.point_num_box.setFixedSize(90, 30)
        self.point_num_box.setEnabled(False)

        self.z_position_box = pg.SpinBox(value=0, suffix='nm',
                                         dec=True)
        self.z_position_box.setFixedSize(90, 30)
        self.z_position_box.setEnabled(False)

        #######################添加######################

        self.position_dock_widget.addWidget(self.x_position_label, 0, 0, 1, 2)
        self.position_dock_widget.addWidget(self.y_position_label, 0, 2, 1, 2)
        self.position_dock_widget.addWidget(self.point_num_label, 0, 6, 1, 2)
        self.position_dock_widget.addWidget(self.z_position_label, 0, 4, 1, 2)

        self.position_dock_widget.addWidget(self.x_position_box, 1, 0, 1, 2)
        self.position_dock_widget.addWidget(self.y_position_box, 1, 2, 1, 2)
        self.position_dock_widget.addWidget(self.point_num_box, 1, 6, 1, 2)
        self.position_dock_widget.addWidget(self.z_position_box, 1, 4, 1, 2)

    def _image_Window(self):
        #################label####################
        # self.image_label = QtWidgets.QLabel()
        #################image####################
        self.image = pg.ImageView()  # 绘制窗口是个widget,view=pg.PlotItem()可显示坐标轴
        self.colors = [(139, 0, 255), (0, 0, 255), (0, 127, 255), (0, 255, 0), (255, 255, 0), (255, 165, 0),
                       (255, 0, 0)]
        self.color_map = pg.ColorMap(pos=np.linspace(0.0, 1.0, 7), color=self.colors)  # 将三种颜色作为节点，平滑过渡
        self.image.setColorMap(self.color_map)
        self.image.view.invertY(b=False)
        self.image.view.invertX(b=False)
        self.image.getHistogramWidget().setVisible(False)
        self.image.ui.menuBtn.setVisible(False)
        self.image.ui.roiBtn.setVisible(False)
        #######################添加######################

        self.image_dock_widget.addWidget(self.image)

        # image = Image.open('D:/ZJY/20220419-find-spots-test/scan-image/20220419-(10_10)-xy-real_position.jpg')
        # data = np.array(image)
        # data = np.rot90(data)
        # data = np.rot90(data)
        # data = np.rot90(data)
        # self.image.setImage(data)

    def _lock_Window(self):
        ###################label######################
        self.lock_uprate_label = QtWidgets.QLabel('uprate')
        self.lock_downrate_label = QtWidgets.QLabel('downrate')
        self.lock_step_label = QtWidgets.QLabel('step')
        ################box###########################
        self.lock_uprate_box = pg.SpinBox(value=2,
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
        self.lock_checkbox = QtWidgets.QCheckBox('point lock')
        self.lock_checkbox.setChecked(True)

        ######################add########################
        self.lock_dock_widget.addWidget(self.lock_uprate_label, 0, 0, 1, 2)
        self.lock_dock_widget.addWidget(self.lock_downrate_label, 2, 0, 1, 2)
        self.lock_dock_widget.addWidget(self.lock_step_label, 4, 0, 1, 2)

        self.lock_dock_widget.addWidget(self.lock_uprate_box, 1, 0, 1, 2)
        self.lock_dock_widget.addWidget(self.lock_downrate_box, 3, 0, 1, 2)
        self.lock_dock_widget.addWidget(self.lock_step_box, 5, 0, 1, 2)

        self.lock_dock_widget.addWidget(self.lock_checkbox, 6, 0, 1, 2)

        self.lock_dock_widget.addWidget(self.Text_Edit, 0, 4, 7, 3)

    def _MW_Window(self):
        ###############label##################
        self.Freq_start_label = QtGui.QLabel('start frequency')
        self.Fre_stop_label = QtGui.QLabel('stop frequency')
        self.Fre_step_label = QtGui.QLabel('frequency step')

        self.MW_model_label = QtGui.QLabel('MW model')
        self.MW_Power_label = QtGui.QLabel('MW Power')

        self.measure_time_label = QtGui.QLabel('measure time')

        self.cyc_label = QtGui.QLabel('cyc')

        ##############box######################
        self.Freq_start_box = pg.SpinBox(value=1300, suffix='MHz',
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

        self.Fre_step_box = pg.SpinBox(value=2, suffix='MHz',
                                       dec=False,
                                       decimals=4,
                                       step=0.1, minStep=0.01,
                                       bounds=[0, 50])
        self.Fre_step_box.setFixedSize(100, 30)

        self.MW_Power_box = pg.SpinBox(value=-25, suffix='dBm',
                                       dec=False,
                                       decimals=4,
                                       step=1, minStep=0.01,
                                       bounds=[-60, -10])
        self.MW_Power_box.setFixedSize(100, 30)

        self.measure_time_box = pg.SpinBox(value=10)
        self.measure_time_box.setFixedSize(100, 30)

        self.cyc_box = pg.SpinBox(value=0)
        self.cyc_box.setFixedSize(100, 30)
        self.cyc_box.setEnabled(False)

        ######################combobox#######################
        self.MW_model_comboBox = QtWidgets.QComboBox()
        self.MW_model_comboBox.setFixedSize(100, 30)
        self.MW_model_comboBox.addItems(['Agilent','Mini'])

        #############添加##########################
        self.MW_dock_widget.addWidget(self.MW_model_label, 0, 0, 1, 2)
        self.MW_dock_widget.addWidget(self.MW_Power_label, 1, 0, 1, 2)
        self.MW_dock_widget.addWidget(self.MW_model_comboBox, 0, 2, 1, 2)
        self.MW_dock_widget.addWidget(self.MW_Power_box, 1, 2, 1, 2)

        self.MW_dock_widget.addWidget(self.Freq_start_label, 2, 0, 1, 2)
        self.MW_dock_widget.addWidget(self.Fre_stop_label, 3, 0, 1, 2)
        self.MW_dock_widget.addWidget(self.Fre_step_label, 4, 0, 1, 2)

        self.MW_dock_widget.addWidget(self.Freq_start_box, 2, 2, 1, 2)
        self.MW_dock_widget.addWidget(self.Fre_stop_box, 3, 2, 1, 2)
        self.MW_dock_widget.addWidget(self.Fre_step_box, 4, 2, 1, 2)

        self.MW_dock_widget.addWidget(self.measure_time_label, 5, 0, 1, 2)
        self.MW_dock_widget.addWidget(self.measure_time_box, 5, 2, 1, 2)

        self.MW_dock_widget.addWidget(self.cyc_label, 6, 0, 1, 2)
        self.MW_dock_widget.addWidget(self.cyc_box, 6, 2, 1, 2)

    def _spin_Window(self):
        ######################plot_window#######################
        self.plot_1_dock_widget = pg.PlotWidget(title='single')
        self.plot_1_dock_widget.setLabel('left', 'Counts')
        self.plot_1_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_1_curve = self.plot_1_dock_widget.plot(pen=(255, 0, 0))

        self.plot_all_dock_widget = pg.PlotWidget(title='integration')
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))


        #######################添加##################################
        self.spin_dock_layout.addWidget(self.plot_1_dock_widget, 0, 0, 4, 6)
        self.spin_dock_layout.addWidget(self.plot_all_dock_widget, 4, 0, 4, 6)

    def _function_connect(self):

        pass


    def _Save_last_para(self):

        last_para = {'Gray T(z)':self.gray_thresh_z_box.value(),
                     'CB Max(z)':self.color_bar_max_z_box.value(),
                     'Gray T(xy)':self.gray_thresh_box.value(),
                     'CB Max(xy)':self.color_bar_max_box.value(),
                     'Z bias':self.z_bias_box.value(),
                     'Data Path':self.data_path_edit.text(),
                     'Data Name':self.data_name_edit.text(),
                     'MW type':self.MW_model_comboBox.currentIndex(),
                     'MW Power':self.MW_Power_box.value(),
                     'start F':self.Freq_start_box.value(),
                     'stop F':self.Fre_stop_box.value(),
                     'step F':self.Fre_step_box.value(),
                     'Measure time':self.measure_time_box.value(),
                     'uprate':self.lock_uprate_box.value(),
                     'downrate':self.lock_downrate_box.value(),
                     'lock step':self.lock_step_box.value(),
                     'scan stop x':self.scan_stop_x_box.value(),
                     'scan stop y':self.scan_stop_y_box.value(),
                     'scan range x':self.scan_range_x_box.value(),
                     'scan range y':self.scan_range_y_box.value(),
                     'z start': self.z_start_box.value(),
                     'z stop': self.z_stop_box.value(),
                     'z step':self.z_step_box.value(),
                     'numP min xy':self.numP_min_xy_box.value(),
                     'numP max xy':self.numP_max_xy_box.value(),
                     'numP min z':self.numP_min_z_box.value()}
        np.save(os.getcwd()+'\\history_data\\last_para_SF.npy',last_para)
        print('last SF paras saved')


    def _Load_last_para(self):
        try:
            last_data = np.load(os.getcwd()+'\\history_data\\last_para_SF.npy',allow_pickle=True).item()
            self.gray_thresh_z_box.setValue(last_data['Gray T(z)'])
            self.color_bar_max_z_box.setValue(last_data['CB Max(z)'])
            self.gray_thresh_box.setValue(last_data['Gray T(xy)'])
            self.color_bar_max_box.setValue(last_data['CB Max(xy)'])
            self.z_bias_box.setValue(last_data['Z bias'])
            self.data_path_edit.setText(last_data['Data Path'])
            self.data_name_edit.setText(last_data['Data Name'])
            self.MW_model_comboBox.setCurrentIndex(last_data['MW type'])
            self.MW_Power_box.setValue(last_data['MW Power'])
            self.Freq_start_box.setValue(last_data['start F'])
            self.Fre_stop_box.setValue(last_data['stop F'])
            self.Fre_step_box.setValue(last_data['step F'])
            self.measure_time_box.setValue(last_data['Measure time'])
            self.lock_uprate_box.setValue(last_data['uprate'])
            self.lock_downrate_box.setValue(last_data['downrate'])
            self.lock_step_box.setValue(last_data['lock step'])
            self.scan_stop_x_box.setValue(last_data['scan stop x'])
            self.scan_stop_y_box.setValue(last_data['scan stop y'])
            self.scan_range_x_box.setValue(last_data['scan range x'])
            self.scan_range_y_box.setValue(last_data['scan range y'])

            self.z_start_box.setValue(last_data['z start'])
            self.z_stop_box.setValue(last_data['z stop'])
            self.z_step_box.setValue(last_data['z step'])
            self.numP_min_xy_box.setValue(last_data['numP min xy'])
            self.numP_max_xy_box.setValue(last_data['numP max xy'])
            self.numP_min_z_box.setValue(last_data['numP min z'])

        except:
            print('last SF data is not exist')






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui_main = Spot_Finder_MainWindow()
    gui_main.show()
    sys.exit(app.exec_())

