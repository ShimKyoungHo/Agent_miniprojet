# agents/tech_analysis_agent.py

from typing import Dict, Any, Optional, List
import asyncio
import os
from datetime import datetime
from tavily import TavilyClient
from .base_agent import BaseAgent


class TechAnalysisAgent(BaseAgent):
    """기술 분석 Agent - Tavily 웹 검색 활용"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("tech_analysis", llm, config)
        
        # Tavily 클라이언트 초기화
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
            self.logger.info("Tavily 클라이언트 초기화 완료")
        else:
            self.tavily_client = None
            self.logger.warning("TAVILY_API_KEY가 설정되지 않았습니다. 검색 기능이 제한됩니다.")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """기술 분석 메인 프로세스"""
        self.logger.info("기술 분석 시작...")
        
        # 기업 기술 데이터 확인
        company_tech_data = state.get('company_tech_data', {})
        
        try:
            # 병렬로 기술 분석
            tasks = [
                self._analyze_battery_technology(),
                self._analyze_charging_technology(),
                self._analyze_autonomous_technology(),
                self._analyze_manufacturing_innovation(),
                self._analyze_software_platform(),
                self._analyze_future_technologies()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 통합
            tech_analysis = {
                'battery_tech': results[0] if not isinstance(results[0], Exception) else None,
                'charging_tech': results[1] if not isinstance(results[1], Exception) else None,
                'autonomous_tech': results[2] if not isinstance(results[2], Exception) else None,
                'manufacturing_tech': results[3] if not isinstance(results[3], Exception) else None,
                'software_platform': results[4] if not isinstance(results[4], Exception) else None,
                'future_tech': results[5] if not isinstance(results[5], Exception) else None,
                'company_tech_data': company_tech_data,
                'timestamp': self.get_timestamp()
            }
            
            # 기술 성숙도 평가
            maturity = await self._assess_technology_maturity(tech_analysis)
            tech_analysis['maturity_assessment'] = maturity
            
            # 기술 로드맵 생성
            roadmap = await self._create_technology_roadmap(tech_analysis)
            tech_analysis['roadmap'] = roadmap
            
            # LLM 종합 분석
            if self.llm:
                synthesis = await self._synthesize_tech_insights(tech_analysis)
                tech_analysis['synthesis'] = synthesis
            
            # 상태 업데이트
            state['tech_trends'] = tech_analysis
            
            # 결과 저장
            self.save_output(tech_analysis, 'tech_analysis.json')
            
            self.logger.info("✅ 기술 분석 완료")
            return state
            
        except Exception as e:
            self.logger.error(f"기술 분석 중 오류: {e}")
            state['errors'].append(f"tech_analysis: {str(e)}")
            return state
    
    async def _analyze_battery_technology(self) -> Dict:
        """배터리 기술 분석"""
        self.logger.info("  🔋 배터리 기술 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_battery_tech()
        
        try:
            queries = [
                "electric vehicle battery technology trends 2025 lithium ion solid state",
                "EV battery energy density improvement 2025",
                "battery manufacturing cost reduction technology",
                "next generation battery technology electric vehicles"
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
                'battery_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"배터리 기술 분석 오류: {e}")
            return self._get_fallback_battery_tech()
    
    async def _analyze_charging_technology(self) -> Dict:
        """충전 기술 분석"""
        self.logger.info("  ⚡ 충전 기술 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_charging_tech()
        
        try:
            queries = [
                "electric vehicle fast charging technology 2025 ultra rapid",
                "wireless charging EV technology development",
                "vehicle to grid V2G technology adoption",
                "EV charging speed improvement battery health"
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
                'charging_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"충전 기술 분석 오류: {e}")
            return self._get_fallback_charging_tech()
    
    async def _analyze_autonomous_technology(self) -> Dict:
        """자율주행 기술 분석"""
        self.logger.info("  🤖 자율주행 기술 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_autonomous_tech()
        
        try:
            queries = [
                "electric vehicle autonomous driving technology integration 2025",
                "ADAS advanced driver assistance systems EV",
                "self driving technology level 3 level 4 electric vehicles",
                "AI software defined vehicle electric car"
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
                'autonomous_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"자율주행 기술 분석 오류: {e}")
            return self._get_fallback_autonomous_tech()
    
    async def _analyze_manufacturing_innovation(self) -> Dict:
        """제조 혁신 분석"""
        self.logger.info("  🏭 제조 혁신 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_manufacturing_tech()
        
        try:
            queries = [
                "electric vehicle manufacturing innovation giga casting 2025",
                "EV production efficiency automation robotics",
                "electric vehicle platform architecture scalability",
                "battery manufacturing vertical integration"
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
                'manufacturing_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"제조 혁신 분석 오류: {e}")
            return self._get_fallback_manufacturing_tech()
    
    async def _analyze_software_platform(self) -> Dict:
        """소프트웨어 플랫폼 분석"""
        self.logger.info("  💻 소프트웨어 플랫폼 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_software_platform()
        
        try:
            queries = [
                "electric vehicle software platform OTA updates 2025",
                "software defined vehicle SDV architecture",
                "EV operating system connectivity ecosystem"
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
                'software_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"소프트웨어 플랫폼 분석 오류: {e}")
            return self._get_fallback_software_platform()
    
    async def _analyze_future_technologies(self) -> Dict:
        """미래 기술 전망"""
        self.logger.info("  🔮 미래 기술 전망 중...")
        
        if not self.tavily_client:
            return self._get_fallback_future_tech()
        
        try:
            queries = [
                "electric vehicle future technology 2030 breakthrough",
                "hydrogen fuel cell electric vehicle development",
                "graphene battery technology commercialization",
                "AI powered battery management system"
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
                'future_tech_searches': results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"미래 기술 전망 오류: {e}")
            return self._get_fallback_future_tech()
    
    async def _assess_technology_maturity(self, tech_data: Dict) -> Dict:
        """기술 성숙도 평가"""
        self.logger.info("  📊 기술 성숙도 평가 중...")
        
        if not self.llm:
            return self._get_default_maturity()
        
        try:
            prompt = """전기차 주요 기술들의 성숙도를 평가하세요.

