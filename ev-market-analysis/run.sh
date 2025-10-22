#!/bin/bash
# run.sh - Linux/macOS 실행 스크립트

echo "🚗 EV Market Analysis Multi-Agent System"
echo "========================================"

# Python 버전 확인
python_version=$(python3 --version 2>&1)
echo "Python Version: $python_version"

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# 패키지 설치 확인
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys!"
    exit 1
fi

# 필수 디렉토리 생성
echo "Setting up directories..."
mkdir -p data/raw data/processed data/cache
mkdir -p outputs/market_analysis outputs/consumer_insights outputs/company_analysis
mkdir -p outputs/tech_trends outputs/stock_analysis outputs/charts
mkdir -p reports/daily reports/weekly reports/monthly
mkdir -p configs logs checkpoints

# 실행 모드 선택
echo ""
echo "Select execution mode:"
echo "1) Full Analysis (Complete)"
echo "2) Quick Analysis (Fast)"
echo "3) Test Mode (Minimal)"
echo "4) Monitor Mode (Real-time)"
echo "5) Resume from Checkpoint"
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "Starting Full Analysis..."
        python main.py --mode full
        ;;
    2)
        echo "Starting Quick Analysis..."
        python main.py --mode quick
        ;;
    3)
        echo "Starting Test Mode..."
        python main.py --mode test
        ;;
    4)
        echo "Starting Monitor Mode..."
        python main.py --mode monitor
        ;;
    5)
        echo "Available checkpoints:"
        ls -la checkpoints/*.json 2>/dev/null
        read -p "Enter checkpoint file name: " checkpoint
        python main.py --resume "checkpoints/$checkpoint"
        ;;
    *)
        echo "Invalid choice. Starting default mode..."
        python main.py
        ;;
esac

echo ""
echo "✅ Analysis Complete!"
echo "📊 Check 'reports/' directory for results"

---

@echo off
REM run.bat - Windows 실행 스크립트

echo 🚗 EV Market Analysis Multi-Agent System
echo ========================================

REM Python 버전 확인
python --version

REM 가상환경 확인 및 활성화
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM 패키지 설치 확인
echo Checking dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM 환경 변수 확인
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your API keys!
    pause
    exit /b 1
)

REM 필수 디렉토리 생성
echo Setting up directories...
mkdir data\raw 2>nul
mkdir data\processed 2>nul
mkdir data\cache 2>nul
mkdir outputs\market_analysis 2>nul
mkdir outputs\consumer_insights 2>nul
mkdir outputs\company_analysis 2>nul
mkdir outputs\tech_trends 2>nul
mkdir outputs\stock_analysis 2>nul
mkdir outputs\charts 2>nul
mkdir reports\daily 2>nul
mkdir reports\weekly 2>nul
mkdir reports\monthly 2>nul
mkdir configs 2>nul
mkdir logs 2>nul
mkdir checkpoints 2>nul

REM 실행 모드 선택
echo.
echo Select execution mode:
echo 1) Full Analysis (Complete)
echo 2) Quick Analysis (Fast)
echo 3) Test Mode (Minimal)
echo 4) Monitor Mode (Real-time)
echo 5) Resume from Checkpoint
set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" (
    echo Starting Full Analysis...
    python main.py --mode full
) else if "%choice%"=="2" (
    echo Starting Quick Analysis...
    python main.py --mode quick
) else if "%choice%"=="3" (
    echo Starting Test Mode...
    python main.py --mode test
) else if "%choice%"=="4" (
    echo Starting Monitor Mode...
    python main.py --mode monitor
) else if "%choice%"=="5" (
    echo Available checkpoints:
    dir /b checkpoints\*.json 2>nul
    set /p checkpoint="Enter checkpoint file name: "
    python main.py --resume "checkpoints\%checkpoint%"
) else (
    echo Invalid choice. Starting default mode...
    python main.py
)

echo.
echo ✅ Analysis Complete!
echo 📊 Check 'reports/' directory for results
pause