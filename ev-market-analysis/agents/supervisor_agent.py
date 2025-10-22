# Supervisor Agent - 전체 워크플로우 조정
# agents/supervisor_agent.py

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
from datetime import datetime
from .base_agent import BaseAgent

class WorkflowStage(Enum):
    """워크플로우 단계"""
    INITIALIZATION = "initialization"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    REPORTING = "reporting"
    COMPLETED = "completed"

class SupervisorAgent(BaseAgent):
    """전체 워크플로우를 조정하는 Supervisor Agent"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("supervisor", llm, config)
        self.current_stage = WorkflowStage.INITIALIZATION
        self.agent_status = {}
        self.iteration_count = 0
        self.max_iterations = config.get('max_iterations', 10) if config else 10
        
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Supervisor 메인 로직"""
        self.logger.info(f"Supervisor 시작 - 현재 단계: {self.current_stage.value}")
        
        # 반복 횟수 체크
        self.iteration_count += 1
        if self.iteration_count > self.max_iterations:
            self.logger.warning("최대 반복 횟수 초과")
            state['error'] = "Maximum iterations exceeded"
            return state
        
        # 현재 워크플로우 단계에 따른 처리
        if self.current_stage == WorkflowStage.INITIALIZATION:
            state = await self._initialize_workflow(state)
            
        elif self.current_stage == WorkflowStage.DATA_COLLECTION:
            state = await self._coordinate_data_collection(state)
            
        elif self.current_stage == WorkflowStage.ANALYSIS:
            state = await self._coordinate_analysis(state)
            
        elif self.current_stage == WorkflowStage.SYNTHESIS:
            state = await self._coordinate_synthesis(state)
            
        elif self.current_stage == WorkflowStage.REPORTING:
            state = await self._coordinate_reporting(state)
            
        # 상태 저장
        self.save_output({
            'stage': self.current_stage.value,
            'iteration': self.iteration_count,
            'agent_status': self.agent_status,
            'timestamp': self.get_timestamp()
        }, f'supervisor_state_{self.iteration_count}.json')
        
        return state
    
    async def _initialize_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 초기화"""
        self.logger.info("워크플로우 초기화 중...")
        
        # 필요한 Agent들 초기화
        state['required_agents'] = [
            'market_research',
            'company_analysis', 
            'stock_analysis'
        ]
        
        state['workflow_metadata'] = {
            'started_at': self.get_timestamp(),
            'initiated_by': 'supervisor',
            'workflow_id': f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Agent 상태 초기화
        for agent in state['required_agents']:
            self.agent_status[agent] = 'pending'
        
        self.current_stage = WorkflowStage.DATA_COLLECTION
        state['next_agents'] = ['market_research', 'company_analysis', 'stock_analysis']
        
        return state
    
    async def _coordinate_data_collection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 수집 단계 조정"""
        self.logger.info("데이터 수집 단계 조정 중...")
        
        # 병렬 실행할 Agent들 확인
        pending_agents = [
            agent for agent, status in self.agent_status.items() 
            if status == 'pending'
        ]
        
        if not pending_agents:
            # 모든 기본 데이터 수집 완료
            self.current_stage = WorkflowStage.ANALYSIS
            state['next_agents'] = ['consumer_analysis', 'tech_analysis']
            
            # 분석 Agent들 상태 추가
            self.agent_status['consumer_analysis'] = 'pending'
            self.agent_status['tech_analysis'] = 'pending'
        else:
            # 아직 수집 중
            state['pending_agents'] = pending_agents
        
        return state
    
    async def _coordinate_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """분석 단계 조정"""
        self.logger.info("분석 단계 조정 중...")
        
        # 분석 완료 확인
        analysis_complete = all([
            state.get('market_trends'),
            state.get('consumer_patterns'),
            state.get('company_analysis'),
            state.get('tech_trends'),
            state.get('stock_analysis')
        ])
        
        if analysis_complete:
            self.current_stage = WorkflowStage.SYNTHESIS
            state['next_agents'] = ['chart_generation']
            self.agent_status['chart_generation'] = 'pending'
        
        return state
    
    async def _coordinate_synthesis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """종합 단계 조정"""
        self.logger.info("종합 단계 조정 중...")
        
        if state.get('charts_generated'):
            self.current_stage = WorkflowStage.REPORTING
            state['next_agents'] = ['report_generation']
            self.agent_status['report_generation'] = 'pending'
        
        return state
    
    async def _coordinate_reporting(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """보고서 생성 단계 조정"""
        self.logger.info("보고서 생성 단계 조정 중...")
        
        if state.get('final_report'):
            self.current_stage = WorkflowStage.COMPLETED
            state['workflow_complete'] = True
            state['completed_at'] = self.get_timestamp()
            
            # 최종 요약
            summary = self._create_workflow_summary(state)
            self.save_output(summary, 'workflow_summary.json')
            
            self.logger.info("워크플로우 완료!")
        
        return state
    
    def _create_workflow_summary(self, state: Dict[str, Any]) -> Dict:
        """워크플로우 요약 생성"""
        return {
            'workflow_id': state['workflow_metadata']['workflow_id'],
            'started_at': state['workflow_metadata']['started_at'],
            'completed_at': state['completed_at'],
            'total_iterations': self.iteration_count,
            'agents_executed': list(self.agent_status.keys()),
            'final_stage': self.current_stage.value,
            'outputs': {
                'market_trends': bool(state.get('market_trends')),
                'consumer_patterns': bool(state.get('consumer_patterns')),
                'company_analysis': bool(state.get('company_analysis')),
                'tech_trends': bool(state.get('tech_trends')),
                'stock_analysis': bool(state.get('stock_analysis')),
                'charts': bool(state.get('charts_generated')),
                'report': bool(state.get('final_report'))
            }
        }
    
    def update_agent_status(self, agent_name: str, status: str):
        """Agent 상태 업데이트"""
        self.agent_status[agent_name] = status
        self.logger.info(f"Agent 상태 업데이트: {agent_name} -> {status}")
    
    def get_next_agents(self, state: Dict[str, Any]) -> List[str]:
        """다음에 실행할 Agent들 반환"""
        return state.get('next_agents', [])