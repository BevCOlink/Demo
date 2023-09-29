#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: user_defined_interface.py
@time: 2022/6/23 16:18
@desc:
'''
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction
from pyqtgraph.dockarea import *
import ButtonStyle
import numpy as np
import os,ctypes,ast

class user_defined_control_MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None, QtCore.Qt.Widget)
        self.setWindowTitle('User-defined Control')
        self.setFixedSize(1000, 600)
        self.menu()
        self.set_sizepolicy()
        self.Dock_Window()
        self.general_Winodw()
        self.Task_Window()
        self.plot_Window()
        self._plot_layout_setting()

        #
        self.task_dict = {}
        self.combx_index = []

        self.control_sign='None' #是否测量OMDR
        self.setWindowIcon(QtGui.QIcon(QtCore.QDir.currentPath() + '/ico/spin_control.ico'))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self._connect_function()
        self._init_Task()

    def _connect_function(self):
        self.c_lock_checkbox.clicked.connect(self._c_lock_action)
        self.scan_lock_checkbox.clicked.connect(self._scan_lock_action)
        # self.start_button.clicked.connect(self._print_text)
        self.load_task_button.clicked.connect(self._load_Task)
        self.save_task_button.clicked.connect(self._save_Task)
        self.task_combbox.activated.connect(self._select_Task)

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

    #Task operating functions
    def _save_Task(self):
        fn = pg.QtGui.QFileDialog.getSaveFileName(
            self, "Save State..", "untitled.tsk", "Task File (*.tsk)")
        if len(fn) > 1:
            fn = fn[0]
        if fn == '':
            return
        with open(fn, 'w', encoding='utf8') as f:
            content = self.text_edit.toPlainText()
            # print('The Content:',content)
            f.write(content)

    def _load_Task(self):
        fn = pg.QtGui.QFileDialog.getOpenFileName(
            self, "Load Task..", os.getcwd(),
            "Task File (*.tsk)")
        if len(fn) > 1:
            fn = fn[0]
        if str(fn) is None or str(fn) is False:
            print('loadFile Error: not find config file')
            return
        infile = open(str(fn), 'r', encoding='utf8')
        self.text_edit.setPlainText(infile.read())
        infile.close()
        #record tasks informations
        self.task_dict[os.path.basename(fn).split('.')[0]] = fn
        self.combx_index = []
        for index,key in self.task_dict.items():
            self.combx_index.append(index)
        self.task_combbox.clear()
        self.task_combbox.addItems(self.combx_index)
        self.task_combbox.setCurrentText(os.path.basename(fn).split('.')[0])
        data_path = os.getcwd() + '\\history_data'
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        np.save(data_path+'\\task_dict.npy', self.task_dict)

    def _select_Task(self):
        fn = self.task_dict[self.task_combbox.currentText()]
        try:
            infile = open(str(fn), 'r', encoding='utf8')
            self.text_edit.setPlainText(infile.read())
            infile.close()
        except:
            del(self.task_dict[self.task_combbox.currentText()])
            np.save(os.getcwd() + '\\history_data' + '\\task_dict.npy', self.task_dict)
            self.combx_index.remove(self.task_combbox.currentText())
            self.task_combbox.clear()
            self.task_combbox.addItems(self.combx_index)
            print("task's path wrong or doesn't exist, try to reload this task")

    def save_current_Task(self):
        try:
            fn = self.task_dict[self.task_combbox.currentText()]
            with open(fn, 'w', encoding='utf8') as f:
                content = self.text_edit.toPlainText()
                # print('The Content:',content)
                f.write(content)
        except:
            print('Remember saving current task first!')


    def _init_Task(self):
        try:
            data_path = os.getcwd() + '\\history_data'
            self.task_dict = np.load(data_path + '\\task_dict.npy').item()
            for index, key in self.task_dict.items():
                self.combx_index.append(index)
            self.task_combbox.addItems(self.combx_index)
        except:
            print("task_dict doesn't exist")

    #interface settings
    def set_sizepolicy(self):
        self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.sizePolicy.setHorizontalStretch(1)
        self.sizePolicy.setVerticalStretch(0)

    def menu(self):
        # self.statusBar()
        self.menu=self.menuBar()
        self.tool_menu = self.menu.addMenu('Tools')
        self.tool_menu.addSeparator()

        self.show_list_action = QAction('Show List', self)
        self.tool_menu.addAction(self.show_list_action)

    def Dock_Window(self):
        self.main_area = DockArea()
        self.setCentralWidget(self.main_area)
        #####整体框架,所有测量中这些变量名称保持一致！！！
        self.para_dock_widget=pg.LayoutWidget()
        self.para_dock_layout=Dock('parameters',size=(100,300))

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

        self.main_area.addDock(self.para_dock_layout, 'left')
        self.main_area.addDock(self.function_dock_layout, 'bottom', self.para_dock_layout)
        self.main_area.addDock(self.button_dock_layout, 'bottom', self.function_dock_layout)
        self.main_area.addDock(self.plot_all_dock_layout, 'right')

    def Task_Window(self):
        self.v_layout = QtWidgets.QVBoxLayout()
        self.h_layout = QtWidgets.QHBoxLayout()

        self.task_label = QtWidgets.QLabel('Task')
        self.task_combbox=QtWidgets.QComboBox()
        self.task_combbox.setSizePolicy(self.sizePolicy)

        self.save_task_button = QtWidgets.QPushButton('Save')
        self.load_task_button = QtWidgets.QPushButton('Load')
        self.text_edit = QtWidgets.QPlainTextEdit()

        self.h_layout.addWidget(self.task_label)
        self.h_layout.addWidget(self.task_combbox)
        self.h_layout.addWidget(self.save_task_button)
        self.h_layout.addWidget(self.load_task_button)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.text_edit)

        # self.para_dock_layout.addLayout(self.h_layout)

        self.task_widget = QtWidgets.QWidget()
        self.task_widget.setLayout(self.v_layout)
        self.para_dock_layout.addWidget(self.task_widget)


        # sizePolicy.setHeightForWidth(False)

        # self.task_widget.setSizePolicy(sizePolicy)

    def _plot_layout_setting(self):
        self.v_layout_plot = QtWidgets.QVBoxLayout()
        self.v_widget_plot = QtWidgets.QWidget()
        self.v_widget_plot.setLayout(self.v_layout_plot)


    def _layout_delete(self):
        self.main_area.deleteLater()
        self.plot_all_dock_layout.deleteLater()
        self.v_layout_plot.deleteLater()
        self.v_widget_plot.deleteLater()

    def _layout_Window(self):
        self.main_area = DockArea()
        self.setCentralWidget(self.main_area)

        self.plot_all_dock_layout = Dock('', size=(3000, 300))

        self._plot_layout_setting()


        self.main_area.addDock(self.para_dock_layout, 'left')
        self.main_area.addDock(self.function_dock_layout, 'bottom', self.para_dock_layout)
        self.main_area.addDock(self.button_dock_layout, 'bottom', self.function_dock_layout)
        self.main_area.addDock(self.plot_all_dock_layout, 'right')

    def t_scan_Window(self):
        print('t_scan')
        self._layout_delete()
        self.plot_Window()
        self._layout_Window()
        self.v_layout_plot.addWidget(self.plot_all_dock_widget)
        self.plot_all_dock_layout.addWidget(self.v_widget_plot)

    def freq_scan_Window(self):
        self._layout_delete()
        self.plot_Window()
        self._layout_Window()
        self.v_layout_plot.addWidget(self.plot_1_dock_widget)
        self.v_layout_plot.addWidget(self.plot_all_dock_widget)
        self.plot_all_dock_layout.addWidget(self.v_widget_plot)

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

        ###################lineedit###################
        self.cyc_label = QtGui.QLabel('cyc')

        self.cyc_edit = QtWidgets.QLineEdit('0')
        self.cyc_edit.setEnabled(False)
        self.cyc_edit.setFixedSize(80, 20)


        ######################checkbox########################
        # self._group = QtWidgets.QButtonGroup()
        self.c_lock_checkbox = QtWidgets.QCheckBox('continue')
        self.scan_lock_checkbox = QtWidgets.QCheckBox('scan')
        # self._group.addButton(self.c_lock_checkbox)
        # self._group.addButton(self.scan_lock_checkbox)
        # self._group.setExclusive(True)

        self.c_pointlock_dock_widget.addWidget(self.cyc_label, 0, 0, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.cyc_edit, 0, 2, 1, 2)

        self.c_pointlock_dock_widget.addWidget(self.lock_uprate_label, 1, 0, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_downrate_label, 2, 0, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_step_label, 3, 0, 1, 2)

        self.c_pointlock_dock_widget.addWidget(self.lock_uprate_box, 1, 2, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_downrate_box, 2, 2, 1, 2)
        self.c_pointlock_dock_widget.addWidget(self.lock_step_box, 3, 2, 1, 2)

        self.c_pointlock_dock_widget.addWidget(self.c_lock_checkbox, 4, 0, 1, 1)
        self.c_pointlock_dock_widget.addWidget(self.scan_lock_checkbox, 4, 2, 1, 1)

        self.c_pointlock_dock_widget.addWidget(self.Text_Edit,0,4,5,3)

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

    def plot_Window(self):
        #####plot_window
        ######################plot_window#######################
        self.plot_1_dock_widget = pg.PlotWidget(title='single')
        self.plot_1_dock_widget.setLabel('left', 'Counts')
        self.plot_1_dock_widget.setLabel('bottom', 'frequency', units='MHz')
        self.plot_1_curve = self.plot_1_dock_widget.plot(pen=(255, 0, 0))

        self.plot_all_dock_widget = pg.PlotWidget()
        self.plot_all_dock_widget.setLabel('left', 'Counts')
        self.plot_all_dock_widget.setLabel('bottom', 'times', units='kns')
        self.plot_all_curve = self.plot_all_dock_widget.plot(pen=(0, 255, 0))


    def ui_close(self):
        self.close()

    def _print_text(self):
        text = self.text_edit.toPlainText()
        control_inf = eval(text)
        print('control inf:',control_inf['list'])
        print(control_inf['list'])




if __name__ == '__main__':
    app = QtGui.QApplication([])
    # win = QtGui.QMainWindow()
    from pyqtgraph import exporters

    aa = user_defined_control_MainWindow()

    # ex_all = exporters.ImageExporter(aa.scene())
    # ex_all.export(fileName='D:/test.jpg')
    aa.show()
    app.exec_()