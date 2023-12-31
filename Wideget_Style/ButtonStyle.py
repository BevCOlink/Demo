#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: ButtonStyle.py
@time: 2022/4/15/0015 15:30:57
@desc:
'''
style_button_highlight = """
QPushButton {
    font-family: Arial Narrow;
    border-width: 2px;
    font-size:15px;
    border-color:#666666;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #E0F1E0, stop: 0.1 #C1E3C1,
                                stop: 0.49 #A3D6A3, stop: 0.5 #84C884,
                                stop: 1.00 #66BB66)
}
"""

disconected = """
QPushButton {
    font-family: Arial Narrow;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    font-size: 15px;
    background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                      stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                      stop: 1.00 #FF6666)
}
"""
conected = """
QPushButton {
    font-family: Arial Narrow;
    border-width: 2px;
    font-size:15px;
    border-color:#666666;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #E0F1E0, stop: 0.1 #C1E3C1,
                                stop: 0.49 #A3D6A3, stop: 0.5 #84C884,
                                stop: 1.00 #66BB66)
}
"""

style_quit = """
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    font-size: 15px;
    background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                      stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                      stop: 1.00 #FF6666)
}
"""

button_datetime = '''
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: white;
    border-style: solid;
    border-radius: 7;
    font-size: 15px;
    background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                      stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                      stop: 1.00 #FF6666)
}
'''

button_box = '''
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: gray;
    border-style: solid;
    border-radius: 7;
    background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                      stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                      stop: 1.00 #FF6666)
}
'''

button_Small = '''
QPushButton {
    font-family: Arial Narrow;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    font-size: 15px;
    background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                      stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                      stop: 1.00 #FF6666)
}
'''

style_tab_button = """
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0.00 #B8E2EF, stop: 0.1 #A5DBEB,
                                      stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1,
                                      stop: 1.00 #57BCD9)
}
"""

style_tab_new = """
QPushButton {
    font-family: Verdana;
    border-width: 3px;
    border-color: #111111;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #E0F1E0, stop: 0.1 #C1E3C1,
                                stop: 0.49 #A3D6A3, stop: 0.5 #84C884,
                                stop: 1.00 #66BB66)
}
"""

style_tab_old = """
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #B8E2EF, stop: 0.1 #A5DBEB,
                                stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1,
                                stop: 1.00 #57BCD9)
}
"""



style_button_enter_green = """
QPushButton {
    font-family: Verdana;
    border-width: 3px;
    border-color: #111111;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #E0F1E0, stop: 0.1 #C1E3C1,
                                stop: 0.49 #A3D6A3, stop: 0.5 #84C884,
                                stop: 1.00 #66BB66)
}
"""

style_button_enter = """
QPushButton {
    font-family: Verdana;
    border-width: 3px;
    border-color:#111111;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1
                                stop: 0.00 #B8E2EF, stop: 0.1 #A5DBEB,
                                stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1,
                                stop: 1.00 #57BCD9)
}
"""

style_button_leave_green = """
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #E0F1E0, stop: 0.1 #C1E3C1,
                                stop: 0.49 #A3D6A3, stop: 0.5 #84C884,
                                stop: 1.00 #66BB66)
}
"""

style_button_leave = """
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #B8E2EF, stop: 0.1 #A5DBEB,
                                stop: 0.49 #8CD1E6, stop: 0.5 #7BCAE1,
                                stop: 1.00 #57BCD9)
}
"""

style_exit_enter = """
QPushButton {
    font-family: Verdana;
    border-width: 3px;
    border-color: #111111;
    border-style: solid;
    border-radius: 7;
    font-size: 16px;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                stop: 1.00 #FF6666)
}
"""

style_exit_leave = """
QPushButton {
    font-family: Verdana;
    border-width: 2px;
    border-color: #666666;
    border-style: solid;
    border-radius: 7;
    font-size: 16px;
    background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.00 #FFAAAA, stop: 0.1 #FF9999,
                                stop: 0.49 #FF8888, stop: 0.5 #FF7777,
                                stop: 1.00 #FF6666)
}
"""
