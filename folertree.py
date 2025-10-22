#!/usr/bin/env python3
"""
전기차 시장 분석 Multi-Agent 시스템 프로젝트 구조 생성 스크립트
"""

import os
from pathlib import Path


def create_directory_structure():
    """프로젝트 디렉토리 구조 생성"""
    
    # 프로젝트 루트 디렉토리
    project_root = Path("ev-market-analysis")
    
    # 생성할 디렉토리 목록
    directories = [
        project_root / "agents",
        project_root / "data",
        project_root / "outputs",
        project_root / "reports",
        project_root / "configs",
        project_root / "tests",
        project_root / "logs",
        project_root / "checkpoints",
    ]
    
    # 디렉토리 생성
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ 디렉토리 생성: {directory}")
    
    return project_root


def create_agent_files(project_root):
    """agents 폴더 내 파일들 생성"""
    
    agents_dir = project_root / "agents"
    
    # agents/__init__.py
    init_content = '''"""
전기차 시장 분석 Multi-Agent 시스템
Agents 패키지
"""

from .base_agent import BaseAgent
from .supervisor_agent import SupervisorAgent
from .market_research_agent import MarketResearchAgent
from .consumer_analysis_agent import ConsumerAnalysisAgent
from .company_analysis_agent import CompanyAnalysisAgent
from .tech_analysis_agent import TechAnalysisAgent
from .stock_analysis_agent import StockAnalysisAgent
from .chart_generation_agent import ChartGenerationAgent
from .report_generation_agent import ReportGenerationAgent

__all__ = [
    'BaseAgent',
    'SupervisorAgent',
    'MarketResearchAgent',
    'ConsumerAnalysisAgent',
    'CompanyAnalysisAgent',
    'TechAnalysisAgent',
    'StockAnalysisAgent',
    'ChartGenerationAgent',
    'ReportGenerationAgent',
]
'''
    
    agent_files = {
        "__init__.py": init_content,
        "base_agent.py": "# Base Agent 클래스\n",
        "supervisor_agent.py": "# Supervisor Agent - 전체 워크플로우 조정\n",
        "market_research_agent.py": "# 시장 조사 Agent - 산업 트렌드 및 정책 분석\n",
        "consumer_analysis_agent.py": "# 소비자 분석 Agent - 소비자 패턴 분석\n",
        "company_analysis_agent.py": "# 기업 분석 Agent - 주요 기업 동향 분석\n",
        "tech_analysis_agent.py": "# 기술 분석 Agent - 기술 동향 분석\n",
        "stock_analysis_agent.py": "# 주가 분석 Agent - 주가 및 재무 분석\n",
        "chart_generation_agent.py": "# 차트 생성 Agent - 데이터 시각화\n",
        "report_generation_agent.py": "# 리포트 생성 Agent - 최종 보고서 작성\n",
    }
    
    for filename, content in agent_files.items():
        filepath = agents_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 파일 생성: {filepath}")


