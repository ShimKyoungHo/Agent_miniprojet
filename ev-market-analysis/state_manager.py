# state_manager.py

from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime
import json
from pathlib import Path

class AgentState(TypedDict):
    """전체 Multi-Agent 시스템의 공유 상태"""
    
    # 메시지 히스토리
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 워크플로우 메타데이터
    workflow_metadata: Dict[str, Any]
    workflow_id: str
    current_iteration: int
    workflow_stage: str
    workflow_complete: bool
    
    # Agent 실행 상태
    next_agents: List[str]
    pending_agents: List[str]
    completed_agents: List[str]
    agent_errors: Dict[str, str]
    
    # 시장 분석 데이터
    market_trends: Optional[Dict]
    government_policies: Optional[Dict]
    market_data: Optional[Dict]
    
    # 소비자 분석 데이터
    consumer_patterns: Optional[Dict]
    
    # 기업 분석 데이터
    company_analysis: Optional[Dict]
    company_tech_data: Optional[Dict]
    
    # 기술 분석 데이터
    tech_trends: Optional[Dict]
    
    # 주가 분석 데이터
    stock_analysis: Optional[Dict]
    
    # 생성된 결과물
    charts: Optional[List[Dict]]
    charts_generated: bool
    chart_files: Optional[Dict[str, str]]
    dashboard: Optional[Dict]
    
    # 최종 리포트
    final_report: Optional[Dict]
    report_generated: bool
    report_paths: Optional[Dict[str, str]]
    
    # 에러 및 로그
    errors: List[str]
    warnings: List[str]
    logs: List[str]


