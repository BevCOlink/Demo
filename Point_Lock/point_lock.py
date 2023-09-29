# -*- coding: utf-8 -*-
# @Author: Yanff
# @Date:   2019-09-28 16:40:10
# @Last Modified by:   Yanff
# @Last Modified time: 2019-09-29 11:22:12


import threading
from PyQt5 import QtGui,QtCore



# class Logger(object):
#     def __init__(self, filename="Default.log"):
#         self.terminal = sys.stdout
#         self.log = open(filename, "w")
#
#     def write(self, message):
#         self.terminal.write(message)
#         self.log.write(message)
#
#     def flush(self):
#         pass
class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def run_(self, message):
        self.trigger.emit(message)


class Lock(object):
    def __init__(self, Pi, text_browser=0, uprate=1.06, downrate=0.8, step=0.05):

        self.lock_state = False
        self.lock_z_finish = False
        self.count_init = 0
        self.count_init_paste = 0
        self.count_list = []
        self.start_num = 0  # 判断是否连续两次都小于阈值的参数
        self.lock_num = 0  # 记录连续锁点次数
        self.downrate = downrate
        self.uprate = uprate
        self.text_browser = text_browser
        self.PI_axis = 0
        self.force_start_sign=0
        self.step = step
        self.position_list = []
        self.pi = Pi
        self.status_update = QtCore.QTimer()
        self.position_init = self.pi.getposition()
        self.threads=MyThread(None)
        self.threads.trigger.connect(self.text_browser_append)

    def init_parameters(self):
        self.lock_state = False
        self.lock_z_finish = False
        self.count_init = 0
        self.count_init_paste = 0
        self.count_list = []
        self.start_num = 0  # 判断是否连续两次都小于阈值的参数
        self.lock_num = 0  # 记录连续锁点次数
        self.PI_axis = 0
        self.force_start_sign = 0
        self.position_list = []
        self.position_init = self.pi.getposition()


    def text_browser_threads(self,text):
        self.threads.run_(text)

    def text_browser_append(self,text):
        self.text_browser.append(text)
        self.text_browser.moveCursor(self.text_browser.textCursor().End)
        if len(self.text_browser.toPlainText())>80000:
            self.text_browser.clear()


    def set_downrate(self,downrate):
        self.downrate=downrate

    def set_uprate(self,uprate):
        self.uprate=uprate

    def set_step(self,step):
        self.step=step

    def show_counts(self,count):
        self.text_browser_threads('now count: %d' % count)
