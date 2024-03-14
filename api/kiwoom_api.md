kiwoom api 사용관련

1. 로그인
- 설치한 API를 사용할 수 있도록 설정 (_make_kiwoom_instance)
- 로그인, 실시간 정보, 기타 제공받을 수 있는 데이터에 대한 응답을 받을 수 있는 slot함수들을 등록합니다. (_set_signal_slots)
- 로그인 요청을 보냅니다. (_comm_connect)
- 로그인 요청에 대한 응답을 _set_signal_slots를 사용하여 등록한 slot(_login_slot)에서 받아 옵니다. 


## 주식체결 + 주식호가잔량
koa.SetRealRemove('ALL', 'ALL')
koa.SetRealReg('0001', '005930', '20;41', '0')
koa.SetRealReg('0001', '093230', '20;41', '1')
# 5930: 주식체결+호가잔량, 093230: 주식체결+호가잔량