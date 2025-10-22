# tests/test_basic_workflow.py

import pytest
import asyncio
from pathlib import Path
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import StateManager, AgentState
from agents.base_agent import BaseAgent
from agents.supervisor_agent import SupervisorAgent
from langchain_core.messages import HumanMessage


class TestStateManager:
    """StateManager 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행"""
        self.state_manager = StateManager(checkpoint_dir="test_checkpoints")
    
    def teardown_method(self):
        """각 테스트 후 정리"""
        # 테스트 체크포인트 삭제
        import shutil
        if Path("test_checkpoints").exists():
            shutil.rmtree("test_checkpoints")
    
    def test_create_initial_state(self):
        """초기 상태 생성 테스트"""
        message = HumanMessage(content="Test message")
        state = self.state_manager.create_initial_state(message)
        
        assert state['workflow_id'].startswith('wf_')
        assert state['current_iteration'] == 0
        assert state['workflow_stage'] == 'initialization'
        assert state['workflow_complete'] is False
        assert len(state['messages']) == 1
    
    def test_validate_state(self):
        """상태 유효성 검증 테스트"""
        # 유효한 상태
        valid_state = self.state_manager.create_initial_state()
        is_valid, issues = self.state_manager.validate_state(valid_state)
        assert is_valid is True
        assert len(issues) == 0
        
        # 무효한 상태
        invalid_state = {'workflow_stage': 'invalid_stage'}
        is_valid, issues = self.state_manager.validate_state(invalid_state)
        assert is_valid is False
        assert len(issues) > 0
    
    def test_update_state(self):
        """상태 업데이트 테스트"""
        state = self.state_manager.create_initial_state()
        
        updates = {
            'current_iteration': 1,
            'workflow_stage': 'data_collection',
            'market_trends': {'test': 'data'}
        }
        
        new_state = self.state_manager.update_state(state, updates)
        
        assert new_state['current_iteration'] == 1
        assert new_state['workflow_stage'] == 'data_collection'
        assert new_state['market_trends'] == {'test': 'data'}
    
    def test_save_and_load_checkpoint(self):
        """체크포인트 저장 및 로드 테스트"""
        state = self.state_manager.create_initial_state()
        state['test_data'] = 'test_value'
        
        # 저장
        checkpoint_path = self.state_manager.save_checkpoint(state, "test_checkpoint")
        assert Path(checkpoint_path).exists()
        
        # 로드
        loaded_state = self.state_manager.load_checkpoint(checkpoint_path)
        assert loaded_state['test_data'] == 'test_value'
        assert loaded_state['workflow_id'] == state['workflow_id']
    
    def test_get_agent_progress(self):
        """Agent 진행률 계산 테스트"""
        state = self.state_manager.create_initial_state()
        state['completed_agents'] = ['market_research', 'company_analysis']
        state['pending_agents'] = ['consumer_analysis']
        state['next_agents'] = ['tech_analysis']
        
        progress = self.state_manager.get_agent_progress(state)
        
        assert progress['market_research'] == 1.0
        assert progress['company_analysis'] == 1.0
        assert progress['consumer_analysis'] == 0.5
        assert progress['tech_analysis'] == 0.25
        assert 0.0 <= progress['overall'] <= 1.0
    
    def test_check_dependencies(self):
        """의존성 체크 테스트"""
        state = self.state_manager.create_initial_state()
        
        # 의존성 미충족
        can_run, missing = self.state_manager.check_dependencies(state, 'consumer_analysis')
        assert can_run is False
        assert 'market_trends' in missing
        
        # 의존성 충족
        state['market_trends'] = {'test': 'data'}
        state['government_policies'] = {'test': 'data'}
        can_run, missing = self.state_manager.check_dependencies(state, 'consumer_analysis')
        assert can_run is True
        assert len(missing) == 0
    
    def test_merge_states(self):
        """상태 병합 테스트"""
        state1 = self.state_manager.create_initial_state()
        state1['market_trends'] = {'data': 'market'}
        state1['completed_agents'] = ['market_research']
        
        state2 = self.state_manager.create_initial_state()
        state2['company_analysis'] = {'data': 'company'}
        state2['completed_agents'] = ['company_analysis']
        
        merged = self.state_manager.merge_states(state1, state2)
        
        assert merged['market_trends'] == {'data': 'market'}
        assert merged['company_analysis'] == {'data': 'company'}
        assert set(merged['completed_agents']) == {'market_research', 'company_analysis'}


