import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime

BASE_URL = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='
CODES = [0, 1]  # KOSPI:0, KOSDAQ:1
START_PAGE = 1
fields = []
now = datetime.now()
formattedDate = now.strftime("%Y%m%d")


def execute_crawler():
    # KOSPI, KOSDAQ 종목을 하나로 합치는데 사용할 변수
    df_total = []

    # CODES에 담긴 KOSPI, KOSDAQ 종목 모두를 크롤링하기 위해 for문을 사용
    for code in CODES:

        # 전체 페이지 개수를 가져오기 위한 코드
        res = requests.get(BASE_URL + str(CODES[0]))
        page_soup = BeautifulSoup(res.text, 'lxml')

        # '맨뒤'에 해당하는 태그를 기준으로 전체 페이지 개수 추출하기
        total_page_num = page_soup.select_one('td.pgRR > a')
        total_page_num = int(total_page_num.get('href').split('=')[-1])

        # 조회할 수 있는 항목정보들 추출
        ipt_html = page_soup.select_one('div.subcnt_sise_item_top')

        # 전역변수 fields에 항목들을 담아 다른 함수에서도 접근가능하도록 만듬
        global fields
        fields = [item.get('value') for item in ipt_html.select('input')]

        # page마다 존재하는 모든 종목들의 항목정보를 크롤링해서 result에 저장(여기서 crawler 함수가 한 페이씩 크롤링해오는 역할을 담당)
        result = [crawler(code, str(page)) for page in range(1, total_page_num + 1)]

        # 전체 페이지를 저장한 result를 하나의 데이터프레임으로 만듬
        df = pd.concat(result, axis=0, ignore_index=True)

        # 변수 df는 KOSPI, KOSDAQ별로 크롤링한 종목 정보이고 이를 하나로 합치기 위해 df_total에 추가
        df_total.append(df)

    # df_total를 하나의 데이터프레임으로 만듬
    df_total = pd.concat(df_total)

    # 합친 데이터프레임의 index 번호를 새로 매김
    df_total.reset_index(inplace=True, drop=True)

    # 전체 크롤링 결과를 엑셀 출력
    df_total.to_excel('NaverFinance.xlsx')

    # 크롤링 결과를 반환
    return df_total


def crawler(code, page):

    global fields

    # Naver finance에 전달할 값들 세팅(요청을 보낼 때는 menu, fieldIds, returnUrl을 지정해서 보내야 함)
    data = {'menu': 'market_sum',
            'fieldIds': fields,
            'returnUrl': BASE_URL + str(code) + "&page=" + str(page)}

    # 네이버로 요청을 전달(post방식)
    res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data)

    page_soup = BeautifulSoup(res.text, 'lxml')

    # 크롤링할 table의 html 가져오는 코드(크롤링 대상 요소의 클래스는 브라우저에서 확인)
    table_html = page_soup.select_one('div.box_type_l')

    # column명을 가공
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

    # 가로 x 세로 크기에 맞게 행렬화
    number_data.resize(len(no_data), len(header_data))

    # 한 페이지에서 얻은 정보를 모아 DataFrame로 만들어 반환
    df = pd.DataFrame(data=number_data, columns=header_data)
    return df


def get_universe():
    # 크롤링 결과를 얻어옴
    df = execute_crawler()

    mapping = {',': '', 'N/A': '0'}
    df.replace(mapping, regex=True, inplace=True)

    # 사용할 column들 설정
    cols = ['거래량', '매출액', '매출액증가율', 'ROE', 'PER']

    # column들을 숫자타입으로 변환(Naver Finance를 크롤링해온 데이터는 str 형태)
    df[cols] = df[cols].astype(float)

    # 유니버스 구성 조건 (1)~(4)를 만족하는 데이터 가져오기
    df = df[(df['거래량'] > 0) & (df['매출액'] > 0) & (df['매출액증가율'] > 0) & (df['ROE'] > 0) & (df['PER'] > 0) & (~df.종목명.str.contains("지주")) & (~df.종목명.str.contains("홀딩스"))]

    # PER의 역수
    df['1/PER'] = 1 / df['PER']

    # ROE의 순위 계산
    df['RANK_ROE'] = df['ROE'].rank(method='max', ascending=False)

    # 1/PER의 순위 계산
    df['RANK_1/PER'] = df['1/PER'].rank(method='max', ascending=False)

    # ROE 순위, 1/PER 순위 합산한 랭킹
    df['RANK_VALUE'] = (df['RANK_ROE'] + df['RANK_1/PER']) / 2

    # RANK_VALUE을 기준으로 정렬
    df = df.sort_values(by=['RANK_VALUE'])

    # 필터링한 데이터프레임의 index 번호를 새로 매김
    df.reset_index(inplace=True, drop=True)

    # 상위 200개만 추출
    df = df.loc[:199]

    # 유니버스 생성 결과를 엑셀 출력
    df.to_excel('universe.xlsx')
    return df['종목명'].tolist()


if __name__ == "__main__":
    print('Start!')
    universe = get_universe()
    print(universe)
    print('End')