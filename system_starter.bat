@echo off

:init
@echo Started: %date% %time%
echo init starts
cd C:\Users\82103\PycharmProjects\SystemTrading
call activate system_trading_py38_32
@taskkill /f /im "python.exe"
set loop=0
set max_loop=900

:loop
set /a loop+=1
echo %loop%
timeout 2 > NUL
if %loop%==%max_loop% goto init
if %loop%==1 goto starter
if not %loop%==1 goto loop

:starter
start python main.py
timeout 10 > NUL
goto loop
