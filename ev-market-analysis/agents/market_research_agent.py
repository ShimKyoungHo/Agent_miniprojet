# agents/market_research_agent.py

from typing import Dict, Any, Optional, List
import asyncio
import os
from datetime import datetime
from tavily import TavilyClient
from .base_agent import BaseAgent


class MarketResearchAgent(BaseAgent):
    """시장 조사 Agent - Tavily 웹 검색 활용"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("market_research", llm, config)
        
        # Tavily 클라이언트 초기화
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
            self.logger.info("Tavily 클라이언트 초기화 완료")
        else:
            self.tavily_client = None
            self.logger.warning("TAVILY_API_KEY가 설정되지 않았습니다. 검색 기능이 제한됩니다.")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """시장 조사 메인 프로세스"""
        self.logger.info("시장 조사 시작...")
        
        try:
            # 병렬로 여러 데이터 소스 조사
            tasks = [
                self._analyze_global_market(),
                self._analyze_regional_markets(),
                self._analyze_government_policies(),
                self._analyze_market_trends()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 통합
            market_data = {
                'global_market': results[0] if not isinstance(results[0], Exception) else None,
                'regional_markets': results[1] if not isinstance(results[1], Exception) else None,
                'government_policies': results[2] if not isinstance(results[2], Exception) else None,
                'trends': results[3] if not isinstance(results[3], Exception) else None,
                'timestamp': self.get_timestamp()
            }
            
            # LLM을 통한 종합 분석
            if self.llm:
                synthesis = await self._synthesize_market_insights(market_data)
                market_data['synthesis'] = synthesis
            
            # 상태 업데이트
            state['market_data'] = market_data
            state['market_trends'] = market_data.get('trends')
            state['government_policies'] = market_data.get('government_policies')
            
            # 결과 저장
            self.save_output(market_data, 'market_research.json')
            
            self.logger.info("✅ 시장 조사 완료")
            return state
            
        except Exception as e:
            self.logger.error(f"시장 조사 중 오류: {e}")
            state['errors'].append(f"market_research: {str(e)}")
            return state
    
    async def _analyze_global_market(self) -> Dict:
        """글로벌 전기차 시장 분석"""
        self.logger.info("  📊 글로벌 시장 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_global_market()
        
        try:
            # Tavily 검색
            query = "electric vehicle market size growth forecast 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=5
            )
            
            # 검색 결과 처리
            market_info = {
                'query': query,
                'results': search_results.get('results', []),
                'analysis_date': datetime.now().isoformat()
            }
            
            # LLM으로 분석
            if self.llm and search_results.get('results'):
                analysis = await self._analyze_search_results(
                    search_results['results'],
                    "글로벌 전기차 시장 규모와 성장률을 분석하세요."
                )
                market_info['llm_analysis'] = analysis
            
            return market_info
            
        except Exception as e:
            self.logger.error(f"글로벌 시장 분석 오류: {e}")
            return self._get_fallback_global_market()
    
    async def _analyze_regional_markets(self) -> Dict:
        """지역별 전기차 시장 분석"""
        self.logger.info("  🌍 지역별 시장 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_regional_markets()
        
        try:
            # 주요 지역별 검색
            regions = ['China', 'Europe', 'USA', 'Korea']
            regional_data = {}
            
            for region in regions:
                query = f"electric vehicle market share {region} 2025"
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query=query,
                    max_results=3
                )
                
                regional_data[region] = {
                    'query': query,
                    'results': search_results.get('results', [])
                }
            
            return {
                'regions': regional_data,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"지역별 시장 분석 오류: {e}")
            return self._get_fallback_regional_markets()
    
    async def _analyze_government_policies(self) -> Dict:
        """정부 정책 분석"""
        self.logger.info("  🏛️ 정부 정책 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_government_policies()
        
        try:
            # 정책 관련 검색
            queries = [
                "electric vehicle subsidy policy 2025",
                "EV charging infrastructure government support",
                "carbon emission regulations electric vehicles"
            ]
            
            policy_data = []
            for query in queries:
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query=query,
                    max_results=3
                )
                
                policy_data.append({
                    'query': query,
                    'results': search_results.get('results', [])
                })
            
            return {
                'policies': policy_data,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"정부 정책 분석 오류: {e}")
            return self._get_fallback_government_policies()
    
    async def _analyze_market_trends(self) -> Dict:
        """시장 트렌드 분석"""
        self.logger.info("  📈 시장 트렌드 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_market_trends()
        
        try:
            # 트렌드 검색
            query = "electric vehicle market trends consumer preferences 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=5
            )
            
            return {
                'query': query,
                'results': search_results.get('results', []),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"시장 트렌드 분석 오류: {e}")
            return self._get_fallback_market_trends()
    
    async def _analyze_search_results(self, results: List[Dict], instruction: str) -> str:
        """검색 결과를 LLM으로 분석"""
        if not self.llm or not results:
            return "분석 불가"
        
        try:
            # 검색 결과를 텍스트로 변환
            context = "\n\n".join([
                f"출처: {r.get('url', 'Unknown')}\n제목: {r.get('title', 'No title')}\n내용: {r.get('content', 'No content')}"
                for r in results[:3]  # 상위 3개만 사용
            ])
            
            prompt = f"""다음 검색 결과를 바탕으로 {instruction}

