from SpinCore import spincore
from spinapi import *
import numpy as np

List=[[]]
list1 = [0xF, Inst.CONTINUE, 0, 1 * ms]
list2 = [0x0, Inst.CONTINUE, 0, 1.0 * ms]
list3 = [0x0, Inst.BRANCH, 0, 100.0 * ms]
list4=[0x0, Inst.CONTINUE, 0, 100.0* ms]
for i in np.arange(0,2000,1):
    List[0].append(tuple(list1))
    List[0].append(tuple(list2))




List[0].append(tuple(list3))

sc=spincore()
sc.porgramming_board_v2(List)
sc.start_board()