class StateManager:
    """Multi-Agent 시스템의 상태 관리자"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        """
        Args:
            checkpoint_dir: 체크포인트 저장 디렉토리
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.state_history = []
        self.max_history = 100
        
    def create_initial_state(self, initial_message: BaseMessage = None) -> AgentState:
        """초기 상태 생성"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        initial_state = {
            # 메시지
            'messages': [initial_message] if initial_message else [],
            
            # 워크플로우
            'workflow_metadata': {
                'started_at': datetime.now().isoformat(),
                'version': '1.0',
                'initiated_by': 'user'
            },
            'workflow_id': workflow_id,
            'current_iteration': 0,
            'workflow_stage': 'initialization',
            'workflow_complete': False,
            
            # Agent 상태
            'next_agents': [],
            'pending_agents': [],
            'completed_agents': [],
            'agent_errors': {},
            
            # 분석 데이터 (모두 None으로 초기화)
            'market_trends': None,
            'government_policies': None,
            'market_data': None,
            'consumer_patterns': None,
            'company_analysis': None,
            'company_tech_data': None,
            'tech_trends': None,
            'stock_analysis': None,
            
            # 결과물
            'charts': None,
            'charts_generated': False,
            'dashboard': None,
            'final_report': None,
            'report_generated': False,
            'report_paths': None,
            
            # 로그
            'errors': [],
            'warnings': [],
            'logs': [f"Workflow {workflow_id} initialized at {datetime.now().isoformat()}"]
        }
        
        return initial_state
    
    def validate_state(self, state: AgentState) -> tuple[bool, List[str]]:
        """
        상태 유효성 검증
        
        Returns:
            (유효성 여부, 문제점 리스트)
        """
        issues = []
        
        # 필수 필드 확인
        required_fields = ['workflow_id', 'current_iteration', 'workflow_stage']
        for field in required_fields:
            if field not in state or state[field] is None:
                issues.append(f"Required field '{field}' is missing or None")
        
        # 반복 횟수 체크
        if state.get('current_iteration', 0) > 1000:
            issues.append("Iteration count exceeds maximum limit (1000)")
        
        # 워크플로우 단계 유효성
        valid_stages = ['initialization', 'data_collection', 'analysis', 
                       'synthesis', 'reporting', 'completed']
        if state.get('workflow_stage') not in valid_stages:
            issues.append(f"Invalid workflow stage: {state.get('workflow_stage')}")
        
        # 순환 참조 체크
        if state.get('next_agents'):
            if len(set(state['next_agents'])) != len(state['next_agents']):
                issues.append("Duplicate agents in next_agents list")
        
        return len(issues) == 0, issues
    
    def update_state(self, state: AgentState, updates: Dict[str, Any]) -> AgentState:
        """
        상태 업데이트
        
        Args:
            state: 현재 상태
            updates: 업데이트할 필드들
            
        Returns:
            업데이트된 상태
        """
        # 깊은 복사로 불변성 보장
        new_state = state.copy()
        
        for key, value in updates.items():
            if key in new_state:
                if key == 'messages' and isinstance(value, list):
                    # 메시지는 추가
                    new_state['messages'].extend(value)
                elif key in ['errors', 'warnings', 'logs'] and isinstance(value, list):
                    # 로그류는 추가
                    new_state[key].extend(value)
                elif key in ['next_agents', 'pending_agents', 'completed_agents']:
                    # Agent 리스트는 병합 또는 교체
                    if isinstance(value, list):
                        new_state[key] = value
                else:
                    # 나머지는 덮어쓰기
                    new_state[key] = value
            else:
                # 새 필드 추가 (주의 필요)
                new_state[key] = value
                new_state['warnings'].append(f"New field added to state: {key}")
        
        # 상태 히스토리에 추가
        self._add_to_history(new_state)
        
        return new_state
    
    def save_checkpoint(self, state: AgentState, checkpoint_name: str = None) -> str:
        """
        상태 체크포인트 저장
        
        Args:
            state: 저장할 상태
            checkpoint_name: 체크포인트 이름 (없으면 자동 생성)
            
        Returns:
            체크포인트 파일 경로
        """
        if checkpoint_name is None:
            checkpoint_name = f"{state['workflow_id']}_iter{state['current_iteration']}"
        
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_name}.json"
        
        # BaseMessage 객체를 직렬화 가능한 형태로 변환
        serializable_state = self._make_serializable(state)
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_state, f, indent=2, ensure_ascii=False)
        
        state['logs'].append(f"Checkpoint saved: {checkpoint_file}")
        
        return str(checkpoint_file)
    
    def load_checkpoint(self, checkpoint_path: str) -> AgentState:
        """
        체크포인트에서 상태 복원
        
        Args:
            checkpoint_path: 체크포인트 파일 경로
            
        Returns:
            복원된 상태
        """
        checkpoint_file = Path(checkpoint_path)
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            serialized_state = json.load(f)
        
        # 직렬화된 데이터를 원래 형태로 복원
        state = self._deserialize_state(serialized_state)
        
        state['logs'].append(f"State restored from checkpoint: {checkpoint_file}")
        
        return state
    
    def get_state_summary(self, state: AgentState) -> Dict[str, Any]:
        """
        상태 요약 생성
        
        Args:
            state: 요약할 상태
            
        Returns:
            상태 요약 딕셔너리
        """
        summary = {
            'workflow_id': state['workflow_id'],
            'stage': state['workflow_stage'],
            'iteration': state['current_iteration'],
            'is_complete': state['workflow_complete'],
            'agents': {
                'pending': len(state.get('pending_agents', [])),
                'completed': len(state.get('completed_agents', [])),
                'next': state.get('next_agents', [])
            },
            'data_status': {
                'market_data': state.get('market_data') is not None,
                'consumer_data': state.get('consumer_patterns') is not None,
                'company_data': state.get('company_analysis') is not None,
                'tech_data': state.get('tech_trends') is not None,
                'stock_data': state.get('stock_analysis') is not None
            },
            'outputs': {
                'charts_generated': state.get('charts_generated', False),
                'report_generated': state.get('report_generated', False)
            },
            'errors': len(state.get('errors', [])),
            'warnings': len(state.get('warnings', []))
        }
        
        return summary
    
    def get_agent_progress(self, state: AgentState) -> Dict[str, float]:
        """
        Agent별 진행률 계산
        
        Returns:
            Agent별 진행률 (0.0 ~ 1.0)
        """
        all_agents = [
            'market_research', 'consumer_analysis', 'company_analysis',
            'tech_analysis', 'stock_analysis', 'chart_generation',
            'report_generation'
        ]
        
        progress = {}
        completed = state.get('completed_agents', [])
        
        for agent in all_agents:
            if agent in completed:
                progress[agent] = 1.0
            elif agent in state.get('pending_agents', []):
                progress[agent] = 0.5
            elif agent in state.get('next_agents', []):
                progress[agent] = 0.25
            else:
                progress[agent] = 0.0
        
        # 전체 진행률
        progress['overall'] = sum(progress.values()) / len(all_agents)
        
        return progress
    
    def check_dependencies(self, state: AgentState, agent_name: str) -> tuple[bool, List[str]]:
        """
        Agent 실행을 위한 의존성 체크
        
        Args:
            state: 현재 상태
            agent_name: 체크할 Agent 이름
            
        Returns:
            (실행 가능 여부, 누락된 의존성 리스트)
        """
        dependencies = {
            'consumer_analysis': ['market_trends', 'government_policies'],
            'tech_analysis': ['company_tech_data'],
            'chart_generation': ['market_data', 'consumer_patterns', 
                               'company_analysis', 'tech_trends', 'stock_analysis'],
            'report_generation': ['charts_generated']
        }
        
        agent_deps = dependencies.get(agent_name, [])
        missing_deps = []
        
        for dep in agent_deps:
            if dep.endswith('_generated'):
                # 플래그 체크
                if not state.get(dep, False):
                    missing_deps.append(dep)
            else:
                # 데이터 체크
                if state.get(dep) is None:
                    missing_deps.append(dep)
        
        return len(missing_deps) == 0, missing_deps
    
    def merge_states(self, state1: AgentState, state2: AgentState) -> AgentState:
        """
        두 상태를 병합 (병렬 실행 결과 통합용)
        
        Args:
            state1: 첫 번째 상태
            state2: 두 번째 상태
            
        Returns:
            병합된 상태
        """
        merged = state1.copy()
        
        # 데이터 필드 병합 (None이 아닌 값 우선)
        data_fields = [
            'market_trends', 'government_policies', 'market_data',
            'consumer_patterns', 'company_analysis', 'company_tech_data',
            'tech_trends', 'stock_analysis', 'charts', 'dashboard', 
            'final_report'
        ]
        
        for field in data_fields:
            if merged.get(field) is None and state2.get(field) is not None:
                merged[field] = state2[field]
        
        # 리스트 필드 병합
        list_fields = ['completed_agents', 'errors', 'warnings', 'logs']
        for field in list_fields:
            if field in state2:
                merged[field] = list(set(merged.get(field, []) + state2[field]))
        
        # Agent 에러 병합
        if 'agent_errors' in state2:
            merged['agent_errors'].update(state2['agent_errors'])
        
        # 플래그 병합 (OR 연산)
        flag_fields = ['charts_generated', 'report_generated', 'workflow_complete']
        for field in flag_fields:
            merged[field] = merged.get(field, False) or state2.get(field, False)
        
        # 반복 횟수는 최대값
        merged['current_iteration'] = max(
            merged.get('current_iteration', 0),
            state2.get('current_iteration', 0)
        )
        
        return merged
    
    def rollback(self, state: AgentState, steps: int = 1) -> Optional[AgentState]:
        """
        이전 상태로 롤백
        
        Args:
            state: 현재 상태
            steps: 롤백할 단계 수
            
        Returns:
            롤백된 상태 또는 None
        """
        if len(self.state_history) < steps:
            state['warnings'].append(f"Cannot rollback {steps} steps - insufficient history")
            return None
        
        # 히스토리에서 이전 상태 가져오기
        previous_state = self.state_history[-(steps + 1)]
        previous_state['logs'].append(f"Rolled back {steps} steps at {datetime.now().isoformat()}")
        
        return previous_state
    
    def _add_to_history(self, state: AgentState):
        """상태 히스토리에 추가"""
        self.state_history.append(state.copy())
        
        # 최대 히스토리 크기 유지
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
    
    def _make_serializable(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """상태를 직렬화 가능한 형태로 변환"""
        serializable = {}
        
        for key, value in state.items():
            if key == 'messages' and isinstance(value, list):
                serializable[key] = [
                    self._serialize_message(msg) for msg in value
                ]
            elif isinstance(value, dict):
                serializable[key] = self._make_serializable(value)
            elif isinstance(value, list):
                serializable[key] = [
                    self._make_serializable(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                serializable[key] = value
        
        return serializable

    def _serialize_message(self, msg):
        """메시지를 직렬화"""
        # 이미 dict인 경우 그대로 반환
        if isinstance(msg, dict):
            return msg
        
        # 객체인 경우 속성 추출
        try:
            return {
                'type': type(msg).__name__,
                'content': msg.content if hasattr(msg, 'content') else str(msg),
                'role': msg.role if hasattr(msg, 'role') else 'unknown',
                'name': msg.name if hasattr(msg, 'name') else None
            }
        except Exception as e:
            # 변환 실패 시 문자열로 변환
            self.logger.warning(f"메시지 직렬화 실패: {e}")
            return {'type': 'unknown', 'content': str(msg)}
    
    def _deserialize_state(self, serialized: Dict) -> AgentState:
        """직렬화된 데이터를 AgentState로 복원"""
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        state = serialized.copy()
        
        # 메시지 복원
        if 'messages' in state:
            messages = []
            for msg_dict in state['messages']:
                msg_type = msg_dict['type']
                content = msg_dict['content']
                
                if msg_type == 'HumanMessage':
                    messages.append(HumanMessage(content=content))
                elif msg_type == 'AIMessage':
                    messages.append(AIMessage(content=content))
                elif msg_type == 'SystemMessage':
                    messages.append(SystemMessage(content=content))
                else:
                    messages.append(HumanMessage(content=content))
            
            state['messages'] = messages
        
        return state
    
    def generate_state_report(self, state: AgentState) -> str:
        """
        상태 리포트 생성 (디버깅/모니터링용)
        
        Returns:
            포맷된 상태 리포트
        """
        summary = self.get_state_summary(state)
        progress = self.get_agent_progress(state)
        
        report = f"""
