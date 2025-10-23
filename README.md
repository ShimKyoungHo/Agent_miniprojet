# 🚗 전기차 시장 분석 Multi-Agent 시스템

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

## 👥 만든이
심경호

## 기존과 바뀐점

### Before
- Supervisor_agent 사용하여 하위 agent들을 관리
- 3 chain 으로 이루어져 시장 분석 -> 소비자 분석, 기업 분석 -> 기술 분석, 주식분석
  으로 병렬 처리 진행
- State 상태

### After
- agent들 역할 및 특성상 Supervisor 불필요 -> 순차 처리 및 병렬 처리로 변경
- 주식 분석 agent에 기업 목록이 필요하여 2 chain으로 구성 후
  기업 분석 -> 기술 분석과 병렬로 처리
- State 추가로 설정