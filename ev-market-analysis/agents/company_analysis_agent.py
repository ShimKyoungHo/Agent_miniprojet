# agents/company_analysis_agent.py

from typing import Dict, Any, Optional, List
import asyncio
import os
from datetime import datetime
from tavily import TavilyClient
from .base_agent import BaseAgent


class CompanyAnalysisAgent(BaseAgent):
    """기업 분석 Agent - Tavily 웹 검색 활용 (동적 기업 발굴)"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("company_analysis", llm, config)
        
        # 동적 발굴을 사용할지 여부
        self.use_dynamic_discovery = config.get('use_dynamic_discovery', True) if config else True
        
        # Fallback용 기본 기업 목록 (동적 발굴 실패 시)
        self.fallback_companies = config.get('target_companies', [
            'Tesla', 'BYD', 'Volkswagen', 'Hyundai', 'GM', 
            'Ford', 'Rivian', 'NIO', 'XPeng', 'Stellantis'
        ]) if config else ['Tesla', 'BYD', 'Volkswagen', 'Hyundai', 'GM']
        
        self.max_companies = config.get('max_companies', 10) if config else 10
        
        # Tavily 클라이언트 초기화
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
            self.logger.info("Tavily 클라이언트 초기화 완료")
        else:
            self.tavily_client = None
            self.logger.warning("TAVILY_API_KEY가 설정되지 않았습니다. 검색 기능이 제한됩니다.")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """기업 분석 메인 프로세스"""
        self.logger.info("기업 분석 시작...")
        
        try:
            # 1단계: 상위 전기차 기업 발굴
            if self.use_dynamic_discovery and self.tavily_client:
                self.logger.info("🔍 전기차 시장 상위 기업 발굴 중...")
                companies = await self._discover_top_companies()
                
                if not companies:
                    self.logger.warning("동적 발굴 실패. Fallback 기업 목록 사용")
                    companies = self.fallback_companies[:self.max_companies]
            else:
                companies = self.fallback_companies[:self.max_companies]
            
            # 상위 N개로 제한
            companies = companies[:self.max_companies]
            self.logger.info(f"✅ 분석 대상 기업 ({len(companies)}개): {', '.join(companies)}")
            
            # 2단계: 병렬로 여러 기업 분석
            tasks = []
            for company in companies:
                tasks.append(self._analyze_company(company))
            
            company_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 3단계: 결과 통합 및 핵심 기술 추출
            companies_data = {}
            tech_portfolio = {}
            
            for i, company in enumerate(companies):
                if not isinstance(company_results[i], Exception):
                    company_data = company_results[i]
                    companies_data[company] = company_data
                    
                    # 핵심 기술 추출
                    key_tech = await self._extract_key_technologies(company, company_data)
                    if key_tech:
                        tech_portfolio[company] = key_tech
                else:
                    self.logger.error(f"{company} 분석 실패: {company_results[i]}")
            
            # 4단계: 산업 전체 분석
            industry_analysis = await self._analyze_industry_dynamics(companies_data)
            
            # 5단계: LLM을 통한 종합 분석
            synthesis = None
            if self.llm:
                synthesis = await self._synthesize_company_insights(companies_data, industry_analysis)
            
            # 상태 업데이트
            state['company_analysis'] = {
                'companies': companies_data,
                'industry_analysis': industry_analysis,
                'synthesis': synthesis,
                'discovered_companies': companies,  # 발굴된 기업 리스트
                'timestamp': self.get_timestamp()
            }
            state['company_tech_data'] = tech_portfolio  # 기술 데이터 전달
            
            # 결과 저장
            self.save_output(state['company_analysis'], 'company_analysis.json')
            self.save_output(tech_portfolio, 'company_tech_portfolio.json')
            
            self.logger.info(f"✅ 기업 분석 완료 ({len(companies_data)}개 기업, {len(tech_portfolio)}개 기술 포트폴리오)")
            return state
            
        except Exception as e:
            self.logger.error(f"기업 분석 중 오류: {e}")
            import traceback
            traceback.print_exc()
            state['errors'].append(f"company_analysis: {str(e)}")
            return state
    
    async def _discover_top_companies(self) -> List[str]:
        """전기차 시장 상위 기업 발굴"""
        try:
            # 여러 검색 쿼리로 종합적으로 조사
            queries = [
                "top electric vehicle manufacturers market share 2025",
                "leading EV companies sales volume 2025",
                "largest electric car makers by production 2025"
            ]
            
            all_companies = []
            
            for query in queries:
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query=query,
                    max_results=5
                )
                
                # 검색 결과에서 기업명 추출
                companies = await self._extract_companies_from_search(
                    search_results.get('results', []),
                    query
                )
                all_companies.extend(companies)
            
            # 중복 제거 및 빈도순 정렬
            company_counts = {}
            for company in all_companies:
                company_counts[company] = company_counts.get(company, 0) + 1
            
            # 빈도순으로 정렬 (많이 언급된 기업이 상위)
            sorted_companies = sorted(
                company_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # 기업명만 추출
            top_companies = [company for company, count in sorted_companies[:self.max_companies]]
            
            self.logger.info(f"발굴된 상위 기업: {top_companies}")
            
            return top_companies
            
        except Exception as e:
            self.logger.error(f"기업 발굴 중 오류: {e}")
            return []
    
    async def _extract_companies_from_search(self, search_results: List[Dict], query: str) -> List[str]:
        """검색 결과에서 기업명 추출 (LLM 활용)"""
        if not search_results or not self.llm:
            return []
        
        try:
            # 검색 결과를 텍스트로 변환
            results_text = "\n\n".join([
                f"제목: {r.get('title', '')}\n내용: {r.get('content', '')[:300]}"
                for r in search_results[:5]
            ])
            
            prompt = f"""다음 검색 결과에서 전기차를 생산하는 주요 기업명을 추출하세요.

