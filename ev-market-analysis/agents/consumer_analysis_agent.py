# agents/consumer_analysis_agent.py

from typing import Dict, Any, Optional, List
import asyncio
import os
from datetime import datetime
from tavily import TavilyClient
from .base_agent import BaseAgent


class ConsumerAnalysisAgent(BaseAgent):
    """소비자 분석 Agent - Tavily 웹 검색 활용"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("consumer_analysis", llm, config)
        
        # Tavily 클라이언트 초기화
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
            self.logger.info("Tavily 클라이언트 초기화 완료")
        else:
            self.tavily_client = None
            self.logger.warning("TAVILY_API_KEY가 설정되지 않았습니다. 검색 기능이 제한됩니다.")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """소비자 분석 메인 프로세스"""
        self.logger.info("소비자 분석 시작...")
        
        # Market Research 데이터 확인
        market_data = state.get('market_data', {})
        market_trends = state.get('market_trends', {})
        
        try:
            # 병렬로 소비자 데이터 수집
            tasks = [
                self._analyze_purchase_factors(),
                self._analyze_consumer_demographics(),
                self._analyze_price_sensitivity(),
                self._analyze_brand_preferences(),
                self._analyze_adoption_barriers(),
                self._analyze_consumer_sentiment(),
                self._analyze_vehicle_type_preferences()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 통합
            consumer_data = {
                'purchase_factors': results[0] if not isinstance(results[0], Exception) else None,
                'demographics': results[1] if not isinstance(results[1], Exception) else None,
                'price_sensitivity': results[2] if not isinstance(results[2], Exception) else None,
                'brand_preferences': results[3] if not isinstance(results[3], Exception) else None,
                'adoption_barriers': results[4] if not isinstance(results[4], Exception) else None,
                'consumer_sentiment': results[5] if not isinstance(results[5], Exception) else None,
                'vehicle_preferences': results[6] if not isinstance(results[6], Exception) else None,
                'timestamp': self.get_timestamp()
            }
            
            # preferences 구조 추가 (차트 호환성)
            if consumer_data['vehicle_preferences']:
                consumer_data['preferences'] = {
                    'vehicle_type': consumer_data['vehicle_preferences'].get('vehicle_type', {})
                }
            
            # 영향 가중치 계산
            weights = await self._calculate_influence_weights(consumer_data)
            consumer_data['influence_weights'] = weights
            
            # 시장 데이터와 통합 분석
            integrated_analysis = await self._integrate_with_market_data(
                consumer_data, market_data, market_trends
            )
            consumer_data['integrated_analysis'] = integrated_analysis
            
            # LLM 종합 분석
            if self.llm:
                synthesis = await self._synthesize_consumer_insights(consumer_data)
                consumer_data['synthesis'] = synthesis
            
            # 상태 업데이트
            state['consumer_patterns'] = consumer_data
            
            # 결과 저장
            self.save_output(consumer_data, 'consumer_analysis.json')
            
            self.logger.info("✅ 소비자 분석 완료")
            return state
            
        except Exception as e:
            self.logger.error(f"소비자 분석 중 오류: {e}")
            state['errors'].append(f"consumer_analysis: {str(e)}")
            return state
    
    async def _analyze_purchase_factors(self) -> Dict:
        """구매 결정 요인 분석"""
        self.logger.info("  🛒 구매 결정 요인 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_purchase_factors()
        
        try:
            query = "electric vehicle purchase decision factors consumer survey 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=5
            )
            
            # 추가 검색: 구매 장벽
            query2 = "why consumers buy electric vehicles main reasons"
            search_results2 = await asyncio.to_thread(
                self.tavily_client.search,
                query=query2,
                max_results=3
            )
            
            return {
                'main_query': {
                    'query': query,
                    'results': search_results.get('results', [])
                },
                'secondary_query': {
                    'query': query2,
                    'results': search_results2.get('results', [])
                },
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"구매 요인 분석 오류: {e}")
            return self._get_fallback_purchase_factors()
    
    async def _analyze_consumer_demographics(self) -> Dict:
        """소비자 인구통계 분석"""
        self.logger.info("  👥 소비자 인구통계 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_demographics()
        
        try:
            queries = [
                "electric vehicle buyer demographics age income 2025",
                "EV adoption by generation millennials gen z statistics",
                "electric vehicle ownership by region urban rural"
            ]
            
            results = []
            for query in queries:
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query=query,
                    max_results=3
                )
                results.append({
                    'query': query,
                    'results': search_results.get('results', [])
                })
            
            return {
                'demographic_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"인구통계 분석 오류: {e}")
            return self._get_fallback_demographics()
    
    async def _analyze_price_sensitivity(self) -> Dict:
        """가격 민감도 분석"""
        self.logger.info("  💰 가격 민감도 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_price_sensitivity()
        
        try:
            query = "electric vehicle price sensitivity consumer willingness to pay 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=5
            )
            
            # 추가: 가격 대비 가치
            query2 = "electric vehicle total cost ownership vs gasoline"
            search_results2 = await asyncio.to_thread(
                self.tavily_client.search,
                query=query2,
                max_results=3
            )
            
            return {
                'price_sensitivity': {
                    'query': query,
                    'results': search_results.get('results', [])
                },
                'value_comparison': {
                    'query': query2,
                    'results': search_results2.get('results', [])
                },
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"가격 민감도 분석 오류: {e}")
            return self._get_fallback_price_sensitivity()
    
    async def _analyze_brand_preferences(self) -> Dict:
        """브랜드 선호도 분석"""
        self.logger.info("  🏷️ 브랜드 선호도 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_brand_preferences()
        
        try:
            query = "electric vehicle brand preference consumer survey loyalty 2025"
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
            self.logger.error(f"브랜드 선호도 분석 오류: {e}")
            return self._get_fallback_brand_preferences()
    
    async def _analyze_adoption_barriers(self) -> Dict:
        """도입 장벽 분석"""
        self.logger.info("  🚧 도입 장벽 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_adoption_barriers()
        
        try:
            queries = [
                "electric vehicle adoption barriers challenges 2025",
                "EV charging infrastructure concerns consumer",
                "electric vehicle range anxiety statistics"
            ]
            
            results = []
            for query in queries:
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query=query,
                    max_results=3
                )
                results.append({
                    'query': query,
                    'results': search_results.get('results', [])
                })
            
            return {
                'barrier_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"도입 장벽 분석 오류: {e}")
            return self._get_fallback_adoption_barriers()
    
    async def _analyze_vehicle_type_preferences(self) -> Dict:
        """차량 타입 선호도 분석 - 새로운 함수"""
        self.logger.info("  🚗 차량 타입 선호도 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_vehicle_preferences()
        
        try:
            query = "electric vehicle type preferences SUV sedan truck consumer survey 2024"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=5
            )
            
            # LLM으로 분석
            if self.llm and search_results.get('results'):
                analysis = await self._analyze_vehicle_preferences_with_llm(search_results)
                return {
                    'search_results': search_results.get('results', []),
                    'vehicle_type': analysis.get('vehicle_type', {}),
                    'llm_analysis': analysis.get('summary', ''),
                    'analysis_date': datetime.now().isoformat()
                }
            else:
                return self._get_fallback_vehicle_preferences()
            
        except Exception as e:
            self.logger.error(f"차량 타입 선호도 분석 오류: {e}")
            return self._get_fallback_vehicle_preferences()
    
    async def _analyze_vehicle_preferences_with_llm(self, search_results: Dict) -> Dict:
        """LLM으로 차량 타입 선호도 분석"""
        
        context = "\n\n".join([
            f"Source {i+1}: {r.get('content', '')[:500]}"
            for i, r in enumerate(search_results.get('results', [])[:3])
        ])
        
        prompt = f"""Based on the following search results about electric vehicle preferences, 
