from api.Kiwoom import *
from util.make_up_universe import *
from util.db_helper import *
from util.time_helper import *
from util.notifier import *
import math


class RSIStrategy(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.strategy_name = "RSIStrategy"
        self.kiwoom = Kiwoom()

        # 전략운영에 사용할 변수 모음
        self.universe = {}  # 유니버스 정보

        self.deposit = 0  # 계좌 예수금

        self.is_init_success = False  # 초기화 함수 정상수행 여부 확인변수

        self.init_strategy()

    def init_strategy(self):
        """전략 초기화 기능을 수행하는 함수"""
        try:
            # 유니버스 조회, 없으면 생성
            self.check_and_get_universe()

            # 가격정보 조회, 없으면 생성
            self.check_and_get_price_data()

            # Kiwoom > 주문정보 확인
            self.kiwoom.get_order()

            # Kiwoom > 포지션 확인
            self.kiwoom.get_position()

            # Kiwoom > 예수금 확인
            self.deposit = self.kiwoom.get_deposit()

            # 유니버스 실시간 체결정보 등록
            self.set_universe_real_time()

            # 초기화 정상실행 확인
            self.is_init_success = True
        except Exception as e:
            print(traceback.format_exc())

            # LINE 메시지를 보내는 부분
            send_message(traceback.format_exc(), RSI_STRATEGY_MESSAGE_TOKEN)

    def check_and_get_universe(self):
        """유니버스가 존재하는지 확인하고 없다면 생성하는 함수"""
        if not check_table_exist(self.strategy_name, 'universe'):
            universe_name_list = get_universe()

            universe = {}
            now = datetime.now().strftime("%Y%m%d")

            # KOSPI(0)에 상장된 모든 종목 코드를 가져와 code_list에 저장
            code_list = self.kiwoom.get_code_list_by_market("0")

            # 모든 종목 코드를 바탕으로 반복문 수행
            for code in code_list:
                # 코드 > 종목명을 얻어옴
                code_name = self.kiwoom.get_master_code_name(code)

                # 이렇게 얻어온 종목명이 유니버스에 포함되어 있다면 딕셔너리에 추가
                if code_name in universe_name_list:
                    universe[code] = code_name

            # 유니버스, 코드-종목명으로 구성한 딕셔너리를 DataFrame으로 생성
            universe_df = pd.DataFrame({
                'code': universe.keys(),
                'code_name': universe.values(),
                'created_at': [now] * len(universe.keys())
            })

            # 'universe'라는 테이블명으로 Dataframe을 DB에 삽입함
            insert_df_to_db(self.strategy_name, 'universe', universe_df)

        # 생성한 유니버스가 존재하는 경우
        sql = "select * from universe"
        cur = execute_sql(self.strategy_name, sql)
        universe_list = cur.fetchall()
        for item in universe_list:
            idx, code, code_name, created_at = item
            self.universe[code] = {
                'code_name': code_name
            }
        print(self.universe)

    def check_and_get_price_data(self):
        """일봉 데이터가 존재하는지 확인하고 없다면 생성하는 함수"""
        for idx, code in enumerate(self.universe.keys()):
            print("({}/{}) {}".format(idx + 1, len(self.universe), code))
            # 가격 데이터가 없는 종목코드인지 확인
            if not check_table_exist(self.strategy_name, code):

                price_df = self.kiwoom.get_price_data(code)
                # code명을 테이블로 Dataframe을 DB에 삽입함
                insert_df_to_db(self.strategy_name, code, price_df)

                # DataFrame을 class 변수, universe에 저장
                self.universe[code]['price_df'] = price_df
            else:
                # 가격 데이터가 있는 경우
                # 1.장종료인 경우(API 호출을 통해 데이터를 받아 저장한다.)
                if check_transaction_closed():
                    # 저장된 가격 데이터 중 가장 최근 일자를 조회한다.
                    sql = "select max(`{}`) from `{}`".format('index', code)
                    cur = execute_sql(self.strategy_name, sql)

                    last_date = cur.fetchone()

                    # 오늘 날짜를 조회
                    now = datetime.now().strftime("%Y%m%d")

                    # 최근 저장일자가 오늘이 아니라면 수행 ( 최근 저장일자 == 오늘 > 오늘 것 저장한 것임)
                    if last_date[0] != now:
                        price_df = self.kiwoom.get_price_data(code)
                        # code명을 테이블로 Dataframe을 DB에 삽입함
                        insert_df_to_db(self.strategy_name, code, price_df)

                # 2.그 외 경우(장 시작 전, 장 중) DB에 저장한 것 그대로 가져온다.
                else:
                    # 생성한 유니버스가 존재하는 경우
                    sql = "select * from `{}`".format(code)
                    cur = execute_sql(self.strategy_name, sql)
                    cols = [column[0] for column in cur.description]

                    # DB에서 조회한 데이터를 DataFrame으로 만듬
                    # 조회한 값을 DataFrame로 만들지 않고 처음부터 DataFrame으로 얻어오는 방법도 존재합니다.
                    # https://stackoverflow.com/questions/36028759/how-to-open-and-convert-sqlite-database-to-pandas-dataframe
                    price_df = pd.DataFrame.from_records(data=cur.fetchall(), columns=cols)
                    price_df = price_df.set_index('index')
                    # DataFrame을 class 변수, universe에 저장
                    self.universe[code]['price_df'] = price_df

                # TEST CODE
                # 조회해옴
                # TODO 지워야 함
                # sql = "select * from `{}`".format(code)
                # cur = execute_sql(self.strategy_name, sql)
                # cols = [column[0] for column in cur.description]
                # # DB에서 조회한 데이터를 DataFrame으로 만듬
                # # 이렇게 할 수도 있지만 execute_sql 이외의 db_helper 코드를 늘이지 않기 위해 https://stackoverflow.com/questions/36028759/how-to-open-and-convert-sqlite-database-to-pandas-dataframe
                # price_df = pd.DataFrame.from_records(data=cur.fetchall(), columns=cols)
                # price_df = price_df.set_index('index')
                # # DataFrame을 class 변수, universe에 저장
                # self.universe[code]['price_df'] = price_df

    def set_universe_real_time(self):
        """유니버스 실시간 체결정보 수신 등록하는 함수"""
        # 임의의 fid를 하나 전달하기 위한 코드(아무 값의 fid라도 하나 이상 전달해야 정보를 얻어올 수 있음)
        fids = get_fid("체결시간")

        # 장운영구분을 확인하고 싶으면 사용할 코드
        # self.kiwoom.set_real_reg("1000", "", get_fid("장운영구분"), "0")

        # universe 딕셔너리의 key값들은 종목코드들을 의미
        codes = self.universe.keys()

        # 종목코드들을 ';'을 기준으로 묶어주는 작업
        codes = ";".join(map(str, codes))

        # ;로 연결한 유니버스의 코드들 출력
        print(codes)

        # 화면번호 9999에 종목코드들의 실시간 체결정보 수신을 요청
        self.kiwoom.set_real_reg("9999", codes, fids, "0")

    def run(self):
        """실질적 수행역할을 하는 함수"""
        while self.is_init_success:
            try:
                # (0)장중인지 확인
                if not check_transaction_open():
                    print("장시간이 아니므로 5분간 대기합니다.")
                    time.sleep(5 * 60)
                    continue

                for idx, code in enumerate(self.universe.keys()):
                    print('[{}/{}_{}]'.format(idx+1, len(self.universe), self.universe[code]['code_name']))
                    time.sleep(0.5)

                    # (1)접수한 주문이 있는지 확인
                    if code in self.kiwoom.order.keys():
                        # (2)주문이 존재
                        print('접수 주문', self.kiwoom.order[code])

                        # (2.1) 미체결 종목인지 확인하는 방법은 '미체결수량' 확인
                        if self.kiwoom.order[code]['미체결수량'] > 0:
                            # do something
                            pass

                    # (3)보유 종목인지 확인
                    elif code in self.kiwoom.position.keys():
                        print('보유 종목', self.kiwoom.position[code])
                        # (6)매도대상 확인
                        if self.check_sell_signal(code):
                            # (7)매도대상이면 매도 주문 접수
                            self.order_sell(code)
                    else:
                        # (4)접수 주문 및 보유 종목이 아니라면 매수대상인지 확인 후 주문접수
                        self.check_buy_signal_and_order(code)

            except Exception as e:
                print(traceback.format_exc())
                # LINE 메시지를 보내는 부분
                send_message(traceback.format_exc(), RSI_STRATEGY_MESSAGE_TOKEN)

    def check_sell_signal(self, code):
        """매도대상인지 확인하는 함수"""
        # (0)현재 시간이 종가부근인지 확인하는 함수
        if not check_adjacent_transaction_closed():
            return False

        universe_item = self.universe[code]

        # (1)현재 체결정보가 존재하지 않는지 확인
        if code not in self.kiwoom.universe_realtime_transaction_info.keys():
            # 존재하지 않다면 더이상 진행하지 않고 함수 종료
            print("매도대상 확인 과정에서 아직 체결정보가 없습니다.")
            return

        df = universe_item['price_df'].copy()

        # (2)체결정보가 존재한다면 현 시점의 시가 / 고가 / 저가 / 현재가 / 누적거래량을 변수에 저장
        open = self.kiwoom.universe_realtime_transaction_info[code]['시가']
        high = self.kiwoom.universe_realtime_transaction_info[code]['고가']
        low = self.kiwoom.universe_realtime_transaction_info[code]['저가']
        close = self.kiwoom.universe_realtime_transaction_info[code]['현재가']
        volume = self.kiwoom.universe_realtime_transaction_info[code]['누적거래량']

        # 리스트를 만들어 담는 이유는 DataFrame의 행으로 추가하기 위함
        today_price_data = [open, high, low, close, volume]

        # 과거 데이터 마지막 행에 금일 데이터 추가
        df.loc[datetime.now().strftime('%Y%m%d')] = today_price_data

        # 종가(close)를 기준으로 이동평균 구하기, 5일이 아니라 다르게 설정하고 싶다면 window=값을 변경
        df['ma5'] = df['close'].rolling(window=5, min_periods=1).mean()

        # RSI(N) 계산
        period = 2  # 기준일 N 설정
        date_index = df.index.astype('str')
        U = np.where(df['close'].diff(1) > 0, df['close'].diff(1), 0)  # df.diff를 통해 (기준일 종가 - 기준일 전일 종가)를 계산하여 0보다 크면 증가분을 감소했으면 0을 넣어줌
        D = np.where(df['close'].diff(1) < 0, df['close'].diff(1) * (-1), 0)  # df.diff를 통해 (기준일 종가 - 기준일 전일 종가)를 계산하여 0보다 작으면 감소분을 증가했으면 0을 넣어줌
        AU = pd.DataFrame(U, index=date_index).rolling(window=period).mean()  # AU, period=2일 동안의 U의 평균
        AD = pd.DataFrame(D, index=date_index).rolling(window=period).mean()  # AD, period=2일 동안의 D의 평균
        RSI = AU / (AD + AU) * 100  # 0부터 1로 표현되는 RSI에 100을 곱함
        df['RSI(2)'] = RSI

        # 보유 종목의 매입가격 구하기
        purchase_price = self.kiwoom.position[code]['매입가']
        # df[-1:]은 제일 마지막 행(금일)을 의미함. 금일의 RSI(2), ma5 구하기
        rsi = df[-1:]['RSI(2)'].values[0]
        ma5 = df[-1:]['ma5'].values[0]

        '''
        매도조건에 맞으면 True 
        (1)현재가 > 5일 이동평균(종가)
        (2)RSI(2) > 80
        (3)현재가 > 매수가
        '''
        if close > ma5 and rsi > 80 and close > purchase_price:
            return True
        else:
            return False

    def order_sell(self, code):
        """매도주문 접수함수"""
        universe_item = self.universe[code]
        code_name = universe_item['code_name']

        # 보유수량 확인(전량매도 방식으로 보유한 수량을 모두 매도주문 함)
        quantity = self.kiwoom.position[code]['보유수량']

        # 최우선 매도호가 확인
        ask = self.kiwoom.universe_realtime_transaction_info[code]['(최우선)매도호가']

        '''
        KOA 가이드를 보면 주문접수가 정상적으로 이루어졌을 때 order_result 값이 0이라 설명하지만
        주문접수가 정상적이지 않을지라도 order_result 값이 0이 될 수 있다. 
        '''
        order_result = self.kiwoom.send_order('send_sell_order', '1001', 2, code, quantity, ask, '00')

        # LINE 메시지를 보내는 부분
        message = "[{}]sell order is done! quantity:{}, ask:{}".format(code_name, quantity, ask)
        send_message(message, RSI_STRATEGY_MESSAGE_TOKEN)

    def get_position_count(self):
        """매도주문 접수되지 않은 보유 종목수를 계산하는 함수"""
        position_count = len(self.kiwoom.position)
        # 보유 포지션으로 kiwoom position에 존재하는 종목이 매도주문 접수 이후 체결이 되었다면 포지션에 제외시킴
        for code in self.kiwoom.order.keys():
            if code in self.kiwoom.position and self.kiwoom.order[code]['주문구분'] == "매도" and self.kiwoom.order[code]['미체결수량'] == 0:
                position_count = position_count - 1
        return position_count

    def get_buy_order_count(self):
        """체결이 다 완료되지 않은 매도주문 종목수를 계산하는 함수"""
        buy_order_count = 0
        # 아직 체결이 완료되지 않은 매수주문
        for code in self.kiwoom.order.keys():
            if code not in self.kiwoom.position and self.kiwoom.order[code]['주문구분'] == "매수":
                buy_order_count = buy_order_count + 1
        return buy_order_count

    def check_buy_signal_and_order(self, code):
        """매수대상인지 확인하고 주문을 접수하는 함수"""
        # 매수가능 시간 확인
        if not check_adjacent_transaction_closed_for_buying():
            return False

        universe_item = self.universe[code]
        code_name = universe_item['code_name']

        # (1)현재 체결정보가 존재하지 않는지 확인
        if code not in self.kiwoom.universe_realtime_transaction_info.keys():
            # 존재하지 않다면 더이상 진행하지 않고 함수 종료
            print("매수대상 확인 과정에서 아직 체결정보가 없습니다.")
            return

        df = universe_item['price_df'].copy()

        # (2)체결정보가 존재한다면 현 시점의 시가 / 고가 / 저가 / 현재가 / 누적거래량을 변수에 저장
        open = self.kiwoom.universe_realtime_transaction_info[code]['시가']
        high = self.kiwoom.universe_realtime_transaction_info[code]['고가']
        low = self.kiwoom.universe_realtime_transaction_info[code]['저가']
        close = self.kiwoom.universe_realtime_transaction_info[code]['현재가']
        volume = self.kiwoom.universe_realtime_transaction_info[code]['누적거래량']

        # 리스트를 만들어 담는 이유는 DataFrame의 행으로 추가하기 위함
        today_price_data = [open, high, low, close, volume]

        # 과거 데이터 마지막 행에 금일 데이터 추가
        df.loc[datetime.now().strftime('%Y%m%d')] = today_price_data

        # 종가(close)를 기준으로 이동평균 구하기
        df['ma20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['ma60'] = df['close'].rolling(window=60, min_periods=1).mean()

        # RSI(N) 계산
        period = 2  # 기준일 N 설정
        date_index = df.index.astype('str')
        U = np.where(df['close'].diff(1) > 0, df['close'].diff(1),0)  # df.diff를 통해 (기준일 종가 - 기준일 전일 종가)를 계산하여 0보다 크면 증가분을 감소했으면 0을 넣어줌
        D = np.where(df['close'].diff(1) < 0, df['close'].diff(1) * (-1),0)  # df.diff를 통해 (기준일 종가 - 기준일 전일 종가)를 계산하여 0보다 작으면 감소분을 증가했으면 0을 넣어줌
        AU = pd.DataFrame(U, index=date_index).rolling(window=period).mean()  # AU, period=2일 동안의 U의 평균
        AD = pd.DataFrame(D, index=date_index).rolling(window=period).mean()  # AD, period=2일 동안의 D의 평균
        RSI = AU / (AD + AU) * 100  # 0부터 1로 표현되는 RSI에 100을 곱함
        df['RSI(2)'] = RSI

        # 2 거래일 전 index를 구함
        idx = df.index.get_loc(datetime.now().strftime('%Y%m%d')) - 2

        # 위 index로부터 2 거래일 전 종가를 얻어옴
        close_days_ago = df.iloc[idx]['close']

        # 2 거래일 전 종가와 현재가를 비교함
        diff_days_ago = (close - close_days_ago) / close_days_ago * 100

        rsi = df[-1:]['RSI(2)'].values[0]
        ma20 = df[-1:]['ma20'].values[0]
        ma60 = df[-1:]['ma60'].values[0]

        # (3)매수신호 확인 (매수조건에 부합한다면 다음 코드로 넘어가 주문접수한다.)
        if close > ma20 > ma60 and rsi < 10 and diff_days_ago < -2:
            now = datetime.now().strftime("%Y%m%d")
            # 매수신호가 들어온 종목 계산식을 엑셀파일 저장 확인
            df.to_excel('[buy_signal]%s_%s.xlsx' % (universe_item['code_name'], now))
        # 매수신호가 없다면 그대로 종료
        else:
            return

        # (4)이미 보유한 종목, 매수주문 접수한 종목의 합이 보유가능 최대치(10개)라면 더이상 매수 불가하므로 종료
        if (self.get_position_count() + self.get_buy_order_count()) >= 10:
            return

        # (5)주문에 사용할 금액 계산 (10은 최대 보유 종목수로써 consts.py에 상수로 만들어 관리하는 것도 좋음)
        budget = round(self.deposit / (10 - (self.get_position_count() + self.get_buy_order_count())))

        # 최우선 매도호가 확인
        bid = self.kiwoom.universe_realtime_transaction_info[code]['(최우선)매수호가']

        # (6)주문수량 계산(소수점은 제거하기 위해 버림 사용)
        quantity = math.floor(budget / bid)

        # (7)주문 주식수량이 1 미만이라면 매수불가하므로 체크
        if quantity < 1:
            return

        # (8)현재 예수금에서 수수료를 곱한 투입금액(주문수량 * 주문가격)을 제외해서 계산
        amount = quantity * bid
        self.deposit = self.deposit - amount * 1.00015

        # (9)예수금이 0보다 작아질 정도로 주문할 수는 없으므로 체크
        if self.deposit < 0:
            return

        '''
        KOA 가이드를 보면 주문접수가 정상적으로 이루어졌을 때 order_result 값이 0이라 설명하지만
        주문접수가 정상적이지 않을지라도 order_result 값이 0이 될 수 있다. 
        '''
        # (9)계산을 바탕으로 지정가 매수주문 접수
        order_result = self.kiwoom.send_order('send_buy_order', '1001', 1, code, quantity, bid, '00')

        # LINE 메시지를 보내는 부분
        message = "[{}]buy order is done! quantity:{}, bid:{}, order_result:{}, deposit:{}".format(code_name, quantity, bid, order_result, self.deposit)
        send_message(message, RSI_STRATEGY_MESSAGE_TOKEN)

        # LINE 메시지 보내는 부분2
        message = "현재 보유 종목수 : {}, 현재 매수주문접수 종목수 : {}".format(self.get_position_count(), self.get_buy_order_count())
        send_message(message, RSI_STRATEGY_MESSAGE_TOKEN)