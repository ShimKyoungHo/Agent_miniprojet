# graph_builder.py
"""
전기차 시장 분석 Graph Builder
2개의 독립적인 분석 체인을 병렬로 실행하는 구조
Chain 2에서 Tech Analysis와 Stock Analysis를 병렬 실행
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import asyncio
import logging

# Agent imports
from agents.market_research_agent import MarketResearchAgent
from agents.consumer_analysis_agent import ConsumerAnalysisAgent
from agents.company_analysis_agent import CompanyAnalysisAgent
from agents.tech_analysis_agent import TechAnalysisAgent
from agents.stock_analysis_agent import StockAnalysisAgent
from agents.chart_generation_agent import ChartGenerationAgent
from agents.report_generation_agent import ReportGenerationAgent

# State management
from state_manager import AgentState, StateManager


class EVMarketAnalysisGraph:
    """전기차 시장 분석 Multi-Agent Graph - 2개 체인 병렬 실행 + 내부 병렬화"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self.state_manager = StateManager()
        
        # LLM 초기화
        self.llm = self._initialize_llm()
        
        # Agent 초기화
        self.agents = self._initialize_agents()
        
        # Graph 구성
        self.graph = self._build_graph()
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('EVMarketAnalysis')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_llm(self) -> ChatOpenAI:
        """LLM 초기화"""
        llm_config = self.config.get('llm', {})
        
        return ChatOpenAI(
            model=llm_config.get('model', 'gpt-4'),
            temperature=llm_config.get('temperature', 0.7),
            api_key=llm_config.get('api_key')
        )
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """모든 Agent 초기화"""
        agents = {
            'market_research': MarketResearchAgent(self.llm, self.config.get('market_research', {})),
            'consumer_analysis': ConsumerAnalysisAgent(self.llm, self.config.get('consumer_analysis', {})),
            'company_analysis': CompanyAnalysisAgent(self.llm, self.config.get('company_analysis', {})),
            'tech_analysis': TechAnalysisAgent(self.llm, self.config.get('tech_analysis', {})),
            'stock_analysis': StockAnalysisAgent(self.llm, self.config.get('stock_analysis', {})),
            'chart_generation': ChartGenerationAgent(self.llm, self.config.get('chart_generation', {})),
            'report_generation': ReportGenerationAgent(self.llm, self.config.get('report_generation', {}))
        }
        
        self.logger.info(f"Initialized {len(agents)} agents")
        return agents
    
    def _build_graph(self) -> StateGraph:
        """LangGraph 구성 - 2개 체인 병렬 실행"""
        workflow = StateGraph(AgentState)
        
        # 병렬 실행 노드 (동기 래퍼 사용)
        workflow.add_node("parallel_chains", self._execute_parallel_chains_sync)
        
        # 개별 Agent 노드 (필요시 직접 호출용)
        for agent_name, agent in self.agents.items():
            workflow.add_node(agent_name, self._create_agent_wrapper_sync(agent))
        
        # 엣지 연결
        workflow.set_entry_point("parallel_chains")
        workflow.add_edge("parallel_chains", "chart_generation")
        workflow.add_edge("chart_generation", "report_generation")
        workflow.add_edge("report_generation", END)
        
        self.logger.info("Graph built successfully (2-chain parallel execution with nested parallelism)")
        return workflow.compile()
    
    async def _execute_chain_1(self, state: AgentState) -> AgentState:
        """
        Chain 1: Market Research → Consumer Analysis
        """
        self.logger.info("🔗 Chain 1 시작: Market Research → Consumer Analysis")
        
        try:
            # 1. Market Research
            self.logger.info("  ├─ Market Research Agent 실행 중...")
            state = await self.agents['market_research'].process(state)
            state['completed_agents'].append('market_research')
            self.logger.info("  ├─ Market Research Agent 완료 ✅")
            
            # 2. Consumer Analysis (Market Research 결과 사용)
            self.logger.info("  └─ Consumer Analysis Agent 실행 중...")
            state = await self.agents['consumer_analysis'].process(state)
            state['completed_agents'].append('consumer_analysis')
            self.logger.info("  └─ Consumer Analysis Agent 완료 ✅")
            
            self.logger.info("🔗 Chain 1 완료!")
            return state
            
        except Exception as e:
            error_msg = f"Chain 1 실행 중 오류: {str(e)}"
            self.logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
    
    async def _execute_chain_2(self, state: AgentState) -> AgentState:
        """
        Chain 2: Company Analysis → (Tech Analysis ∥ Stock Analysis)
        Company Analysis 완료 후 Tech와 Stock을 병렬 실행
        """
        self.logger.info("🔗 Chain 2 시작: Company Analysis → (Tech ∥ Stock)")
        
        try:
            # 1. Company Analysis (선행 필수)
            self.logger.info("  ├─ Company Analysis Agent 실행 중...")
            state = await self.agents['company_analysis'].process(state)
            state['completed_agents'].append('company_analysis')
            self.logger.info("  ├─ Company Analysis Agent 완료 ✅")
            
            # 2. Tech Analysis와 Stock Analysis 병렬 실행 ⭐
            self.logger.info("  ├─ Tech Analysis ∥ Stock Analysis 병렬 실행 중...")
            
            # 각각을 위한 state 복사본 생성
            state_tech = dict(state)
            state_stock = dict(state)
            
            # 병렬 실행
            parallel_tasks = [
                self._run_tech_analysis(state_tech),
                self._run_stock_analysis(state_stock)
            ]
            
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            
            # 결과 병합
            for i, result in enumerate(parallel_results):
                if isinstance(result, Exception):
                    agent_name = 'tech_analysis' if i == 0 else 'stock_analysis'
                    error_msg = f"{agent_name} 실행 실패: {str(result)}"
                    self.logger.error(f"  │  ❌ {error_msg}")
                    state['errors'].append(error_msg)
                else:
                    state = self._merge_states(state, result)
            
            self.logger.info("  └─ Tech ∥ Stock 병렬 실행 완료 ✅")
            
            self.logger.info("🔗 Chain 2 완료!")
            return state
            
        except Exception as e:
            error_msg = f"Chain 2 실행 중 오류: {str(e)}"
            self.logger.error(error_msg)
            state['errors'].append(error_msg)
            return state
    
    async def _run_tech_analysis(self, state: AgentState) -> AgentState:
        """Tech Analysis 실행"""
        try:
            self.logger.info("  │  ├─ Tech Analysis Agent 실행 중...")
            state = await self.agents['tech_analysis'].process(state)
            state['completed_agents'].append('tech_analysis')
            self.logger.info("  │  ├─ Tech Analysis Agent 완료 ✅")
            return state
        except Exception as e:
            self.logger.error(f"  │  ├─ Tech Analysis 오류: {e}")
            state['errors'].append(f"tech_analysis: {str(e)}")
            raise
    
    async def _run_stock_analysis(self, state: AgentState) -> AgentState:
        """Stock Analysis 실행"""
        try:
            self.logger.info("  │  └─ Stock Analysis Agent 실행 중...")
            state = await self.agents['stock_analysis'].process(state)
            state['completed_agents'].append('stock_analysis')
            self.logger.info("  │  └─ Stock Analysis Agent 완료 ✅")
            return state
        except Exception as e:
            self.logger.error(f"  │  └─ Stock Analysis 오류: {e}")
            state['errors'].append(f"stock_analysis: {str(e)}")
            raise
    
    async def _execute_parallel_chains(self, state: AgentState) -> AgentState:
        """
        2개의 분석 체인을 병렬로 실행하고 결과를 취합
        """
        self.logger.info("=" * 70)
        self.logger.info("🚀 2개 분석 체인 병렬 실행 시작")
        self.logger.info("  - Chain 1: Market Research → Consumer Analysis")
        self.logger.info("  - Chain 2: Company Analysis → (Tech ∥ Stock)")
        self.logger.info("=" * 70)
        
        # 각 체인을 위한 state 복사본 생성
        state_1 = dict(state)
        state_2 = dict(state)
        
        # 2개 체인 병렬 실행
        tasks = [
            self._execute_chain_1(state_1),
            self._execute_chain_2(state_2)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 취합
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 결과 취합 중...")
        self.logger.info("=" * 70)
        
        merged_state = state
        
        for i, chain_state in enumerate(results, 1):
            if isinstance(chain_state, Exception):
                error_msg = f"Chain {i} 실행 실패: {str(chain_state)}"
                self.logger.error(f"❌ {error_msg}")
                merged_state['errors'].append(error_msg)
            else:
                self.logger.info(f"✅ Chain {i} 결과 병합 완료")
                merged_state = self._merge_states(merged_state, chain_state)
        
        self.logger.info(f"\n총 완료된 Agent: {len(merged_state['completed_agents'])}개")
        self.logger.info(f"완료 목록: {', '.join(merged_state['completed_agents'])}")
        
        if merged_state['errors']:
            self.logger.warning(f"발생한 에러: {len(merged_state['errors'])}개")
        
        self.logger.info("=" * 70)
        
        return merged_state
    
    def _execute_parallel_chains_sync(self, state: AgentState) -> AgentState:
        """
        동기 래퍼: asyncio.run()으로 비동기 함수 실행
        """
        return asyncio.run(self._execute_parallel_chains(state))
    
    def _merge_states(self, base_state: AgentState, new_state: AgentState) -> AgentState:
        """
        두 상태를 병합
        
        Args:
            base_state: 기본 상태
            new_state: 병합할 새로운 상태
            
        Returns:
            병합된 상태
        """
        # analysis_results 병합 (중요!)
        if 'analysis_results' not in base_state:
            base_state['analysis_results'] = {}
        
        if 'analysis_results' in new_state and new_state['analysis_results']:
            base_state['analysis_results'].update(new_state['analysis_results'])
        
        # 데이터 필드 병합
        data_fields = [
            'market_trends', 'government_policies', 'market_data',
            'consumer_patterns',
            'company_analysis', 'company_tech_data',
            'tech_trends',
            'stock_analysis'
        ]
        
        for field in data_fields:
            if new_state.get(field) is not None:
                base_state[field] = new_state[field]
        
        # 리스트 필드는 중복 제거하며 병합
        list_fields = ['completed_agents', 'errors', 'warnings', 'logs']
        
        for field in list_fields:
            if new_state.get(field):
                existing = set(base_state.get(field, []))
                new_items = set(new_state[field])
                base_state[field] = list(existing | new_items)
        
        # messages는 추가
        if new_state.get('messages'):
            base_state['messages'].extend(new_state['messages'])
        
        return base_state
    
    def _create_agent_wrapper(self, agent):
        """Agent를 비동기로 실행하는 래퍼"""
        async def wrapper(state: AgentState) -> AgentState:
            try:
                self.logger.info(f"▶ {agent.name} 시작")
                result_state = await agent.process(state)
                self.logger.info(f"✅ {agent.name} 완료")
                return result_state
            except Exception as e:
                self.logger.error(f"❌ {agent.name} 오류: {e}")
                state['errors'].append(f"{agent.name}: {str(e)}")
                state['agent_errors'][agent.name] = str(e)
                return state
        
        return wrapper
    
    def _create_agent_wrapper_sync(self, agent):
        """Agent를 동기로 실행하는 래퍼"""
        def wrapper(state: AgentState) -> AgentState:
            try:
                self.logger.info(f"▶ {agent.name} 시작")
                # 비동기 함수를 동기로 실행
                result_state = asyncio.run(agent.process(state))
                self.logger.info(f"✅ {agent.name} 완료")
                return result_state
            except Exception as e:
                self.logger.error(f"❌ {agent.name} 오류: {e}")
                state['errors'].append(f"{agent.name}: {str(e)}")
                state['agent_errors'][agent.name] = str(e)
                return state
        
        return wrapper
    
    def run(self, initial_message: str = None) -> AgentState:
        """
        워크플로우 실행 (동기)
        
        Args:
            initial_message: 초기 메시지
            
        Returns:
            최종 상태
        """
        self.logger.info("🚗 전기차 시장 분석 시스템 시작")
        
        # 초기 상태 생성
        initial_state = self.state_manager.create_initial_state()
        if initial_message:
            initial_state['messages'].append({'role': 'user', 'content': initial_message})
        
        # Graph 실행
        final_state = self.graph.invoke(initial_state)
        
        self.logger.info("\n✅ 전기차 시장 분석 완료!")
        self.logger.info(f"완료된 Agent 수: {len(final_state['completed_agents'])}")
        
        # 체크포인트 저장
        self.state_manager.save_checkpoint(final_state, "final_state")
        
        return final_state
    
    async def run_async(self, initial_message: str = None) -> AgentState:
        """
        워크플로우 실행 (비동기)
        
        Args:
            initial_message: 초기 메시지
            
        Returns:
            최종 상태
        """
        self.logger.info("🚗 전기차 시장 분석 시스템 시작 (비동기)")
        
        # 초기 상태 생성
        initial_state = self.state_manager.create_initial_state()
        if initial_message:
            initial_state['messages'].append({'role': 'user', 'content': initial_message})
        
        # Graph 실행
        final_state = await self.graph.ainvoke(initial_state)
        
        self.logger.info("\n✅ 전기차 시장 분석 완료!")
        self.logger.info(f"완료된 Agent 수: {len(final_state['completed_agents'])}")
        
        # 체크포인트 저장
        self.state_manager.save_checkpoint(final_state, "final_state")
        
        return final_state


def build_graph(config: Dict[str, Any] = None):
    """
    Graph 빌더 함수
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        컴파일된 LangGraph
    """
    builder = EVMarketAnalysisGraph(config)
    return builder.graph


def create_and_run_analysis(config: Dict[str, Any] = None, initial_message: str = None):
    """
    분석 시스템 생성 및 실행
    
    Args:
        config: 설정 딕셔너리
        initial_message: 초기 메시지
        
    Returns:
        최종 분석 결과 상태
    """
    builder = EVMarketAnalysisGraph(config)
    return builder.run(initial_message)


if __name__ == "__main__":
    # 테스트 실행
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config = {
        'llm': {
            'model': 'gpt-4',
            'temperature': 0.7,
            'api_key': os.getenv('OPENAI_API_KEY')
        }
    }
    
    result = create_and_run_analysis(
        config=config,
        initial_message="2025년 전기차 시장 분석을 시작합니다."
    )
    
    print("\n" + "=" * 70)
    print("분석 완료!")
    print(f"완료된 Agent: {result['completed_agents']}")
    print(f"에러: {result['errors']}")
    print("=" * 70)