from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import datetime
import pandas as pd
import time
import traceback
from util.const import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._make_kiwoom_instance()
        self._set_signal_slots()
        self._comm_connect()

        # 계좌번호 저장 (모의투자:8xxxxxxxx, 실계좌: 5xxxxxxxx)
        self.account_number = self.get_account_number()

        # TR 응답 대기에 사용할 변수
        self.tr_event_loop = QEventLoop()

        # 당일 전체 주문 목록
        self.order = {}

        # 유니버스 종목의 실시간 데이터 정보
        self.universe_realtime_transaction_info = {}

    def _make_kiwoom_instance(self):
        """Kiwoom API 사용을 등록하는 함수"""
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        """API로 보내는 요청들을 받아올 slot을 등록하는 함수"""

        # 로그인 응답의 결과를 _on_login_connect을 통해 받도록 설정
        self.OnEventConnect.connect(self._login_slot)

        # TR의 응답결과를 _on_receive_tr_data을 통해 받도록 설정
        self.OnReceiveTrData.connect(self._on_receive_tr_data)

        # 주문체결 결과를 _on_chejan_slot을 통해 받도록 설정
        self.OnReceiveChejanData.connect(self._on_chejan_slot)

        # 실시간 데이터를 _on_receive_real_data을 통해 받도록 설정
        self.OnReceiveRealData.connect(self._on_receive_real_data)

    def _login_slot(self, err_code):
        """로그인 응답의 결과를 얻는 함수"""
        if err_code == 0:
            print("connected")
        else:
            print("not connected")

        # 로그인 응답대기 종료
        self.login_event_loop.exit()

    def _comm_connect(self):
        """로그인 요청 시그널을 보낸 이후 응답대기 설정하는 함수 => 로그인 함수"""
        self.dynamicCall("CommConnect()")

        # 로그인 응답대기 시작
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def get_account_number(self, tag="ACCNO"):
        """계좌번호 얻어오는 함수"""
        print("[Kiwoom] get_account_number starts!")
        account_list = self.dynamicCall("GetLoginInfo(QString)", tag)  # tag로 전달한 요청에 대한 응답을 받아옴
        account_number = account_list.split(';')[0]
        print(account_number)
        return account_number

    def get_code_list_by_market(self, market_type):
        """시장내 종목코드 얻어오는 함수"""
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_type)
        code_list = code_list.split(';')[:-1]
        return code_list

    def get_master_code_name(self, code):
        """종목코드를 받아 종목이름을 반환하는 함수"""
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_price_data(self, code):
        """종목의 상장일부터 가장 최근일자까지의 일봉정보를 가져오는 함수"""
        print("[Kiwoom] get_price_data starts!")
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", 0, "0001")

        self.tr_event_loop.exec_()
        ohlcv = self.tr_data

        while self.has_next_tr_data:
            self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", 2, "0001")
            self.tr_event_loop.exec_()

            for key, val in self.tr_data.items():
                ohlcv[key][-1:] = val

        df = pd.DataFrame(ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=ohlcv['date'])

        return df[::-1]

    def get_deposit(self):
        """조회대상 계좌의 예수금을 얻어오는 함수"""
        print("[Kiwoom] get_deposit starts!")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0002")

        self.tr_event_loop.exec_()
        return self.tr_data

    def get_order(self):
        """주문 정보를 얻어오는 함수"""
        print("[Kiwoom] get order starts!")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", "0")
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "0")  # 0:전체, 1:미체결, 2:체결
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")  # 0:전체, 1:매도, 2:매수
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10075_req", "opt10075", 0, "0002")

        self.tr_event_loop.exec_()
        return self.tr_data

    def get_position(self):
        """계좌의 포지션을 얻어오는 함수"""
        print("[Kiwoom] get_position starts!")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0002")

        self.tr_event_loop.exec_()
        return self.tr_data

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        print("[Kiwoom] _on_receive_tr_data is called {} / {} / {}".format(screen_no, rqname, trcode))
        tr_data_cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)

        if next == '2':
            self.has_next_tr_data = True
        else:
            self.has_next_tr_data = False

        if rqname == "opt10081_req":
            ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

            for i in range(tr_data_cnt):
                date = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "일자")
                open = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "시가")
                high = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "고가")
                low = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "저가")
                close = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "현재가")
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "거래량")

                ohlcv['date'].append(date.strip())
                ohlcv['open'].append(int(open))
                ohlcv['high'].append(int(high))
                ohlcv['low'].append(int(low))
                ohlcv['close'].append(int(close))
                ohlcv['volume'].append(int(volume))

            self.tr_data = ohlcv

        elif rqname == "opw00001_req":
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, 0, "예수금")
            self.tr_data = int(deposit)
            print(self.tr_data)
        
        elif rqname == "opt10075_req":
            # 당일 주문정보
            self.order = {}

            for i in range(tr_data_cnt):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "종목코드")
                code_name = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "종목명")
                order_number = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "주문번호")  # 유일키, 중요함
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "주문상태")  # 출력: 접수, 확인, 체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "주문가격")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "현재가")
                order_type = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "주문구분")
                left_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "미체결수량")
                executed_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "체결량")
                ordered_at = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "시간")
                fee = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "당일매매수수료")
                tax = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "당일매매세금")

                # 데이터형 변환 및 가공
                code = code.strip()
                code_name = code_name.strip()
                order_number = str(int(order_number.strip()))
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())

                current_price = int(current_price.strip().lstrip('+').lstrip('-'))
                order_type = order_type.strip().lstrip('+').lstrip('-')  # +매수,-매도처럼 +,- 제거
                left_quantity = int(left_quantity.strip())
                executed_quantity = int(executed_quantity.strip())
                ordered_at = ordered_at.strip()
                fee = int(fee)
                tax = int(tax)

                # code를 key값으로 한 dict 변환
                self.order[code] = {
                    '종목코드': code,
                    '종목명': code_name,
                    '주문번호': order_number,
                    '주문상태': order_status,
                    '주문수량': order_quantity,
                    '주문가격': order_price,
                    '현재가': current_price,
                    '주문구분': order_type,
                    '미체결수량': left_quantity,
                    '체결량': executed_quantity,
                    '주문시간': ordered_at,
                    '당일매매수수료': fee,
                    '당일매매세금': tax
                }

            self.tr_data = self.order
            
        elif rqname == "opw00018_req":
            # 보유 종목정보
            self.position = {}

            for i in range(tr_data_cnt):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "종목번호")
                code_name = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "종목명")
                quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "보유수량")
                purchase_price = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i,"매입가")
                return_rate = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i,"수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i,"현재가")
                total_purchase_price = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode,rqname, i, "매입금액")
                available_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname,i, "매매가능수량")

                # 받아온 데이터 형 변환
                code = code.strip()[1:]
                code_name = code_name.strip()
                quantity = int(quantity)
                purchase_price = int(purchase_price)
                return_rate = float(return_rate)
                current_price = int(current_price)
                total_purchase_price = int(total_purchase_price)
                available_quantity = int(available_quantity)

                self.position[code] = {
                    '종목명': code_name,
                    '보유수량': quantity,  # 보유수량
                    '매입가': purchase_price,  # 매입가
                    '수익률': return_rate,  # 수익률(%)
                    '현재가': current_price,  # 현재가
                    '매입금액': total_purchase_price,  # 매입금액
                    '매매가능수량': available_quantity  # 매매가능수량
                }

            print(self.position)
            self.tr_data = self.position

        self.tr_event_loop.exit()
        time.sleep(0.5)

    def _on_chejan_slot(self, s_gubun, n_item_cnt, s_fid_list):
        """
        실시간 체결정보 수신 slot 함수
        s_gubun > 0:주문체결, 1:잔고, 3:특이신호
        s_fid_list > 해당 응답에서 얻을 수 있는 데이터(fid)
        """
        print('_on_chejan_slot')
        print(s_gubun, n_item_cnt, s_fid_list)

        if int(s_gubun) == 0:
            # 9001-종목코드 얻어오기, 종목코드는 A007700처럼 오기 때문에 앞자리를 제거함
            code = self.dynamicCall("GetChejanData(int)", '9001')[1:]

            # order dictionary에 코드정보가 없다면 신규생성
            if code not in self.order.keys():
                self.order[code] = {}

            # 9201;9203;9205;9001;912;913;302;900;901; 이런 식으로 전달되는 fid이 리스트를 ';' 기준으로 구분함
            for fid in s_fid_list.split(";"):
                if fid in FID_CODES:
                    data = self.dynamicCall("GetChejanData(int)", fid)

                    # 데이터에 +,-가 붙어있는 경우 (ex:+매수, -매도) 제거
                    data = data.strip().lstrip('+').lstrip('-')

                    # fid 코드에 해당하는 key값을 찾음(ex: fid=9201 > key:계좌번호)
                    key = FID_CODES[fid]

                    # 수신한 데이터는 전부 문자형인데 문자형 중에 숫자인 항목들(ex:매수가)은 숫자로 변형이 필요함
                    if data.isdigit():
                        data = int(data)

                    print("{}: {}".format(key, data))

                    # 코드를 키값으로 항목들을 저장
                    self.order[code][key] = data

        # 저장한 order 출력
        print(self.order)

        try:
            pass
        except Exception as e:
            print(traceback.format_exc())

    def send_order(self, rqname, screen_no, order_type, code, order_quantity, order_price, order_classification,
                   origin_order_number=""):
        """
          [SendOrder() 함수]
          SendOrder(
          BSTR sRQName, // 사용자 구분명
          BSTR sScreenNo, // 화면번호
          BSTR sAccNo,  // 계좌번호 10자리
          LONG nOrderType,  // 주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
          BSTR sCode, // 종목코드
          LONG nQty,  // 주문수량
          LONG nPrice, // 주문가격
          BSTR sHogaGb,   // 거래구분(혹은 호가구분)은 아래 참고
          BSTR sOrgOrderNo  // 원주문번호입니다. 신규주문에는 공백, 정정(취소)주문할 원주문번호를 입력합니다.
          )

          9개 인자값을 가진 국내 주식주문 함수이며 리턴값이 0이면 성공이며 나머지는 에러입니다.
          1초에 5회만 주문가능하며 그 이상 주문요청하면 에러 -308을 리턴합니다.

          [거래구분]
          모의투자에서는 지정가 주문과 시장가 주문만 가능합니다.
        """
        # 지정가는 사용하지 않을 예정
        if order_classification == "시장가":
            order_classification = '03'
        elif order_classification == "지정가":
            order_classification = '00'

        order_result = self.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [rqname, screen_no, self.account_number, order_type, code, order_quantity, order_price,
             order_classification, origin_order_number])

        return order_result

    def set_real_reg(self, str_screen_no, str_code_list, str_fid_list, str_opt_type):
        """
        :param str_screen_no: 화면번호
        :param str_code_list: 종목코드리스트
        :param str_fid_list: 실시간 FID리스트
        :param str_opt_type: 실시간 등록 타입 0,1 0: 최초등록, 1:추가등록
        :return:
        """
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", str_screen_no, str_code_list, str_fid_list, str_opt_type)

        # request 제한이 있기 때문에 딜레이를 줌
        time.sleep(0.5)

    def _on_receive_real_data(self, s_code, real_type, real_data):
        """실시간 데이터 수신"""
        if real_type == "장시작시간":
            pass

        elif real_type == "주식체결":
            signed_at = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid("체결시간"))  # HHMMSS

            close = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid("현재가"))  # +(-)7000
            close = abs(int(close))

            high = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid('고가'))  # +(-)7000
            high = abs(int(high))

            open = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid('시가'))  # +(-)7000
            open = abs(int(open))

            low = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid('저가'))  # +(-)7000
            low = abs(int(low))

            top_priority_ask = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid('(최우선)매도호가'))  # +(-)7000
            top_priority_ask = abs(int(top_priority_ask))

            top_priority_bid = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid('(최우선)매수호가'))  # +(-)7000
            top_priority_bid = abs(int(top_priority_bid))

            accum_volume = self.dynamicCall("GetCommRealData(QString, int)", s_code, get_fid('누적거래량'))  # 출력 : 77777
            accum_volume = abs(int(accum_volume))

            # code를 key값으로 한 dict 변환
            self.universe_realtime_transaction_info[s_code] = {
                '체결시간': signed_at,
                '현재가': close,
                '고가': high,
                '시가': open,
                '저가': low,
                '(최우선)매도호가': top_priority_ask,
                '(최우선)매수호가': top_priority_bid,
                '누적거래량': accum_volume
            }