def create_main_files(project_root):
    """프로젝트 메인 파일들 생성"""
    
    # main.py
    main_content = '''"""
전기차 시장 분석 Multi-Agent 시스템
메인 실행 파일
"""

import argparse
from graph_builder import build_graph
from state_manager import StateManager


def main():
    parser = argparse.ArgumentParser(description='전기차 시장 분석 시스템')
    parser.add_argument('--mode', type=str, default='quick', 
                       choices=['quick', 'full', 'monitor'],
                       help='실행 모드 선택')
    parser.add_argument('--resume', type=str, default=None,
                       help='체크포인트 파일 경로')
    
    args = parser.parse_args()
    
    print("🚗 전기차 시장 분석 Multi-Agent 시스템 시작")
    print(f"📊 모드: {args.mode}")
    
    # LangGraph 워크플로우 빌드
    graph = build_graph()
    
    # 상태 관리자 초기화
    state_manager = StateManager()
    
    # 시스템 실행
    # TODO: 워크플로우 실행 로직 구현
    
    print("✅ 분석 완료!")


if __name__ == "__main__":
    main()
'''
    
    # graph_builder.py
    graph_content = '''"""
LangGraph 워크플로우 빌드
"""

from langgraph.graph import StateGraph
from typing import TypedDict


class AgentState(TypedDict):
    """Agent 간 공유되는 상태"""
    messages: list
    market_data: dict
    company_data: dict
    consumer_data: dict
    tech_data: dict
    stock_data: dict
    charts: list
    final_report: str


def build_graph():
    """LangGraph 워크플로우 생성"""
    
    workflow = StateGraph(AgentState)
    
    # TODO: 노드 및 엣지 추가
    
    return workflow.compile()
'''
    
    # state_manager.py
    state_content = '''"""
상태 관리 및 체크포인트
"""

import json
from pathlib import Path
from datetime import datetime


class StateManager:
    """시스템 상태 관리 클래스"""
    
    def __init__(self, checkpoint_dir="checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def save_checkpoint(self, state, name=None):
        """체크포인트 저장"""
        if name is None:
            name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = self.checkpoint_dir / f"{name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 체크포인트 저장: {filepath}")
    
    def load_checkpoint(self, filepath):
        """체크포인트 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        print(f"📂 체크포인트 로드: {filepath}")
        return state
'''
    
    # requirements.txt
    requirements_content = '''# 전기차 시장 분석 Multi-Agent 시스템 의존성

# LangChain & LangGraph
langchain>=0.1.0
langgraph>=0.0.20
langchain-openai>=0.0.5

# AI & ML
openai>=1.0.0
anthropic>=0.7.0

# 데이터 처리
pandas>=2.0.0
numpy>=1.24.0

# 웹 스크래핑
beautifulsoup4>=4.12.0
requests>=2.31.0

# 차트 생성
matplotlib>=3.7.0
plotly>=5.14.0
seaborn>=0.12.0

# 주가 데이터
yfinance>=0.2.28

# 리포트 생성
reportlab>=4.0.0
jinja2>=3.1.2

# 환경 변수
python-dotenv>=1.0.0

# 유틸리티
tqdm>=4.65.0
'''
    
    # .env.example
    env_content = '''# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangChain
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=ev-market-analysis

# 기타 설정
LOG_LEVEL=INFO
MAX_RETRIES=3
'''
    
    # README.md
    readme_content = '''# 🚗 전기차 시장 분석 Multi-Agent 시스템

LangGraph 기반 전기차 산업 종합 분석 및 투자 리포트 생성 시스템

## 📋 프로젝트 개요

이 시스템은 여러 개의 전문 AI Agent들이 협력하여 전기차 시장을 다각도로 분석하고, 
투자 인사이트를 제공하는 종합 리포트를 자동으로 생성합니다.

## 🏗️ 시스템 구조

### Agent 구성
- **Supervisor Agent**: 전체 워크플로우 조정
- **Market Research Agent**: 시장 트렌드 및 정책 분석
- **Consumer Analysis Agent**: 소비자 패턴 분석
- **Company Analysis Agent**: 주요 기업 동향 분석
- **Tech Analysis Agent**: 기술 동향 분석
- **Stock Analysis Agent**: 주가 및 재무 분석
- **Chart Generation Agent**: 데이터 시각화
- **Report Generation Agent**: 최종 보고서 작성

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

### 2. 실행
```bash
# 빠른 분석
python main.py --mode quick

# 전체 분석
python main.py --mode full

# 이전 분석 이어서
python main.py --resume checkpoints/checkpoint_xxxxx.json
```

## 📁 프로젝트 구조
```
ev-market-analysis/
├── agents/              # Agent 클래스들
├── data/               # 원본 데이터
├── outputs/            # 중간 결과물
├── reports/            # 최종 리포트
├── configs/            # 설정 파일
├── tests/              # 테스트 코드
├── logs/               # 로그 파일
└── checkpoints/        # 체크포인트
```

## 📊 결과물
- 시장 성장률 예측 차트
- 기업별 경쟁력 분석
- 기술 발전 로드맵
- 투자 추천 및 리스크 분석
- 종합 투자 리포트 (PDF)

## 📝 라이선스
MIT License

## 👥 기여자
프로젝트 팀
'''
    
    # run.sh (Linux/Mac)
    run_sh_content = '''#!/bin/bash
# 전기차 시장 분석 시스템 실행 스크립트 (Linux/Mac)

echo "🚗 전기차 시장 분석 Multi-Agent 시스템"
echo "========================================"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo "📥 의존성 설치 중..."
pip install -r requirements.txt --quiet

# 메인 프로그램 실행
echo "🚀 시스템 시작..."
python main.py "$@"

echo "✅ 완료!"
'''
    
    # run.bat (Windows)
    run_bat_content = '''@echo off
REM 전기차 시장 분석 시스템 실행 스크립트 (Windows)

echo 🚗 전기차 시장 분석 Multi-Agent 시스템
echo ========================================

REM 가상환경 확인
if not exist "venv" (
    echo 📦 가상환경 생성 중...
    python -m venv venv
)

REM 가상환경 활성화
call venv\\Scripts\\activate.bat

REM 의존성 설치
echo 📥 의존성 설치 중...
pip install -r requirements.txt --quiet

REM 메인 프로그램 실행
echo 🚀 시스템 시작...
python main.py %*

echo ✅ 완료!
pause
'''
    
    files = {
        "main.py": main_content,
        "graph_builder.py": graph_content,
        "state_manager.py": state_content,
        "requirements.txt": requirements_content,
        ".env.example": env_content,
        "README.md": readme_content,
        "run.sh": run_sh_content,
        "run.bat": run_bat_content,
    }
    
    for filename, content in files.items():
        filepath = project_root / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 파일 생성: {filepath}")
    
    # run.sh 실행 권한 부여 (Unix 계열)
    try:
        os.chmod(project_root / "run.sh", 0o755)
        print("✅ run.sh 실행 권한 설정 완료")
    except:
        pass


