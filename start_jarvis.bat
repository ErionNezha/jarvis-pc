@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === JARVIS PC — Nisje me 1 klik ===

if not exist ".env" (
  echo [GABIM] Mungon file-i .env! Kopjo .env.example si .env dhe mbush celesat.
  echo Udhezimet: README-JARVIS-AL.md
  pause
  exit /b 1
)

if not exist ".venv" (
  echo Po krijohet ambienti virtual...
  python -m venv .venv
  if errorlevel 1 (
    echo [GABIM] S'u krijua .venv — kontrollo që Python 3.12 është instaluar.
    pause
    exit /b 1
  )
)
call ".venv\Scripts\activate.bat"

echo.
echo Po instalohen paketat (heren e pare merr disa minuta)...
pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [GABIM] pip install deshtoi — shiko gabimin lart.
  pause
  exit /b 1
)

echo.
echo Po kontrollohen celesat...
python check_keys.py
if errorlevel 1 (
  echo.
  echo Ka problem me celesat - rregullo .env dhe ekzekuto perseri.
  pause
  exit /b 1
)

echo.
echo Po niset workeri i zerit (dritare e re)...
start "JARVIS worker" cmd /k "cd /d "%~dp0" ^& ".venv\Scripts\activate.bat" ^& python agent.py dev"
timeout /t 12 /nobreak >nul

echo Po niset serveri i klientit (dritare e re)...
start "JARVIS client" cmd /k "cd /d "%~dp0" ^& ".venv\Scripts\activate.bat" ^& python token_server.py"
timeout /t 4 /nobreak >nul

echo Po hapet faqja...
start http://localhost:8765/
echo.
echo Gati! Fol me Jarvis nga faqja qe u hap. Prit 30 sekonda per agjentin.
pause
