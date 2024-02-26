from strategy.RSIStrategy import *
from strategy.PBC_Buy1st import *
import sys

app = QApplication(sys.argv)

# rsi_strategy = RSIStrategy()
# rsi_strategy.start()

pbc1st_strategy = PBC_Buy1st()
pbc1st_strategy.start()

app.exec_()
