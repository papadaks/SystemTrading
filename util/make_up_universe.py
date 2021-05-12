import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime

BASE_URL = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='
# CODES = {0: 'KOSPI', 1: 'KOSDAQ'}
CODES = {0: 'KOSPI'}
START_PAGE = 1
fields = []
now = datetime.now()
formattedDate = now.strftime("%Y%m%d")


def get_universe():

    # CODES는 KOSPI, KOSDAQ 모두를 대상으로 유니버스를 구성하고 싶은 경우 사용, 현재는 KOSPI만 대상
    for code in CODES.keys():

        # total_page을 가져오기 위한 requests
        res = requests.get(BASE_URL + str(code) + "&page=" + str(START_PAGE))
        page_soup = BeautifulSoup(res.text, 'lxml')

        # total_page 가져오기
        total_page_num = page_soup.select_one('td.pgRR > a')
        total_page_num = int(total_page_num.get('href').split('=')[-1])

        # 가져올 수 있는 항목명들을 추출
        ipt_html = page_soup.select_one('div.subcnt_sise_item_top')

        # fields라는 변수에 담아 다른 곳에서도 사용할 수 있도록 global 키워드를 붙임
        global fields
        fields = [item.get('value') for item in ipt_html.select('input')]

        # page마다 정보를 긁어오게끔 하여 result에 저장
        result = [crawler(code, str(page)) for page in range(1, total_page_num + 1)]

        # page마다 가져온 정보를 df에 하나로 합침
        df = pd.concat(result, axis=0, ignore_index=True)

        df.to_excel('NaverFinance.xlsx')

        # Naver Finance에서 긁어온 종목들을 바탕으로 유니버스 구성
        # N/A로 값이 없는 필드 0으로 채우기
        mapping = {',': '', 'N/A': '0'}
        df.replace(mapping, regex=True, inplace=True)

        # 사용할 column들 설정
        cols = ['거래량', '매출액', '매출액증가율', 'ROE', 'PBR', 'PER']

        # column들을 숫자타입으로 변환(Naver Finance에서 제공 받은 원래 데이터는 str 형태)
        df[cols] = df[cols].astype(float)

        '''
        1. 거래량, 매출액이 0보다 크다 > 거래중지 및 우선주, ETF 제외 필터
        2. 매출액증가율이 0보다 큰 종목
        3. ROE, PBR이 0보다 큰 종목(이 지표들은 낮을수록 좋은 것으로 알려져 게산해다가는 -인 값들도 포함하게 되므로)
        4. 종목명이 지주사(홀딩스)인 데이터 제외 
        '''
        df = df[(df['거래량'] > 0) & (df['매출액'] > 0) & (df['매출액증가율'] > 0) & (df['ROE'] > 0) & (df['PBR'] > 0) & (df['PER'] > 0) & (~df.종목명.str.contains("지주")) & (~df.종목명.str.contains("홀딩스"))]

        # PER의 역수
        df['1/PER'] = 1 / df['PER']

        # ROE의 순위 계산
        df['RANK_ROE'] = df['ROE'].rank(method='max', ascending=False)  # ROE의 순위

        # 1/PER의 순위 계산
        df['RANK_1/PER'] = df['1/PER'].rank(method='max', ascending=False)  # 1/PER의 순위

        # ROE 순위, 1/PER 순위 합산한 랭킹
        df['RANK_VALUE'] = (df['RANK_ROE'] + df['RANK_1/PER']) / 2  # 합산 랭킹

        df = df.sort_values(by=['RANK_VALUE'])  # 가치평가 순위로 정렬
        df = df.reset_index(drop=True)
        df = df.loc[:49]

        # 엑셀로 내보내기
        df.to_excel('NaverFinance_%s_%s.xlsx' % (CODES[code], formattedDate))
        print(df['종목명'].tolist())
        return df['종목명'].tolist()


def crawler(code, page):

    # get_universe에서 저장한 항목명들 모음
    global fields

    # naver finance에 전달할 값들을 만듬, fieldIds에 먼저 가져온 항목명들을 전달하면 이에 대한 응답을 준다.
    data = {'menu': 'market_sum',
            'fieldIds': fields,
            'returnUrl': BASE_URL + str(code) + "&page=" + str(page)}

    # requests.get 요청대신 post 요청을 보낸다.
    res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data)

    page_soup = BeautifulSoup(res.text, 'lxml')

    # 크롤링할 table html 가져온다. 실질적으로 사용할 부분
    table_html = page_soup.select_one('div.box_type_l')

    # column명을 가공한다.
    header_data = [item.get_text().strip() for item in table_html.select('thead th')][1:-1]

    # 종목명 + 수치 추출 (a.title = 종목명, td.number = 기타 수치)
    inner_data = [item.get_text().strip() for item in table_html.find_all(lambda x:
                                                                          (x.name == 'a' and
                                                                           'tltle' in x.get('class', [])) or
                                                                          (x.name == 'td' and
                                                                           'number' in x.get('class', []))
                                                                          )]

    # page마다 있는 종목의 순번 가져오기
    no_data = [item.get_text().strip() for item in table_html.select('td.no')]
    number_data = np.array(inner_data)

    # 가로x 세로 크기에 맞게 행렬화
    number_data.resize(len(no_data), len(header_data))

    # 한 페이지에서 얻은 정보를 모아 DataFrame로 만들어 리턴
    df = pd.DataFrame(data=number_data, columns=header_data)
    return df


if __name__ == "__main__":
    print('Start!')
    get_universe()
    print('End')
