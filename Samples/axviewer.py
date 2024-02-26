import sys 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        # self.ocx.dynamicCall("CommConnect()")
        # self.ocx.OnEventConnect.connect(self.slot_login)

    def slot_login(self, err_code):
        print(err_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()    