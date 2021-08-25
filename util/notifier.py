import requests

TARGET_URL = 'https://notify-api.line.me/api/notify'


def send_message(message, token=None):
    """LINE Notify를 사용한 메세지 보내기"""
    try:
        response = requests.post(
            TARGET_URL,
            headers={
                'Authorization': 'Bearer ' + token
            },
            data={
                'message': message
            }
        )
        status = response.json()['status']
        # 전송 실패 체크
        if status != 200:
            # 에러 발생 시에만 로깅
            raise Exception('Fail need to check. Status is %s' % status)

    except Exception as e:
        raise Exception(e)
