#!/usr/bin/env python3
"""
전기차 시장 분석 Multi-Agent 시스템
메인 실행 파일
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from graph_builder import EVMarketAnalysisGraph
from state_manager import StateManager


def setup_environment():
    """환경 설정"""
    # .env 파일 로드
    load_dotenv(override=True)
    
    # 필수 디렉토리 생성
    directories = ['data', 'outputs', 'reports', 'logs', 'checkpoints']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  경고: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일을 생성하고 API 키를 설정해주세요.")
        return False
    
    return True


def load_config(mode: str) -> dict:
    """
    실행 모드에 따른 설정 로드
    
    Args:
        mode: 실행 모드 (quick, full, monitor)
        
    Returns:
        설정 딕셔너리
    """
    base_config = {
        'llm': {
            'model': 'gpt-4',
            'temperature': 0.7,
            'api_key': os.getenv('OPENAI_API_KEY')
        },
        'market_research': {
            'api_endpoints': {},
            'max_retries': 3
        },
        'company_analysis': {
            'company_analysis': {
                'use_dynamic_discovery': True,  # 동적 발굴 활성화
                'max_companies': 10,            # 상위 10개 분석
                'target_companies': [           # Fallback
                    "BYD", "Tesla", "Volkswagen", "Geely", "Hyundai",
                    "GM", "Ford", "Stellantis", "Renault", "NIO"
                ]
            }
            
        },
        'stock_analysis': {
            'tickers': {
                'TSLA': 'Tesla',
                'BYD': 'BYD',
                'RIVN': 'Rivian',
                'LCID': 'Lucid',
                'NIO': 'NIO'
            }
        }
    }
    
    # 모드별 설정 조정
    if mode == 'quick':
        # 빠른 테스트: 간단한 분석
        base_config['llm']['model'] = 'gpt-3.5-turbo'
        base_config['company_analysis']['max_companies'] = 3
    elif mode == 'full':
        # 전체 분석: 상세한 분석
        base_config['llm']['model'] = 'gpt-4'
        base_config['company_analysis']['max_companies'] = 10
    elif mode == 'monitor':
        # 모니터링 모드: 실시간 데이터 중심
        base_config['stock_analysis']['real_time'] = True
    
    return base_config


def print_banner():
    """배너 출력"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        🚗 전기차 시장 분석 Multi-Agent 시스템 🚗            ║
    ║                                                               ║
    ║              3-Chain Parallel Execution Model                ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_workflow_structure():
    """워크플로우 구조 출력"""
    workflow = """
    📊 워크플로우 구조:
    
    ┌─────────────────────────────────────────────────────────────┐
    │                        시작 (START)                          │
    └─────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
    ┌───────────────▼───────┐  ┌──▼──────────┐  ┌─▼────────────┐
    │   Chain 1 (순차)      │  │  Chain 2    │  │   Chain 3    │
    │                       │  │  (순차)     │  │   (독립)     │
    │  ┌─────────────────┐ │  │ ┌─────────┐ │  │ ┌──────────┐ │
    │  │ Market Research │ │  │ │ Company │ │  │ │  Stock   │ │
    │  │     Agent       │ │  │ │ Analysis│ │  │ │ Analysis │ │
    │  └────────┬────────┘ │  │ └────┬────┘ │  │ │  Agent   │ │
    │           │          │  │      │      │  │ └──────────┘ │
    │           ▼          │  │      ▼      │  │              │
    │  ┌─────────────────┐ │  │ ┌─────────┐ │  │              │
    │  │   Consumer      │ │  │ │  Tech   │ │  │              │
    │  │   Analysis      │ │  │ │ Analysis│ │  │              │
    │  │     Agent       │ │  │ │  Agent  │ │  │              │
    │  └─────────────────┘ │  │ └─────────┘ │  │              │
    └───────────┬───────────┘  └──────┬──────┘  └──────┬───────┘
                │                     │                │
                └─────────────┬───────┴────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Chart Generation  │
                    │       Agent        │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Report Generation │
                    │       Agent        │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │      완료 (END)     │
                    │   최종 보고서 생성   │
                    └────────────────────┘
    """
    print(workflow)