================================================================================
WORKFLOW STATE REPORT
================================================================================
Workflow ID: {summary['workflow_id']}
Stage: {summary['stage']} | Iteration: {summary['iteration']}
Status: {'COMPLETE' if summary['is_complete'] else 'IN PROGRESS'}
Overall Progress: {progress['overall']*100:.1f}%

AGENT STATUS
--------------------------------------------------------------------------------
Pending: {summary['agents']['pending']} | Completed: {summary['agents']['completed']}
Next to Execute: {', '.join(summary['agents']['next']) if summary['agents']['next'] else 'None'}

DATA COLLECTION STATUS
--------------------------------------------------------------------------------
✓ Market Data: {'YES' if summary['data_status']['market_data'] else 'NO'}
✓ Consumer Data: {'YES' if summary['data_status']['consumer_data'] else 'NO'}
✓ Company Data: {'YES' if summary['data_status']['company_data'] else 'NO'}
✓ Technology Data: {'YES' if summary['data_status']['tech_data'] else 'NO'}
✓ Stock Data: {'YES' if summary['data_status']['stock_data'] else 'NO'}

OUTPUT STATUS
--------------------------------------------------------------------------------
Charts Generated: {'YES' if summary['outputs']['charts_generated'] else 'NO'}
Report Generated: {'YES' if summary['outputs']['report_generated'] else 'NO'}

