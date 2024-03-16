from api.Kiwoom import *
from util.make_up_universe import *
from util.db_helper import *
from util.time_helper import *
from util.notifier import *
import math
import traceback
import logging

class PBC_Buy1st (QThread):
    def __init__(self):
        QThread.__init__(self)
        self.strategy_name = "PBC_Buy1st"
        self.kiwoom = Kiwoom()

        self.logger = logging.getLogger(name='PBC_Buy1st')
        self.logger.setLevel(logging.DEBUG)
        print(self.logger)

        formatter = logging.Formatter('|%(asctime)s||%(name)s||%(levelname)s| %(message)s', datefmt='%Y-%m-%d %H:%M:%S') 

        if self.logger.hasHandlers():            ## 핸들러 존재 여부    
            self.logger.handlers.clear()         ## 핸들러 삭제

    #    stream_handler = logging.StreamHandler()    ## 스트림 핸들러 생성
    #    stream_handler.setFormatter(formatter)      ## 텍스트 포맷 설정
    #    logger.addHandler(stream_handler)           ## 핸들러 등록

        file_handler = logging.FileHandler('test.log', mode='w')  ## 파일 핸들러 생성  mode='a'
        file_handler.setFormatter(formatter)            ## 텍스트 포맷 설정
        self.logger.addHandler(file_handler)                 ## 핸들러 등록

        #for i in range(1, 6):
        #    logger.info(f'{i} 번째 접속')
        import os
        print('current directory:',os.getcwd())
        self.target_items = []
        import csv
        with open('./pbc_1st_sample.csv','r') as f:
            target_item = {
                '종목코드' : "083450",
                'is시가Down'     : False,    #시가 아래로 내려가면 True   ## 확실하게 하기 위해 -1% 이하로 떨어졌다가 올라올때 True
                '주문수량'       : 10,       # 10주, 살수 있는 가격으로 나중에 계산 필요.
                '매수금액'       : 2000000,  # 매수 금액이 필요할 수 있다.  
                'CntAfterOrder'    : 0,        # 매수 후 채결정보 받은 cnt,  매수후 바로 팔지 않도록 사용할 수 있음. 
                'is시가UpAgain'     : False,    #시가 아래로 갔다 올라오면 True
                '목표수익율'        : 2,        # 2% 수익나면 익절 
                '매수시현재가'       : 0,     # 매수 가격
                '매수시저가'        : 0,     # 매수시점 저점 가격 저장으로 매도시 사용 함.
                '체결수신Cnt'       : 0,     # 체결정보 수신 Cnt
                }
        
            reader = csv.DictReader(f)
            for row in reader:
                print ("code", row['종목코드'])
                ti = target_item.copy()

                ti['종목코드'] = row['종목코드']
                
                if row['종목코드']:
                    ti['종목코드'] = ti['종목코드'][1:]
                    self.target_items.append(ti)
        import pprint
        pprint.pprint({ 'self.target_items' : self.target_items})
        # self.target_items[3]
        #quit(0)


        # 주문할 ticker를 담을딕셔너리
        
        self.logger.info('Target Items')
        for item in self.target_items:
            print(item)
            print(item['종목코드'])
            self.logger.info(f'{item}')
        

        # 계좌 예수금
        self.deposit = 0

        # 초기화 함수 성공 여부 확인 변수
        self.is_init_success = False
        self.stock_account = ""

        self.init_strategy()


    def init_strategy(self):
        """전략 초기화 기능을 수행하는 함수"""
        try:

            # 감시 종목 조회, 없으면 생성
            self.check_and_get_target_items()
            
            #df = self.kiwoom.get_price_data("005930")
            #print(df)

            # Kiwoom > 주문정보 확인
            self.kiwoom.get_order()

            # Kiwoom > 잔고 확인
            self.kiwoom.get_balance()
            self.logger.info('현재 보유 종목: start ------')
            for item in self.kiwoom.balance:
                self.logger.info(f'{self.kiwoom.balance[item]}')
            self.logger.info('현재 보유 종목: end ------')

            accounts = self.kiwoom.GetLoginInfo("ACCNO")

            #self.text_edit.append("계좌번호 :" + accounts.rstrip(';'))

            self.stock_account = accounts.rstrip(';')

            # Kiwoom > 예수금 확인
            self.deposit = self.kiwoom.get_deposit()

            print (accounts)
            send_message_bot(self.stock_account,0)
            send_message_bot(self.deposit,0)
            self.is_init_success = True

        except Exception as e:
            print(traceback.format_exc())
            # LINE 메시지를 보내는 부분
            send_message_bot(traceback.format_exc(), 0)

    def check_and_get_target_items(self):
        """관심종목 존재하는지 확인하고 없으면 생성하는 함수"""
        #fids = get_fid("체결시간") 20 체결시간, 41 호가 정보. 
        fids = "20;41"
        idx = 0
        self.logger.info('체결시간 실시가 요청: start ------')
        for item in self.target_items:
            codes = item['종목코드']
            print ('체결시간 실시간 요청 완료 :', codes)
            self.logger.info(f'종목코드 : {codes}')
            if idx == 0:
                self.kiwoom.set_real_reg("9999", codes, fids, "0")      # "0" 최초, "1" 추가 등록 
                idx = idx + 1
            else:
                self.kiwoom.set_real_reg("9999", codes, fids, "1")      # 첨부터 1이어도 등록한다고는 함. 
        self.logger.info('체결시간 실시가 요청: end ------')
       
    def run(self):
        """실질적 수행 역할을 하는 함수"""
        while self.is_init_success:
            try:
                # (0)장중인지 확인
                if not check_transaction_open():
                    print("장시간이 아니므로 5분간 대기합니다.")
                    # time.sleep(1 * 60)
                    # continue

                for item in self.target_items:
                    #print (code)
                    code = item['종목코드']

                    # (1)접수한 주문이 있는지 확인
                    if code in self.kiwoom.order.keys():
                        # (2)주문이 있음
                        # print('접수 주문', self.kiwoom.order[code])
                        self.logger.info(f'접수주문(kiwoom.order) : {self.kiwoom.order[code]}')

                        # (2.1) '미체결수량' 확인하여 미체결 종목인지 확인
                        if self.kiwoom.order[code]['미체결수량'] > 0:
                            pass
                    if code in self.kiwoom.kiwoom_realtime_hoga_info.keys():
                        self.logger.info(f'호가(kiwoom.hoga) : {self.kiwoom.kiwoom_realtime_hoga_info[code]}')

                    # (3)보유 종목인지 확인
                    if code in self.kiwoom.balance.keys():
                        #print('보유 종목', self.kiwoom.balance[code])
                        print('보유수량', self.kiwoom.balance[code]['보유수량'])
                        # (6)매도 대상 확인
                        if self.kiwoom.balance[code]['보유수량'] > 0:
                            if self.check_sell_signal(code, item):
                                # (7)매도 대상이면 매도 주문 접수
                                # hts에서 매도해 보자. 
                                #print ("call order_sell")
                                self.order_sell(code)

                    else:
                        # (4)접수 주문 및 보유 종목이 아니라면 매수대상인지 확인 후 주문접수
                        self.check_buy_signal_and_order(code,item)

                    time.sleep(0.3)
                    # Kiwoon.py  에서 받은 json 의 값을 하나하나씩 적용하는 것만 여기 추가하면 됨
                    # 우리가 수행할때는 --localtest 일 경우 이 내용이 수행되게 하면 좋을 것임.
            except Exception as e:
                print(traceback.format_exc())
                # telegram 메시지를 보내는 부분
                send_message_bot(traceback.format_exc(), 0)

    def check_sell_signal(self, code, item):
        """매도대상인지 확인하는 함수"""
        #universe_item = self.universe[code]

        # (1)현재 체결정보가 존재하지 않는지 확인
        if code not in self.kiwoom.universe_realtime_transaction_info.keys():
            # 체결 정보가 없으면 더 이상 진행하지 않고 함수 종료
            print("매도대상 확인 과정에서 아직 체결정보가 없습니다.")
            return
        
        # (2)실시간 체결 정보가 존재하면 현시점의 시가 / 고가 / 저가 / 현재가 / 누적 거래량이 저장되어 있음
        open = self.kiwoom.universe_realtime_transaction_info[code]['시가']
        high = self.kiwoom.universe_realtime_transaction_info[code]['고가']
        low = self.kiwoom.universe_realtime_transaction_info[code]['저가']
        close = self.kiwoom.universe_realtime_transaction_info[code]['현재가']
        volume = self.kiwoom.universe_realtime_transaction_info[code]['누적거래량']

        # 오늘 가격 데이터를 과거 가격 데이터(DataFrame)의 행으로 추가하기 위해 리스트로 만듦
        today_price_data = [open, high, low, close, volume]
        #print (today_price_data)

        self.logger.info(f'실시간 체결정보: check_sell {code} 시가 {open}, 고가 {high}, 저가 {low}, 현재가 {close}, 누적거래량 {volume}')

        # 사자마자 팔지 않도록 조치가 필요하다. (때로는)
        item['CntAfterOrder'] = item['CntAfterOrder'] + 1
        if item['CntAfterOrder'] < 10:      #10번정도 체결정보를 받은 후 결정.
            print ("매수한지 얼마 안되었다 조금 기다리자. ")
            return False
        
        # 다시 시가 아래로 내려가면 매도 (손절)
        # 시가 아래로 내려오면 (50% 매도), 매수 할 당시의 저가를 내려가면 나머지 50% 매도 할 수도 있다. 
        if close < (open - ((open * 1) / 100)): 
            print ("시가아래로 내려감 ! 손절!!! -1% ")
            return True
        
        #수익보고 익절 해야 함. (익절)
        if close > (open + ((open * item['목표수익율']) / 100)):
            print ("익절... 조건은 시가에 샀다고 치고..  내려감 ! 손절!!!")
            return True

        return False

    def order_sell(self, code):
        """매도 주문 접수 함수"""
        # 보유 수량 확인(전량 매도 방식으로 보유한 수량을 모두 매도함)
        quantity = self.kiwoom.balance[code]['보유수량']

        # 최우선 매도 호가 확인
        ask = self.kiwoom.universe_realtime_transaction_info[code]['(최우선)매도호가']

        order_result = self.kiwoom.send_order('send_sell_order', '1001', 2, code, quantity, ask, '03', '00')

        # LINE 메시지를 보내는 부분
        message = "[{}]sell order is done! quantity:{}, ask:{}, order_result:{}".format(code, quantity, ask,
                                                                                        order_result)
        send_message_bot(message, 0)
        self.logger.info(f'{message}')

    def check_buy_signal_and_order(self, code, item):
        """매수 대상인지 확인하고 주문을 접수하는 함수"""

        # 매수 가능 시간 확인
       # if not check_adjacent_transaction_closed():
        #    return False
        
        print (item['종목코드'], "시가 아래: ",  item['is시가Down'])

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

        self.logger.info(f'실시간 체결정보: check_buy {code} 시가 {open}, 고가 {high}, 저가 {low}, 현재가 {close}, 누적거래량 {volume}')

        """ 매수조건
        1. 현재가가 시가 아래로 내렸갔다 올라와야 한다. 
        2. 매수는 한종목 당 일일 1번만 한다. 
        """
        if item['CntAfterOrder'] >= 1:
            print ("오늘 한번 매수 했음")
            return

        #if close < open:
            # 시가 아래로 내려 갔다.
        #    if item['is시가Down'] is not True:
        #        item['is시가Down'] = True
        #    pass    
        if close < (open - ((open * 1) / 100)):
            if item['is시가Down'] is not True:
                item['is시가Down'] = True
            pass

        # item['is시가Down'] = True      # test
        if close >= open:   #현재가가 시가보다 크거나 같으면.. (상승)
            if item['is시가Down'] is True:
                # 다시 올라오면 매수. 
                item['is시가UpAgain'] = True
                item['CntAfterOrder'] = 1           # 1이상이면 매수했다는 의미
                item['매수시현재가'] = close
                item['매수시저가'] = low
                # 주문 수량
                quantity = item['주문수량']
                bid = close         # 시장가 매수라 영향은 없을 것 같다. 

                # (9)계산을 바탕으로 지정가(00), 시장가(03) 매수 주문 접수
                order_result = self.kiwoom.send_order('send_buy_order', '1001', 1, code, quantity, bid, '03')
                print(order_result)

                # _on_chejan_slot가 늦게 동작할 수도 있기 때문에 미리 약간의 정보를 넣어둠
                self.kiwoom.order[code] = {'주문구분': '매수', '미체결수량': quantity}

                # Telegram 메시지를 보내는 부분
                message = "[{}]buy order is done! quantity:{}, bid:{}, order_result:{}, deposit:{}, get_balance_count:{}, get_buy_order_count:{}, balance_len:{}".format(
                    code, quantity, bid, order_result, self.deposit, self.get_balance_count(), self.get_buy_order_count(),
                    len(self.kiwoom.balance))
                send_message_bot(message, 0)
                self.logger.info(f'{message}')
            else:
                print ("시가 아래로 내려온적이 없음")        
    
    def get_balance_count(self):
        """매도 주문이 접수되지 않은 보유 종목 수를 계산하는 함수"""
        balance_count = len(self.kiwoom.balance)
        # kiwoom balance에 존재하는 종목이 매도 주문 접수되었다면 보유 종목에서 제외시킴
        for code in self.kiwoom.order.keys():
            if code in self.kiwoom.balance and self.kiwoom.order[code]['주문구분'] == "매도" and self.kiwoom.order[code]['미체결수량'] == 0:
                balance_count = balance_count - 1
        return balance_count

    def get_buy_order_count(self):
        """매수 주문 종목 수를 계산하는 함수"""
        buy_order_count = 0
        # 아직 체결이 완료되지 않은 매수 주문
        for code in self.kiwoom.order.keys():
            if code not in self.kiwoom.balance and self.kiwoom.order[code]['주문구분'] == "매수":
                buy_order_count = buy_order_count + 1
        return buy_order_count