def create_test_files(project_root):
    """테스트 파일 생성"""
    
    test_content = '''"""
기본 워크플로우 테스트
"""

import unittest
from graph_builder import build_graph


class TestBasicWorkflow(unittest.TestCase):
    """기본 워크플로우 테스트"""
    
    def setUp(self):
        """테스트 초기화"""
        self.graph = build_graph()
    
    def test_graph_creation(self):
        """그래프 생성 테스트"""
        self.assertIsNotNone(self.graph)
    
    # TODO: 추가 테스트 케이스 작성


if __name__ == '__main__':
    unittest.main()
'''
    
    test_file = project_root / "tests" / "test_basic_workflow.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"✅ 파일 생성: {test_file}")
    
    # tests/__init__.py
    init_file = project_root / "tests" / "__init__.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write("# Tests 패키지\n")
    print(f"✅ 파일 생성: {init_file}")


def create_config_files(project_root):
    """설정 파일 생성"""
    
    config_content = '''# 전기차 시장 분석 시스템 설정

# LLM 설정
llm:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000

# Agent 설정
agents:
  market_research:
    enabled: true
    sources: ["news", "government", "reports"]
  
  company_analysis:
    enabled: true
    companies: ["Tesla", "BYD", "Volkswagen", "Hyundai", "GM"]
  
  stock_analysis:
    enabled: true
    api: "yfinance"

# 리포트 설정
report:
  format: "pdf"
  language: "ko"
  include_charts: true
  
# 시스템 설정
system:
  max_retries: 3
  timeout: 300
  parallel_execution: true
'''
    
    config_file = project_root / "configs" / "agent_config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print(f"✅ 파일 생성: {config_file}")


def create_gitignore(project_root):
    """`.gitignore` 파일 생성"""
    
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# 환경 변수
.env

# 데이터
data/*
!data/.gitkeep
outputs/*
!outputs/.gitkeep
reports/*
!reports/.gitkeep
checkpoints/*
!checkpoints/.gitkeep
logs/*
!logs/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# 테스트
.pytest_cache/
.coverage
htmlcov/

# 기타
*.log
'''
    
    gitignore_file = project_root / ".gitignore"
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print(f"✅ 파일 생성: {gitignore_file}")
    
    # .gitkeep 파일 생성 (빈 디렉토리 유지용)
    for subdir in ["data", "outputs", "reports", "checkpoints", "logs"]:
        gitkeep = project_root / subdir / ".gitkeep"
        gitkeep.touch()
        print(f"✅ 파일 생성: {gitkeep}")


def main():
    """메인 실행 함수"""
    
    print("=" * 60)
    print("🚗 전기차 시장 분석 Multi-Agent 시스템 프로젝트 구조 생성")
    print("=" * 60)
    print()
    
    # 1. 디렉토리 구조 생성
    print("📁 1. 디렉토리 구조 생성 중...")
    project_root = create_directory_structure()
    print()
    
    # 2. Agent 파일 생성
    print("🤖 2. Agent 파일 생성 중...")
    create_agent_files(project_root)
    print()
    
    # 3. 메인 파일들 생성
    print("📄 3. 메인 파일 생성 중...")
    create_main_files(project_root)
    print()
    
    # 4. 테스트 파일 생성
    print("🧪 4. 테스트 파일 생성 중...")
    create_test_files(project_root)
    print()
    
    # 5. 설정 파일 생성
    print("⚙️ 5. 설정 파일 생성 중...")
    create_config_files(project_root)
    print()
    
    # 6. .gitignore 생성
    print("🔒 6. Git 설정 파일 생성 중...")
    create_gitignore(project_root)
    print()
    
    print("=" * 60)
    print("✅ 프로젝트 구조 생성 완료!")
    print("=" * 60)
    print()
    print(f"📂 프로젝트 경로: {project_root.absolute()}")
    print()
    print("🚀 다음 단계:")
    print(f"   1. cd {project_root}")
    print("   2. .env 파일에 API 키 설정")
    print("   3. pip install -r requirements.txt")
    print("   4. python main.py --mode quick")
    print()


if __name__ == "__main__":
    main()