ISSUES
--------------------------------------------------------------------------------
Errors: {summary['errors']}
Warnings: {summary['warnings']}
"""
        
        # 최근 에러 추가
        if state.get('errors'):
            report += "\nRecent Errors:\n"
            for error in state['errors'][-3:]:
                report += f"  - {error}\n"
        
        report += "=" * 80 + "\n"
        
        return report


class StateMonitor:
    """상태 모니터링 및 알림"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.alerts = []
        self.thresholds = {
            'max_iterations': 100,
            'max_errors': 10,
            'max_pending_time': 300  # seconds
        }
    
    def check_state_health(self, state: AgentState) -> List[Dict[str, Any]]:
        """
        상태 건강성 체크
        
        Returns:
            발견된 문제 리스트
        """
        issues = []
        
        # 반복 횟수 체크
        if state['current_iteration'] > self.thresholds['max_iterations']:
            issues.append({
                'severity': 'HIGH',
                'type': 'iteration_overflow',
                'message': f"Iteration count ({state['current_iteration']}) exceeds threshold"
            })
        
        # 에러 수 체크
        if len(state.get('errors', [])) > self.thresholds['max_errors']:
            issues.append({
                'severity': 'HIGH',
                'type': 'too_many_errors',
                'message': f"Error count ({len(state['errors'])}) exceeds threshold"
            })
        
        # 정체 상태 체크
        if state.get('pending_agents'):
            if len(state['pending_agents']) > 5:
                issues.append({
                    'severity': 'MEDIUM',
                    'type': 'agent_bottleneck',
                    'message': f"Too many pending agents: {len(state['pending_agents'])}"
                })
        
        # 메모리 사용량 체크 (간단한 추정)
        estimated_memory = len(str(state)) / 1024  # KB
        if estimated_memory > 1024:  # 1MB 이상
            issues.append({
                'severity': 'LOW',
                'type': 'high_memory_usage',
                'message': f"State size is large: {estimated_memory:.1f} KB"
            })
        
        return issues
    
    def generate_alert(self, state: AgentState, issue: Dict[str, Any]):
        """알림 생성"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'workflow_id': state['workflow_id'],
            'issue': issue,
            'state_summary': self.state_manager.get_state_summary(state)
        }
        
        self.alerts.append(alert)
        
        # 심각도에 따른 처리
        if issue['severity'] == 'HIGH':
            print(f"🚨 ALERT: {issue['message']}")
        elif issue['severity'] == 'MEDIUM':
            print(f"⚠️  WARNING: {issue['message']}")
        
        return alert