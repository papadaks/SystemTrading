# 쉽게 따라 만드는 주식자동매매시스템

# git hub 사용법
https://technote.kr/353


# 환경설정
windows 
- anaconda 설치 (kiwoom api는 32bits) : 64bits용으로 설치하였음. 
-- conda 가상 환경을 만들고 32bits로 변경할 수 있음. 
-- https://separang.tistory.com/107 
-- conda create -n '가상환경 이름'  // 예 py38_32
-- conda activate '가상환경 이름'
-- conda config --env --set subdir win-32
-- conda install python=3.8        // 가상환경 안에서 설치해야 함. 
-- conda info
-- python (32bits 확인)
-- import platform
-- print(Platform.architecture())
- 코드 실행시 발행하는 에러는 pip install로 설치하면 됨. 

- vscode 설치
https://code.visualstudio.com/download

- PyQt5
Kiwoom API는 ActiveX Control인 OCX방식으로 연결하게 되어 있음. (32bits)
(base) conda env list
(base) conda activate py38_32
(py38_32) pip install pyqt5 

- 키움 API 
https://www.kiwoom.com/h/customer/download/VOpenApiInfoView?dummyVal=0
pykiwoom은 계속해서 업데이트 되고 있는 모듈입니다. 한 번 설치한 후에도 최신 버전이 나왔다면 여러분도 새로 설치를 해야합니다. 기존에 설치된 버전을 지우고 새로 설치하려면 아나콘다 프롬프트를 실행한 후 다음과 같이 입력하면 됩니다.
pip install -U pykiwoom
최근 버전은 다음 웹 페이지를 통해 확인할 수 있습니다.
https://pypi.org/project/pykiwoom/



- System Trading 구조
|--- api package
|------ __init__.py  // api 폴더가 package임을 표시한 빈파일
|------ Kiwoom.py 
|--- util package
|------ __init__.py
|--- strategy package
|------ __init__.py
---- main.py


- 실현 계획
1) 관심종목 리스트를 화면에 보여주기 (csv 파일로 읽어오는게 빠를것 같다)
2) 관심종목별 시가를 확인하고, 장 시작 후 시가 아래로 갔다가 시가를 돌파할때 1차 매수 하기. 



- 참고사이트
https://wikidocs.net/book/1173  // 퀀트투자를 위한 키움증권 API (파이썬 버전)
https://doc.qt.io/qtforpython-6/examples/example_axcontainer_axviewer.html  // Qt for python, win32지원 안함. pyQt5로해야 함.
https://doc.qt.io/qt-5/reference-overview.html 
https://doc.qt.io/qtforpython-5/gettingstarted.html 
https://trustyou.tistory.com/  // 참고사이트