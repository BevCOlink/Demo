#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: interface.py
@time: 2021/6/24/0024 20:34
@desc:
'''

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys
import pyqtgraph as pg
import numpy as np
import time
import nidaqmx

Device_str = b"Dev2/ctr2"
i = 0  # 计数个数标记
j=0
data = []  # 计数卡数据list
data1 = 0  # 计数卡单次数据
data_last = 0  # 计数卡上次数据
ptr1 = []  # 横坐标（时间）
data_count = np.zeros([10,10])


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(None, QtCore.Qt.Widget)
        self.setupUi()
        self.setupCounter()
        self.update_time = 1000  # 单位 ms
        self.data_average = 0

    def setupUi(self):
        self.setFixedSize(1200, 700)

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.top_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.top_widget.setObjectName('top_widget')
        self.top_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.top_widget.setLayout(self.top_layout)  # 设置左侧部件布局为网格

        self.buttom_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.buttom_widget.setObjectName('buttom_widget')
        self.buttom_layout = QtWidgets.QGridLayout()
        self.buttom_widget.setLayout(self.buttom_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.top_widget, 0, 0, 10, 12)
        self.main_layout.addWidget(self.buttom_widget, 10, 0, 2, 12)
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件,必须设置

        self.image = pg.ImageView(view=pg.PlotItem())  # 绘制窗口是个widget
        self.colors = [(85, 0, 255), (0,0,255),(255, 0, 0)]
        self.color_map = pg.ColorMap(pos=np.linspace(0.0, 1.0, 3), color=self.colors)  #将三种颜色作为节点，平滑过渡
        self.image.setColorMap(self.color_map)
        self.image.vLine = pg.InfiniteLine(pos=5, angle=90, movable=True)
        self.image.hLine = pg.InfiniteLine(pos=5, angle=0, movable=True)
        self.image.addItem(self.image.vLine, ignoreBounds=True)
        self.image.addItem(self.image.hLine, ignoreBounds=True)
        self.image.view.invertY(b=False)
        self.image.view.invertX(b=False)
        self.main_layout.addWidget(self.image, 0, 0, 10, 10)

        self.poltting = QtCore.QTimer()  # 计时器
        self.poltting.timeout.connect(self.update)

    def setupCounter(self):
        self.DAQ_Counter = nidaqmx.Task()
        self.DAQ_Counter.ci_channels.add_ci_count_edges_chan(Device_str)
        self.DAQ_Counter.start()

    def update(self):
        global ptr1, data, data1, data_last, i,j,data_count
        x=np.linspace(1,10,1)
        data=np.random.normal(10)
        data_count[j, i] = data
        self.image.setImage(data_count, autoRange=True, autoHistogramRange=True, pos=(0, 0),scale=(1,1))
        if j<9:
            j+=1
        else:
            if i<9:
                i+=1
                j=0
            else:
                self.poltting.stop()





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui_main = MainWindow()
    gui_main.show()
    gui_main.poltting.start(gui_main.update_time)
    sys.exit(app.exec_())

