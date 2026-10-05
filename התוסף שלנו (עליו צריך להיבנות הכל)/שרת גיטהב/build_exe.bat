@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo(
echo  ==========================================
echo   YoniTube Build Both EXEs
echo  ==========================================
echo(

python --version 2>&1 | find "Python" > nul
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

set MISS=0
:: yt-dlp required | ffmpeg/ffprobe auto-downloaded by server.py at runtime
for %%f in (yt-dlp.exe server.py server_bg.py) do (
    if not exist "%%f" (
        echo MISSING: %%f
        set MISS=1
    )
)
if "%MISS%"=="1" ( pause & exit /b 1 )
set "FF_FLAG="
set "FP_FLAG="
if exist "ffmpeg.exe"  ( set "FF_FLAG=--add-data ffmpeg.exe;."  ) else ( echo NOTE: ffmpeg.exe not found - will be downloaded at first run )
if exist "ffprobe.exe" ( set "FP_FLAG=--add-data ffprobe.exe;." ) else ( echo NOTE: ffprobe.exe not found - will be downloaded at first run )

if exist "yonitube_gui.py" (
    copy /Y "yonitube_gui.py" "yonitube guy.py" > nul 2>&1
    set "GUI=yonitube_gui.py"
) else if exist "yonitube guy.py" (
    set "GUI=yonitube guy.py"
) else (
    echo ERROR: yonitube_gui.py not found
    pause
    exit /b 1
)
echo OK: Using %GUI%

python -m pip install pyinstaller flask flask-cors psutil requests Pillow --quiet 2>nul

set "ICON_FLAG="
if exist "icon.png" (
    python -c "from PIL import Image;img=Image.open('icon.png');img.save('icon.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(256,256)])" 2>nul
)
if exist "icon.ico" set "ICON_FLAG=--icon icon.ico"

set "ARIA_FLAG="
if exist "aria2c.exe" set "ARIA_FLAG=--add-data aria2c.exe;."

echo [1/2] Building YoniTube_Server.exe ...
python -m PyInstaller --onefile --noconsole --name YoniTube_Server %ICON_FLAG% %FF_FLAG% %FP_FLAG% --add-data "yt-dlp.exe;." --add-data "server.py;." %ARIA_FLAG% --hidden-import flask --hidden-import flask_cors --hidden-import flask.json.provider --hidden-import werkzeug --hidden-import psutil --hidden-import multiprocessing --hidden-import queue --hidden-import glob --hidden-import hashlib --collect-all flask --collect-all flask_cors --collect-submodules psutil --collect-submodules werkzeug --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module tkinter --log-level WARN server_bg.py
if errorlevel 1 (
    echo FAILED: YoniTube_Server.exe
    pause
    exit /b 1
)
echo OK: YoniTube_Server.exe

echo [2/2] Building YoniTube.exe ...
python -m PyInstaller --onefile --noconsole --name YoniTube %ICON_FLAG% %FF_FLAG% %FP_FLAG% --add-data "yt-dlp.exe;." --add-data "server.py;." %ARIA_FLAG% --hidden-import flask --hidden-import flask_cors --hidden-import flask.json.provider --hidden-import werkzeug --hidden-import psutil --hidden-import requests --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.font --hidden-import tkinter.filedialog --hidden-import multiprocessing --hidden-import queue --collect-all flask --collect-all flask_cors --collect-submodules psutil --collect-submodules werkzeug --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --log-level WARN "%GUI%"
if errorlevel 1 (
    echo FAILED: YoniTube.exe
    pause
    exit /b 1
)
echo OK: YoniTube.exe

if not exist "dist" mkdir dist

echo @echo off > "dist\register_native_host.bat"
echo chcp 65001 ^> nul >> "dist\register_native_host.bat"
echo cd /d "%%~dp0" >> "dist\register_native_host.bat"
echo set "EXE=%%~dp0YoniTube_Server.exe" >> "dist\register_native_host.bat"
echo set "NM=%%LOCALAPPDATA%%\Google\Chrome\User Data\NativeMessagingHosts" >> "dist\register_native_host.bat"
echo if not exist "%%NM%%" mkdir "%%NM%%" >> "dist\register_native_host.bat"
echo (echo { ^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo   "name": "com.yonitube.server", ^>^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo   "description": "YoniTube Server", ^>^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo   "path": "%%EXE:\=/%%", ^>^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo   "type": "stdio", ^>^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo   "allowed_origins": ["chrome-extension://*/"] ^>^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo }) ^>^> "%%NM%%\com.yonitube.server.json" >> "dist\register_native_host.bat"
echo echo OK: Done. Reload Chrome extension. >> "dist\register_native_host.bat"
echo pause >> "dist\register_native_host.bat"

echo(
echo ==========================================
echo SUCCESS!
echo   dist\YoniTube_Server.exe  (headless - auto-start)
echo   dist\YoniTube.exe         (GUI app)
echo(
echo SETUP:
echo   1. Copy both EXEs to any folder e.g. C:\YoniTube\
echo   2. Run register_native_host.bat once
echo   3. Add YoniTube_Server.exe shortcut to shell:startup
echo ==========================================
echo(
if exist "dist" explorer dist
pause
