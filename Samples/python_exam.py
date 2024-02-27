
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