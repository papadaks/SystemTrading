
var1 = 1
print (type(var1))

var2 = 1.0
print(type(var2))

var3 = 1 + 2j
print(type(var3))

var4 = 'Type?'
print(type(var4))

var5 = True
print(type(var5))

print (var1 + var2 + var3)

test_tuple = (1)
print(type(test_tuple))

test_tuple2 = (2,)
print(type(test_tuple2))


#문자열  '' , ""
var6 = 1
var7 = '1'
txt1 = """10.0
1
200
"""
txt2 = ''' 11.0
2
300
'''
txt3 = '1234567890'
print(txt3[1:9])
print(txt3[2:])
print(txt3[:])

# formatting 
message = "수익률 : {}%".format("10")
print(message)
message2 = "수익류 : {}%, 직전 수익률 : {}%".format(var6, "5")
print(message2)

# tuple- 선언하면, 변경안됨. , list - 선언후에도 변경할 수 있음.
test_tuple2 = (1,2,3)
print(test_tuple2)

test_tuple2 = (1, "hello", 1/4, True)
test_list1 = [1, "hello", 1/4, True]
print(test_tuple2)
print(test_list1)
print(len(test_tuple2))

test_list1.append(4)
print(test_list1)
test_list1[4] = "111"
print(test_list1)
del test_list1[3]
print(test_list1)

#packing , unpacking 
a, b, c, d = test_list1
print(a, b, c, d)

# dictionary
s_price_dict = {'시가': 40000, '종가':40100, '고가': 40500, '저가':39000, '거래량': 1000000000}
print(s_price_dict)
print(s_price_dict['시가'])

print ('52주최고가' in s_price_dict)
print(s_price_dict.keys())
print(s_price_dict.values())

#반복문
i = 0, 1, 3
for i in range(len(i)):
    print(i)
    print("{} * {} = {}".format(2, i, 2*i))

for i in s_price_dict.values():
    print(i)

#break, continue, pass 
    
target_codes = {}
target_codes ['005930'] = {
            '종목코드' : "005930",
            'is시가Down'    : False,   #시가 아래로 내려가면 True
            'is시가UpAgain' : False,   #시가 아래로 갔다 올라오면 True
            '감시시작' : 0,     # 0 감시시작x 1 시작 
            '매수여부' : 0,     # 0 매수안함, 1 매수
            '매도여부' : 0,     # 0 매도안함, 1 매도
            }
print (target_codes)
# print (target_codes['005930'].keys)

# 주문할 ticker를 담을 딕셔너리
target_items = [
            {
            '종목코드' : "041020",
            'is시가Down'    : False,   #시가 아래로 내려가면 True
            'is시가UpAgain' : False,   #시가 아래로 갔다 올라오면 True
            '감시시작' : 0,     # 0 감시시작x 1 시작 
            '매수여부' : 0,     # 0 매수안함, 1 매수
            '매도여부' : 0,     # 0 매도안함, 1 매도
            },
             {
            '종목코드' : "041020",
            'is시가Down'    : False,   #시가 아래로 내려가면 True
            'is시가UpAgain' : False,   #시가 아래로 갔다 올라오면 True
            '감시시작' : 0,     # 0 감시시작x 1 시작 
            '매수여부' : 0,     # 0 매수안함, 1 매수
            '매도여부' : 0,     # 0 매도안함, 1 매도
            },
            ]
for item in target_items:
    print(item)
    print(item['종목코드'])

# universe 딕셔너리의 key값들은 종목코드들을 의미
#codes = universe.keys()

# 종목코드들을 ';'을 기준으로 묶어주는 작업
#codes = ";".join(map(str, codes))

v = (1000 + ((1000 * 2) / 100))
print (v)
v = (1000 - ((1000 * 1) / 100))
print (v)