검색 결과:
{context}

한국어로 간결하게 3-5문장으로 분석해주세요."""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"LLM 분석 오류: {e}")
            return "분석 중 오류 발생"
    
    async def _synthesize_market_insights(self, market_data: Dict) -> str:
        """시장 데이터를 종합 분석"""
        if not self.llm:
            return "종합 분석 불가 (LLM 미설정)"
        
        try:
            prompt = f"""다음 전기차 시장 조사 데이터를 종합하여 핵심 인사이트를 도출하세요:

글로벌 시장: {market_data.get('global_market', {}).get('llm_analysis', '데이터 없음')}
지역별 시장: 중국, 유럽, 미국, 한국 시장 데이터 수집 완료
정부 정책: 보조금, 충전 인프라, 환경 규제 관련 정책 분석 완료
시장 트렌드: 최신 소비자 선호도 및 기술 트렌드 조사 완료

다음 형식으로 종합 분석해주세요:
1. 시장 현황 (2-3문장)
2. 주요 트렌드 (3-4개 bullet points)
3. 정책 영향 (2-3문장)
4. 투자 시사점 (2-3문장)
"""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"종합 분석 오류: {e}")
            return "종합 분석 중 오류 발생"
    
    # Fallback 데이터 (Tavily 사용 불가 시)
    def _get_fallback_global_market(self) -> Dict:
        """Fallback 글로벌 시장 데이터"""
        return {
            'market_size_2025': '약 5000억 달러',
            'growth_rate': '연평균 18-22%',
            'forecast_2030': '약 1조 5000억 달러',
            'note': 'Fallback 데이터 (웹 검색 미사용)'
        }
    
    def _get_fallback_regional_markets(self) -> Dict:
        """Fallback 지역별 시장 데이터"""
        return {
            'China': {'market_share': '약 50%', 'status': '세계 최대 시장'},
            'Europe': {'market_share': '약 25%', 'status': '빠른 성장'},
            'USA': {'market_share': '약 15%', 'status': '정책 지원 확대'},
            'Korea': {'market_share': '약 2%', 'status': '내수 + 수출'},
            'note': 'Fallback 데이터 (웹 검색 미사용)'
        }
    
    def _get_fallback_government_policies(self) -> Dict:
        """Fallback 정부 정책 데이터"""
        return {
            'subsidies': '주요국 보조금 정책 유지',
            'infrastructure': '충전 인프라 확충 지속',
            'regulations': '탄소 배출 규제 강화',
            'note': 'Fallback 데이터 (웹 검색 미사용)'
        }
    
    def _get_fallback_market_trends(self) -> Dict:
        """Fallback 시장 트렌드 데이터"""
        return {
            'battery_tech': '배터리 기술 발전 (주행거리 증가)',
            'price_parity': '가격 경쟁력 개선',
            'consumer_acceptance': '소비자 수용도 증가',
            'note': 'Fallback 데이터 (웹 검색 미사용)'
        }