검색 쿼리: {query}

검색 결과:
{results_text}

조건:
1. 실제로 전기차를 생산하는 기업만 추출
2. 브랜드명이 아닌 기업명으로 통일 (예: Audi → Volkswagen, Chevrolet Bolt → GM)
3. 영어 기업명으로 표기
4. 중국 기업은 정식 영어명 사용

다음 형식의 JSON으로만 응답하세요:
{{
  "companies": ["Tesla", "BYD", "Volkswagen", ...]
}}

JSON만 출력하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # JSON 파싱
            import json
            import re
            
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                companies = data.get('companies', [])
                self.logger.info(f"추출된 기업 ({len(companies)}개): {companies}")
                return companies
            else:
                self.logger.warning("기업명 추출 실패 - JSON 파싱 오류")
                return []
                
        except Exception as e:
            self.logger.error(f"기업명 추출 오류: {e}")
            return []
    
    async def _analyze_company(self, company: str) -> Dict:
        """개별 기업 분석"""
        self.logger.info(f"  🏢 {company} 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_company_data(company)
        
        try:
            # 병렬로 여러 측면 조사
            tasks = [
                self._search_company_strategy(company),
                self._search_company_production(company),
                self._search_company_technology(company),
                self._search_company_market_position(company),
                self._search_company_news(company)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            company_data = {
                'name': company,
                'strategy': results[0] if not isinstance(results[0], Exception) else None,
                'production': results[1] if not isinstance(results[1], Exception) else None,
                'technology': results[2] if not isinstance(results[2], Exception) else None,
                'market_position': results[3] if not isinstance(results[3], Exception) else None,
                'news': results[4] if not isinstance(results[4], Exception) else None,
                'analysis_date': datetime.now().isoformat()
            }
            
            # LLM 종합 분석
            if self.llm:
                analysis = await self._analyze_company_comprehensive(company, company_data)
                company_data['llm_analysis'] = analysis
            
            return company_data
            
        except Exception as e:
            self.logger.error(f"{company} 분석 오류: {e}")
            return self._get_fallback_company_data(company)
    
    async def _search_company_strategy(self, company: str) -> Dict:
        """기업 전략 검색"""
        try:
            query = f"{company} electric vehicle strategy roadmap 2025 2030"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=3
            )
            
            return {
                'query': query,
                'results': search_results.get('results', [])
            }
        except Exception as e:
            self.logger.error(f"{company} 전략 검색 오류: {e}")
            return {'error': str(e)}
    
    async def _search_company_production(self, company: str) -> Dict:
        """생산 능력 검색"""
        try:
            query = f"{company} electric vehicle production capacity sales volume 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=3
            )
            
            return {
                'query': query,
                'results': search_results.get('results', [])
            }
        except Exception as e:
            self.logger.error(f"{company} 생산 검색 오류: {e}")
            return {'error': str(e)}
    
    async def _search_company_technology(self, company: str) -> Dict:
        """기술 개발 검색"""
        try:
            query = f"{company} electric vehicle battery technology innovation platform 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=4
            )
            
            return {
                'query': query,
                'results': search_results.get('results', [])
            }
        except Exception as e:
            self.logger.error(f"{company} 기술 검색 오류: {e}")
            return {'error': str(e)}
    
    async def _search_company_market_position(self, company: str) -> Dict:
        """시장 지위 검색"""
        try:
            query = f"{company} electric vehicle market share position ranking 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=3
            )
            
            return {
                'query': query,
                'results': search_results.get('results', [])
            }
        except Exception as e:
            self.logger.error(f"{company} 시장 지위 검색 오류: {e}")
            return {'error': str(e)}
    
    async def _search_company_news(self, company: str) -> Dict:
        """최신 뉴스 검색"""
        try:
            query = f"{company} electric vehicle news latest developments 2025"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=5
            )
            
            return {
                'query': query,
                'results': search_results.get('results', [])
            }
        except Exception as e:
            self.logger.error(f"{company} 뉴스 검색 오류: {e}")
            return {'error': str(e)}
    
    async def _extract_key_technologies(self, company: str, company_data: Dict) -> Dict:
        """기업의 핵심 기술 추출 (Tech Analysis Agent에 전달)"""
        if not self.llm:
            return self._extract_basic_technologies(company_data)
        
        try:
            # 기술 관련 정보 수집
            tech_info = self._extract_key_info(company_data.get('technology', {}))
            strategy_info = self._extract_key_info(company_data.get('strategy', {}))
            
            prompt = f"""{company}의 전기차 관련 핵심 기술을 다음 정보에서 추출하세요:

기술 정보: {tech_info}
전략 정보: {strategy_info}

다음 카테고리별로 핵심 기술을 추출하세요:
1. 배터리 기술 (Battery Technology)
2. 충전 기술 (Charging Technology)
3. 모터/파워트레인 (Motor/Powertrain)
4. 자율주행 (Autonomous Driving)
5. 플랫폼/아키텍처 (Platform/Architecture)
6. 소프트웨어 (Software)
7. 기타 혁신 기술 (Other Innovations)

다음 형식의 JSON으로만 응답하세요:
{{
  "battery": "구체적 기술명 및 설명",
  "charging": "구체적 기술명 및 설명",
  "motor_powertrain": "구체적 기술명 및 설명",
  "autonomous": "구체적 기술명 및 설명",
  "platform": "구체적 기술명 및 설명",
  "software": "구체적 기술명 및 설명",
  "other": "기타 혁신 기술",
  "key_differentiators": ["차별화 요소 1", "차별화 요소 2", ...]
}}

해당 카테고리에 기술이 없으면 "N/A"로 표시하세요.
JSON만 출력하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # JSON 파싱
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                tech_data = json.loads(json_match.group())
                self.logger.info(f"{company} 핵심 기술 추출 완료")
                return tech_data
            else:
                self.logger.warning(f"{company} 기술 추출 실패 - JSON 파싱 오류")
                return self._extract_basic_technologies(company_data)
                
        except Exception as e:
            self.logger.error(f"{company} 기술 추출 오류: {e}")
            return self._extract_basic_technologies(company_data)
    
    def _extract_basic_technologies(self, company_data: Dict) -> Dict:
        """기본적인 기술 정보 추출 (LLM 없을 때)"""
        tech_data = company_data.get('technology', {})
        
        if tech_data and 'results' in tech_data:
            results = tech_data['results'][:2]
            tech_summary = " | ".join([
                r.get('content', '')[:100] for r in results if r.get('content')
            ])
            
            return {
                'battery': tech_summary[:200] if tech_summary else 'N/A',
                'charging': 'N/A',
                'motor_powertrain': 'N/A',
                'autonomous': 'N/A',
                'platform': 'N/A',
                'software': 'N/A',
                'other': 'N/A',
                'key_differentiators': ['검색 결과 기반 추출']
            }
        
        return {
            'battery': 'N/A',
            'charging': 'N/A',
            'motor_powertrain': 'N/A',
            'autonomous': 'N/A',
            'platform': 'N/A',
            'software': 'N/A',
            'other': 'N/A',
            'key_differentiators': []
        }
    
    async def _analyze_company_comprehensive(self, company: str, data: Dict) -> str:
        """기업 데이터 종합 분석"""
        if not self.llm:
            return "종합 분석 불가 (LLM 미설정)"
        
        try:
            # 검색 결과에서 핵심 정보 추출
            strategy_info = self._extract_key_info(data.get('strategy', {}))
            production_info = self._extract_key_info(data.get('production', {}))
            tech_info = self._extract_key_info(data.get('technology', {}))
            market_info = self._extract_key_info(data.get('market_position', {}))
            
            prompt = f"""{company}의 전기차 사업을 다음 정보를 바탕으로 종합 분석하세요:

전략: {strategy_info}
생산: {production_info}
기술: {tech_info}
시장 지위: {market_info}

다음 항목을 간결하게 분석해주세요:
1. 시장 포지션 및 점유율 (2-3문장)
2. 핵심 경쟁력 (3-4개 bullet points)
3. 사업 전략 및 투자 방향 (2-3문장)
4. 주요 리스크 (2-3문장)
5. 향후 전망 (2-3문장)

한국어로 작성하세요."""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"{company} 종합 분석 오류: {e}")
            return "분석 중 오류 발생"
    
    def _extract_key_info(self, search_data: Dict) -> str:
        """검색 결과에서 핵심 정보 추출"""
        if not search_data or 'results' not in search_data:
            return "정보 없음"
        
        results = search_data['results'][:3]  # 상위 3개
        info_parts = []
        
        for r in results:
            title = r.get('title', '')
            content = r.get('content', '')[:250]  # 250자로 증가
            if title or content:
                info_parts.append(f"{title}: {content}")
        
        return " | ".join(info_parts) if info_parts else "정보 없음"
    
    async def _analyze_industry_dynamics(self, companies_data: Dict) -> Dict:
        """산업 전체 역학 분석"""
        self.logger.info("  📊 산업 역학 분석 중...")
        
        if not self.tavily_client:
            return self._get_fallback_industry_analysis()
        
        try:
            queries = [
                "electric vehicle industry competition market dynamics 2025",
                "EV market share leaders ranking 2025",
                "electric vehicle industry trends consolidation 2025"
            ]
            
            all_results = []
            for query in queries:
                search_results = await asyncio.to_thread(
                    self.tavily_client.search,
                    query=query,
                    max_results=3
                )
                all_results.extend(search_results.get('results', []))
            
            return {
                'queries': queries,
                'results': all_results,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"산업 분석 오류: {e}")
            return self._get_fallback_industry_analysis()
    
    async def _synthesize_company_insights(self, companies_data: Dict, industry_data: Dict) -> str:
        """기업 분석 종합"""
        if not self.llm:
            return "종합 분석 불가 (LLM 미설정)"
        
        try:
            # 상위 5개 기업만 요약에 포함
            top_companies = list(companies_data.keys())[:5]
            companies_summary = "\n".join([
                f"- {name}: {companies_data[name].get('llm_analysis', '분석 없음')[:300]}"
                for name in top_companies
            ])
            
            prompt = f"""전기차 주요 기업들({len(companies_data)}개)의 분석 결과를 종합하세요:

주요 기업 분석:
{companies_summary}

다음 형식으로 종합 정리해주세요:
1. 산업 리더 및 시장 구도 (3-4문장)
2. 경쟁 구도 및 차별화 전략 (3-4문장)
3. 주요 변화 및 트렌드 (4-5개 bullet points)
4. 기술 혁신 동향 (2-3문장)
5. 투자 시사점 (3-4문장)

한국어로 작성하세요."""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"종합 분석 오류: {e}")
            return "종합 분석 중 오류 발생"
    
    # Fallback 데이터
    def _get_fallback_company_data(self, company: str) -> Dict:
        """Fallback 기업 데이터"""
        fallback_data = {
            'Tesla': {
                'name': company,
                'strategy': 'FSD 및 에너지 통합, 수직 통합 전략',
                'production': '연간 200만대 목표, 기가팩토리 확장',
                'technology': '4680 배터리, FSD (Full Self-Driving)',
                'market_position': '프리미엄 전기차 시장 리더',
                'llm_analysis': 'Tesla는 프리미엄 전기차 시장을 선도하며, 자체 배터리 생산과 자율주행 기술로 차별화하고 있습니다.'
            },
            'BYD': {
                'name': company,
                'strategy': '버티컬 통합, 다양한 가격대 라인업',
                'production': '연간 300만대 이상, 세계 최대 EV 생산',
                'technology': 'Blade 배터리, e-Platform 3.0',
                'market_position': '글로벌 판매 1위',
                'llm_analysis': 'BYD는 수직 통합된 생산 체계와 Blade 배터리로 가격 경쟁력을 확보하여 글로벌 1위를 차지했습니다.'
            },
            'Volkswagen': {
                'name': company,
                'strategy': 'ID 시리즈 확대, 전동화 전환 가속',
                'production': '연간 150만대 목표',
                'technology': 'MEB 플랫폼, PowerCo 배터리',
                'market_position': '유럽 시장 강자',
                'llm_analysis': 'Volkswagen은 MEB 플랫폼을 기반으로 전 브랜드에 전기차를 확대하며 유럽 시장을 주도하고 있습니다.'
            }
        }
        
        return fallback_data.get(company, {
            'name': company,
            'strategy': f'{company} 전략 정보 (웹 검색 미사용)',
            'production': f'{company} 생산 정보 (웹 검색 미사용)',
            'technology': f'{company} 기술 정보 (웹 검색 미사용)',
            'market_position': '정보 없음',
            'note': 'Fallback 데이터',
            'llm_analysis': f'{company}는 전기차 시장의 주요 플레이어입니다.'
        })
    
    def _get_fallback_industry_analysis(self) -> Dict:
        """Fallback 산업 분석 데이터"""
        return {
            'competition': '치열한 경쟁 구도',
            'market_leaders': 'BYD, Tesla, Volkswagen, Hyundai, GM',
            'emerging_players': 'Rivian, Lucid, NIO, XPeng',
            'trends': '가격 경쟁 심화, 기술 혁신 가속화',
            'note': 'Fallback 데이터 (웹 검색 미사용)'
        }