def print_summary(state: dict):
    """분석 결과 요약 출력"""
    print("\n" + "=" * 70)
    print("📊 분석 결과 요약")
    print("=" * 70)
    
    # 완료된 Agent 목록
    print(f"\n✅ 완료된 Agent ({len(state['completed_agents'])}개):")
    
    # Chain별로 그룹화
    chain_1 = [a for a in state['completed_agents'] if a in ['market_research', 'consumer_analysis']]
    chain_2 = [a for a in state['completed_agents'] if a in ['company_analysis', 'tech_analysis']]
    chain_3 = [a for a in state['completed_agents'] if a in ['stock_analysis']]
    
    if chain_1:
        print(f"   🔗 Chain 1: {', '.join(chain_1)}")
    if chain_2:
        print(f"   🔗 Chain 2: {', '.join(chain_2)}")
    if chain_3:
        print(f"   🔗 Chain 3: {', '.join(chain_3)}")
    
    # 기타 Agent
    other_agents = [a for a in state['completed_agents'] 
                   if a not in chain_1 + chain_2 + chain_3]
    if other_agents:
        print(f"   📊 기타: {', '.join(other_agents)}")
    
    # 에러 확인
    if state['errors']:
        print(f"\n❌ 에러 ({len(state['errors'])}개):")
        for error in state['errors']:
            print(f"   - {error}")
    
    # 경고 확인
    if state['warnings']:
        print(f"\n⚠️  경고 ({len(state['warnings'])}개):")
        for warning in state['warnings']:
            print(f"   - {warning}")
    
    # 생성된 결과물
    print("\n📁 생성된 결과물:")
    if state.get('charts'):
        print(f"   - 차트: {len(state['charts'])}개 생성")
    if state.get('final_report'):
        print(f"   - 최종 리포트: 생성 완료")
    if state.get('report_paths'):
        print(f"   - 리포트 경로:")
        for format_type, path in state['report_paths'].items():
            print(f"      * {format_type}: {path}")
    
    print("\n" + "=" * 70)


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description='전기차 시장 분석 Multi-Agent 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python main.py --mode quick              # 빠른 테스트
  python main.py --mode full               # 전체 분석
  python main.py --resume checkpoint.json  # 이전 분석 이어서
  python main.py --show-workflow           # 워크플로우 구조 확인
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        default='quick',
        choices=['quick', 'full', 'monitor'],
        help='실행 모드 선택 (default: quick)'
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        default=None,
        help='체크포인트 파일 경로'
    )
    
    parser.add_argument(
        '--message',
        type=str,
        default=None,
        help='초기 분석 메시지'
    )
    
    parser.add_argument(
        '--async',
        dest='use_async',
        action='store_true',
        help='비동기 실행 모드'
    )
    
    parser.add_argument(
        '--show-workflow',
        action='store_true',
        help='워크플로우 구조만 표시하고 종료'
    )
    
    args = parser.parse_args()
    
    # 워크플로우 구조만 표시
    if args.show_workflow:
        print_banner()
        print_workflow_structure()
        sys.exit(0)
    
    # 배너 출력
    print_banner()
    
    # 환경 설정
    print("🔧 환경 설정 중...")
    if not setup_environment():
        print("❌ 환경 설정 실패. 프로그램을 종료합니다.")
        sys.exit(1)
    print("✅ 환경 설정 완료")
    
    # 설정 로드
    print(f"\n⚙️  설정 로드 중... (모드: {args.mode})")
    config = load_config(args.mode)
    
    # 초기 메시지 설정
    initial_message = args.message or f"{datetime.now().strftime('%Y년 %m월')} 전기차 시장 분석을 시작합니다."
    
    try:
        # Graph 빌더 생성
        print("\n🏗️  분석 시스템 초기화 중...")
        builder = EVMarketAnalysisGraph(config)
        print("✅ 시스템 초기화 완료")
        
        # 이전 체크포인트에서 재개
        if args.resume:
            print(f"\n📂 체크포인트 로드: {args.resume}")
            state_manager = StateManager()
            initial_state = state_manager.load_checkpoint(args.resume)
            print("✅ 체크포인트 로드 완료")
        else:
            initial_state = None
        
        # 분석 실행
        print("\n" + "=" * 70)
        print("🚀 전기차 시장 분석 시작!")
        print("   3개의 분석 체인이 병렬로 실행됩니다.")
        print("=" * 70)
        
        if args.use_async:
            # 비동기 실행
            print("\n⚡ 비동기 모드로 실행합니다.\n")
            final_state = asyncio.run(builder.run_async(initial_message))
        else:
            # 동기 실행
            print("\n🔄 동기 모드로 실행합니다.\n")
            final_state = builder.run(initial_message)
        
        # 결과 요약 출력
        print_summary(final_state)
        
        # 성공 메시지
        print("\n" + "=" * 70)
        print("✅ 전기차 시장 분석이 성공적으로 완료되었습니다!")
        print("=" * 70)
        print(f"\n📊 결과 확인:")
        print(f"   - 체크포인트: checkpoints/final_state.json")
        print(f"   - 로그: logs/")
        print(f"   - 결과물: outputs/")
        if final_state.get('report_paths'):
            print(f"   - 최종 리포트: {final_state['report_paths']}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        print("   체크포인트가 저장되었습니다. --resume 옵션으로 재개할 수 있습니다.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()