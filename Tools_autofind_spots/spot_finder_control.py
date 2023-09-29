#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: spot_finder_control.py
@time: 2022/4/16/0016 11:44:29
@desc:
'''
import numpy as np
import pyqtgraph as pg
import pandas as pd
import os,shutil
from interface_spot_finder import Spot_Finder_MainWindow
import sys
from pyqtgraph.Qt import QtWidgets, QtGui,QtCore
import threading
import time
import ButtonStyle
from spots_finder import Spots_Finder
from user_qthread import Thread
from PIL import Image
from pyqtgraph import exporters
from user_threading import thread_with_exception

#用于图像处理的路径不能有中文名称！！！
dir_txt = '/scan-data'
dir_image = '/scan-image'
dir_ODMR = '/scan-ODMR'

class Spots_Finder_Control(Spot_Finder_MainWindow,Spots_Finder):
    def __init__(self,confocal_control=0):
        super().__init__()
        #扫描相关参数
        self.scan_position_list_x = []
        self.scan_position_list_y = []
        self.i = 0
        self.j = 0
        self.k = 0   #作用于扫描循环中，分别表示x,y,z
        self.z_position = 0
        self.x_range = 0
        self.y_range = 0
        self.z_range = 0
        self.x_step = 0
        self.y_step = 0
        self.z_step = 0
        self.focal_P = 0
        self.step = []

        self.image_data = 0
        self.image_i = 0
        self.image_j = 0
        self.image_scan_x_array = 0
        self.image_scan_y_array = 0
        self.image_scan_z_array = 0
        self.image_scan_x_array_num = 0
        self.image_scan_y_array_num = 0
        self.image_scan_z_array_num = 0

        #spin相关参数
        self.XData = 0
        self.YData = 0
        self.YData_last = 0
        self.YData_all = 0
        self.spin_cyc = 0
        self.spin_i = 0
        self.cyc_list = 1000  # 测量序列循环次数后读取数据
        self.already_measured_xy = []

        #optimal参数
        self.opt_data_path='D:/ZJY'
        self.opt_data_name = 0
        self.opt_fileName=0

        self.z_list = 0

        #sc list time
        self.sc_list_t = 0

        #定时器
        self.image_update_timer = QtCore.QTimer()  # 计时器
        self.image_update_timer.setTimerType(QtCore.Qt.PreciseTimer)

        self.plot_update_timer = QtCore.QTimer()  # 计时器
        self.plot_update_timer.setTimerType(QtCore.Qt.PreciseTimer)

        self.image_update_control_timer = QtCore.QTimer()  # 计时器
        self.image_update_control_timer.setTimerType(QtCore.Qt.PreciseTimer)

        #信号
        self.stop_sign = 0
        self.scan_axis_sign = 0
        self.Autorange = True
        #image update timer
        self.timer_sign = 0
        self.timer_start_sign = 0
        #plot update timer
        self.plot_timer_sign = 0
        self.plot_timer_start_sign = 0


        self.spin_sign = 0
        self.load_im_sign = 0
        self.measure_num_sign = 0
        #路径
        self.data_path='D:/ZJY'
        #设备和功能
        self.confcocal_control = confocal_control

        #初始化参数
        self.gray_T_xy = self.gray_thresh_box.value()
        self.CB_max_xy = self.color_bar_max_box.value()

        self.gray_T_z = self.gray_thresh_z_box.value()
        self.CB_max_z = self.color_bar_max_z_box.value()

        self._function_connect()
    def init_device_func(self):

        self.sc = self.confcocal_control.sc
        self.counter = self.confcocal_control.counter
        self.PI = self.confcocal_control.PI
        self.spin_control = self.confcocal_control.Spin_control
        self.operator = self.confcocal_control.operator
        self.MW = self.spin_control.MW
        self.point_lock = self.confcocal_control.Point_Lock


    def _function_connect(self):
        #按钮信号
        self.select_path_button.clicked.connect(self.select_path)
        self.start_button.clicked.connect(self.start_find_spots)
        self.exit_button.clicked.connect(self.close)
        self.exit_button.clicked.connect(self._Save_last_para)

        self.select_txt_button.clicked.connect(self.optimal_para)
        self.refresh_txt_button.clicked.connect(self.refresh_para)

        #值改变信号
        self.gray_thresh_box.valueChanged.connect(self._thresh_changed)
        self.color_bar_max_box.valueChanged.connect(self._color_bar_max_changed)

        self.gray_thresh_z_box.valueChanged.connect(self._thresh_z_changed)
        self.color_bar_max_z_box.valueChanged.connect(self._color_bar_max_z_changed)

        self.lock_uprate_box.valueChanged.connect(lambda: self.point_lock.set_uprate(self.lock_uprate_box.value()))
        self.lock_downrate_box.valueChanged.connect(lambda: self.point_lock.set_downrate(self.lock_downrate_box.value()))
        self.lock_step_box.valueChanged.connect(lambda: self.point_lock.set_step(self.lock_step_box.value()))

        #计时器信号
        self.image_update_timer.timeout.connect(self.image_update_SF)
        self.image_update_control_timer.timeout.connect(self._image_timer_control)
        self.plot_update_timer.timeout.connect(self.spin_plot_update_SF)

    def _image_timer_control(self):
        if self.timer_sign == 1 and self.timer_start_sign == 0:
            self.image_update_timer.start(10)
            self.timer_start_sign = 1

        elif self.timer_sign == 0 and self.timer_start_sign == 1:
            self.image_update_timer.stop()
            self.timer_start_sign = 0

        if self.plot_timer_sign == 1 and self.plot_timer_start_sign == 0:
            self.plot_update_timer.start(self.sc_list_t)
            self.plot_timer_start_sign = 1

        elif self.plot_timer_sign == 0 and self.plot_timer_start_sign == 1:
            self.plot_update_timer.stop()
            self.plot_timer_start_sign = 0

        #在主线程load图片可以使autolevel正常运行
        if self.load_im_sign == 1:
            self.load_im_sign = 0
            image = Image.open(self.load_im_path)
            data = np.array(image)
            data = np.rot90(data)
            data = np.rot90(data)
            data = np.rot90(data)
            self.image.setImage(data,autoLevels=True)

    def _thresh_changed(self):
        self.gray_T_xy = self.gray_thresh_box.value()
        print('gray T(xy):',self.gray_T_xy)

    def _color_bar_max_changed(self):
        self.CB_max_xy = self.color_bar_max_box.value()
        print('CB_xy Max:',self.CB_max_xy)

    def _thresh_z_changed(self):
        self.gray_T_z = self.gray_thresh_z_box.value()
        print('gray T(z):',self.gray_T_z)

    def _color_bar_max_z_changed(self):
        self.CB_max_z = self.color_bar_max_z_box.value()
        print('CB_z Max:',self.CB_max_z)

    def _similar_position_judge(self,list,position):
        for i in list:
            dx = np.abs(i[0] - position[0])
            dy = np.abs(i[1] - position[1])
            if dx < 0.4 and dy < 0.4:
                judge = True
                break
            else:
                judge = False

        return judge


    def select_path(self):
        fileName = QtGui.QFileDialog.getExistingDirectory(None,'选择路径',self.data_path)
        self.data_path_edit.setText(fileName)
        self.data_path = fileName

    def optimal_para(self):
        fileFormat = 'txt'
        self.opt_fileName = 0
        self.opt_fileName = QtGui.QFileDialog.getOpenFileName(self.select_txt_button, "Save As",
                                                     self.opt_data_path,
                                                     "%s Files (*.%s);;All Files (*)" % (
                                                         fileFormat.upper(), fileFormat))[0]
        self.opt_data_path = os.path.split(self.opt_fileName)[0]
        self.opt_data_name = os.path.split(self.opt_fileName)[1]
        self.opt_data_name = '/'+self.opt_data_name.split('.')[0]

        self.LoadScan(self.opt_fileName)
        self.opt_path_edit.setText(self.opt_fileName)
        if self.scan_axis_sign == 1:
            cnts = self.label_real_position_xy(data_path=self.opt_data_path,data_name=self.opt_data_name,vmax=self.CB_max_xy,gray_thresh=self.gray_T_xy,numP_min=self.numP_min_xy_box.value(),numP_max=self.numP_max_xy_box.value())
            if cnts ==[]:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-xy.jpg')
            else:
                image = Image.open(self.opt_data_path+self.opt_data_name+'-xy-real_position.jpg')
            data = np.array(image)
            data = np.rot90(data)
            data = np.rot90(data)
            data = np.rot90(data)
            self.image.setImage(data, autoLevels=True)
        elif self.scan_axis_sign == 2 or self.scan_axis_sign == 3:
            cnts = self.label_real_position_z(data_path=self.opt_data_path, data_name=self.opt_data_name, vmax=self.CB_max_z,
                                        gray_thresh=self.gray_T_z,numP=self.numP_min_z_box.value())
            if cnts == []:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-z.jpg')
            else:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-z-real_position.jpg')
            data = np.array(image)
            data = np.rot90(data)
            data = np.rot90(data)
            data = np.rot90(data)
            self.image.setImage(data, autoLevels=True)

    def refresh_para(self):
        self.LoadScan(self.opt_fileName)
        if self.scan_axis_sign == 1:
            cnts = self.label_real_position_xy(data_path=self.opt_data_path, data_name=self.opt_data_name,
                                               vmax=self.CB_max_xy, gray_thresh=self.gray_T_xy,numP_min=self.numP_min_xy_box.value(),numP_max=self.numP_max_xy_box.value())
            if cnts == []:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-xy.jpg')
            else:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-xy-real_position.jpg')
            data = np.array(image)
            data = np.rot90(data)
            data = np.rot90(data)
            data = np.rot90(data)
            self.image.setImage(data, autoLevels=True)
        elif self.scan_axis_sign == 2 or self.scan_axis_sign == 3:
            cnts = self.label_real_position_z(data_path=self.opt_data_path, data_name=self.opt_data_name,
                                              vmax=self.CB_max_z,
                                              gray_thresh=self.gray_T_z,numP=self.numP_min_z_box.value())
            if cnts == []:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-z.jpg')
            else:
                image = Image.open(self.opt_data_path + self.opt_data_name + '-z-real_position.jpg')
            data = np.array(image)
            data = np.rot90(data)
            data = np.rot90(data)
            data = np.rot90(data)
            self.image.setImage(data, autoLevels=True)




    def start_find_spots(self):
        if self.start_button.isChecked():
            self.start_button.setStyleSheet(ButtonStyle.disconected)
            self.start_button.setText('Stop')
        ################初始化参数###########################
            self.confcocal_control.counter_poltting.stop()
            self.image_update_control_timer.start(1)
            self.scan_sign = 1
            self.stop_sign = 1

            def func():
                self.para_init()
                if self.s_z_mode_radio_button.isChecked():
                    self.find_spots_loop_single_z()
                elif self.m_z_mode_radio_button.isChecked():
                    self.find_spots_loop_multiple_z()
                elif self.e_z_mode_radio_button.isChecked():
                    self.find_spots_loop_scan_every_z()

                self.close_SF()

            self.thd = thread_with_exception(target=func,name='aaa')
            self.thd.start()

        else:
            self.close_SF()


    def find_spots_loop_single_z(self):      #仅在最开始扫描z
        #---------扫z-----------#
        if self.stop_sign == 1:
            position = [self.z_position,self.z_position,self.z_position]
            range = [self.z_range, self.z_range, self.z_range]
            self.step = [self.z_step, self.z_step, self.z_step]
            self.start_scan_z_for_SF()
            self.timer_sign = 1
            while self.scan_sign:
                self.image_data_update_SF(position,range,self.step)
            self.timer_sign = 0
            try:
                data_path = self.data_path + dir_txt
                data_name = self.data_name+('-(%d_%d)' %(self.i,self.j))+'-z.txt'
                # self.SaveScan_SF(position=position,range=range,step=self.step,path=data_path,name=data_name)
                self.SaveScan(data=self.image_data, position=position, range=range, step=self.step,
                              scan_axis=self.scan_axis_sign, int_time=self.confcocal_control.image_time_Box.value(),
                              path=data_path, name=data_name)
                print('z txt saved!')
            except:
                print('z save failed!')

        # ---------分析z-----------#
        if self.stop_sign == 1:
            self.LoadScan(data_path+data_name)
            data_path = self.data_path + dir_image
            data_name = self.data_name + ('-(%d_%d)' %(self.i,self.j))
            self.focal_P = self.label_real_position_z(data_path=data_path, data_name=data_name, vmax=self.CB_max_z,
                                                      gray_thresh=self.gray_T_z, numP=self.numP_min_z_box.value())[1] - self.z_bias_box.value()
            print('z分析完毕')
            self.operator.pool.submit(self.z_position_box.setValue, self.focal_P)
        #--------循环开始-------------#
        for self.i in self.scan_position_list_x:
            if self.stop_sign == 0:  # 如果没有即使stop按钮循环也会一直进行直到结束
                break
            self.operator.pool.submit(self.x_position_box.setValue, self.i)
            for self.j in self.scan_position_list_y:
                if self.stop_sign == 0:  # 如果没有即使stop按钮循环也会一直进行直到结束
                    break
                self.operator.pool.submit(self.y_position_box.setValue, self.j)
                #——————————扫xy————————————#
                if self.stop_sign == 1:
                    print('x,y:', self.i, self.j)
                    self.start_scan_xy_for_SF()
                    position=[self.i,self.j,self.focal_P]
                    range = [self.x_range, self.y_range, self.z_range]
                    self.step = [self.x_step, self.y_step, self.z_step]
                    self.timer_sign = 1
                    while self.scan_sign:
                        self.image_data_update_SF(position,range,self.step)

                    self.timer_sign = 0

                    data_path = self.data_path + dir_txt
                    data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j)) + '-xy.txt'
                    try:
                        # self.SaveScan_SF(position, range, self.step, data_path, data_name)
                        self.SaveScan(data=self.image_data, position=position, range=range, step=self.step,
                                      scan_axis=self.scan_axis_sign,
                                      int_time=self.confcocal_control.image_time_Box.value(), path=data_path,
                                      name=data_name)
                        print('xy txt saved!')

                    except:
                        print('xy save failed!')
                #--------分析xy：找点----------#
                if self.stop_sign == 1:
                    self.LoadScan(data_path + data_name)
                    data_path = self.data_path + dir_image
                    data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j))
                    real_position = self.label_real_position_xy(data_path=data_path, data_name=data_name,
                                                                vmax=self.CB_max_xy,gray_thresh=self.gray_T_xy,
                                                                numP_min=self.numP_min_xy_box.value(),
                                                                numP_max=self.numP_max_xy_box.value())
                    if real_position == []:
                        pass
                    else:
                #-------——图像展示-------------#
                        if self.stop_sign == 1:
                            self.load_im_sign = 1
                            self.load_im_path = data_path+data_name+'-xy-real_position.jpg'

                #---------spin control-------#
                        if self.stop_sign == 1:
                            data_path = self.data_path + dir_ODMR
                            data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j))
                            self.start_spin_SF()
                            for i,p in enumerate(real_position):
                                self.spin_sign = 1
                                print('Point:',i+1)
                                self.operator.pool.submit(self.point_num_box.setValue, i+1)
                                self.PI.position_move_x(p[0])
                                self.PI.position_move_y(p[1])
                                self.plot_timer_sign = 1
                                self.counter.DAQ_Counter.start()
                                self.sc.start_board_2()
                                while self.spin_sign:
                                    self.spin_update_SF()
                                    self.operator.pool.submit(self.x_position_box.setValue, self.PI.position_read_x())
                                    self.operator.pool.submit(self.y_position_box.setValue, self.PI.position_read_y())
                                    if self.spin_cyc > self.measure_time_box.value():
                                        self.SaveSpin_SF(data_path,data_name,i+1)
                                        self.spin_sign = 0
                                        self.plot_timer_sign = 0
                                        self.counter.DAQ_Counter.stop()
                                        self.sc.stop_board()
                                        self.point_lock.init_parameters()
                                        self.init_spin_SF()
                                        self.focal_P = np.round(self.PI.position_read_z(),2)
                                        self.operator.pool.submit(self.z_position_box.setValue, self.focal_P)
                                        print('ODMR finished')

                            self.stop_spin_SF()

    def find_spots_loop_multiple_z(self):  #同一区域扫描多个z
        #-------------构造z-----------#
        if self.stop_sign == 1:
            self.z_list = np.round(np.arange(self.z_start_box.value(),self.z_stop_box.value(),self.z_step_box.value()),2)
        # --------循环开始-------------#
        for self.i in self.scan_position_list_x:
            if self.stop_sign == 0:  # 如果没有即使stop按钮循环也会一直进行直到结束
                break
            self.operator.pool.submit(self.x_position_box.setValue, self.i)
            for self.j in self.scan_position_list_y:
                if self.stop_sign == 0:  # 如果没有即使stop按钮循环也会一直进行直到结束
                    break
                self.operator.pool.submit(self.y_position_box.setValue, self.j)
                self.measure_num_sign = 0
                self.already_measured_xy = []
                for self.k in self.z_list:
                    if self.stop_sign == 0:
                        break
                    self.operator.pool.submit(self.z_position_box.setValue, self.k)
                    #----------扫xy----------#
                    if self.stop_sign == 1:
                        print('x,y,z:', self.i, self.j,self.k)
                        self.start_scan_xy_for_SF()
                        position = [self.i, self.j, self.k]
                        range = [self.x_range, self.y_range, self.z_range]
                        self.step = [self.x_step, self.y_step, self.z_step]
                        self.timer_sign = 1
                        while self.scan_sign:
                            self.image_data_update_SF(position, range, self.step)
                        self.timer_sign = 0

                        data_path = self.data_path + dir_txt
                        data_name = self.data_name + ('-(%d_%d_%d)' % (self.i, self.j, self.k)) + '-xy.txt'
                        try:
                            # self.SaveScan_SF(position, range, self.step, data_path, data_name)
                            self.SaveScan(data=self.image_data, position=position, range=range, step=self.step,
                                          scan_axis=self.scan_axis_sign,
                                          int_time=self.confcocal_control.image_time_Box.value(), path=data_path,
                                          name=data_name)
                            print('xy txt saved!')

                        except:
                            print('xy save failed!')
                    # --------分析xy：找点----------#
                    if self.stop_sign == 1:
                        self.LoadScan(data_path + data_name)
                        data_path = self.data_path + dir_image
                        data_name = self.data_name + ('-(%d_%d_%d)' % (self.i, self.j, self.k))
                        real_position = self.label_real_position_xy(data_path=data_path, data_name=data_name,
                                                                    vmax=self.CB_max_xy,
                                                                    gray_thresh=self.gray_T_xy,
                                                                    numP_min=self.numP_min_xy_box.value(),
                                                                    numP_max=self.numP_max_xy_box.value())
                        if real_position == []:
                            pass
                        else:
                    # -------——图像展示-------------#
                            if self.stop_sign == 1:
                                self.load_im_sign = 1
                                self.load_im_path = data_path + data_name + '-xy-real_position.jpg'
                    # ---------spin control-------#
                            if self.stop_sign == 1:
                                data_path = self.data_path + dir_ODMR
                                data_name = self.data_name + ('-(%d_%d_%d)' % (self.i, self.j, self.k))
                                self.start_spin_SF()
                                for i, p in enumerate(real_position):
                                    if self.measure_num_sign == 0:
                                        self.already_measured_xy.append(p)
                                        no_pos_sign = 1
                                    elif self.measure_num_sign == 1:
                                        if self._similar_position_judge(self.already_measured_xy,p):
                                            no_pos_sign = 0
                                        else:
                                            self.already_measured_xy.append(p)
                                            no_pos_sign = 1
                                    if no_pos_sign == 1:
                                        self.spin_sign = 1
                                        print('Point:', i + 1)
                                        self.operator.pool.submit(self.point_num_box.setValue, i + 1)
                                        self.PI.position_move_x(p[0])
                                        self.PI.position_move_y(p[1])
                                        self.plot_timer_sign = 1
                                        self.counter.DAQ_Counter.start()
                                        self.sc.start_board_2()
                                        while self.spin_sign:
                                            self.spin_update_SF()
                                            self.operator.pool.submit(self.x_position_box.setValue,
                                                                      self.PI.position_read_x())
                                            self.operator.pool.submit(self.y_position_box.setValue,
                                                                      self.PI.position_read_y())
                                            if self.spin_cyc > self.measure_time_box.value():
                                                self.SaveSpin_SF(data_path, data_name, i + 1)
                                                self.spin_sign = 0
                                                self.plot_timer_sign = 0
                                                self.counter.DAQ_Counter.stop()
                                                self.sc.stop_board()
                                                self.point_lock.init_parameters()
                                                self.init_spin_SF()
                                                print('ODMR finished')

                                self.stop_spin_SF()
                                self.measure_num_sign = 1

    def find_spots_loop_scan_every_z(self):    #每次换区域都扫一次z
        #--------循环开始-------------#
        for self.i in self.scan_position_list_x:
            if self.stop_sign == 0:  # 如果没有即使stop按钮循环也会一直进行直到结束
                break
            self.operator.pool.submit(self.x_position_box.setValue, self.i)
            for self.j in self.scan_position_list_y:
                if self.stop_sign == 0:  # 如果没有即使stop按钮循环也会一直进行直到结束
                    break
                self.operator.pool.submit(self.y_position_box.setValue, self.j)
                # ---------扫z-----------#
                if self.stop_sign == 1:
                    position = [self.i, self.j, self.z_position]
                    range = [self.x_range, self.z_range, self.z_range]
                    self.step = [self.z_step, self.z_step, self.z_step]
                    self.start_scan_z_for_SF()
                    self.timer_sign = 1
                    while self.scan_sign:
                        self.image_data_update_SF(position, range, self.step)
                    self.timer_sign = 0
                    try:
                        data_path = self.data_path + dir_txt
                        data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j)) + '-z.txt'
                        # self.SaveScan_SF(position=position, range=range, step=self.step, path=data_path, name=data_name)
                        self.SaveScan(data=self.image_data, position=position, range=range, step=self.step,
                                      scan_axis=self.scan_axis_sign,
                                      int_time=self.confcocal_control.image_time_Box.value(), path=data_path,
                                      name=data_name)
                        print('z txt saved!')
                    except:
                        print('z save failed!')

                # ---------分析z-----------#
                if self.stop_sign == 1:
                    self.LoadScan(data_path + data_name)
                    data_path = self.data_path + dir_image
                    data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j))
                    self.focal_P = self.label_real_position_z(data_path=data_path, data_name=data_name,
                                                              vmax=self.CB_max_z,gray_thresh=self.gray_T_z,
                                                              numP=self.numP_min_z_box.value())[1] - self.z_bias_box.value()
                    print('z分析完毕')
                    self.operator.pool.submit(self.z_position_box.setValue, self.focal_P)

                #——————————扫xy————————————#
                if self.stop_sign == 1:
                    print('x,y:', self.i, self.j)
                    self.start_scan_xy_for_SF()
                    position=[self.i,self.j,self.focal_P]
                    range = [self.x_range, self.y_range, self.z_range]
                    self.step = [self.x_step, self.y_step, self.z_step]
                    self.timer_sign = 1
                    while self.scan_sign:
                        self.image_data_update_SF(position,range,self.step)

                    self.timer_sign = 0

                    data_path = self.data_path + dir_txt
                    data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j)) + '-xy.txt'
                    try:
                        # self.SaveScan_SF(position, range, self.step, data_path, data_name)
                        self.SaveScan(data=self.image_data, position=position, range=range, step=self.step,
                                      scan_axis=self.scan_axis_sign,
                                      int_time=self.confcocal_control.image_time_Box.value(), path=data_path,
                                      name=data_name)
                        print('xy txt saved!')

                    except:
                        print('xy save failed!')
                #--------分析xy：找点----------#
                if self.stop_sign == 1:
                    self.LoadScan(data_path + data_name)
                    data_path = self.data_path + dir_image
                    data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j))
                    real_position = self.label_real_position_xy(data_path=data_path, data_name=data_name,vmax=self.CB_max_xy,gray_thresh=self.gray_T_xy,numP_min=self.numP_min_xy_box.value(),numP_max=self.numP_max_xy_box.value())
                    if real_position == []:
                        pass
                    else:
                #-------——图像展示-------------#
                        if self.stop_sign == 1:
                            self.load_im_sign = 1
                            self.load_im_path = data_path+data_name+'-xy-real_position.jpg'

                #---------spin control-------#
                        if self.stop_sign == 1:
                            data_path = self.data_path + dir_ODMR
                            data_name = self.data_name + ('-(%d_%d)' % (self.i, self.j))
                            self.start_spin_SF()
                            for i,p in enumerate(real_position):
                                self.spin_sign = 1
                                print('Point:',i+1)
                                self.operator.pool.submit(self.point_num_box.setValue, i+1)
                                self.PI.position_move_x(p[0])
                                self.PI.position_move_y(p[1])
                                self.plot_timer_sign = 1
                                self.counter.DAQ_Counter.start()
                                self.sc.start_board_2()
                                while self.spin_sign:
                                    self.spin_update_SF()
                                    self.operator.pool.submit(self.x_position_box.setValue, self.PI.position_read_x())
                                    self.operator.pool.submit(self.y_position_box.setValue, self.PI.position_read_y())
                                    if self.spin_cyc > self.measure_time_box.value():
                                        self.SaveSpin_SF(data_path,data_name,i+1)
                                        self.spin_sign = 0
                                        self.plot_timer_sign = 0
                                        self.counter.DAQ_Counter.stop()
                                        self.sc.stop_board()
                                        self.point_lock.init_parameters()
                                        self.init_spin_SF()
                                        self.focal_P = np.round(self.PI.position_read_z(),2)
                                        self.operator.pool.submit(self.z_position_box.setValue, self.focal_P)
                                        print('ODMR finished')

                            self.stop_spin_SF()



    def para_init(self):
        self.scan_position_list_x = np.arange(self.scan_start_x_box.value()+self.scan_range_x_box.value() / 2, self.scan_stop_x_box.value()+self.scan_range_x_box.value() / 2,
                                            self.scan_range_x_box.value())
        self.scan_position_list_y = np.arange(self.scan_start_y_box.value() + self.scan_range_y_box.value() / 2,
                                              self.scan_stop_y_box.value() + self.scan_range_y_box.value() / 2,
                                              self.scan_range_y_box.value())

        self.z_position = self.scan_position_z_box.value()

        self.x_range = self.scan_range_x_box.value() / 2
        self.y_range = self.scan_range_y_box.value() / 2
        self.z_range = self.scan_range_z_box.value() / 2


        self.x_step = self.scan_step_x_box.value()
        self.y_step = self.scan_step_y_box.value()
        self.z_step = self.scan_step_z_box.value()

        self.data_path = self.data_path_edit.text()
        self.data_name = '/' + self.data_name_edit.text()

        isExists = os.path.exists(self.data_path+dir_txt)
        if not isExists:
            os.makedirs(self.data_path+dir_txt)
        else:
            shutil.rmtree(self.data_path+dir_txt)
            os.makedirs(self.data_path + dir_txt)

        isExists = os.path.exists(self.data_path + dir_image)
        if not isExists:
            os.makedirs(self.data_path + dir_image)
        else:
            shutil.rmtree(self.data_path + dir_image)
            os.makedirs(self.data_path + dir_image)

        isExists = os.path.exists(self.data_path + dir_ODMR)
        if not isExists:
            os.makedirs(self.data_path + dir_ODMR)
        else:
            shutil.rmtree(self.data_path + dir_ODMR)
            os.makedirs(self.data_path + dir_ODMR)

        self.timer_start_sign = 0
        self.plot_timer_start_sign = 0



 #=================控件相关==================#
    def start_scan_z_for_SF(self):
        self.operator.thread_stop = 0
        self.sc.close_board()
        pluse_time = 10
        self.sc.programming_board(pluse_time)
        self.sc.start_board()

        self.operator.data_num_sign = 0
        self.image_i = 0
        self.image_j = 0
        self.scan_axis_sign = 2
        self.scan_sign = 1


    def start_scan_xy_for_SF(self):
        self.operator.thread_stop = 0
        self.sc.close_board()
        pluse_time = self.confcocal_control.image_time_Box.value()
        self.sc.programming_board(pluse_time)
        self.sc.start_board()

        self.operator.data_num_sign = 0
        self.image_i = 0
        self.image_j = 0
        self.scan_axis_sign = 1
        self.scan_sign = 1

    def start_spin_SF(self):
        # self.Text_Edit.clear()
        self.operator.thread_stop = 0
        if self.lock_checkbox.isChecked():
            self.point_lock.uprate = self.lock_uprate_box.value()
            self.point_lock.downrate = self.lock_downrate_box.value()
            self.point_lock.step = self.lock_step_box.value()
            self.point_lock.text_browser = self.Text_Edit
        self.counter.DAQ_Counter.stop()
        self.sc.stop_board()
        self.operator.data_num_sign = 0
        self.image_i = 0
        self.image_j = 0
        self.scan_axis_sign = 0
        self.scan_sign = 0
        self.spin_sign = 1
        self.plot_timer_sign = 0
        #初始化测量参数
        self.XData = np.arange(self.Freq_start_box.value(), self.Fre_stop_box.value(), self.Fre_step_box.value())
        self.init_spin_SF()
        ########设置序列#########
        InstListArray = self.spin_control.ODMR_list()
        self.sc.porgramming_board_v2(InstListArray)

        InstListArray = np.array(InstListArray)[0]
        self.sc_list_t = np.sum(InstListArray[:, 3]) / 1000


        ####开启微波###

        self.MW.set_MW_Freq(self.Freq_start_box.value())
        self.MW.set_MW_Ampl(self.MW_Power_box.value())
        self.MW.set_MW_ON()
        ###########
        # 设置counter
        self.counter.spin_control_setting()

    def init_spin_SF(self):
        self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_last = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.spin_cyc = 1
        self.cyc_box.setValue(self.spin_cyc)
        self.spin_i = 0
        self.point_lock.force_start_sign = 1



    def stop_spin_SF(self):
        self.MW.set_MW_OFF()

        self.operator.data_num_sign = 0

        self.counter.scanning_setting()

    def image_data_update_SF(self, position, range, step):
        if self.operator.data_num_sign == 0:
            self.operator.data_num_sign = 1

            self.operator.read_data_SpotsFind()

            self.image_scan_x_array_num = int(2 * range[0] / step[0] + 1)
            self.image_scan_y_array_num = int(2 * range[1] / step[1] + 1)
            self.image_scan_z_array_num = int(2 * range[2] / step[2] + 1)

            self.image_scan_x_array = np.linspace(position[0] - range[0],
                                                  position[0] + range[0],
                                                  self.image_scan_x_array_num)
            self.image_scan_y_array = np.linspace(position[1] - range[1],
                                                  position[1] + range[1],
                                                  self.image_scan_y_array_num)
            self.image_scan_z_array = np.linspace(position[2] - range[2],
                                                  position[2] + range[2],
                                                  self.image_scan_z_array_num)

            if self.scan_axis_sign == 1:  # 扫描x-y
                self.image_data = np.zeros([self.image_scan_x_array_num, self.image_scan_y_array_num])
                self.PI.position_move_x(round(self.image_scan_x_array[0], 4))
                self.PI.position_move_y(round(self.image_scan_y_array[0], 4))
                self.PI.position_move_z(round(position[2], 4))


            elif self.scan_axis_sign == 2:
                self.image_data = np.zeros([self.image_scan_x_array_num, self.image_scan_z_array_num])
                self.PI.position_move_x(round(self.image_scan_x_array[0], 4))
                self.PI.position_move_y(round(position[1], 4))
                self.PI.position_move_z(round(self.image_scan_z_array[0], 4))


            elif self.scan_axis_sign == 3:  # 扫描y-z
                self.image_data = np.zeros([self.image_scan_y_array_num, self.image_scan_z_array_num])
                self.PI.position_move_x(round(position[0], 4))
                self.PI.position_move_y(round(self.image_scan_y_array[0], 4))
                self.PI.position_move_z(round(self.image_scan_z_array[0], 4))

        else:

            if self.image_i < self.image_data.shape[0]:  # 行数
                self.image_data[self.image_i, self.image_j] = self.operator.read_data_SpotsFind()

                if self.image_j < self.image_data.shape[1] - 1:  # 列数
                    self.image_j += 1
                else:
                    self.image_j = 0
                    self.image_i += 1
                    if (self.scan_axis_sign == 1) & (self.image_i < self.image_data.shape[0]):
                        self.PI.position_move_x(self.image_scan_x_array[self.image_i])
                    elif (self.scan_axis_sign == 2) & (self.image_i < self.image_data.shape[0]):
                        self.PI.position_move_x(self.image_scan_x_array[self.image_i])
                    elif (self.scan_axis_sign == 3) & (self.image_i < self.image_data.shape[0]):
                        self.PI.position_move_y(self.image_scan_y_array[self.image_i])
                    else:
                        pass
                if self.scan_axis_sign == 1:
                    self.PI.position_move_y(self.image_scan_y_array[self.image_j])

                elif self.scan_axis_sign == 2:
                    self.PI.position_move_z(self.image_scan_z_array[self.image_j])

                elif self.scan_axis_sign == 3:
                    self.PI.position_move_z(self.image_scan_z_array[self.image_j])

            else:
                self.operator.data_num_sign = 0
                self.image_i = 0
                self.image_j = 0
                self.scan_sign = 0

    def image_update_SF(self):
        try:
            if self.scan_axis_sign == 1:
                self.image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                    pos=(self.image_scan_x_array[0] - self.step[0] / 2,
                                         self.image_scan_y_array[0] - 5 * self.step[1] / 2),
                                    scale=(self.step[0], self.step[1]),
                                    levels=(np.min(self.image_data),2*self.CB_max_xy))
            elif self.scan_axis_sign == 2:
                self.image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                    pos=(self.image_scan_x_array[0] - self.step[0] / 2,
                                         self.image_scan_z_array[0] - self.step[2] / 2),
                                    scale=(self.step[0], self.step[2]),
                                    levels=(0,2*self.CB_max_z))

            elif self.scan_axis_sign == 3:
                self.image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                    pos=(self.image_scan_y_array[0] - self.step[1] / 2,
                                         self.image_scan_z_array[0] - self.step[2] / 2),
                                    scale=(self.step[1], self.step[2]),
                                    levels=(0,2*self.CB_max_z))
        except:
            pass

    def spin_update_SF(self):
        self.MW.set_MW_Freq(self.XData[self.spin_i])

        origin_data = np.array(self.operator.read_data_spincontrol(self.cyc_list * 2,continue_sign=1), dtype=float)
        origin_data = origin_data.reshape(self.cyc_list, 2)
        data_diff = (origin_data[:, 0] - origin_data[:, 1]) / sum(origin_data[:, 1])

        if self.lock_checkbox.isChecked():
            self.point_lock.position_keep(sum(origin_data[:, 1]))

        self.YData[self.spin_i] = np.sum(data_diff)
        self.YData_all[self.spin_i] = (self.YData_all[self.spin_i] + self.YData[self.spin_i])

        self.spin_i += 1
        if self.spin_i >= len(self.XData):
            self.spin_i = 0
            self.YData_last = self.YData
            self.YData = np.zeros(len(self.XData))
            self.spin_cyc += 1
            self.cyc_box.setValue(self.spin_cyc)

    def spin_plot_update_SF(self):
        pg.QtGui.QApplication.processEvents()
        self.plot_1_curve.setData(self.XData, self.YData)
        pg.QtGui.QApplication.processEvents()
        self.plot_all_curve.setData(self.XData, self.YData_all)


    def SaveScan_SF(self, position, range, step, path, name):

        header1 = 'XYZ Center: %.4f %.4f %.4f\n' % (
            position[0], position[1], position[2])
        header2 = 'XYZ Step: %.2f %.2f %.2f\n' % (
            step[0], step[1], step[2])
        header3 = 'XYZ Range: %.2f %.2f %.2f\n' % (
            range[0], range[1], range[2])
        header4 = 'Count Time: %d ms\n' % self.confcocal_control.image_time_Box.value()
        header5 = 'scan axis: %d\n' % self.scan_axis_sign
        header_all = header1 + header2 + header3 + header4 + header5
        header_all = header_all.encode('utf-8').decode(
            'latin1')  # 将编码方式改写，否则报错（https://blog.csdn.net/u014744494/article/details/41986647）
        np.savetxt(path + name, self.image_data, fmt='%.2f', newline='\n', header=header_all)
        # print('保存完毕')

    def SaveSpin_SF(self,data_path,data_name,ser):
        sr_ODMR = pd.DataFrame({'x-freq(MHz)': self.XData, 'y-counts': self.YData_all - self.YData})
        sr_ODMR.to_csv(data_path+data_name+'-P'+str(ser)+'-cyc_'+str(self.spin_cyc-1)+'-ODMR.csv', header=True, index=False, index_label=False)
        ex_all = exporters.ImageExporter(self.plot_all_dock_widget.scene())
        ex_all.export(data_path+data_name+'-P'+str(ser)+'-cyc_'+str(self.spin_cyc-1)+'-ODMR.jpg')

    def close_SF(self):

        self.scan_sign = 0
        self.spin_sign = 0
        self.stop_sign = 0

        self.thd.raise_exception()

        self.stop_spin_SF()

        self.image_update_control_timer.stop()
        self.image_update_timer.stop()
        self.plot_update_timer.stop()

        self.operator.thread_stop = 1

        self.sc.stop_board()
        self.sc.programming_board(self.confcocal_control.count_int_Box.value())
        self.sc.start_board()
        self.operator.pool.submit(self.operator.read_data, 1, 1)

        self.operator.gui_state = 1
        self.confcocal_control.counter_poltting.start(self.confcocal_control.count_int_Box.value())
        self.confcocal_control.x_psoition_adjust_Box.setValue(self.confcocal_control.PI.position_read_x())
        self.confcocal_control.y_psoition_adjust_Box.setValue(self.confcocal_control.PI.position_read_y())
        self.confcocal_control.z_psoition_adjust_Box.setValue(self.confcocal_control.PI.position_read_z())
        self.start_button.setStyleSheet(ButtonStyle.conected)
        self.start_button.setText('Start')




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    aa=Spots_Finder_Control()
    aa.show()
    # finder.show()
    # finder.LoadScan()
    # pixel_position=finder.label_bright_spots(data_path='F:/xy.txt',save_path='D:/',save_name='point_array')
    # pixel_0,pixel_position_rate=finder.pixel_to_real_position(save_path='D:/', save_name='point_array')
    # real_position = finder.label_real_position()
    # print(real_position)
    sys.exit(app.exec_())