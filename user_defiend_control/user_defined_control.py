#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: user_defined_control.py
@time: 2022/6/23 16:18
@desc:
'''
from user_defined_interface import user_defined_control_MainWindow
from pyqtgraph import exporters

from pyqtgraph.Qt import QtWidgets,QtGui,QtCore
import sys,ButtonStyle,time
import numpy as np
from spinapi import *
import threading,os
import pyqtgraph as pg
from list_show_operator import list_show
import pandas as pd
from spots_finder import Spots_Finder
from PIL import Image
class User_defined_Control(user_defined_control_MainWindow):
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
        self._continue_sign = False
        self._read_rate = 1
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
        com_str = eval(self.text_edit.toPlainText())
        InstListArray = self.spincore.str_list_to_list(com_str['list'])
        self.sl.bit_list_show(InstListArray[0], 7)

    def SaveData(self):
        fileFormat = 'csv'
        imgFormat = '.png'
        # filename仅返回选取的文件路径

        try:
            fileName = QtGui.QFileDialog.getSaveFileName(self.save_button, "Save As",
                                                         self.initialPath,
                                                         "%s Files (*.%s);;All Files (*)" % (
                                                             fileFormat.upper(), fileFormat))
            if self.com_str['task'] == 'freq scan':
                sr = pd.DataFrame(
                    {'1-x-freq(MHz)': self.XData, '2-y-counts': self.YData_all - self.YData, '3-cyc num': self.cyc,
                     '4-x-freq(MHz)': self.XData, '5-y-counts-ave': (self.YData_all - self.YData) / self.cyc})
            else:
                sr = pd.DataFrame({'1-x-time(us)': self.XData, '2-y-counts': self.YData_all,
                                       '3-y-counts-a.u.': self.YData_all / np.max(self.YData_all)})

            sr.to_csv(fileName[0], header=True, index=False, index_label=False)  # 保存为csv文件
            fileName = fileName[0].replace('.csv', imgFormat)
            ex_all = exporters.ImageExporter(self.plot_all_dock_widget.scene())
            ex_all.export(fileName=fileName)
            self.initialPath = os.path.dirname(fileName)
        except:
            print('未选取保存文件')

        # ----------spin control---------------#

    def start_spin_control(self):
        self.save_current_Task()
        #######预操作#########
        if self.start_button.isChecked():

            self.general_init()

            self.para_init()

            ####开启微波###
            self.MW.set_MW_Ampl(self.com_str['MW power'])
            if self.com_str['task'] == 'freq scan':
                self.MW.set_MW_Freq(self.XData[0])
            else:
                self.MW.set_MW_Freq(self.com_str['freq'])
            self.MW.set_MW_ON()
            # -------------------------------#

            time.sleep(1)
            if self.com_str['task'] != 'freq scan':
                self.counter.DAQ_Counter.start()
                self.spincore.start_board_2()
            self.plot_update_timer.start(self.sc_list_t)

            def loop_func(self):
                while self.running:
                    self.loop()

            self.thd = threading.Thread(target=loop_func, args=[self])
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
        self.MW.set_MW_OFF()
        ############
        self.counter.DAQ_Counter.stop()
        self.spincore.stop_board()
        self.start_button.setEnabled(False)
        self.exit_button.setEnabled(False)

    def _pause_spin_control_start(self):

        self.MW.set_MW_ON()
        ###########
        self.running = 1
        self.operator.reset_origin_data(self.cyc_list * self._read_rate)
        if self.com_str['task']!= 'freq scan':
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
        self.origin_data = np.array(self.operator.read_data_spincontrol(self.cyc_list * self._read_rate,
                                                                        continue_sign=self._continue_sign),
                                    dtype=float)

        if self.com_str['task'] == 'freq scan':
            self.MW.set_MW_Freq(self.XData[self.i])
            if self.ref:
                self.origin_data = self.origin_data.reshape(self.cyc_list, self._read_rate)
                data_diff = (self.origin_data[:, 0] - self.origin_data[:, 1]) / sum(self.origin_data[:, 1])
                self.YData[self.i] = np.sum(data_diff)
                self.YData_all[self.i] = (self.YData_all[self.i] + self.YData[self.i])
                self.YData_lock = self.YData_lock + self.origin_data[:, 1]
            else:
                self.YData[self.i] = np.sum(self.origin_data)
                self.YData_all[self.i] = (self.YData_all[self.i] + self.YData[self.i])
                self.YData_lock = self.YData_lock + self.origin_data
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

    def stop_control(self):
        self.running = 0
        self.thd.join()
        ###关闭微波##
        self.MW.set_MW_OFF()
        ############
        if self.scan_lock_checkbox.isChecked() and self.time_mode_checkbox.isChecked():
            self.scan_lock_time_timer.stop()
        self.plot_update_timer.stop()

        self.counter.DAQ_Counter.stop()
        self.spincore.stop_board()

        self.operator.data_num_sign = 0
        self.operator.thread_stop = 1
        self.ref = False

        if self.com_str['task'] == 'freq scan':
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
        if self.com_str['task'] == 'freq scan':
            pg.QtGui.QApplication.processEvents()
            self.plot_1_curve.setData(self.XData, self.YData)

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

    def para_init(self):
        #读取edit
        self.com_str = eval(self.text_edit.toPlainText())
        if self.com_str['task'] == 't scan':
            self.t_scan_Window()
            ########设置优先参数########
            self.ref = self.com_str['ref']
            self._continue_sign = True
            if self.ref:
                self._read_rate = 4
            else:
                self._read_rate = 2
            #########设置参数#########
            t=self.com_str['t']
            self.cyc_list = int(t[2])
            step = (t[1] - t[0]) / self.cyc_list
            self.XData = np.arange(t[0],t[1],step)
            self.operator.reset_origin_data(self.cyc_list * self._read_rate)
            self.YData = np.zeros(len(self.XData))
            self.YData_all = np.zeros(len(self.XData))
            self.YData_lock = np.zeros(len(self.XData))
            ########设置序列#########
            self.InstListArray = self.spincore.str_list_to_list(self.com_str['list'],t_list=self.XData)
            self.spincore.porgramming_board_v2(self.InstListArray)
            self.sc_list_t = 1000

        elif self.com_str['task'] == 'freq scan':
            ########设置优先参数########
            self.freq_scan_Window()
            self.ref = self.com_str['ref']
            self._continue_sign = False
            if self.ref:
                self._read_rate = 2
            else:
                self._read_rate = 1
            #########设置参数#########
            freq = self.com_str['freq']
            self.cyc_list = 1000
            self.XData = np.arange(freq[0],freq[1],freq[2])
            self.operator.reset_origin_data(self.cyc_list * self._read_rate)
            self.YData = np.zeros(len(self.XData))
            self.YData_all = np.zeros(len(self.XData))
            self.YData_lock = np.zeros(self.cyc_list)
            self.YData_last = np.zeros(len(self.XData))
            ########设置序列#########
            self.InstListArray = self.spincore.str_list_to_list(self.com_str['list'])
            self.spincore.porgramming_board_v2(self.InstListArray)
            self.sc_list_t = np.sum(np.array(self.InstListArray)[0][:,3])/1000


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

        self.spincore.porgramming_board_v2(self.InstListArray)

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
    aa = User_defined_Control(1, 2, 3, 4, 5, 6)
    aa.show()
    sys.exit(app.exec_())