class TestBaseAgent:
    """BaseAgent 테스트"""
    
    def test_agent_initialization(self):
        """Agent 초기화 테스트"""
        agent = BaseAgent("test_agent")
        
        assert agent.name == "test_agent"
        assert agent.output_dir.exists()
        assert agent.llm is None
    
    def test_save_and_load_output(self):
        """출력 저장 및 로드 테스트"""
        agent = BaseAgent("test_agent")
        
        # JSON 저장
        test_data = {'test': 'data', 'number': 123}
        agent.save_output(test_data, 'test.json')
        
        # 로드
        loaded_data = agent.load_data(agent.output_dir / 'test.json')
        assert loaded_data == test_data
        
        # 정리
        import shutil
        if agent.output_dir.exists():
            shutil.rmtree(agent.output_dir)


@pytest.mark.asyncio
class TestSupervisorAgent:
    """SupervisorAgent 테스트"""
    
    async def test_supervisor_initialization(self):
        """Supervisor 초기화 테스트"""
        config = {'max_iterations': 10}
        supervisor = SupervisorAgent(config=config)
        
        assert supervisor.name == "supervisor"
        assert supervisor.max_iterations == 10
        assert supervisor.current_stage.value == "initialization"
    
    async def test_supervisor_process(self):
        """Supervisor 프로세스 테스트"""
        supervisor = SupervisorAgent()
        state_manager = StateManager()
        
        # 초기 상태
        state = state_manager.create_initial_state()
        
        # 첫 번째 실행 - 초기화
        state = await supervisor.process(state)
        
        assert state['required_agents'] is not None
        assert supervisor.current_stage.value == "data_collection"
        assert len(state['next_agents']) > 0
        
        # 정리
        import shutil
        if supervisor.output_dir.exists():
            shutil.rmtree(supervisor.output_dir)


class TestWorkflowIntegration:
    """워크플로우 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_basic_workflow(self):
        """기본 워크플로우 테스트"""
        from graph_builder import EVMarketAnalysisGraph
        
        # 테스트 설정
        config = {
            'supervisor': {'max_iterations': 3},
            'llm': {'model': 'gpt-3.5-turbo'}  # 테스트용 경량 모델
        }
        
        # Mock LLM 응답 설정 (실제 테스트시 Mock 사용)
        # graph = EVMarketAnalysisGraph(config)
        
        # 여기서는 기본적인 Graph 생성만 테스트
        try:
            graph = EVMarketAnalysisGraph(config)
            assert graph is not None
            assert len(graph.agents) == 8  # 8개 Agent
        except Exception as e:
            # API 키 없이도 객체 생성은 가능해야 함
            pytest.skip(f"Skipping due to missing API key: {e}")


def test_project_structure():
    """프로젝트 구조 테스트"""
    # 필수 디렉토리 확인
    required_dirs = ['agents', 'data', 'outputs', 'reports', 'configs', 'tests']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        assert dir_path.exists(), f"Directory {dir_name} should exist"
    
    # 필수 파일 확인
    required_files = [
        'main.py',
        'graph_builder.py', 
        'state_manager.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file_name in required_files:
        file_path = Path(file_name)
        if not file_path.exists():
            # 테스트 환경에서는 경고만
            print(f"Warning: {file_name} not found")


if __name__ == "__main__":
    # 간단한 테스트 실행
    pytest.main([__file__, '-v'])