from api.Kiwoom import *
from util.make_up_universe import *
from util.db_helper import *
from util.time_helper import *
from util.notifier import *
import math
import traceback


class PBC_Buy1st (QThread):
    def __init__(self):
        QThread.__init__(self)
        self.strategy_name = "PBC_Buy1st"
        self.kiwoom = Kiwoom()

        # 유니버스 정보를 담을 딕셔너리
        self.target_items = {}

        # 계좌 예수금
        self.deposit = 0

        # 초기화 함수 성공 여부 확인 변수
        self.is_init_success = False
        self.stock_account = ""
        self.stock_code = "005930"  #삼전

        self.init_strategy()

    def check_and_get_target_items(self):
        """관심종목 존재하는지 확인하고 없으면 생성하는 함수"""
       # target_items[code] = "000270"   #kia
       # print(self.target_items)

    def init_strategy(self):
        """전략 초기화 기능을 수행하는 함수"""
        try:

            # 감시 종목 조회, 없으면 생성
            self.check_and_get_target_items()

            # Kiwoom > 잔고 확인
            self.kiwoom.get_balance()
            # Kiwoom > 예수금 확인
            self.deposit = self.kiwoom.get_deposit()

            # 주식계좌
            accounts = self.kiwoom.GetLoginInfo("ACCNO")

            #self.text_edit.append("계좌번호 :" + accounts.rstrip(';'))

            self.stock_account = accounts.rstrip(';')

            print (accounts)
            send_message_bot(self.stock_account,0)
            send_message_bot(self.deposit,0)
            self.is_init_success = True

        except Exception as e:
            print(traceback.format_exc())
            # LINE 메시지를 보내는 부분
            send_message_bot(traceback.format_exc(), 0)

    def run(self):
        """실질적 수행 역할을 하는 함수"""
        while self.is_init_success:
            try:
                # (0)장중인지 확인
                if not check_transaction_open():
                    print("장시간이 아니므로 5분간 대기합니다.")
                    time.sleep(1 * 60)
                    continue


                time.sleep(0.5)
            except Exception as e:
                print(traceback.format_exc())
                # LINE 메시지를 보내는 부분
                send_message_bot(traceback.format_exc(), 0)

    def check_buy_signal_and_order(self, code):
        """매수 대상인지 확인하고 주문을 접수하는 함수"""

        # 매수 가능 시간 확인
        if not check_adjacent_transaction_closed():
            return False
        
        # (1)현재 체결정보가 존재하지 않는지 확인
        if code not in self.kiwoom.universe_realtime_transaction_info.keys():
            # 존재하지 않다면 더이상 진행하지 않고 함수 종료
            print("매수대상 확인 과정에서 아직 체결정보가 없습니다.")
            return
        
        # (2)실시간 체결 정보가 존재하면 현 시점의 시가 / 고가 / 저가 / 현재가 / 누적 거래량이 저장되어 있음
        open = self.kiwoom.universe_realtime_transaction_info[code]['시가']
        high = self.kiwoom.universe_realtime_transaction_info[code]['고가']
        low = self.kiwoom.universe_realtime_transaction_info[code]['저가']
        close = self.kiwoom.universe_realtime_transaction_info[code]['현재가']
        volume = self.kiwoom.universe_realtime_transaction_info[code]['누적거래량']

        # 오늘 가격 데이터를 과거 가격 데이터(DataFrame)의 행으로 추가하기 위해 리스트로 만듦
        today_price_data = [open, high, low, close, volume]
    