기술 분야:
1. 배터리 기술 (Battery Technology)
2. 충전 기술 (Charging Technology)
3. 자율주행 기술 (Autonomous Driving)
4. 제조 기술 (Manufacturing)
5. 소프트웨어 플랫폼 (Software Platform)

각 기술의 성숙도를 다음 5단계로 평가하고 JSON으로 응답하세요:
- 1: 연구 단계 (Research)
- 2: 개발 단계 (Development)
- 3: 초기 상용화 (Early Commercialization)
- 4: 성숙 단계 (Mature)
- 5: 최적화 단계 (Optimized)

JSON 형식:
{
  "battery_technology": {"level": 4, "note": "리튬이온 성숙, 고체전지 개발 중"},
  "charging_technology": {"level": 3, "note": "급속충전 확대, 무선충전 초기"},
  "autonomous_driving": {"level": 3, "note": "L2/L3 상용화, L4 테스트 중"},
  "manufacturing": {"level": 4, "note": "자동화 고도화"},
  "software_platform": {"level": 3, "note": "OTA 보급, 생태계 구축 중"}
}

JSON만 출력하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # JSON 파싱
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                maturity = json.loads(json_match.group())
                self.logger.info(f"기술 성숙도 평가 완료")
                return maturity
            else:
                return self._get_default_maturity()
            
        except Exception as e:
            self.logger.error(f"성숙도 평가 오류: {e}")
            return self._get_default_maturity()
    
    def _get_default_maturity(self) -> Dict:
        """기본 성숙도 데이터"""
        return {
            "battery_technology": {"level": 4, "note": "리튬이온 성숙, 고체전지 개발 중"},
            "charging_technology": {"level": 3, "note": "급속충전 확대, 무선충전 초기"},
            "autonomous_driving": {"level": 3, "note": "L2/L3 상용화, L4 테스트 중"},
            "manufacturing": {"level": 4, "note": "자동화 고도화"},
            "software_platform": {"level": 3, "note": "OTA 보급, 생태계 구축 중"}
        }
    
    async def _create_technology_roadmap(self, tech_data: Dict) -> Dict:
        """기술 로드맵 생성"""
        self.logger.info("  🗺️ 기술 로드맵 생성 중...")
        
        if not self.llm:
            return self._get_default_roadmap()
        
        try:
            maturity = tech_data.get('maturity_assessment', self._get_default_maturity())
            
            prompt = f"""전기차 기술 로드맵을 2025-2030년 기간으로 작성하세요.

현재 성숙도:
- 배터리: Level {maturity.get('battery_technology', {}).get('level', 4)}
- 충전: Level {maturity.get('charging_technology', {}).get('level', 3)}
- 자율주행: Level {maturity.get('autonomous_driving', {}).get('level', 3)}

다음 시기별로 주요 기술 마일스톤을 예측하세요:

1. 2025-2026 (단기)
   - 배터리: 
   - 충전:
   - 자율주행:
   
2. 2027-2028 (중기)
   - 배터리:
   - 충전:
   - 자율주행:
   
3. 2029-2030 (장기)
   - 배터리:
   - 충전:
   - 자율주행:

각 항목은 1-2문장으로 간결하게 작성하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'roadmap_text': content,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"로드맵 생성 오류: {e}")
            return self._get_default_roadmap()
    
    def _get_default_roadmap(self) -> Dict:
        """기본 로드맵"""
        return {
            '2025-2026': {
                'battery': '에너지 밀도 300Wh/kg 달성, 고체전지 초기 상용화',
                'charging': '350kW 급속충전 보편화',
                'autonomous': 'L3 자율주행 대중화'
            },
            '2027-2028': {
                'battery': '고체전지 본격 양산, 500km+ 주행거리 표준화',
                'charging': '무선 고속충전 상용화',
                'autonomous': 'L4 자율주행 특정 지역 운영'
            },
            '2029-2030': {
                'battery': '차세대 배터리 기술 등장, 비용 대폭 감소',
                'charging': '초고속 충전 (5분 80%)',
                'autonomous': 'L4/L5 자율주행 확대'
            }
        }
    
    async def _synthesize_tech_insights(self, tech_data: Dict) -> str:
        """기술 분석 종합"""
        if not self.llm:
            return "종합 분석 불가 (LLM 미설정)"
        
        try:
            maturity = tech_data.get('maturity_assessment', self._get_default_maturity())
            
            prompt = f"""전기차 기술 분석 결과를 종합하세요:

