#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: point_lock_interface.py
@time: 2021/7/2/0024 20:34
@desc:
'''
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys
import pyqtgraph as pg
import LableStyle, ButtonStyle

class PointLockWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None, QtCore.Qt.Widget)
        self.status_update=QtCore.QTimer()
        self.setWindowTitle('Point Lock')
        self.initialPath = QtCore.QDir.currentPath()
        self.setWindowIcon(QtGui.QIcon(self.initialPath+'/point_lock_interface.ico'))
        self.clear_TextBrowser=QtCore.QTimer()
        self.setupUi()
        self._para_Window()
        self._button_Window()
        self._text_Window()

    def setupUi(self):
        self.resize(400, 400)
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setWindowTitle('PI Scanning')
        self.main_layout = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        self.para_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.para_widget.setObjectName('para_widget')
        self.par_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.para_widget.setLayout(self.par_layout)  # 设置左侧部件布局为网格
        self.par_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.button_widget = QtWidgets.QWidget()
        self.button_widget.setObjectName('button_widget')
        self.button_layout = QtWidgets.QGridLayout()
        self.button_widget.setLayout(self.button_layout)
        self.button_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.text_widget = QtWidgets.QWidget()
        self.text_widget.setObjectName('text_widget')
        self.text_layout = QtWidgets.QGridLayout()
        self.text_widget.setLayout(self.text_layout)
        self.text_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.main_layout.addWidget(self.para_widget, 0, 0, 20, 10)
        self.main_layout.addWidget(self.button_widget, 20, 0, 10, 10)
        self.main_layout.addWidget(self.text_widget, 0, 10, 30, 10)
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件,必须设置

    def _para_Window(self):
        ####################标签#########################
        self.Lock_label = QtWidgets.QLabel("Point-Lock Parameter")
        self.Lock_label.setStyleSheet(LableStyle.lable_subtitle_2)
        self.uprate_label = QtWidgets.QLabel("uprate")
        self.uprate_label.setStyleSheet(LableStyle.lable_tex_white)
        self.downrate_label = QtWidgets.QLabel("downrate")
        self.downrate_label.setStyleSheet(LableStyle.lable_tex_white)
        self.step_label = QtWidgets.QLabel("PI step")
        self.step_label.setStyleSheet(LableStyle.lable_tex_white)
        ####################数值框#########################
        self.uprate_Box = pg.SpinBox(value=1.06,
                                         dec=True,
                                         step=1.0, minStep=0.01,
                                         bounds=[0, 100])
        self.uprate_Box.setFixedSize(100, 30)
        self.downrate_Box = pg.SpinBox(value=0.9,
                                         dec=True,
                                         step=1.0, minStep=0.01,
                                         bounds=[0, 100])
        self.downrate_Box.setFixedSize(100, 30)
        self.step_Box = pg.SpinBox(value=0.03, suffix='um',
                                       dec=True,
                                       step=1.0, minStep=0.01,
                                       bounds=[0, 100])
        self.step_Box.setFixedSize(100, 30)
        ####################按键#########################
        self.force_lock_button=QtWidgets.QPushButton('Force Lock')
        self.force_lock_button.setFixedSize(80, 60)
        self.force_lock_button.setMouseTracking(True)
        self.force_lock_button.setStyleSheet(ButtonStyle.conected)
        ##############################################################
        self.par_layout.addWidget(self.Lock_label, 0, 0, 1, 8)
        self.par_layout.addWidget(self.uprate_label, 2, 0, 2, 2)
        self.par_layout.addWidget(self.downrate_label, 4, 0, 2, 2)
        self.par_layout.addWidget(self.step_label, 6, 0, 2, 2)
        self.par_layout.addWidget(self.uprate_Box, 2, 2, 2, 8)
        self.par_layout.addWidget(self.downrate_Box, 4, 2, 2, 8)
        self.par_layout.addWidget(self.step_Box, 6, 2, 2, 8)
        self.par_layout.addWidget(self.force_lock_button, 9, 2, 2, 8)

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

    def _button_Window(self):
        ####################按钮#########################
        self.start_lock_button = QtWidgets.QPushButton('Strat')
        self.start_lock_button.setFixedSize(80, 60)
        self.start_lock_button.setMouseTracking(True)
        self.start_lock_button.setStyleSheet(ButtonStyle.conected)

        self.stop_lock_button = QtWidgets.QPushButton('Stop')
        self.stop_lock_button.setFixedSize(80, 60)
        self.stop_lock_button.setMouseTracking(True)
        self.stop_lock_button.setStyleSheet(ButtonStyle.disconected)
        ##############################################################
        self.button_layout.addWidget(self.start_lock_button, 0, 0, 1, 5)
        self.button_layout.addWidget(self.stop_lock_button, 0, 5, 1, 5)
        ####################图层格式#########################
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

    def _text_Window(self):
        ####################标签#####################################
        self.Text_label = QtWidgets.QLabel("Locking status")
        self.Text_label.setStyleSheet(LableStyle.lable_subtitle_2)
        #############################################################
        self.Text_Edit=QtWidgets.QTextBrowser()
        self.Text_Edit.setFixedSize(200,400)
        ##############################################################
        self.text_layout.addWidget(self.Text_label, 0, 4,1,1)
        self.text_layout.addWidget(self.Text_Edit, 1, 0,29,10)
        ####################图层格式########################
        self.text_widget.setStyleSheet('''
                                                    QWidget#text_widget{
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
    def ui_close(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui_main = PointLockWindow()
    gui_main.show()
    sys.exit(app.exec_())
