import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from pykiwoom import *
from api.Kiwoom import *
from strategy.PBC_Buy1st import *


form_class = uic.loadUiType("./ui/test.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)
        form_class.__init__(self)

        self.setupUi(self)                              # UI 초기값 셋업 반드시 필요

        """
        Qt UI connect 
        """
        self.testBtn.clicked.connect(self.btnClick)
        
        #self.setGeometry(300, 300, 300, 300)
        #self.setWindowTitle("GoodToo Ver0.9")

        #self.kiwoom = Kiwoom()
        #self.kiwoom.CommConnect(self.callback_login)
        """
        전략 Thread 시작
        """
        self.pcb1st_strategy = PBC_Buy1st(self)
        self.pcb1st_strategy.start()                    # start run() func

    def btnClick(self):
        ticker = self.lineEditTicker.text()
        print("버튼이 클릭되었습니다.", ticker)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()