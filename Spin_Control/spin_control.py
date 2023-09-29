#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: spin_control.py
@time: 2021/12/10 20:20
@desc:
'''
from interface_spin_control import spin_control_MainWindow
from pyqtgraph import exporters

from pyqtgraph.Qt import QtWidgets, QtGui, QtCore
import sys, ButtonStyle, time
import numpy as np
from spinapi import *
import threading, os
import pyqtgraph as pg
from list_show_operator import list_show
import pandas as pd
from spots_finder import Spots_Finder
from PIL import Image


class Spin_Control(spin_control_MainWindow):
    def __init__(self, gui_main, MW_generater, spincore, operator, counter, point_lock):
        super().__init__()
        # 对象
        self.gui_main = gui_main
        self.MW = MW_generater
        self.spincore = spincore
        self.operator = operator
        self.counter = counter
        self.spots_finder = Spots_Finder()
        # 参数
        self.cyc = 1  # 测量循环次数
        self.cyc_list = 0  # 测量序列循环次数后读取数据
        self.i = 0  # 当前微波频率计数
        self.scan_lock_time = 0  # 计时器定时时间
        self.XData = []  # 横坐标
        self.YData = []  # 纵坐标
        self.YData_last = []  # 上一次的YData
        self.YData_all = []  # 纵坐标加和
        self.YData_lock = []
        self.running = 0  # 测量运行标志
        self.sc_list_t = 0  # plot更新时间
        self.ref = False  # 测量是否存在参考
        self.initialPath = 'D:/'  # 保存数据初始路径
        # 状态标记
        self.scan_image_start = False
        self.plot_closed = False
        self.time_lock_closed = False

        #######锁点相关
        self.point_lock = point_lock
        self.sl = list_show()
        self._temp_data = 0
        self.PI = self.gui_main.PI
        self.load_im_path = 0
        #######update plot timer#########
        self.plot_update_timer = QtCore.QTimer()
        self.plot_update_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.plot_update_timer.timeout.connect(self.plot_update)

        self.scan_image_update_timer = QtCore.QTimer()
        self.scan_image_update_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.scan_image_update_timer.timeout.connect(self._scan_image_update)

        self.start_plot_timer = QtCore.QTimer()
        self.start_plot_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.start_plot_timer.timeout.connect(self._start_plot)

        self.scan_lock_time_timer = QtCore.QTimer()
        self.scan_lock_time_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.scan_lock_time_timer.timeout.connect(self._start_time_mode_lock)

        self.connect_function()

    def _start_plot(self):
        if self.scan_image_start:
            self.scan_image_update_timer.start(10)
            self.scan_image_start = False
        if self.plot_closed:
            self.plot_update_timer.start(self.sc_list_t)
            self.plot_closed = False
            self.start_plot_timer.stop()
            self.scan_image_update_timer.stop()
            # 在主线程中设置锁点找点的图像
            image = Image.open(self.load_im_path)
            data = np.array(image)
            data = np.rot90(data)
            data = np.rot90(data)
            data = np.rot90(data)
            self.scan_lock_image.setImage(data, autoLevels=True)
        if self.time_lock_closed:
            self.scan_lock_time_timer.start(self.scan_lock_time)

    def _start_time_mode_lock(self):
        self.point_lock.force_start_sign = 1

    def connect_function(self):
        # self.ODMR_action.triggered.connect(self.ODMR_para_init)
        self.start_button.clicked.connect(self.start_spin_control)
        self.pause_button.clicked.connect(self.pause_spin_control)
        self.save_button.clicked.connect(self.SaveData)
        self.exit_button.clicked.connect(self.ui_close)
        self.show_list_action.triggered.connect(self.show_list_function)
        self.lock_uprate_box.valueChanged.connect(lambda: self.point_lock.set_uprate(self.lock_uprate_box.value()))
        self.lock_downrate_box.valueChanged.connect(
            lambda: self.point_lock.set_downrate(self.lock_downrate_box.value()))
        self.lock_step_box.valueChanged.connect(lambda: self.point_lock.set_step(self.lock_step_box.value()))

    def show_list_function(self):
        if self.control_sign == 'ODMR':
            self.sl.bit_list_show(self.ODMR_list()[0], 4)
        elif self.control_sign == 'ODNMR':
            self.sl.bit_list_show(self.ODNMR_list()[0], 4)
        elif self.control_sign == 'Rabi':
            self.sl.bit_list_show(self.Rabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                                 self.rabi_points_box.value())[0], 4)
        elif self.control_sign == 'NRabi':
            self.sl.bit_list_show(self.NRabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                                  self.rabi_points_box.value())[0], 4)
        elif self.control_sign == 'Hahn':
            self.sl.bit_list_show(self.Hahn_list(self.hahn_start_time_box.value(), self.hahn_stop_time_box.value(),
                                                 self.hahn_points_box.value())[0], 4)
        elif self.control_sign == 'Ramsey':
            self.sl.bit_list_show(
                self.Ramsey_list(self.Ramsey_start_time_box.value(), self.Ramsey_stop_time_box.value(),
                                 self.Ramsey_points_box.value())[0], 4)
        elif self.control_sign == 'T1':
            self.sl.bit_list_show(self.T1_list(self.T1_start_time_box.value(), self.T1_stop_time_box.value(),
                                               self.T1_points_box.value())[0], 4)
        elif self.control_sign == 'nuRabi':
            self.sl.bit_list_show(self.nuRabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                                   self.rabi_points_box.value())[0], 4)

    def SaveData(self):
        fileFormat = 'csv'
        imgFormat = '.png'
        # filename仅返回选取的文件路径

        try:
            fileName = QtGui.QFileDialog.getSaveFileName(self.save_button, "Save As",
                                                         self.initialPath,
                                                         "%s Files (*.%s);;All Files (*)" % (
                                                             fileFormat.upper(), fileFormat))
            if self.control_sign == 'ODMR' or self.control_sign == 'ODNMR':
                sr_PLE = pd.DataFrame(
                    {'1-x-freq(MHz)': self.XData, '2-y-counts': self.YData_all - self.YData, '3-cyc num': self.cyc - 1,
                     '4-x-freq(MHz)': self.XData, '5-y-counts-ave': (self.YData_all - self.YData) / (self.cyc - 1)})
            elif (self.control_sign == 'Rabi') or (self.control_sign == 'nuRabi') or (self.control_sign == 'NRabi'):
                sr_PLE = pd.DataFrame({'1-x-time(us)': np.array(self.XData) / 1000, '2-y-counts': self.YData_all,
                                       '3-y-counts-a.u.': self.YData_all / np.max(self.YData_all)})
            elif (self.control_sign == 'Hahn') or (self.control_sign == 'Ramsey') or (self.control_sign == 'T1'):
                sr_PLE = pd.DataFrame({'1-x-time(us)': self.XData, '2-y-counts': self.YData_all,
                                       '3-y-counts-a.u.': self.YData_all / np.max(self.YData_all)})

            sr_PLE.to_csv(fileName[0], header=True, index=False, index_label=False)  # 保存为csv文件
            fileName = fileName[0].replace('.csv', imgFormat)
            ex_all = exporters.ImageExporter(self.plot_all_dock_widget.scene())
            ex_all.export(fileName=fileName)
            self.initialPath = os.path.dirname(fileName)
        except:
            print('未选取保存文件')

    # ----------spin control---------------#
    def start_spin_control(self):
        #######预操作#########
        if self.start_button.isChecked():

            self.general_init()

            # -------------------------------#
            if self.control_sign == 'ODMR':
                self.ODMR_para_init()

            elif self.control_sign == 'ODNMR':
                self.ODNMR_para_init()

            elif self.control_sign == 'Rabi':
                self.Rabi_para_init()

            elif self.control_sign == 'NRabi':
                self.NRabi_para_init()

            elif self.control_sign == 'Hahn':
                self.Hahn_para_init()

            elif self.control_sign == 'Ramsey':
                self.Ramsey_para_init()

            elif self.control_sign == 'T1':
                self.T1_para_init()

            elif self.control_sign == 'nuRabi':
                self.nuRabi_para_init()

            print('control sign:', self.control_sign)
            ####开启微波###
            if self.MW_model_comboBox.currentText() == 'Zurich':
                self.MW.set_parameter(self.radio_Power_box.value(), self.radio_Freq_box.value(), 1, 0)
                self.MW.set_MW_ON()
            elif self.MW_model_comboBox.currentText() == 'Mini':
                if self.control_sign == 'ODNMR' or self.control_sign == 'NRabi':
                    self.MW.set_MW_Freq(self.MW_Freq_box.value(), self.Freq_start_box.value(), 1)
                    self.MW.set_MW_Ampl(self.MW_Power_box.value(), self.RF_Power_box.value(), 1)
                    self.MW.set_MW_ON(1)
                else:
                    self.MW.set_MW_Ampl(self.MW_Power_box.value(), 0, 0)
                    self.MW.set_MW_Freq(self.Freq_start_box.value(), 0, 0)
                    self.MW.set_MW_ON(0)
            else:
                self.MW.set_MW_Ampl(self.MW_Power_box.value())
                self.MW.set_MW_Freq(self.Freq_start_box.value())
                self.MW.set_MW_ON()

            # self.MW.set_MW_ON()
            # -------------------------------#

            time.sleep(1)

            if self.control_sign != 'ODMR' and self.control_sign != 'ODNMR':
                self.counter.DAQ_Counter.start()
                self.spincore.start_board_2()

            self.plot_update_timer.start(self.sc_list_t)

            def loop_func():
                while self.running:
                    self.loop()

            self.thd = threading.Thread(target=loop_func)
            self.thd.daemon = True
            self.thd.start()
        else:
            self.stop_control()

    def pause_spin_control(self):
        if self.pause_button.isChecked():
            self._pause_spin_control_pause_stop()
        else:
            ########################
            self.operator.thread_stop = 0
            self.counter.spin_control_setting()
            self.spincore.stop_board()
            self.gui_main.counter_poltting.stop()
            self._scan_lock_spin_init()

            ######################
            self._pause_spin_control_start()

    def _pause_spin_control_pause_stop(self):
        self._pause_spin_control_pause()
        #################
        self.spincore.programming_board(self.gui_main.count_int_Box.value())
        self.spincore.start_board()
        self.counter.scanning_setting()
        self.operator.thread_stop = 1
        self.operator.data_num_sign = 0
        self.operator.pool.submit(self.operator.read_data, 1, 1)
        self.gui_main.counter_poltting.start(self.gui_main.count_int_Box.value())
        self.gui_main.x_psoition_adjust_Box.setValue(self.gui_main.PI.position_read_x())
        self.gui_main.y_psoition_adjust_Box.setValue(self.gui_main.PI.position_read_y())
        self.gui_main.z_psoition_adjust_Box.setValue(self.gui_main.PI.position_read_z())

        self.pause_button.setStyleSheet(ButtonStyle.disconected)
        self.pause_button.setText('Paused')

    def _pause_spin_control_pause(self):
        if self.scan_lock_checkbox.isChecked() and self.time_mode_checkbox.isChecked():
            self.scan_lock_time_timer.stop()
        self.plot_update_timer.stop()
        self.running = 0
        self.thd.join()

        if self.MW_model_comboBox.currentText() == 'Mini':
            if self.control_sign == 'ODNMR' or self.control_sign == 'NRabi':
                self.MW.set_MW_OFF(1)
            else:
                self.MW.set_MW_OFF(0)
        else:
            self.MW.set_MW_OFF()
        # self.MW.set_MW_OFF()
        ############
        self.counter.DAQ_Counter.stop()
        self.spincore.stop_board()
        self.start_button.setEnabled(False)
        self.exit_button.setEnabled(False)

    def _pause_spin_control_start(self):

        if self.MW_model_comboBox.currentText() == 'Mini':
            if self.control_sign == 'ODNMR' or self.control_sign == 'NRabi':
                self.MW.set_MW_ON(1)
            else:
                self.MW.set_MW_ON(0)
        else:
            self.MW.set_MW_ON()
        # self.MW.set_MW_ON()
        ###########
        self.running = 1
        if self.ref:
            self.operator.reset_origin_data(self.cyc_list * 4)
        else:
            self.operator.reset_origin_data(self.cyc_list * 2)
        if self.control_sign != 'ODMR' and self.control_sign != 'ODNMR':
            self.counter.DAQ_Counter.start()
            self.spincore.start_board_2()
        if self.scan_lock_checkbox.isChecked() and self.time_mode_checkbox.isChecked():
            self.scan_lock_time = self.scan_lock_time_box.value() * 60 * 1000
            self.time_lock_closed = True

        self.plot_update_timer.start(self.sc_list_t)
        self.pause_button.setStyleSheet(ButtonStyle.conected)
        self.pause_button.setText('Pause')
        self.start_button.setEnabled(True)
        self.exit_button.setEnabled(True)

        def loop_func(self):
            while self.running:
                self.loop()

        self.thd = threading.Thread(target=loop_func, args=[self])
        self.thd.daemon = True
        self.thd.start()

    def loop(self):
        if self.control_sign == 'ODMR':
            if self.MW_model_comboBox.currentText() == 'Mini':
                self.MW.set_MW_Freq(self.XData[self.i], 0, 0)
            else:
                self.MW.set_MW_Freq(self.XData[self.i])
            self.origin_data = np.array(self.operator.read_data_spincontrol(self.cyc_list * 2, continue_sign=0),
                                        dtype=float)
        elif self.control_sign == 'ODNMR':
            self.MW.set_MW_Freq(self.MW_Freq_box.value(), self.XData[self.i], 1)
            self.origin_data = np.array(self.operator.read_data_spincontrol(self.cyc_list * 2, continue_sign=0),
                                        dtype=float)
        else:
            if self.ref:
                self.origin_data = np.array(self.operator.read_data_spincontrol(self.cyc_list * 4, continue_sign=1),
                                            dtype=float)
            else:
                self.origin_data = np.array(self.operator.read_data_spincontrol(self.cyc_list * 2, continue_sign=1),
                                            dtype=float)

        if self.control_sign == 'ODMR' or self.control_sign == 'ODNMR':
            self.origin_data = self.origin_data.reshape(self.cyc_list, 2)
            data_diff = (self.origin_data[:, 0] - self.origin_data[:, 1]) / sum(self.origin_data[:, 1])
            self.YData[self.i] = np.sum(data_diff)
            self.YData_all[self.i] = (self.YData_all[self.i] + self.YData[self.i])
            self.i += 1

            if self.i >= len(self.XData):
                self.i = 0
                self.YData_last = self.YData
                self.YData = np.zeros(len(self.XData))
                self.cyc += 1

        else:
            if self.ref:
                self.origin_data = self.origin_data.reshape(self.cyc_list, 4)
                Y1 = self.origin_data[:, 1]
                Y2 = self.origin_data[:, 3]
                self.YData = Y2 - Y1
                self.YData_all = self.YData_all + self.YData
                self.YData_lock = self.YData_lock + self.origin_data[:, 0] + self.origin_data[:, 2]
                self.cyc += 1
            else:
                self.origin_data = self.origin_data.reshape(self.cyc_list, 2)
                self.YData = self.origin_data[:, 1]

                self.YData_all = self.YData_all + self.YData
                self.YData_lock = self.YData_lock + self.origin_data[:, 0]
                self.cyc += 1

        # if self.MW_model_comboBox.currentText() == 'Zurich':
        #     self.MW.set_MW_ON()

    def stop_control(self):
        self.running = 0
        self.thd.join()
        ###关闭微波##
        if self.MW_model_comboBox.currentText() == 'Mini':
            if self.control_sign == 'ODNMR' or self.control_sign == 'NRabi':
                self.MW.set_MW_OFF(1)
            else:
                self.MW.set_MW_OFF(0)
        else:
            self.MW.set_MW_OFF()
        # self.MW.set_MW_OFF()
        ############
        if self.scan_lock_checkbox.isChecked() and self.time_mode_checkbox.isChecked():
            self.scan_lock_time_timer.stop()
        self.plot_update_timer.stop()

        self.counter.DAQ_Counter.stop()
        self.spincore.stop_board()

        self.operator.data_num_sign = 0
        self.operator.thread_stop = 1
        self.ref = False

        if self.control_sign == 'ODMR' or self.control_sign == 'ODNMR':
            pg.QtGui.QApplication.processEvents()
            self.plot_1_curve.setData(self.XData, self.YData_last)
        pg.QtGui.QApplication.processEvents()
        self.plot_all_curve.setData(self.XData, self.YData_all - self.YData)
        pg.QtGui.QApplication.processEvents()

        self.spincore.programming_board(self.gui_main.count_int_Box.value())
        self.spincore.start_board()
        self.counter.scanning_setting()
        self.operator.pool.submit(self.operator.read_data, 1, 1)
        self.gui_main.counter_poltting.start(self.gui_main.count_int_Box.value())
        self.cyc_edit.setText(str(self.cyc - 1))
        self.operator.gui_state = 1
        self.gui_main.x_psoition_adjust_Box.setValue(self.gui_main.PI.position_read_x())
        self.gui_main.y_psoition_adjust_Box.setValue(self.gui_main.PI.position_read_y())
        self.gui_main.z_psoition_adjust_Box.setValue(self.gui_main.PI.position_read_z())
        self.start_button.setStyleSheet(ButtonStyle.conected)
        self.start_button.setText('Start')

    def plot_update(self):
        if self.control_sign == 'ODMR' or self.control_sign == 'ODNMR':
            pg.QtGui.QApplication.processEvents()
            self.plot_1_curve.setData(self.XData, self.YData)
            data = sum(self.origin_data[:, 1])
        else:
            data = sum(self.YData_lock) - self._temp_data
            self._temp_data = sum(self.YData_lock)

        pg.QtGui.QApplication.processEvents()
        self.plot_all_curve.setData(self.XData, self.YData_all)
        self.cyc_edit.setText(str(self.cyc))

        if self.c_lock_checkbox.isChecked():
            self.point_lock.position_keep(data)
        elif self.scan_lock_checkbox.isChecked():
            if self.thread_mode_checkbox.isChecked():
                self.point_lock.position_keep(data, continus=False, func_scan_lock=self._scan_lock,
                                              timer=self.start_plot_timer)
            elif self.time_mode_checkbox.isChecked():
                self.point_lock.start_num = 0
                self.point_lock.position_keep(data, continus=False, func_scan_lock=self._scan_lock,
                                              timer=self.start_plot_timer)
        else:
            self.point_lock.show_counts(data)

    # --------------settings----------------#
    def general_init(self):
        self.operator.thread_stop = 0
        self.counter.spin_control_setting()
        self.spincore.stop_board()
        self.gui_main.counter_poltting.stop()

        self.cyc = 1
        self.running = 1
        self.i = 0
        self.operator.gui_state = 2
        self._temp_data = 0
        self.origin_data = np.array([[0, 0, 0], [0, 0, 0]])

        self.cyc_edit.setText(str(self.cyc))

        self.point_lock.text_browser = self.Text_Edit
        self.Text_Edit.clear()

        if self.c_lock_checkbox.isChecked() or self.scan_lock_checkbox.isChecked():
            self.point_lock.init_parameters()
            self.point_lock.uprate = self.lock_uprate_box.value()
            self.point_lock.downrate = self.lock_downrate_box.value()
            self.point_lock.step = self.lock_step_box.value()
            if self.time_mode_checkbox.isChecked():
                self.scan_lock_time = self.scan_lock_time_box.value() * 60 * 1000
                self.scan_lock_time_timer.start(self.scan_lock_time)

        self.start_button.setStyleSheet(ButtonStyle.disconected)
        self.start_button.setText('Stop')

    def ODMR_para_init(self):
        #######数据初始化#######
        self.cyc_list = 1000
        self.XData = np.arange(self.Freq_start_box.value(), self.Fre_stop_box.value(), self.Fre_step_box.value())
        self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_last = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))

        ########设置序列#########
        InstListArray = self.ODMR_list()
        self.spincore.porgramming_board_v2(InstListArray)
        InstListArray = np.array(InstListArray)[0]
        self.sc_list_t = np.sum(InstListArray[:, 3]) / 1000

    def ODNMR_para_init(self):
        #######数据初始化#######
        self.cyc_list = 50000    # 100000
        self.XData = np.arange(self.Freq_start_box.value(), self.Fre_stop_box.value(), self.Fre_step_box.value())
        self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_last = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))

        ########设置序列#########
        InstListArray = self.ODNMR_list()
        self.spincore.porgramming_board_v2(InstListArray)
        InstListArray = np.array(InstListArray)[0]
        self.sc_list_t = np.sum(InstListArray[:, 3]) / 20     # *cyc_list/1e6

    def Rabi_para_init(self):
        #######数据初始化#######
        self.cyc_list = int(self.rabi_points_box.value())
        step = (self.rabi_stop_time_box.value() - self.rabi_start_time_box.value()) / self.cyc_list
        self.XData = np.arange(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(), step)
        self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.YData_lock = np.zeros(len(self.XData))

        ########设置序列#########

        InstListArray = self.Rabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(), self.cyc_list)
        self.spincore.porgramming_board_v2(InstListArray)
        self.sc_list_t = 1000
        print(InstListArray)

        # ####开启微波###
        # if self.MW_model_comboBox.currentText() == 'Agilent':
        #     self.MW.N5181B.write(':SOUR:POW %f dBm' % self.MW_Power_box.value())
        #     self.MW.N5181B.write(':SOUR:FREQ %f MHz' % self.Freq_start_box.value())
        #     self.MW.N5181B.write(':OUTP ON')
        # elif self.MW_model_comboBox.currentText() == 'Mini':
        #     self.MW.set_MW_Ampl(self.MW_Power_box.value())
        #     self.MW.set_MW_Freq(self.Freq_start_box.value())
        #     self.MW.set_MW_ON()

    def NRabi_para_init(self):
        #######数据初始化#######
        self.cyc_list = int(self.rabi_points_box.value())
        step = (self.rabi_stop_time_box.value() - self.rabi_start_time_box.value()) / self.cyc_list
        self.XData = np.arange(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(), step)
        self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.YData_lock = np.zeros(len(self.XData))

        ########设置序列#########

        InstListArray = self.NRabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(), self.cyc_list)
        self.spincore.porgramming_board_v2(InstListArray)
        self.sc_list_t = 1000
        print(InstListArray)

    def Hahn_para_init(self):
        #######数据初始化#######
        self.cyc_list = int(self.hahn_points_box.value())
        step = (self.hahn_stop_time_box.value() - self.hahn_start_time_box.value()) / self.cyc_list
        self.XData = np.arange(self.hahn_start_time_box.value(), self.hahn_stop_time_box.value(), step)
        if self.ref_checkbox.isChecked():
            self.operator.reset_origin_data(self.cyc_list * 4)
        else:
            self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.YData_lock = np.zeros(len(self.XData))

        ########设置序列#########
        InstListArray = self.Hahn_list(self.hahn_start_time_box.value(), self.hahn_stop_time_box.value(), self.cyc_list)
        if self.ref_checkbox.isChecked():
            self.ref = True
        else:
            self.ref = False
        self.spincore.porgramming_board_v2(InstListArray)
        self.sc_list_t = 1000

        # ####开启微波###
        # if self.MW_model_comboBox.currentText() == 'Agilent':
        #     self.MW.N5181B.write(':SOUR:POW %f dBm' % self.MW_Power_box.value())
        #     self.MW.N5181B.write(':SOUR:FREQ %f MHz' % self.Freq_start_box.value())
        #     self.MW.N5181B.write(':OUTP ON')
        # elif self.MW_model_comboBox.currentText() == 'Mini':
        #     self.MW.set_MW_Ampl(self.MW_Power_box.value())
        #     self.MW.set_MW_Freq(self.Freq_start_box.value())
        #     self.MW.set_MW_ON()

    def Ramsey_para_init(self):
        #######数据初始化#######
        self.cyc_list = int(self.Ramsey_points_box.value())
        step = (self.Ramsey_stop_time_box.value() - self.Ramsey_start_time_box.value()) / self.cyc_list
        self.XData = np.arange(self.Ramsey_start_time_box.value(), self.Ramsey_stop_time_box.value(), step)
        if self.ref_checkbox.isChecked():
            self.operator.reset_origin_data(self.cyc_list * 4)
        else:
            self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.YData_lock = np.zeros(len(self.XData))

        ########设置序列#########

        InstListArray = self.Ramsey_list(self.Ramsey_start_time_box.value(), self.Ramsey_stop_time_box.value(),
                                         self.cyc_list)
        if self.ref_checkbox.isChecked():
            self.ref = True
        else:
            self.ref = False
        self.spincore.porgramming_board_v2(InstListArray)
        self.sc_list_t = 1000

        # ####开启微波###
        # if self.MW_model_comboBox.currentText() == 'Agilent':
        #     self.MW.N5181B.write(':SOUR:POW %f dBm' % self.MW_Power_box.value())
        #     self.MW.N5181B.write(':SOUR:FREQ %f MHz' % self.Freq_start_box.value())
        #     self.MW.N5181B.write(':OUTP ON')
        # elif self.MW_model_comboBox.currentText() == 'Mini':
        #     self.MW.set_MW_Ampl(self.MW_Power_box.value())
        #     self.MW.set_MW_Freq(self.Freq_start_box.value())
        #     self.MW.set_MW_ON()

    def T1_para_init(self):
        #######数据初始化#######
        self.cyc_list = int(self.T1_points_box.value())
        step = (self.T1_stop_time_box.value() - self.T1_start_time_box.value()) / self.cyc_list
        self.XData = np.arange(self.T1_start_time_box.value(), self.T1_stop_time_box.value(), step)
        if self.ref_checkbox.isChecked():
            self.operator.reset_origin_data(self.cyc_list * 4)
        else:
            self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.YData_lock = np.zeros(len(self.XData))

        ########设置序列#########
        InstListArray = self.T1_list(self.T1_start_time_box.value(), self.T1_stop_time_box.value(), self.cyc_list)
        if self.ref_checkbox.isChecked():
            self.ref = True
        else:
            self.ref = False
        self.spincore.porgramming_board_v2(InstListArray)
        self.sc_list_t = 1000

        # ####开启微波###
        # if self.MW_model_comboBox.currentText() == 'Agilent':
        #     self.MW.N5181B.write(':SOUR:POW %f dBm' % self.MW_Power_box.value())
        #     self.MW.N5181B.write(':SOUR:FREQ %f MHz' % self.Freq_start_box.value())
        #     self.MW.N5181B.write(':OUTP ON')
        # elif self.MW_model_comboBox.currentText() == 'Mini':
        #     self.MW.set_MW_Ampl(self.MW_Power_box.value())
        #     self.MW.set_MW_Freq(self.Freq_start_box.value())
        #     self.MW.set_MW_ON()

    def nuRabi_para_init(self):
        #######数据初始化#######
        self.cyc_list = int(self.rabi_points_box.value())
        step = (self.rabi_stop_time_box.value() - self.rabi_start_time_box.value()) / self.cyc_list
        self.XData = np.arange(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(), step)
        self.operator.reset_origin_data(self.cyc_list * 2)
        self.YData = np.zeros(len(self.XData))
        self.YData_all = np.zeros(len(self.XData))
        self.YData_lock = np.zeros(len(self.XData))

        ########设置序列#########

        InstListArray = self.nuRabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                         self.cyc_list)
        self.spincore.porgramming_board_v2(InstListArray)
        self.sc_list_t = 1000
        print(InstListArray)

    # -------------sc lists----------------#
    def ODMR_list(self):
        InstListArray = [[]]
        self.spincore.ODMRmeasuring[3] = 500 * us
        self.spincore.ODMMRpumping[3] = 0.3 * us
        self.spincore.ODMRrefering[3] = 500 * us
        self.spincore.Pumping[3] = 3 * us
        self.spincore.Pumping[1] = Inst.CONTINUE
        InstListArray[0].append(tuple(self.spincore.Pumping))
        InstListArray[0].append(tuple(self.spincore.ODMRmeasuring))
        InstListArray[0].append(tuple(self.spincore.ODMMRpumping))
        InstListArray[0].append(tuple(self.spincore.Pumping))
        InstListArray[0].append(tuple(self.spincore.ODMRrefering))
        self.spincore.Pumping[3] = 0.3 * us
        self.spincore.Pumping[1] = Inst.BRANCH
        InstListArray[0].append(tuple(self.spincore.Pumping))
        print(InstListArray)
        return InstListArray

    def ODNMR_list(self):
        InstListArray = [[]]
        self.spincore.ODNMRPumping[3] = 5 * us
        self.spincore.ODNMROperating_MW[3] = self.MW_len_box.value() * us
        self.spincore.ODNMROperating_RF[3] = self.RF_len_box.value() * us
        self.spincore.ODNMRIdle[3] = 1 * us
        self.spincore.ODNMRIdle[1] = Inst.CONTINUE
        InstListArray[0].append(tuple(self.spincore.ODNMRPumping))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        self.spincore.ODNMRIdle[3] = 0.2 * us
        InstListArray[0].append(tuple(self.spincore.ODNMROperating_MW))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        InstListArray[0].append(tuple(self.spincore.ODNMROperating_RF))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        InstListArray[0].append(tuple(self.spincore.ODNMROperating_MW))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        self.spincore.ODNMRPumping[3] = 0.4 * us
        InstListArray[0].append(tuple(self.spincore.ODNMRPumping))
        InstListArray[0].append(tuple(self.spincore.ODNMRDetecting))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))

        self.spincore.ODNMRPumping[3] = 5 * us
        self.spincore.ODNMRIdle[3] = 1 * us
        InstListArray[0].append(tuple(self.spincore.ODNMRPumping))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        self.spincore.ODNMRIdle[3] = 0.2 * us
        InstListArray[0].append(tuple(self.spincore.ODNMROperating_MW))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        InstListArray[0].append((self.spincore.wordIdle, Inst.CONTINUE, 0, self.RF_len_box.value() * us))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        InstListArray[0].append(tuple(self.spincore.ODNMROperating_MW))
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))
        self.spincore.ODNMRPumping[3] = 0.4 * us
        InstListArray[0].append(tuple(self.spincore.ODNMRPumping))
        InstListArray[0].append(tuple(self.spincore.ODNMRDetecting))
        self.spincore.ODNMRIdle[1] = Inst.BRANCH
        InstListArray[0].append(tuple(self.spincore.ODNMRIdle))

        print(InstListArray)
        return InstListArray

    def Rabi_list(self, start, stop, N):
        InstListArray = [[]]

        step = (stop - start) / N
        print(step)
        TimeList = np.arange(start, stop, step)
        self.spincore.RabiDetecting[3] = self.rabi_detecting_time_box.value() * ns
        self.spincore.RabiDetectRef[3] = self.rabi_pumping_time_box.value() * us

        for t in TimeList:
            InstListArray[0].append(tuple(self.spincore.RabiDetectRef))
            InstListArray[0].append(tuple(self.spincore.RabiDelay))
            if t > 10:
                self.spincore.RabiOperating[3] = t * ns
                InstListArray[0].append(tuple(self.spincore.RabiOperating))
                self.spincore.RabiFill[3] = (stop - t + 200) * ns
            InstListArray[0].append(tuple(self.spincore.RabiFill))
            InstListArray[0].append(tuple(self.spincore.RabiPreDetecting))
            InstListArray[0].append(tuple(self.spincore.RabiDetecting))
            InstListArray[0].append(tuple(self.spincore.RabiInit))

        InstListArray[0].append((self.spincore.wordIdle, Inst.BRANCH, 0, 10 * ns))
        return InstListArray

    def NRabi_list(self, start, stop, N):
        InstListArray = [[]]

        step = (stop - start) / N
        print(step)
        TimeList = np.arange(start, stop, step)
        self.spincore.NRabiDetecting[3] = self.rabi_detecting_time_box.value() * ns
        self.spincore.NRabiDetectRef[3] = self.rabi_pumping_time_box.value() * us
        self.spincore.NRabiOperating_MW[3] = self.rabi_MW_Length_box.value() * us

        for t in TimeList:
            InstListArray[0].append(tuple(self.spincore.NRabiDetectRef))
            InstListArray[0].append((self.spincore.wordIdle, Inst.CONTINUE, 0, 1 * us))
            InstListArray[0].append(tuple(self.spincore.NRabiOperating_MW))
            InstListArray[0].append(tuple(self.spincore.NRabiDelay))
            if t > 10:
                self.spincore.NRabiOperating_RF[3] = t * ns
                InstListArray[0].append(tuple(self.spincore.NRabiOperating_RF))
                self.spincore.NRabiFill[3] = (stop - t + 200) * ns
            InstListArray[0].append(tuple(self.spincore.NRabiFill))
            InstListArray[0].append(tuple(self.spincore.NRabiOperating_MW))
            InstListArray[0].append(tuple(self.spincore.NRabiDelay))
            InstListArray[0].append(tuple(self.spincore.NRabiPreDetecting))
            InstListArray[0].append(tuple(self.spincore.NRabiDetecting))
            InstListArray[0].append(tuple(self.spincore.NRabiInit))

        InstListArray[0].append((self.spincore.wordIdle, Inst.BRANCH, 0, 10 * ns))
        return InstListArray

    def Hahn_list(self, start, stop, N):
        InstListArray = [[]]

        step = (stop - start) / N
        TimeList = np.arange(start, stop, step)

        self.spincore.HahnDetecting[3] = self.hahn_detecting_time_box.value() * ns
        self.spincore.HahnPumping[3] = self.hahn_pumping_time_box.value() * us
        self.spincore.HahnOperating_pi[3] = self.hahn_pi_box.value() * us
        self.spincore.HahnOperating_pid2[3] = self.hahn_pi_box.value() / 2 * us

        for t in TimeList:
            self.spincore.HahnGap[3] = t * us
            InstListArray[0].append(tuple(self.spincore.HahnPumping))
            InstListArray[0].append(tuple(self.spincore.HahnDelay1))

            InstListArray[0].append(tuple(self.spincore.HahnOperating_pid2))
            InstListArray[0].append(tuple(self.spincore.HahnGap))
            InstListArray[0].append(tuple(self.spincore.HahnOperating_pi))
            InstListArray[0].append(tuple(self.spincore.HahnGap))
            InstListArray[0].append(tuple(self.spincore.HahnOperating_pid2))
            InstListArray[0].append(tuple(self.spincore.HahnDelay2))

            InstListArray[0].append(tuple(self.spincore.HahnPreDetecting))
            InstListArray[0].append(tuple(self.spincore.HahnDetecting))
            InstListArray[0].append(tuple(self.spincore.HahnDelay3))

            if self.ref_checkbox.isChecked():
                InstListArray[0].append(tuple(self.spincore.HahnPumping))
                InstListArray[0].append(tuple(self.spincore.HahnDelay1))

                InstListArray[0].append(tuple(self.spincore.HahnOperating_pid2))
                InstListArray[0].append(tuple(self.spincore.HahnGap))
                InstListArray[0].append(tuple(self.spincore.HahnOperating_pi))
                InstListArray[0].append(tuple(self.spincore.HahnGap))
                InstListArray[0].append(tuple(self.spincore.HahnOperating_pid2))
                InstListArray[0].append(tuple(self.spincore.HahnOperating_pi))
                InstListArray[0].append(tuple(self.spincore.HahnDelay2))

                InstListArray[0].append(tuple(self.spincore.HahnPreDetecting))
                InstListArray[0].append(tuple(self.spincore.HahnDetecting))
                InstListArray[0].append(tuple(self.spincore.HahnDelay3))

        InstListArray[0].append((self.spincore.wordIdle, Inst.BRANCH, 0, 10 * ns))
        return InstListArray

    def Ramsey_list(self, start, stop, N):
        InstListArray = [[]]

        step = (stop - start) / N
        TimeList = np.arange(start, stop, step)
        self.spincore.RamseyDetecting[3] = self.Ramsey_detecting_time_box.value() * ns
        self.spincore.RamseyPumping[3] = self.Ramsey_pumping_time_box.value() * us
        self.spincore.RamseyOperating_pid2[3] = self.Ramsey_pi2_box.value() * us

        for t in TimeList:
            self.spincore.RamseyGap[3] = t * us
            InstListArray[0].append(tuple(self.spincore.RamseyPumping))
            InstListArray[0].append(tuple(self.spincore.RamseyDelay1))

            InstListArray[0].append(tuple(self.spincore.RamseyOperating_pid2))
            InstListArray[0].append(tuple(self.spincore.RamseyGap))
            InstListArray[0].append(tuple(self.spincore.RamseyOperating_pid2))
            InstListArray[0].append(tuple(self.spincore.RamseyDelay2))

            InstListArray[0].append(tuple(self.spincore.RamseyPreDetecting))
            InstListArray[0].append(tuple(self.spincore.RamseyDetecting))
            InstListArray[0].append(tuple(self.spincore.RamseyDelay3))

        InstListArray[0].append((self.spincore.wordIdle, Inst.BRANCH, 0, 10 * ns))
        return InstListArray

    def T1_list(self, start, stop, N):
        InstListArray = [[]]

        step = (stop - start) / N
        TimeList = np.arange(start, stop, step)
        self.spincore.T1Detecting[3] = self.T1_detecting_time_box.value() * ns
        self.spincore.T1Pumping[3] = self.T1_pumping_time_box.value() * us
        self.spincore.T1Operating_pi[3] = self.T1_pi_box.value() * us
        self.spincore.T1DelayRef[3] = self.T1_pi_box.value() * us

        for t in TimeList:
            self.spincore.T1Gap[3] = t * us
            InstListArray[0].append(tuple(self.spincore.T1Pumping))
            InstListArray[0].append(tuple(self.spincore.T1Delay1))

            InstListArray[0].append(tuple(self.spincore.T1Operating_pi))
            InstListArray[0].append(tuple(self.spincore.T1Gap))
            InstListArray[0].append(tuple(self.spincore.T1Delay2))

            InstListArray[0].append(tuple(self.spincore.T1PreDetecting))
            InstListArray[0].append(tuple(self.spincore.T1Detecting))
            InstListArray[0].append(tuple(self.spincore.T1Delay3))

            if self.ref_checkbox.isChecked():
                InstListArray[0].append(tuple(self.spincore.T1Pumping))
                InstListArray[0].append(tuple(self.spincore.T1Delay1))

                InstListArray[0].append(tuple(self.spincore.T1DelayRef))
                InstListArray[0].append(tuple(self.spincore.T1Gap))
                InstListArray[0].append(tuple(self.spincore.T1Delay2))

                InstListArray[0].append(tuple(self.spincore.T1PreDetecting))
                InstListArray[0].append(tuple(self.spincore.T1Detecting))
                InstListArray[0].append(tuple(self.spincore.T1Delay3))

        InstListArray[0].append((self.spincore.wordIdle, Inst.BRANCH, 0, 10 * ns))
        return InstListArray

    def nuRabi_list(self, start, stop, N):
        InstListArray = [[]]

        step = (stop - start) / N
        print(step)
        TimeList = np.arange(start, stop, step)
        self.spincore.nuRabiDetecting[3] = self.rabi_detecting_time_box.value() * ns
        self.spincore.nuRabiDetectRef[3] = self.rabi_pumping_time_box.value() * us

        for t in TimeList:
            InstListArray[0].append(tuple(self.spincore.nuRabiDetectRef))
            InstListArray[0].append(tuple(self.spincore.nuRabiDelay))
            if t > 10:
                self.spincore.nuRabiOperating[3] = (stop + 200) * ns
                InstListArray[0].append(tuple(self.spincore.nuRabiOperating))
            InstListArray[0].append(tuple(self.spincore.nuRabiPreDetecting))
            InstListArray[0].append(tuple(self.spincore.nuRabiDetecting))
            InstListArray[0].append(tuple(self.spincore.nuRabiInit))

        InstListArray[0].append((self.spincore.wordIdle, Inst.BRANCH, 0, 10 * ns))
        return InstListArray

    # -----------scan point lock----------------#
    def _scan_lock_pause(self):
        self._pause_spin_control_pause()

        # 扫描参数初始化
        self.image_data = 0
        self.image_i = 0
        self.image_j = 0
        self.image_scan_x_array = 0
        self.image_scan_y_array = 0
        self.image_scan_x_array_num = 0
        self.image_scan_y_array_num = 0

        self.operator.data_num_sign = 0
        # spincore和技数卡初始化
        self.spincore.programming_board(10)
        self.spincore.start_board()
        self.counter.scan_lock_setting()

    def _scan_lock_start(self):
        # 初始化spincore和计数卡
        self.counter.DAQ_Counter.stop()
        self.spincore.stop_board()
        self.counter.spin_control_setting()
        self._scan_lock_spin_init()
        self._pause_spin_control_start()
        self.plot_closed = True

    def _scan_lock_spin_init(self):
        if self.control_sign == 'ODMR':
            InstListArray = self.ODMR_list()

        elif self.control_sign == 'ODNMR':
            InstListArray = self.ODNMR_list()

        elif self.control_sign == 'Rabi':
            InstListArray = self.Rabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                           self.cyc_list)
        elif self.control_sign == 'NRabi':
            InstListArray = self.NRabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                            self.cyc_list)
        elif self.control_sign == 'Hahn':
            InstListArray = self.Hahn_list(self.hahn_start_time_box.value(), self.hahn_stop_time_box.value(),
                                           self.cyc_list)


        elif self.control_sign == 'Ramsey':
            InstListArray = self.Ramsey_list(self.Ramsey_start_time_box.value(), self.Ramsey_stop_time_box.value(),
                                             self.cyc_list)


        elif self.control_sign == 'T1':
            InstListArray = self.T1_list(self.T1_start_time_box.value(), self.T1_stop_time_box.value(), self.cyc_list)


        elif self.control_sign == 'nuRabi':
            InstListArray = self.nuRabi_list(self.rabi_start_time_box.value(), self.rabi_stop_time_box.value(),
                                             self.cyc_list)

        self.spincore.porgramming_board_v2(InstListArray)

    def _scan_lock_image_update(self, position, range, step):
        if self.operator.data_num_sign == 0:
            self.operator.data_num_sign = 1

            self.operator.read_data_SpotsFind()

            self.image_scan_x_array_num = int(2 * range[0] / step[0] + 1)
            self.image_scan_y_array_num = int(2 * range[1] / step[1] + 1)

            self.image_scan_x_array = np.linspace(position[0] - range[0],
                                                  position[0] + range[0],
                                                  self.image_scan_x_array_num)
            self.image_scan_y_array = np.linspace(position[1] - range[1],
                                                  position[1] + range[1],
                                                  self.image_scan_y_array_num)

            self.image_data = np.zeros([self.image_scan_x_array_num, self.image_scan_y_array_num])
            self.PI.position_move_x(round(self.image_scan_x_array[0], 4))
            self.PI.position_move_y(round(self.image_scan_y_array[0], 4))
            self.PI.position_move_z(round(position[2], 4))


        else:

            if self.image_i < self.image_data.shape[0]:  # 行数
                self.image_data[self.image_i, self.image_j] = self.operator.read_data_SpotsFind()

                if self.image_j < self.image_data.shape[1] - 1:  # 列数
                    self.image_j += 1
                else:
                    self.image_j = 0
                    self.image_i += 1
                    if self.image_i < self.image_data.shape[0]:
                        self.PI.position_move_x(self.image_scan_x_array[self.image_i])

                self.PI.position_move_y(self.image_scan_y_array[self.image_j])


            else:
                self.operator.data_num_sign = 0
                self.image_i = 0
                self.image_j = 0
                self.scan_sign = 0

    def _scan_image_update(self):
        try:
            self.scan_lock_image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                          pos=(self.image_scan_x_array[0] - self.step[0] / 2,
                                               self.image_scan_y_array[0] - 5 * self.step[1] / 2),
                                          scale=(self.step[0], self.step[1]),
                                          autoLevels=True)
        except:
            pass

    def _scan_lock(self):
        self._scan_lock_pause()
        real_position = []
        position = self.PI.getposition()
        position = [position['1'], position['2'], position['3']]
        range = self.scan_lock_range_box.value()
        range = [range, range, range]
        step = self.scan_lock_step_box.value()
        self.step = [step, step, step]
        self.scan_image_start = True
        nofindtime = 0
        while real_position == []:
            nofindtime += 1
            # scanning
            self.scan_sign = 1
            while self.scan_sign:
                self._scan_lock_image_update(position, range, self.step)
            # --------图像处理----------#
            # 保存
            data_path = 'D:/scan_lock/'
            data_name = 'scan_lock_xy.txt'
            isExists = os.path.exists(data_path)
            if not isExists:
                os.makedirs(data_path)
            self.spots_finder.SaveScan(data=self.image_data, position=position, range=range, step=self.step,
                                       scan_axis=1, int_time=10, path=data_path, name=data_name)
            self.spots_finder.LoadScan(data_path + data_name)
            # 找点并得到坐标
            data_name = 'scan_lock_xy'
            real_position = self.spots_finder.label_real_position_xy(data_path=data_path, data_name=data_name,
                                                                     vmax=np.max(self.image_data), gray_thresh=90,
                                                                     numP_min=2000, numP_max=30000)
            if nofindtime > 5:
                break
        if nofindtime > 5:
            self.load_im_path = data_path + data_name + '-xy-real_position.jpg'
            self._scan_lock_start()
            time.sleep(0.5)
            self._pause_spin_control_pause_stop()
            self.pause_button.toggle()
        else:
            print('lock position:', real_position)
            real_position = real_position[0]
            self.PI.position_move_x(real_position[0])
            self.PI.position_move_y(real_position[1])
            self.load_im_path = data_path + data_name + '-xy-real_position.jpg'
            self._scan_lock_start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    aa = Spin_Control(1, 2, 3, 4, 5, 6)
    aa.show()
    sys.exit(app.exec_())
