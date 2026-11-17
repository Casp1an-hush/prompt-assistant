@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "URL=http://localhost:8000"

rem 健康判据：必须读到完整的 </html>。不能只看 HTTP 200 或 /api/health，
rem 半死的服务会回头不回身体，浏览器就白屏。

call :page_ok
if not errorlevel 1 (
  start "" "%URL%"
  exit /b 0
)

rem 端口被占但页面不完整 → 只清本项目的 uvicorn/python，绝不误杀别的程序
set "PORT_BUSY="
for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /C:"LISTENING" ^| findstr /C:":8000 "') do set "PORT_BUSY=%%P"
if defined PORT_BUSY (
  for /f "tokens=5" %%P in ('netstat -ano -p tcp ^| findstr /C:"LISTENING" ^| findstr /C:":8000 "') do (
    call :kill_if_ours %%P
    if errorlevel 1 exit /b 1
  )
  echo 正在等待端口释放…
  for /L %%i in (1,1,5) do (
    set "STILL="
    for /f "tokens=5" %%Q in ('netstat -ano -p tcp ^| findstr /C:"LISTENING" ^| findstr /C:":8000 "') do set "STILL=%%Q"
    if not defined STILL goto :port_free
    timeout /t 1 /nobreak >nul
  )
  echo 8000 端口未能及时释放，启动中止，请稍后重试。
  pause
  exit /b 1
)
:port_free

rem 首次运行：自动准备环境
if not exist ".venv\Scripts\python.exe" (
  echo 首次运行，正在准备环境（约 1 分钟）…
  set "PYCMD="
  where py >nul 2>&1 && set "PYCMD=py -3"
  if not defined PYCMD (
    where python >nul 2>&1 && set "PYCMD=python"
  )
  if not defined PYCMD (
    echo 没找到 Python 3，请先安装 Python 3.10+ 并勾选 Add to PATH。
    pause
    exit /b 1
  )
  %PYCMD% -m venv .venv
  if errorlevel 1 (
    echo 创建虚拟环境失败。
    pause
    exit /b 1
  )
  ".venv\Scripts\pip.exe" install -q -r requirements.txt
  if errorlevel 1 (
    echo 安装依赖失败，检查网络后重试。
    pause
    exit /b 1
  )
)

rem 还没配 key：交互式询问并校验，避免用户手动复制 .env
if not exist ".env" (
  echo.
  echo ============================================
  echo   第一次使用，需要填一次 DeepSeek 的 key
  echo ============================================
  echo.
  echo key 是一串以 sk- 开头的英文字母和数字，
  echo 没有中文、没有空格，长度大约 30 多个字符。
  echo 获取方法：浏览器打开 https://platform.deepseek.com
  echo   登录 → 左侧 API keys → 创建 → 复制那串 sk-xxx
  echo.
  :ask_key
  set "RAWKEY="
  set /p "RAWKEY=把 key 粘贴到这里，然后按回车："
  rem PowerShell 会把中文/空格/引号/全角符号全部过滤掉，只留字母数字连字符
  for /f "usebackq delims=" %%K in (`powershell -NoProfile -Command "$k=$env:RAWKEY -replace '[^A-Za-z0-9-]',''; Write-Output $k"`) do set "KEY=%%K"
  if not defined KEY (
    echo ⚠️  没有检测到任何有效字符。请重新复制那串 sk- 开头的 key 再粘。
    goto :ask_key
  )
  echo(!KEY!| findstr /R /C:"^sk-" >nul
  if errorlevel 1 (
    echo ⚠️  这串不是以 sk- 开头，不像 DeepSeek 的 key。请确认复制的是 API keys 页面里那一串。
    goto :ask_key
  )
  for /f %%L in ('powershell -NoProfile -Command "('!KEY!').Length"') do set "KLEN=%%L"
  if !KLEN! LSS 20 (
    echo ⚠️  key 太短（只有 !KLEN! 个字符），可能没复制完整。请重新复制完整的一串。
    goto :ask_key
  )
  >.env echo DEEPSEEK_API_KEY=!KEY!
  icacls .env /inheritance:r /grant "%USERNAME%:F" >nul 2>&1
  echo.
  echo ✓ 已保存 key（长度 !KLEN!），开始启动…
  echo.
)

echo 正在启动，浏览器会在服务就绪后自动打开…
echo 用完直接关掉这个窗口即可停止。

rem 后台轮询：就绪才开浏览器（不靠 sleep 猜）；最多等约 30 秒
start /b "" powershell -NoProfile -Command "$u='%URL%'; Add-Type -AssemblyName System.Net.Http; $h=New-Object System.Net.Http.HttpClient; $h.Timeout=[TimeSpan]::FromSeconds(2); for($i=0;$i -lt 120;$i++){ try { $s=$h.GetStringAsync($u+'/').GetAwaiter().GetResult(); if($s -match '</html>'){ Start-Process $u; exit 0 } } catch {}; Start-Sleep -Milliseconds 250 }; exit 1"

".venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
exit /b %errorlevel%

rem ---------- 子程序 ----------
:page_ok
where curl.exe >nul 2>&1
if not errorlevel 1 (
  curl.exe -fsS --max-time 2 "%URL%/" 2>nul | findstr /C:"</html>" >nul
  exit /b %errorlevel%
)
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%/'; if ($r.Content -match '</html>') { exit 0 } else { exit 1 } } catch { exit 1 }"
exit /b %errorlevel%

:kill_if_ours
set "PID=%~1"
set "CMDLINE="
for /f "usebackq delims=" %%C in (`powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter 'ProcessId=%PID%').CommandLine"`) do set "CMDLINE=%%C"
if not defined CMDLINE (
  echo 无法读取进程 %PID% 的命令行，为避免误杀已停止。
  pause
  exit /b 1
)
echo("%CMDLINE%" | findstr /I "python uvicorn" >nul
if errorlevel 1 (
  echo 8000 端口被其他程序占用（PID %PID%: %CMDLINE%），为避免误杀已停止。
  echo 请先手动关闭它，再重新双击启动。
  pause
  exit /b 1
)
echo 检测到旧服务无响应（PID %PID%），正在清理…
taskkill /PID %PID% /F >nul 2>&1
exit /b 0