기술 성숙도:
- 배터리: Level {maturity.get('battery_technology', {}).get('level', 4)} - {maturity.get('battery_technology', {}).get('note', '')}
- 충전: Level {maturity.get('charging_technology', {}).get('level', 3)} - {maturity.get('charging_technology', {}).get('note', '')}
- 자율주행: Level {maturity.get('autonomous_driving', {}).get('level', 3)} - {maturity.get('autonomous_driving', {}).get('note', '')}

다음 형식으로 종합 분석해주세요:
1. 핵심 기술 현황 (2-3문장)
2. 주요 혁신 트렌드 (3-4개 bullet points)
3. 기술적 과제 (2-3문장)
4. 투자 기회 (2-3문장)
"""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"종합 분석 오류: {e}")
            return "종합 분석 중 오류 발생"
    
    # Fallback 데이터
    def _get_fallback_battery_tech(self) -> Dict:
        return {
            'current_tech': '리튬이온 배터리 주류',
            'energy_density': '250-300 Wh/kg',
            'future_tech': '고체전지, 리튬-메탈',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_charging_tech(self) -> Dict:
        return {
            'fast_charging': '150-350kW 급속충전',
            'wireless': '개발 중',
            'v2g': '초기 시험 단계',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_autonomous_tech(self) -> Dict:
        return {
            'current_level': 'L2/L3',
            'commercialization': 'L2 보편화, L3 확대 중',
            'future': 'L4/L5 개발 중',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_manufacturing_tech(self) -> Dict:
        return {
            'key_innovation': '기가캐스팅, 자동화',
            'efficiency': '생산 시간 단축',
            'cost_reduction': '30-40%',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_software_platform(self) -> Dict:
        return {
            'ota_updates': '보편화',
            'connectivity': '5G, V2X',
            'ecosystem': '앱 스토어, 서비스 플랫폼',
            'note': 'Fallback 데이터'
        }
    
    def _get_fallback_future_tech(self) -> Dict:
        return {
            'breakthrough_tech': [
                '고체전지 상용화',
                '그래핀 배터리',
                '수소 전기차',
                'AI 배터리 관리'
            ],
            'timeline': '2027-2030',
            'note': 'Fallback 데이터'
        }