analyze consumer preferences by vehicle type.

{context}

Provide your analysis in JSON format:
{{
    "vehicle_type": {{
        "SUV": 0.35,
        "Sedan": 0.30,
        "Truck": 0.20,
        "Compact": 0.15
    }},
    "summary": "Brief summary of findings"
}}

The values should be proportions (0-1) that sum to 1.0.
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            
            # JSON 파싱
            import json
            import re
            
            # JSON 부분 추출
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return self._get_fallback_vehicle_preferences()
                
        except Exception as e:
            self.logger.error(f"LLM 분석 오류: {e}")
            return self._get_fallback_vehicle_preferences()
    
    def _get_fallback_vehicle_preferences(self) -> Dict:
        """차량 타입 선호도 기본값"""
        return {
            'vehicle_type': {
                'SUV': 0.35,
                'Sedan': 0.30,
                'Truck': 0.20,
                'Compact': 0.15
            },
            'search_results': [],
            'llm_analysis': '기본 데이터 사용 (검색 실패)',
            'analysis_date': datetime.now().isoformat()
        }
    
    async def _analyze_consumer_sentiment(self) -> Dict:
        """소비자 감성 분석"""
        self.logger.info("  😊 소비자 감성 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_consumer_sentiment()
        
        try:
            query = "electric vehicle consumer sentiment satisfaction reviews 2025"
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
            self.logger.error(f"소비자 감성 분석 오류: {e}")
            return self._get_fallback_consumer_sentiment()
    
    async def _calculate_influence_weights(self, consumer_data: Dict) -> Dict:
        """영향 가중치 계산"""
        self.logger.info("  ⚖️ 영향 가중치 계산 중...")
        
        if not self.llm:
            return self._get_default_weights()
        
        try:
            # 검색 결과 기반으로 가중치 추출 요청
            prompt = """전기차 구매 결정에 영향을 미치는 주요 요인들의 상대적 가중치를 분석하세요.

주요 요인:
1. 가격 (Price)
2. 주행거리 (Range)
3. 충전 인프라 (Charging Infrastructure)
4. 브랜드 신뢰도 (Brand Trust)
5. 환경 의식 (Environmental Concern)
6. 정부 보조금 (Government Incentives)
7. 운영 비용 (Operating Cost)
8. 성능/기술 (Performance/Technology)

다음 형식의 JSON으로 응답해주세요 (합계 100%):
{
  "price": x,
  "range": x,
  "charging_infrastructure": x,
  "brand_trust": x,
  "environmental_concern": x,
  "government_incentives": x,
  "operating_cost": x,
  "performance_technology": x
}

JSON만 출력하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # JSON 파싱 시도
            import json
            import re
            
            # JSON 추출
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                weights = json.loads(json_match.group())
                self.logger.info(f"영향 가중치 계산 완료: {weights}")
                return weights
            else:
                return self._get_default_weights()
            
        except Exception as e:
            self.logger.error(f"가중치 계산 오류: {e}")
            return self._get_default_weights()
    
    def _get_default_weights(self) -> Dict:
        """기본 가중치"""
        return {
            "price": 25,
            "range": 20,
            "charging_infrastructure": 15,
            "brand_trust": 12,
            "environmental_concern": 10,
            "government_incentives": 8,
            "operating_cost": 6,
            "performance_technology": 4
        }
    
    async def _integrate_with_market_data(self, consumer_data: Dict, market_data: Dict, market_trends: Dict) -> str:
        """시장 데이터와 소비자 데이터 통합 분석"""
        if not self.llm:
            return "통합 분석 불가 (LLM 미설정)"
        
        try:
            prompt = f"""시장 데이터와 소비자 분석 결과를 통합하여 인사이트를 도출하세요:

시장 트렌드:
- 전기차 시장 성장률: 연평균 18-22%
- 주요 시장: 중국, 유럽, 미국

소비자 영향 가중치:
{consumer_data.get('influence_weights', self._get_default_weights())}

다음 질문에 답변하세요:
1. 시장 성장과 소비자 수요가 일치하는가? (2-3문장)
2. 소비자의 주요 관심사가 시장 트렌드에 반영되고 있는가? (2-3문장)
3. 향후 6-12개월 소비자 수요 예측 (3-4문장)
"""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"통합 분석 오류: {e}")
            return "통합 분석 중 오류 발생"
    
    async def _synthesize_consumer_insights(self, consumer_data: Dict) -> str:
        """소비자 분석 종합"""
        if not self.llm:
            return "종합 분석 불가 (LLM 미설정)"
        
        try:
            weights = consumer_data.get('influence_weights', self._get_default_weights())
            
            prompt = f"""전기차 소비자 분석 결과를 종합하세요:

영향 가중치 (구매 결정 요인):
- 가격: {weights.get('price', 25)}%
- 주행거리: {weights.get('range', 20)}%
- 충전 인프라: {weights.get('charging_infrastructure', 15)}%
- 브랜드 신뢰: {weights.get('brand_trust', 12)}%
- 환경 의식: {weights.get('environmental_concern', 10)}%

다음 형식으로 종합 분석해주세요:
1. 소비자 프로필 (2-3문장)
2. 주요 구매 동기 (3개 bullet points)
3. 도입 장벽 (3개 bullet points)
4. 마케팅 시사점 (2-3문장)
"""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"종합 분석 오류: {e}")
            return "종합 분석 중 오류 발생"
    
    # Fallback 데이터
    def _get_fallback_purchase_factors(self) -> Dict:
        return {
            'top_factors': ['가격', '주행거리', '충전 편의성', '브랜드 신뢰도'],
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_demographics(self) -> Dict:
        return {
            'age_groups': {
                '25-34': '35%',
                '35-44': '30%',
                '45-54': '20%',
                '55+': '15%'
            },
            'income_level': '중상위층 이상',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_price_sensitivity(self) -> Dict:
        return {
            'sensitivity_level': '높음',
            'acceptable_premium': '20-30% vs 내연기관',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_brand_preferences(self) -> Dict:
        return {
            'top_brands': ['Tesla', 'Hyundai', 'Kia', 'Mercedes'],
            'loyalty_factors': ['기술력', '브랜드 이미지', 'A/S'],
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_adoption_barriers(self) -> Dict:
        return {
            'barriers': [
                '충전 인프라 부족',
                '높은 초기 구매 비용',
                '주행거리 불안감',
                '충전 시간'
            ],
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_consumer_sentiment(self) -> Dict:
        return {
            'overall_sentiment': '긍정적 (70%)',
            'satisfaction_score': '4.2/5.0',
            'note': 'Fallback 데이터'
        }