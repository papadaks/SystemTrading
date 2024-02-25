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

- vscode 설치
https://code.visualstudio.com/download

- PyQt5
Kiwoom API는 ActiveX Control인 OCX방식으로 연결하게 되어 있음. (32bits)
(base) conda env list
(base) conda activate py38_32
(py38_32) pip install pyqt5 


- System Trading 구조
|--- api package
|------ __init__.py  // api 폴더가 package임을 표시한 빈파일
|------ Kiwoom.py 
|--- util package
|------ __init__.py
|--- strategy package
|------ __init__.py
---- main.py
