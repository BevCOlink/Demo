import threading
import ctypes
import time
from pyqtgraph.Qt import QtCore


class Thread(QtCore.QThread):
    def __init__(self):
        super(Thread,self).__init__()


    def run(self):
        pass