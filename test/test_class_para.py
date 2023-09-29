#测试
#类中的变量会随着调用次数累积数据
from test_function import a
class test(a):
    def __init__(self):
        super(test, self).__init__()
        self.y=[0]
        self.set()

    def set(self):
        self.x=2

    def plus(self,data):
        self.y.append(data)
        print(self.y)

P=test()
print(P.x)