#
    def position_keep(self, count1,continus=True,func_scan_lock=None,timer=None):
        count = count1

        self.text_browser_threads('now count: %d' % count)
        self.text_browser_threads('init count: %d' % self.count_init)
        self.text_browser_threads('-----------------')

        if self.count_init == 0:
            self.count_init = count
        elif self.count_init < count and count < self.uprate * self.count_init:
            self.count_init = count
            self.count_init_paste = self.count_init

        if (self.count_init * self.downrate > count) and not self.lock_state:
            self.start_num += 1
        elif (self.count_init * self.downrate < count) and not self.lock_state:
            self.start_num = 0
        # 确保连续两次都小于阈值才使start_num==2

        if (self.start_num == 2) and not self.lock_state:
            self.start_num = 0
            self.text_browser_threads('Lock start')

            self.lock_state = True
            self.position_init = self.pi.getposition()
            self.position_list.append(self.position_init)
            self.PI_axis = 1

        if self.force_start_sign == 1:
            self.force_start_sign=0
            self.text_browser_threads('Force Lock start')
            self.lock_state = True
            self.position_init = self.pi.getposition()
            self.position_list.append(self.position_init)
            self.PI_axis = 1

        if self.lock_state:
            self.count_list.append(count)
            if continus == True:
                self.continus_lock()
            else:
                timer.start(10)
                if self.lock_z_finish == False:
                    self.continus_lock_z()
                else:
                    def func():
                        func_scan_lock()
                        self.init_parameters()
                    thd = threading.Thread(target=func)
                    thd.daemon = True
                    thd.start()

    def continus_lock(self):
        try:
            bool1 = (self.count_list[-3] > self.count_list[-2]) and (self.count_list[-3] > self.count_list[-1])
        except:
            bool1 = False

        if bool1:
            self.pi.position_move(self.position_list[-3])

            self.PI_axis += 1
            self.PI_axis = self.PI_axis % 7

        self.text_browser_threads('lock lock!!: %d' % self.PI_axis)

        if self.PI_axis == 0:
            self.text_browser_threads('lock stop!')
            if (self.count_list[-3] < self.uprate * self.count_init_paste) and \
                    (self.count_list[-3] > self.downrate * self.count_init_paste):
                self.count_init = self.count_list[-3]
                self.lock_num = 0
            else:
                self.lock_num += 1  # 记录锁点不够成功的次数

            if self.lock_num == 5:
                self.count_init = self.count_list[-3]
                self.lock_num = 0

            self.count_list = []
            self.lock_state = False
            self.position_list = []

        elif self.PI_axis == 1:
            self.pi.r_position_move_z(self.step)
            pp = self.pi.getposition()
            self.position_list.append(pp)

        elif self.PI_axis == 2:
            self.pi.r_position_move_z(-self.step)
            pp = self.pi.getposition()
            self.position_list.append(pp)

        elif self.PI_axis == 3:
            pp = self.pi.getposition()
            pp['1'] = pp['1'] + self.step
            if pp['1'] > 100:
                self.PI_axis += 1
            else:
                self.pi.r_position_move_x(self.step)
                self.position_list.append(pp)

        elif self.PI_axis == 4:
            pp = self.pi.getposition()
            pp['1'] = pp['1'] - self.step
            if pp['1'] < 0:
                self.PI_axis += 1
            else:
                self.pi.r_position_move_x(-self.step)
                self.position_list.append(pp)

        elif self.PI_axis == 5:
            pp = self.pi.getposition()
            pp['2'] = pp['2'] + self.step
            if pp['2'] > 100:
                self.PI_axis += 1
            else:
                self.pi.r_position_move_y(self.step)
                self.position_list.append(pp)

        elif self.PI_axis == 6:
            pp = self.pi.getposition()
            pp['2'] = pp['2'] - self.step
            if pp['2'] < 0:
                self.PI_axis += 1
            else:
                self.pi.r_position_move_y(- self.step)
                self.position_list.append(pp)

    def continus_lock_z(self):
        try:
            bool1 = (self.count_list[-3] > self.count_list[-2]) and (self.count_list[-3] > self.count_list[-1])
        except:
            bool1 = False

        if bool1:
            self.pi.position_move(self.position_list[-3])

            self.PI_axis += 1
            self.PI_axis = self.PI_axis % 3

        self.text_browser_threads('lock lock!!: %d' % self.PI_axis)

        if self.PI_axis == 0:
            self.text_browser_threads('lock z finished!')
            self.text_browser_threads('Scan lock start!')
            if (self.count_list[-3] < self.uprate * self.count_init_paste) and \
                    (self.count_list[-3] > self.downrate * self.count_init_paste):
                self.count_init = self.count_list[-3]
                self.lock_num = 0
            else:
                self.lock_num += 1  # 记录锁点不够成功的次数

            if self.lock_num == 5:
                self.count_init = self.count_list[-3]
                self.lock_num = 0

            self.count_list = []
            self.lock_z_finish = True
            self.position_list = []

        elif self.PI_axis == 1:
            self.pi.r_position_move_z(self.step)
            pp = self.pi.getposition()
            self.position_list.append(pp)

        elif self.PI_axis == 2:
            self.pi.r_position_move_z(-self.step)
            pp = self.pi.getposition()
            self.position_list.append(pp)






# aa = Lock()
# print(aa.getposition())