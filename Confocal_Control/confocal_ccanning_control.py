#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: Confocal_Scanning_Control.py
@time: 2022/4/15/0015 11:31:52
@desc:
'''
import pandas as pd
import numpy as np
import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import ButtonStyle
from user_class.user_threading import *
from interface_confocal_scanning_control import MainWindow
from user_timer import PyTimer

class Confocal_Control(MainWindow):
    def __init__(self, operator, sc, PI, counter, point_lock, spin_control=0,find_spots=0,user_defined_spin_control=0):
        super().__init__()
        #数据
        self.image_data = 0
        self.image_i = 0
        self.image_j = 0
        self.image_scan_x_array = 0
        self.image_scan_y_array = 0
        self.image_scan_z_array = 0
        self.image_scan_x_array_num = 0
        self.image_scan_y_array_num = 0
        self.image_scan_z_array_num = 0
        self.counter_record = []
        self.counter_ptr = []
        self.counter_data = []
        self.counter_i = 0
        self.initialPath = 'D:/'
        #信号/标记
        self.scan_axis_sign = 0
        self.Autorange = True
        self.record_sign = 0
        self.dragged_sign = 0
        self.scan_sign = 0
        #设备
        self.operator = operator
        self.sc = sc
        self.PI = PI
        self.counter = counter
        #功能
        self.Point_Lock = point_lock
        self.Spin_control = spin_control
        self.find_spots = find_spots
        self.user_defined_spin_control = user_defined_spin_control
        #初始化功能连接
        self._function_connect_init()
        self._function_init()
        #自定义定时器
        self.image_plot_timer = PyTimer(self.image_update)

    def _function_init(self):
        self.operator.pool.submit(self.operator.read_data, 1, 1)
        self.x_psoition_adjust_Box.setValue(self.PI.position_read_x())
        self.y_psoition_adjust_Box.setValue(self.PI.position_read_y())
        self.z_psoition_adjust_Box.setValue(self.PI.position_read_z())


    def _function_connect_init(self):
        ########################菜单栏信号#######################
        self.spin_control_action.triggered.connect(self.start_spin_control)
        self.find_spots_action.triggered.connect(self.find_spots_show)
        self.user_defined_spincontrol_action.triggered.connect(self.start_user_defiend_spin_control)
        #####################绘图计时器信号#######################################
        self.counter_poltting.timeout.connect(self.counter_update)
        pluse_time = self.count_int_Box.value()
        self.sc.programming_board(pluse_time)
        self.sc.start_board()
        self.counter_poltting.start(self.counter.counter_update_time)
        self.image_poltting.timeout.connect(self.image_update)

        self.Point_Lock.status_update.timeout.connect(self.lock_update)
        #####################按钮信号#######################################
        self.start_scan_button.clicked.connect(self.image_scan_start)
        self.load_position_button.clicked.connect(self.load_button)
        self.load_z_position_button.clicked.connect(self.load_z_button)
        self.pause_button.clicked.connect(self.pause_ui)
        self.active_button.clicked.connect(self.active_ui)
        self.exit_button.clicked.connect(self.exit_ui)
        self.save_scan_button.clicked.connect(self.SaveScan)
        self.load_scan_button.clicked.connect(self.LoadScan)
        self.Point_lock_button.clicked.connect(self.Start_point_lock)
        self.force_lock_button.clicked.connect(self.Force_Lock)
        self.record_count_button.clicked.connect(self.counter_record_start)
        self.clear_count_button.clicked.connect(self.counter_record_clear)
        self.save_count_button.clicked.connect(self.counter_record_save)

        #####################值改变信号#######################################
        self.count_int_Box.valueChanged.connect(self.counter_time_update)  # 当积分时间改变，需要更新counter的积分时间
        self.x_psoition_adjust_Box.valueChanged.connect(self.x_move)
        self.y_psoition_adjust_Box.valueChanged.connect(self.y_move)
        self.z_psoition_adjust_Box.valueChanged.connect(self.z_move)

        self.lock_downrate_box.valueChanged.connect(lambda: self.Point_Lock.set_downrate(self.lock_downrate_box.value()))
        self.lock_uprate_box.valueChanged.connect(lambda: self.Point_Lock.set_uprate(self.lock_uprate_box.value()))
        self.lock_step_box.valueChanged.connect(lambda: self.Point_Lock.set_step(self.lock_step_box.value()))
        #####################拖拽信号#######################################
        self.image.vLine.sigDragged.connect(self.vLine_dragged)
        self.image.hLine.sigDragged.connect(self.hLine_dragged)
        self.image.vLine.sigPositionChangeFinished.connect(self.line_drag_finished)
        self.image.hLine.sigPositionChangeFinished.connect(self.line_drag_finished)

        ##################复选框信号############################################
        self.autorange_checkbox.setChecked(True)
        self.autorange_checkbox.clicked.connect(self.autorange)

########计数记录相关函数#########################
    def counter_record_start(self):
        self.operator.record_sign = 1

    def counter_record_clear(self):
        self.operator.counter_record = []
        self.operator.record_sign = 0

    def counter_record_save(self):
        self.operator.record_sign = 0
        counter_ptr = np.arange(0, len(self.operator.counter_record), 1) * (self.count_int_Box.value() / 1000)
        sr = pd.DataFrame({'counts': self.operator.counter_record}, index=counter_ptr)
        fileFormat = 'csv'
        filetime = time.strftime("%Y%m%d", time.localtime())
        initialPath = 'D:/' + filetime + '-' + '.' + fileFormat
        fileName = QtGui.QFileDialog.getSaveFileName(self.save_count_button, "Save As",
                                                     initialPath,
                                                     "%s Files (*.%s);;All Files (*)" % (
                                                     fileFormat.upper(), fileFormat))
        sr.to_csv(fileName[0], index=True)  # filename返回的是一个tuple，第一个元素是路径
        print('计数已保存')
        self.statusbar.showMessage('计数已保存')
        # gui_main.setStatusTip('计数已保存')


#---------------------------------------------#
############confocal scan相关函数###############

    # imageview扫描功能
    def image_update(self):
        if self.operator.data_num_sign == 0:
            self.operator.data_num_sign = 1

            self.image_scan_x_array_num = int(2 * self.x_range_Box.value() / self.x_step_Box.value() + 1)
            self.image_scan_y_array_num = int(2 * self.y_range_Box.value() / self.y_step_Box.value() + 1)
            self.image_scan_z_array_num = int(2 * self.z_range_Box.value() / self.z_step_Box.value() + 1)

            self.image_scan_x_array = np.linspace(self.x_position_Box.value() - self.x_range_Box.value(),
                                             self.x_position_Box.value() + self.x_range_Box.value(),
                                             self.image_scan_x_array_num)
            self.image_scan_y_array = np.linspace(self.y_position_Box.value() - self.y_range_Box.value(),
                                             self.y_position_Box.value() + self.y_range_Box.value(),
                                             self.image_scan_y_array_num)
            self.image_scan_z_array = np.linspace(self.z_position_Box.value() - self.z_range_Box.value(),
                                             self.z_position_Box.value() + self.z_range_Box.value(),
                                             self.image_scan_z_array_num)

            if self.x_position_checkbox.isChecked() & self.y_position_checkbox.isChecked():
                self.scan_axis_sign = 1  # 扫描x-y
                self.image_data = np.zeros([self.image_scan_x_array_num, self.image_scan_y_array_num])
                self.image.vLine.setPos(self.image_scan_x_array[round(self.image_scan_x_array_num / 2)])
                self.image.hLine.setPos(self.image_scan_y_array[round(self.image_scan_x_array_num / 2)])
                self.image.vLine.setBounds([self.image_scan_x_array[0], self.image_scan_x_array[-1]])
                self.image.hLine.setBounds([self.image_scan_y_array[0], self.image_scan_y_array[-1]])
                self.PI.position_move_x(round(self.image_scan_x_array[0], 4))
                self.PI.position_move_y(round(self.image_scan_y_array[0], 4))
                self.PI.position_move_z(round(self.z_position_Box.value(), 4))


            elif self.x_position_checkbox.isChecked() & self.z_position_checkbox.isChecked():
                self.scan_axis_sign = 2  # 扫描x-z
                self.image_data = np.zeros([self.image_scan_x_array_num, self.image_scan_z_array_num])
                self.image.vLine.setPos(self.image_scan_x_array[round(self.image_scan_x_array_num / 2)])
                self.image.hLine.setPos(self.image_scan_z_array[round(self.image_scan_z_array_num / 2)])
                self.image.vLine.setBounds([self.image_scan_x_array[0], self.image_scan_x_array[-1]])
                self.image.hLine.setBounds([self.image_scan_z_array[0], self.image_scan_z_array[-1]])
                self.PI.position_move_x(round(self.image_scan_x_array[0], 4))
                self.PI.position_move_y(round(self.y_position_Box.value(), 4))
                self.PI.position_move_z(round(self.image_scan_z_array[0], 4))

            elif self.y_position_checkbox.isChecked() & self.z_position_checkbox.isChecked():
                self.scan_axis_sign = 3  # 扫描y-z
                self.image_data = np.zeros([self.image_scan_y_array_num, self.image_scan_z_array_num])
                self.image.vLine.setPos(self.image_scan_y_array[round(self.image_scan_y_array_num / 2)])
                self.image.hLine.setPos(self.image_scan_z_array[round(self.image_scan_z_array_num / 2)])
                self.image.vLine.setBounds([self.image_scan_y_array[0], self.image_scan_y_array[-1]])
                self.image.hLine.setBounds([self.image_scan_z_array[0], self.image_scan_z_array[-1]])
                self.PI.position_move_x(round(self.x_position_Box.value(), 4))
                self.PI.position_move_y(round(self.image_scan_y_array[0], 4))
                self.PI.position_move_z(round(self.image_scan_z_array[0], 4))

            else:
                self.image_poltting.stop()
                self.operator.data_num_sign = 0
                self.counter_poltting.start(self.counter.counter_update_time)

                self.start_scan_button.setStyleSheet(ButtonStyle.conected)
                self.start_scan_button.setText('Start')
                self.start_scan_button.toggle()
        else:
            if self.image_i < self.image_data.shape[0]:  # 行数
                self.image_data[self.image_i, self.image_j] = self.operator.counter_data[-1]

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
                    self.image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                            pos=(self.image_scan_x_array[0] - self.x_step_Box.value() / 2,
                                                 self.image_scan_y_array[0] - 5 * self.y_step_Box.value() / 2),
                                            scale=(self.x_step_Box.value(), self.y_step_Box.value()),
                                            autoLevels=self.Autorange)
                elif self.scan_axis_sign == 2:
                    self.PI.position_move_z(self.image_scan_z_array[self.image_j])
                    self.image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                            pos=(self.image_scan_x_array[0] - self.x_step_Box.value() / 2,
                                                 self.image_scan_z_array[0] - self.z_step_Box.value() / 2),
                                            scale=(self.x_step_Box.value(), self.z_step_Box.value()),
                                            autoLevels=self.Autorange)

                elif self.scan_axis_sign == 3:
                    self.PI.position_move_z(self.image_scan_z_array[self.image_j])
                    self.image.setImage(self.image_data, autoRange=True, autoHistogramRange=True,
                                            pos=(self.image_scan_y_array[0] - self.y_step_Box.value() / 2,
                                                 self.image_scan_z_array[0] - self.z_step_Box.value() / 2),
                                            scale=(self.y_step_Box.value(), self.z_step_Box.value()),
                                            autoLevels=self.Autorange)

                else:
                    pass

            else:
                self.sc.close_board()
                self.operator.data_num_sign = 0
                self.image_poltting.stop()
                pluse_time = self.count_int_Box.value()
                self.sc.programming_board(pluse_time)
                self.sc.start_board()
                self.counter_poltting.start(self.counter.counter_update_time)

                self.start_scan_button.toggle()
                self.image_i = 0
                self.image_j = 0
                self.x_psoition_adjust_Box.setValue(self.PI.position_read_x())
                self.y_psoition_adjust_Box.setValue(self.PI.position_read_y())
                self.z_psoition_adjust_Box.setValue(self.PI.position_read_z())
                self.start_scan_button.setStyleSheet(ButtonStyle.conected)
                self.start_scan_button.setText('Start')
                self.scan_sign = 0

    # 计数框更新功能
    def counter_update(self):
        if self.operator.data_num_sign == 0:
            self.operator.data_num_sign = 1
        else:
            self.counter_data.append(sum(self.operator.counter_data[-1:]))
            self.counter_ptr.append(self.counter_i)  # 横坐标数据处理
            self.counter_i += self.counter.counter_update_time / 1000
            self.counter_i = round(self.counter_i, 2)
            if self.counter_i > 100 * self.counter.counter_update_time / 1000:  # 横坐标保留100个数
                self.counter_data = self.counter_data[-100:]
                self.counter_ptr = self.counter_ptr[-100:]
                self.counter.counter_data_average = [np.mean(self.counter_data)] * 100
                self.curve.setData(self.counter_ptr, self.counter_data)
                self.curve_average.setData(self.counter_ptr, self.counter.counter_data_average)
                self.mean_count_edit.setText(str(self.counter.counter_data_average[1]))

            else:

                self.curve.setData(self.counter_ptr, self.counter_data)

    #start scan button 按下后的准备工作
    def image_scan_start(self):
        if self.start_scan_button.isChecked():
            self.sc.close_board()
            self.operator.data_num_sign = 0
            self.counter_poltting.stop()
            pluse_time = self.image_time_Box.value()
            self.sc.programming_board(pluse_time)
            self.sc.start_board()
            self.scan_sign = 1
            self.image_poltting.start(self.image_time_Box.value())

            self.start_scan_button.setText('Stop')
            self.start_scan_button.setStyleSheet(ButtonStyle.disconected)

        else:
            self.sc.close_board()
            self.image_poltting.stop()
            self.operator.data_num_sign = 0
            pluse_time = self.count_int_Box.value()
            self.sc.programming_board(pluse_time)
            self.sc.start_board()
            self.counter_poltting.start(self.count_int_Box.value())
            self.image_i = 0
            self.image_j = 0
            self.start_scan_button.setStyleSheet(ButtonStyle.conected)
            self.start_scan_button.setText('Start')
            self.scan_sign = 0

    # 当计数框的积分时间框的数值改变后用来更新积分时间
    def counter_time_update(self):
        self.counter_poltting.stop()
        self.sc.close_board()
        pluse_time = self.count_int_Box.value()
        self.sc.programming_board(pluse_time)
        self.sc.start_board()
        self.counter_poltting.start(self.count_int_Box.value())
        self.counter.counter_update_time = pluse_time

    # 游标被拖拽后更新位置并移动PI功能
    def vLine_dragged(self):
        self.dragged_sign = 1
        vline_position = round(self.image.vLine.getPos()[0], 4)
        if self.scan_axis_sign == 1:
            self.x_psoition_adjust_Box.setValue(vline_position)
            self.PI.position_move_x(vline_position)
        elif self.scan_axis_sign == 2:
            self.x_psoition_adjust_Box.setValue(vline_position)
            self.PI.position_move_x(vline_position)
        elif self.scan_axis_sign == 3:
            self.y_psoition_adjust_Box.setValue(vline_position)
            self.PI.position_move_y(vline_position)
        else:
            pass
    def hLine_dragged(self):
        global dragged_sign
        dragged_sign = 1
        hline_position = round(self.image.hLine.getPos()[1], 4)
        if self.scan_axis_sign == 1:
            self.y_psoition_adjust_Box.setValue(hline_position)
            self.PI.position_move_y(hline_position)
        elif self.scan_axis_sign == 2:
            self.z_psoition_adjust_Box.setValue(hline_position)
            self.PI.position_move_z(hline_position)
        elif self.scan_axis_sign == 3:
            self.z_psoition_adjust_Box.setValue(hline_position)
            self.PI.position_move_z(hline_position)
        else:
            pass
    # 拖拽结束信号置0
    def line_drag_finished(self):
        self.dragged_sign = 0

    # 调整框 值改变 动PI
    def x_move(self):
        if self.dragged_sign == 1:
            pass
        else:
            self.PI.position_move_x(round(self.x_psoition_adjust_Box.value(), 4))
    def y_move(self):

        if self.dragged_sign == 1:
            pass
        else:
            self.PI.position_move_y(round(self.y_psoition_adjust_Box.value(), 4))
    def z_move(self):
        if self.dragged_sign == 1:
            pass
        else:
            self.PI.position_move_z(round(self.z_psoition_adjust_Box.value(), 4))

    # 定义load按钮方法
    def load_button(self):
        self.x_position_Box.setValue(self.x_psoition_adjust_Box.value())
        self.y_position_Box.setValue(self.y_psoition_adjust_Box.value())
        self.z_position_Box.setValue(self.z_psoition_adjust_Box.value())
    def load_z_button(self):
        self.z_position_Box.setValue(self.z_psoition_adjust_Box.value())

    # 定义暂停按钮方法
    def pause_ui(self):
        if self.operator.gui_state == 1:
            print('请等待暂停结束...')
            self.statusbar.showMessage('请等待暂停结束...')
            self.operator.thread_stop = 0
            self.counter_poltting.stop()
            self.image_poltting.stop()
            self.sc.close_board()
            self.counter.DAQ_Counter.stop()
            self.PI.close()
            print('暂停完成')
            self.statusbar.showMessage('暂停完成')
        elif self.operator.gui_state == 0:
            print('已暂停')
            self.statusbar.showMessage('已暂停')
        self.operator.gui_state = 0

    # 定义启动按钮方法
    def active_ui(self):
        if self.operator.gui_state == 0:
            print('启动中...')
            self.statusbar.showMessage('启动中...')
            self.operator.thread_stop = 1
            self.operator.data_num_sign = 0
            self.PI.connect()
            self.x_psoition_adjust_Box.setValue(self.PI.position_read_x())
            self.y_psoition_adjust_Box.setValue(self.PI.position_read_y())
            self.z_psoition_adjust_Box.setValue(self.PI.position_read_z())
            pluse_time = self.count_int_Box.value()
            self.sc.programming_board(pluse_time)
            self.counter.DAQ_Counter.start()
            self.sc.start_board()

            self.operator.pool.submit(self.operator.read_data, 1, 1)
            self.counter_poltting.start()

            print('启动成功')
            self.statusbar.showMessage('启动成功')
        elif self.operator.gui_state == 1:
            print('已启动')
            self.statusbar.showMessage('已启动')
        self.operator.gui_state = 1

    # 定义退出按钮方法
    def exit_ui(self):
        if self.operator.gui_state == 1:
            print('退出中...')
            self.statusbar.showMessage('退出中...')
            self.operator.thread_stop = 0
            self.counter_poltting.stop()
            self.image_poltting.stop()
            self.counter.DAQ_Counter.close()
            self.PI.close()
            self.ui_close()
            self.sc.close_board()
            print('退出完成')
            self.statusbar.showMessage('退出完成')
        elif self.operator.gui_state == 2:
            print('测量中...')
            self.statusbar.showMessage('测量中...')

    # 定义保存按钮方法
    def SaveScan(self):

        # 保存信息
        fileFormat = 'txt'
        filetime = time.strftime("%Y%m%d", time.localtime())
        fileName = QtGui.QFileDialog.getSaveFileName(self.save_scan_button, "Save As",
                                                     self.initialPath,
                                                     "%s Files (*.%s);;All Files (*)" % (
                                                     fileFormat.upper(), fileFormat))
        if fileName[0]:
            header1 = 'XYZ Center: %.4f %.4f %.4f\n' % (
                self.x_position_Box.value(), self.y_position_Box.value(), self.z_position_Box.value())
            header2 = 'XYZ Step: %.2f %.2f %.2f\n' % (
                self.x_step_Box.value(), self.y_step_Box.value(), self.z_step_Box.value())
            header3 = 'XYZ Range: %.2f %.2f %.2f\n' % (
                self.x_range_Box.value(), self.y_range_Box.value(), self.z_range_Box.value())
            header4 = 'Count Time: %d ms\n' % self.image_time_Box.value()
            header5 = 'scan axis: %d\n' % self.scan_axis_sign
            header_all = header1 + header2 + header3 + header4 + header5
            header_all = header_all.encode('utf-8').decode(
                'latin1')  # 将编码方式改写，否则报错（https://blog.csdn.net/u014744494/article/details/41986647）


            np.savetxt(fileName[0], self.image_data, fmt='%.2f', newline='\n', header=header_all)
            self.initialPath = os.path.dirname(fileName[0])
            print('保存完毕')
            self.statusbar.showMessage('保存完毕')




    # load按钮方法
    def LoadScan(self):
        initialPath = QtCore.QDir.currentPath()
        fileName = QtGui.QFileDialog.getOpenFileName(self.load_scan_button, "Load Scan",
                                                     initialPath,  # 起始路径
                                                     "All Files (*);;Text Files (*.txt)")
        f = open(fileName[0], 'r', encoding='UTF-8')
        with f:
            # 接受读取的内容，并显示到多行文本框中
            data = f.readlines()
            lists_inf = []
            list_scan = []
            for string in data[:3]:
                string = string.strip()  # 去除换行等符号
                string = string.split(' ')  # 以空格作为分隔符
                string = string[3:]
                string = list(map(float, string))  # 将字符串转换为浮点数，注意需要使用list转换掉map格式
                lists_inf.append(string)
            scan_inf = np.array(lists_inf)
            print(scan_inf)

            for string in data[4:5]:
                string = string.strip()  # 去除换行等符号
                string = string.split(' ')  # 以空格作为分隔符
                string = int(string[3])  # 第三个信息是扫描轴的信息
            self.scan_axis_sign = string


            for string in data[6:]:  # 第6行开始为数据
                string = string.strip()  # 去除换行等符号
                string = string.split(' ')  # 以空格作为分隔符
                string = list(map(float, string))  # 将字符串转换为浮点数，注意需要使用list转换掉map格式
                list_scan.append(string)
            scan_data = np.array(list_scan)
            print(scan_data.shape)

            if self.scan_axis_sign == 1:  # xy
                self.image.setImage(scan_data, autoRange=True, autoHistogramRange=True,
                                        pos=(scan_inf[0, 0] - scan_inf[2, 0], scan_inf[0, 1] - scan_inf[2, 1]),
                                        scale=(scan_inf[1, 0], scan_inf[1, 1]))
                self.image.vLine.setPos(scan_inf[0, 0])
                self.image.hLine.setPos(scan_inf[0, 1])
                self.image.vLine.setBounds([scan_inf[0, 0] - scan_inf[2, 0], scan_inf[0, 0] + scan_inf[2, 0]])
                self.image.hLine.setBounds([scan_inf[0, 1] - scan_inf[2, 1], scan_inf[0, 1] + scan_inf[2, 1]])
                self.PI.position_move_z(scan_inf[0, 2])

            if self.scan_axis_sign == 2:  # xz
                self.image.setImage(scan_data, autoRange=True, autoHistogramRange=True,
                                        pos=(scan_inf[0, 0] - scan_inf[2, 0], scan_inf[0, 2] - scan_inf[2, 2]),
                                        scale=(scan_inf[1, 0], scan_inf[1, 2]))
                self.image.vLine.setPos(scan_inf[0, 0])
                self.image.hLine.setPos(scan_inf[0, 2])
                self.image.vLine.setBounds([scan_inf[0, 0] - scan_inf[2, 0], scan_inf[0, 0] + scan_inf[2, 0]])
                self.image.hLine.setBounds([scan_inf[0, 2] - scan_inf[2, 2], scan_inf[0, 2] + scan_inf[2, 2]])
                self.PI.position_move_y(scan_inf[0, 1])

            if self.scan_axis_sign == 3:  # yz
                self.image.setImage(scan_data, autoRange=True, autoHistogramRange=True,
                                        pos=(scan_inf[0, 1] - scan_inf[2, 1], scan_inf[0, 2] - scan_inf[2, 2]),
                                        scale=(scan_inf[1, 1], scan_inf[1, 2]))
                self.image.vLine.setPos(scan_inf[0, 1])
                self.image.hLine.setPos(scan_inf[0, 2])
                self.image.vLine.setBounds([scan_inf[0, 1] - scan_inf[2, 1], scan_inf[0, 1] + scan_inf[2, 1]])
                self.image.hLine.setBounds([scan_inf[0, 2] - scan_inf[2, 2], scan_inf[0, 2] + scan_inf[2, 2]])
                self.PI.position_move_x(scan_inf[0, 0])

    #image是否autorange
    def autorange(self):
        if self.autorange_checkbox.isChecked():
            self.Autorange = True
        else:
            self.Autorange = False
#---------------------------------------#

############其功能类函数###################
    ##########锁点###########
    def Start_point_lock(self):
        if self.Point_lock_button.isChecked():
            self.Point_Lock.text_browser = self.Text_browser
            self.Point_Lock.uprate = self.lock_uprate_box.value()
            self.Point_Lock.downrate = self.lock_downrate_box.value()
            self.Point_Lock.step = self.lock_step_box.value()
            self.Text_browser.clear()
            self.Point_Lock.init_parameters()
            self.Point_Lock.status_update.start(1000)
            self.Point_lock_button.setStyleSheet(ButtonStyle.disconected)
            self.Point_lock_button.setText('Stop Lock')

        else:
            self.Point_Lock.status_update.stop()
            self.x_psoition_adjust_Box.setValue(self.PI.position_read_x())
            self.y_psoition_adjust_Box.setValue(self.PI.position_read_y())
            self.z_psoition_adjust_Box.setValue(self.PI.position_read_z())
            self.Point_lock_button.setStyleSheet(ButtonStyle.style_tab_button)
            self.Point_lock_button.setText('Start Lock')

    def lock_update(self):
        try:
            Lock_Thread = threading.Thread(target=self.Point_Lock.position_keep, args=[sum(self.operator.counter_data[-10:])])
            Lock_Thread.daemon = True
        except:
            pass
        Lock_Thread.start()

    def Force_Lock(self):
        self.Point_Lock.force_start_sign = 1

    #######spincontrol########
    def start_spin_control(self):
        self.Spin_control.show()

    ###########找点############
    def find_spots_show(self):
        self.find_spots.init_device_func()
        self.find_spots.show()

#######spincontrol########
    def start_user_defiend_spin_control(self):
        self.user_defined_spin_control.show()




if __name__ == "__main__":
    Device_str = "Dev1/ctr2"
    PI_ID = "0118045977"
    TriggerGate = "PFI9"
    from pimove_control import Pi
    from main_operator import Main_Operator
    from counter import Counter
    from SpinCore import spincore
    import point_lock
    app = QtGui.QApplication([])
    # win = QtGui.QMainWindow()
    PI = Pi(PI_ID)
    counter = Counter(Device_str, TriggerGate, 100)
    sc = spincore()
    operator = Main_Operator(counter=counter, spincore=sc)
    Point_Lock = point_lock.Lock(Pi=PI)

    aa = Confocal_Control(operator=operator,sc=sc,PI=PI,counter=counter,point_lock=Point_Lock)
    Point_Lock.text_browser = aa.Text_browser
    aa.show()
    app.exec_()