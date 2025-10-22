# 리포트 생성 Agent - 최종 보고서 작성
# agents/report_generation_agent.py

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
from pathlib import Path
from .base_agent import BaseAgent

class ReportGenerationAgent(BaseAgent):
    """리포트 생성 Agent - 실제 검색 결과 기반"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("report_generation", llm, config)
        self.report_template = config.get('template', 'investment') if config else 'investment'
        
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """리포트 생성 메인 프로세스"""
        self.logger.info("최종 리포트 생성 시작...")
        
        try:
            # 모든 분석 데이터 수집
            analysis_data = self._collect_all_analysis(state)
            
            # 데이터 검증
            if not self._validate_analysis_data(analysis_data):
                self.logger.warning("일부 분석 데이터가 누락되었습니다")
            
            # 1. 요약 (Executive Summary) 생성
            summary = await self._generate_summary(analysis_data)
            
            # 2. 시장 분석
            market_analysis = await self._generate_market_analysis(analysis_data)
            
            # 3. 소비자 분석
            consumer_analysis = await self._generate_consumer_analysis(analysis_data)
            
            # 4. 기업 분석
            company_analysis = await self._generate_company_analysis(analysis_data)
            
            # 5. 기술 분석
            technology_analysis = await self._generate_technology_analysis(analysis_data)
            
            # 6. 최근 주가 분석
            stock_analysis = await self._generate_stock_analysis(analysis_data)
            
            # 7. 향후 전기차 시장 (종합 전망)
            future_outlook = await self._generate_future_outlook(analysis_data)
            
            # 8. 참고 자료
            references = self._generate_references(analysis_data)
            
            # 최종 리포트 조합
            final_report = self._assemble_final_report(
                summary,
                market_analysis,
                consumer_analysis,
                company_analysis,
                technology_analysis,
                stock_analysis,
                future_outlook,
                references,
                analysis_data
            )
            
            # 다양한 포맷으로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Markdown 버전
            markdown_report = self._format_as_markdown(final_report)
            self.save_output(markdown_report, f'report_{timestamp}.md')
            
            # HTML 버전
            html_report = self._format_as_html(final_report)
            self.save_output(html_report, f'report_{timestamp}.html')
            
            # JSON 버전 (구조화된 데이터)
            self.save_output(final_report, f'report_data_{timestamp}.json')
            
            # 상태 업데이트
            state['final_report'] = final_report
            state['report_generated'] = True
            state['report_paths'] = {
                'markdown': f'reports/report_{timestamp}.md',
                'html': f'reports/report_{timestamp}.html',
                'json': f'reports/report_data_{timestamp}.json'
            }
            
            self.logger.info("✅ 최종 리포트 생성 완료")
            
        except Exception as e:
            self.logger.error(f"리포트 생성 중 오류: {e}")
            import traceback
            traceback.print_exc()
            state['report_generation_error'] = str(e)
            
        return state
    
    def _collect_all_analysis(self, state: Dict[str, Any]) -> Dict:
        """모든 분석 데이터 수집 및 정리"""
        return {
            'market_analysis': state.get('market_data', {}),
            'market_trends': state.get('market_trends', {}),
            'government_policies': state.get('government_policies', {}),
            'consumer_analysis': state.get('consumer_patterns', {}),
            'company_analysis': state.get('company_analysis', {}),
            'technology_analysis': state.get('tech_trends', {}),
            'stock_analysis': state.get('stock_analysis', {}),
            'charts': state.get('charts', []),
            'metadata': {
                'report_date': datetime.now().strftime('%Y-%m-%d'),
                'analysis_period': '2024-2030',
                'data_sources': self._get_data_sources(state)
            }
        }
    
    def _validate_analysis_data(self, analysis_data: Dict) -> bool:
        """분석 데이터 유효성 검증"""
        required_keys = ['market_analysis', 'company_analysis', 'consumer_analysis', 
                        'technology_analysis', 'stock_analysis']
        
        missing = [key for key in required_keys if not analysis_data.get(key)]
        
        if missing:
            self.logger.warning(f"누락된 분석: {', '.join(missing)}")
            return False
        return True
    
    async def _generate_summary(self, analysis_data: Dict) -> Dict:
        """요약 섹션 생성"""
        self.logger.info("요약 섹션 생성 중...")
        
        # 각 Agent의 synthesis 추출
        market_synthesis = analysis_data.get('market_analysis', {}).get('synthesis', '')
        company_synthesis = analysis_data.get('company_analysis', {}).get('synthesis', '')
        consumer_synthesis = analysis_data.get('consumer_analysis', {}).get('synthesis', '')
        tech_synthesis = analysis_data.get('technology_analysis', {}).get('synthesis', '')
        stock_insights = analysis_data.get('stock_analysis', {}).get('investment_insights', '')
        
        if self.llm:
            prompt = f"""전기차 시장 분석 결과를 바탕으로 요약을 작성하세요.

**시장 분석:**
{market_synthesis}

**기업 분석:**
{company_synthesis}

**소비자 분석:**
{consumer_synthesis}

**기술 분석:**
{tech_synthesis}

**투자 인사이트:**
{stock_insights}

다음 항목을 포함하여 간결하게 작성하세요:
1. 주요 트렌드 (2-3문장)
2. 시장을 주도하는 기업들 (2-3문장)
3. 소비자 행동 패턴 (2-3문장)
4. 미래 전망 (2-3문장)

한국어로 작성하세요."""
            
            try:
                response = await self.llm.ainvoke(prompt)
                summary_text = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                self.logger.error(f"요약 생성 오류: {e}")
                summary_text = self._generate_default_summary()
        else:
            summary_text = self._generate_default_summary()
        
        return {
            'title': '요약',
            'content': summary_text
        }
    
    async def _generate_market_analysis(self, analysis_data: Dict) -> Dict:
        """시장 분석 섹션 생성"""
        self.logger.info("시장 분석 섹션 생성 중...")
        
        market_data = analysis_data.get('market_analysis', {})
        market_trends = analysis_data.get('market_trends', {})
        government_policies = analysis_data.get('government_policies', {})
        
        if not self.llm:
            return self._get_fallback_market_analysis()
        
        try:
            # 검색 결과에서 핵심 정보 추출
            global_market_info = self._extract_search_insights(
                market_data.get('global_market', {})
            )
            regional_info = self._extract_regional_insights(
                market_data.get('regional_markets', {})
            )
            policy_info = self._extract_policy_insights(government_policies)
            synthesis = market_data.get('synthesis', '')
            
            prompt = f"""전기차 시장에 대한 전반적인 트렌드와 정부 정책을 분석하세요.

**글로벌 시장 현황:**
{global_market_info}

**지역별 시장:**
{regional_info}

**정부 정책:**
{policy_info}

**시장 종합:**
{synthesis}

다음 내용을 포함하여 작성하세요:
1. 전기차 시장의 주요 트렌드 (4-5문장)
2. 글로벌 시장 규모와 성장률 (구체적 수치 포함, 3-4문장)
3. 주요 지역별 시장 특징 (4-5문장)
4. 각국 정부의 주요 정책과 시장에 미치는 영향 (4-5문장)

한국어로 작성하고, 가능한 구체적인 수치와 사실을 포함하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'title': '시장 분석',
                'content': content,
                'data_sources': ['Tavily Web Search', 'Market Research Agent']
            }
            
        except Exception as e:
            self.logger.error(f"시장 분석 섹션 생성 오류: {e}")
            return self._get_fallback_market_analysis()
    
    async def _generate_consumer_analysis(self, analysis_data: Dict) -> Dict:
        """소비자 분석 섹션 생성"""
        self.logger.info("소비자 분석 섹션 생성 중...")
        
        consumer_data = analysis_data.get('consumer_analysis', {})
        
        if not self.llm:
            return self._get_fallback_consumer_analysis()
        
        try:
            synthesis = consumer_data.get('synthesis', '')
            integrated_analysis = consumer_data.get('integrated_analysis', '')
            influence_weights = consumer_data.get('influence_weights', {})
            
            # 주요 가중치 추출
            top_factors = sorted(influence_weights.items(), key=lambda x: x[1], reverse=True)[:5]
            factors_text = "\n".join([f"- {k}: {v}%" for k, v in top_factors])
            
            prompt = f"""전기차에 대한 소비자들의 소비 패턴과 구매 심리를 분석하세요.

**소비자 종합 분석:**
{synthesis}

**시장 통합 분석:**
{integrated_analysis}

**주요 구매 결정 요인 (가중치):**
{factors_text}

다음 내용을 포함하여 작성하세요:
1. 소비자의 전기차 구매 패턴과 선호도 (4-5문장)
2. 주요 구매 결정 요인 및 중요도 (4-5문장)
3. 정부 정책(보조금, 세제혜택)이 소비자 구매 심리에 미치는 영향 (3-4문장)
4. 소비자의 투자 심리 분석 (3-4문장)
5. 인구통계학적 특성 (연령대, 소득 수준 등) (2-3문장)

한국어로 작성하고, 구체적인 통계나 트렌드를 포함하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'title': '소비자 분석',
                'content': content,
                'key_factors': [k for k, v in top_factors],
                'data_sources': ['Tavily Web Search', 'Consumer Analysis Agent']
            }
            
        except Exception as e:
            self.logger.error(f"소비자 분석 섹션 생성 오류: {e}")
            return self._get_fallback_consumer_analysis()
    
    async def _generate_company_analysis(self, analysis_data: Dict) -> Dict:
        """기업 분석 섹션 생성"""
        self.logger.info("기업 분석 섹션 생성 중...")
        
        company_data = analysis_data.get('company_analysis', {})
        
        if not self.llm:
            return self._get_fallback_company_analysis()
        
        try:
            companies = company_data.get('companies', {})
            industry_analysis = company_data.get('industry_analysis', {})
            synthesis = company_data.get('synthesis', '')
            
            # 주요 기업 데이터 추출
            company_summaries = []
            for company_name, data in companies.items():
                llm_analysis = data.get('llm_analysis', '')
                if llm_analysis:
                    company_summaries.append(f"**{company_name}**\n{llm_analysis[:400]}")
            
            companies_text = "\n\n".join(company_summaries)
            
            prompt = f"""전기차 시장을 주도하는 기업들을 분석하세요.

**주요 기업별 분석:**
{companies_text}

**산업 종합 분석:**
{synthesis}

다음 내용을 포함하여 작성하세요:
1. 시장을 주도하는 주요 기업 소개 (각 기업당 2-3문장, 총 5-7개 기업)
2. 각 기업의 현재 시장 점유율 (가능하면 구체적 수치 포함)
3. 기업별 전기차 사업 전략과 투자 방향 (4-5문장)
4. 각 기업의 강점과 차별화 요소 (3-4문장)
5. 최근 주요 개발 현황이나 발표 (3-4문장)

한국어로 작성하고, 기업명과 구체적인 수치를 포함하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'title': '기업 분석',
                'content': content,
                'analyzed_companies': list(companies.keys()),
                'data_sources': ['Tavily Web Search', 'Company Analysis Agent', 'Company Reports']
            }
            
        except Exception as e:
            self.logger.error(f"기업 분석 섹션 생성 오류: {e}")
            return self._get_fallback_company_analysis()
    
    async def _generate_technology_analysis(self, analysis_data: Dict) -> Dict:
        """기술 분석 섹션 생성"""
        self.logger.info("기술 분석 섹션 생성 중...")
        
        tech_data = analysis_data.get('technology_analysis', {})
        
        if not self.llm:
            return self._get_fallback_technology_analysis()
        
        try:
            battery_tech = self._extract_tech_insights(tech_data.get('battery_tech', {}))
            charging_tech = self._extract_tech_insights(tech_data.get('charging_tech', {}))
            autonomous_tech = self._extract_tech_insights(tech_data.get('autonomous_tech', {}))
            manufacturing_tech = self._extract_tech_insights(tech_data.get('manufacturing_tech', {}))
            synthesis = tech_data.get('synthesis', '')
            roadmap = tech_data.get('roadmap', {})
            
            prompt = f"""전기차에 현재 적용된 기술과 향후 적용될 기술을 분석하세요.

**배터리 기술:**
{battery_tech}

**충전 기술:**
{charging_tech}

**자율주행 기술:**
{autonomous_tech}

**제조 기술:**
{manufacturing_tech}

**기술 종합 분석:**
{synthesis}

**기술 로드맵:**
{roadmap}

다음 내용을 포함하여 작성하세요:
1. 현재 전기차에 적용된 주요 기술 (5-6문장)
   - 배터리 기술 (리튬이온, 고체배터리 등)
   - 충전 기술 (급속충전, 무선충전 등)
   - 모터 및 파워트레인 기술
   
2. 향후 적용될 미래 기술 (5-6문장)
   - 차세대 배터리 기술
   - 자율주행 기술
   - V2G(Vehicle-to-Grid) 기술
   - 경량화 기술
   
3. 기술 발전이 시장에 미칠 영향 (3-4문장)

한국어로 작성하고, 구체적인 기술명과 예상 상용화 시기를 포함하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'title': '기술 분석',
                'content': content,
                'data_sources': ['Tavily Web Search', 'Technology Analysis Agent', 'Company Reports']
            }
            
        except Exception as e:
            self.logger.error(f"기술 분석 섹션 생성 오류: {e}")
            return self._get_fallback_technology_analysis()
    
    async def _generate_stock_analysis(self, analysis_data: Dict) -> Dict:
        """최근 주가 분석 섹션 생성"""
        self.logger.info("주가 분석 섹션 생성 중...")
        
        stock_data = analysis_data.get('stock_analysis', {})
        
        if not self.llm:
            return self._get_fallback_stock_analysis()
        
        try:
            investment_insights = stock_data.get('investment_insights', '')
            sector_analysis = stock_data.get('sector_analysis', {})
            valuation_metrics = stock_data.get('valuation_metrics', {})
            individual_stocks = stock_data.get('individual_stocks', {})
            
            # 주요 주식 성과 추출
            stock_performances = []
            for ticker, data in individual_stocks.items():
                company = data.get('company', ticker)
                price_history = data.get('price_history', {})
                financials = data.get('financials', {})
                
                stock_performances.append(
                    f"**{ticker} ({company})**\n"
                    f"- 1년 수익률: {price_history.get('1y_change', 0)*100:.1f}%\n"
                    f"- 시가총액: ${financials.get('market_cap', 0)/1e9:.1f}B\n"
                    f"- 매출 성장률: {financials.get('revenue_growth', 0)*100:.1f}%"
                )
            
            stocks_text = "\n\n".join(stock_performances[:8])
            
            prompt = f"""최근 1년간 전기차 관련 주식의 성과를 분석하고, 기업들의 재무 상황을 평가하세요.

**주요 주식 성과:**
{stocks_text}

**투자 인사이트:**
{investment_insights}

**섹터 분석:**
{sector_analysis}

**밸류에이션:**
- 평균 P/E: {valuation_metrics.get('avg_pe', 'N/A')}
- 평균 P/S: {valuation_metrics.get('avg_ps', 'N/A')}

다음 내용을 포함하여 작성하세요:
1. 최근 1년간 주가 동향 분석 (4-5문장)
   - 시장이 성장하는지 위축되었는지
   - 주요 상승/하락 종목과 원인
   
2. 주요 기업별 재무 상황 분석 (5-6문장)
   - 매출 성장률, 수익성
   - 재무 건전성
   
3. 기업들의 향후 전망 (4-5문장)
   - 시장에서 철수 가능성
   - 시장 지위 유지/확대 가능성
   - 투자 지속 여부

한국어로 작성하고, 구체적인 티커 심볼과 수치를 포함하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'title': '최근 주가 분석',
                'content': content,
                'analyzed_stocks': list(individual_stocks.keys()),
                'data_sources': ['Stock Analysis Agent', 'Financial Data']
            }
            
        except Exception as e:
            self.logger.error(f"주가 분석 섹션 생성 오류: {e}")
            return self._get_fallback_stock_analysis()
    
    async def _generate_future_outlook(self, analysis_data: Dict) -> Dict:
        """향후 전기차 시장 섹션 생성 (종합 전망 + 투자 추천)"""
        self.logger.info("향후 전기차 시장 섹션 생성 중...")
        
        if not self.llm:
            return self._get_fallback_future_outlook()
        
        try:
            # 모든 분석 종합
            market_synthesis = analysis_data.get('market_analysis', {}).get('synthesis', '')
            company_synthesis = analysis_data.get('company_analysis', {}).get('synthesis', '')
            consumer_synthesis = analysis_data.get('consumer_analysis', {}).get('synthesis', '')
            tech_synthesis = analysis_data.get('technology_analysis', {}).get('synthesis', '')
            stock_insights = analysis_data.get('stock_analysis', {}).get('investment_insights', '')
            
            tech_roadmap = analysis_data.get('technology_analysis', {}).get('roadmap', {})
            
            prompt = f"""위 모든 분석 결과를 바탕으로 향후 전기차 시장에 대한 종합적인 전망을 제시하세요.

**시장 분석 요약:**
{market_synthesis[:300]}

**기업 분석 요약:**
{company_synthesis[:300]}

**소비자 분석 요약:**
{consumer_synthesis[:300]}

**기술 분석 요약:**
{tech_synthesis[:300]}

**투자 분석 요약:**
{stock_insights[:300]}

다음 내용을 포함하여 작성하세요:

## 1. 현재 전기차 시장에 대한 종합 견해 (4-5문장)
- 시장의 현재 위치와 성숙도
- 주요 성장 동력과 장애 요인

## 2. 향후 출시될 주요 기술 (4-5문장)
- 2-3년 내 상용화 예상 기술
- 5년 이상 장기 개발 기술
- 게임 체인저가 될 기술

## 3. 시장 성장 가능성 (4-5문장)
- 향후 3-5년 시장 전망
- 지역별/세그먼트별 성장 전망
- 주요 리스크 요인

## 4. 관련 주식 시장 예측
다음 형식의 표로 작성:
| 기업/티커 | 현재 전망 | 투자 매력도 | 기간 | 주요 근거 |
|----------|----------|-----------|------|---------|
| (5-7개 기업에 대해 작성) |

## 5. 투자 추천 및 전략 (4-5문장)
- 단기/중기/장기 투자 전략
- 주목해야 할 기업이나 섹터
- 위험 관리 방안

한국어로 작성하고, 구체적이고 실행 가능한 인사이트를 제공하세요."""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'title': '향후 전기차 시장',
                'content': content
            }
            
        except Exception as e:
            self.logger.error(f"향후 전기차 시장 섹션 생성 오류: {e}")
            return self._get_fallback_future_outlook()
    
    def _generate_references(self, analysis_data: Dict) -> Dict:
        """참고 자료 섹션 생성"""
        self.logger.info("참고 자료 섹션 생성 중...")
        
        data_sources = analysis_data['metadata']['data_sources']
        
        references = {
            'title': '참고 자료',
            'sources': []
        }
        
        # 웹 검색 소스
        references['sources'].append({
            'type': 'Web Search API',
            'name': 'Tavily Search API',
            'description': '실시간 웹 검색을 통한 최신 시장 정보 수집',
            'url': 'https://tavily.com'
        })
        
        # LLM 분석
        if 'LLM Analysis' in str(data_sources):
            references['sources'].append({
                'type': 'AI Analysis',
                'name': 'OpenAI GPT-4',
                'description': 'AI 기반 데이터 분석 및 인사이트 생성',
                'url': 'https://openai.com'
            })
        
        # 주식 데이터
        references['sources'].append({
            'type': 'Financial Data',
            'name': 'Stock Market Data',
            'description': '주가 및 재무 데이터 분석',
            'note': '실제 환경에서는 Yahoo Finance, Alpha Vantage 등 사용'
        })
        
        # 기업 보고서
        references['sources'].append({
            'type': 'Company Reports',
            'name': '기업 공시 자료 및 IR 자료',
            'description': '주요 전기차 제조사의 공식 보고서 및 발표 자료',
            'note': '각 기업의 투자자 관계(IR) 웹사이트 참조'
        })
        
        # 시장 조사 기관
        references['sources'].append({
            'type': 'Market Research',
            'name': '시장 조사 기관',
            'description': 'Bloomberg, Reuters, IHS Markit 등의 시장 분석 자료',
            'note': '웹 검색을 통해 수집된 공개 정보'
        })
        
        return references
    
    # Helper methods for data extraction
    
    def _extract_search_insights(self, search_data: Dict) -> str:
        """검색 결과에서 인사이트 추출"""
        if not search_data or not isinstance(search_data, dict):
            return "데이터 없음"
        
        # synthesis 우선 사용
        if 'llm_analysis' in search_data:
            return search_data['llm_analysis']
        
        # 검색 결과에서 추출
        results = search_data.get('results', [])
        if results:
            insights = []
            for r in results[:3]:
                content = r.get('content', '')[:150]
                if content:
                    insights.append(content)
            return " | ".join(insights)
        
        return "검색 결과 없음"
    
    def _extract_regional_insights(self, regional_data: Dict) -> str:
        """지역별 데이터에서 인사이트 추출"""
        if not regional_data or 'regions' not in regional_data:
            return "지역별 데이터 없음"
        
        regions = regional_data.get('regions', {})
        insights = []
        
        for region, data in regions.items():
            results = data.get('results', [])
            if results:
                content = results[0].get('content', '')[:100]
                insights.append(f"{region}: {content}")
        
        return " | ".join(insights[:3]) if insights else "지역별 데이터 없음"
    
    def _extract_policy_insights(self, policy_data: Dict) -> str:
        """정책 데이터에서 인사이트 추출"""
        if not policy_data:
            return "정책 데이터 없음"
        
        if isinstance(policy_data, dict) and 'policies' in policy_data:
            policies = policy_data.get('policies', [])
            insights = []
            for p in policies[:3]:
                results = p.get('results', [])
                if results:
                    content = results[0].get('content', '')[:100]
                    insights.append(content)
            return " | ".join(insights) if insights else "정책 데이터 없음"
        
        return str(policy_data)[:300]
    
    def _extract_tech_insights(self, tech_data: Dict) -> str:
        """기술 데이터에서 인사이트 추출"""
        if not tech_data:
            return "기술 데이터 없음"
        
        # 검색 결과가 있는 경우
        for key in ['battery_searches', 'charging_searches', 'autonomous_searches', 'manufacturing_searches']:
            if key in tech_data:
                searches = tech_data.get(key, [])
                insights = []
                for s in searches[:2]:
                    results = s.get('results', [])
                    if results:
                        content = results[0].get('content', '')[:100]
                        insights.append(content)
                if insights:
                    return " | ".join(insights)
        
        return str(tech_data)[:200]
    
    def _get_data_sources(self, state: Dict) -> List[str]:
        """데이터 소스 목록"""
        sources = ['Tavily Web Search API']
        
        if state.get('market_data'):
            sources.append('Market Research via Web Search')
        if state.get('company_analysis'):
            sources.append('Company Analysis via Web Search')
        if state.get('consumer_patterns'):
            sources.append('Consumer Analysis via Web Search')
        if state.get('tech_trends'):
            sources.append('Technology Analysis via Web Search')
        if state.get('stock_analysis'):
            sources.append('Stock Market Data')
        if self.llm:
            sources.append('LLM Analysis (OpenAI GPT)')
        
        return sources
    
    # Fallback methods
    
    def _generate_default_summary(self) -> str:
        """기본 요약"""
        return """
전기차 시장은 급속한 성장세를 보이고 있으며, 글로벌 주요 자동차 제조사들이 전기차 전환을 가속화하고 있습니다.
Tesla와 BYD가 시장을 선도하고 있으며, 전통 자동차 제조사들도 대규모 투자를 진행하고 있습니다.
소비자들은 가격, 주행거리, 충전 인프라를 주요 구매 결정 요인으로 고려하고 있습니다.
배터리 기술의 발전과 정부 정책 지원에 힘입어 향후 5-10년간 지속적인 성장이 예상됩니다.
"""
    
    def _get_fallback_market_analysis(self) -> Dict:
        return {
            'title': '시장 분석',
            'content': '전기차 시장은 글로벌적으로 성장하고 있으며, 각국 정부의 정책 지원이 이어지고 있습니다.',
            'note': 'LLM 분석 불가'
        }
    
    def _get_fallback_consumer_analysis(self) -> Dict:
        return {
            'title': '소비자 분석',
            'content': '소비자들은 가격, 주행거리, 충전 편의성을 주요 고려 요소로 보고 있습니다.',
            'note': 'LLM 분석 불가'
        }
    
    def _get_fallback_company_analysis(self) -> Dict:
        return {
            'title': '기업 분석',
            'content': 'Tesla, BYD, Volkswagen 등 주요 기업들이 시장을 주도하고 있습니다.',
            'note': 'LLM 분석 불가'
        }
    
    def _get_fallback_technology_analysis(self) -> Dict:
        return {
            'title': '기술 분석',
            'content': '배터리 기술, 충전 기술, 자율주행 기술이 핵심 기술로 발전하고 있습니다.',
            'note': 'LLM 분석 불가'
        }
    
    def _get_fallback_stock_analysis(self) -> Dict:
        return {
            'title': '최근 주가 분석',
            'content': '전기차 관련 주식들은 변동성을 보이고 있으나, 장기적으로 성장 가능성이 있습니다.',
            'note': 'LLM 분석 불가'
        }
    
    def _get_fallback_future_outlook(self) -> Dict:
        return {
            'title': '향후 전기차 시장',
            'content': '전기차 시장은 지속적으로 성장할 것으로 예상되며, 기술 발전과 정책 지원이 이를 뒷받침할 것입니다.',
            'note': 'LLM 분석 불가'
        }
    
    # Report assembly and formatting
    
    def _assemble_final_report(self, summary: Dict, market_analysis: Dict,
                              consumer_analysis: Dict, company_analysis: Dict,
                              technology_analysis: Dict, stock_analysis: Dict,
                              future_outlook: Dict, references: Dict,
                              analysis_data: Dict) -> Dict:
        """최종 리포트 조합"""
        return {
            'metadata': {
                'title': '전기차 시장 트렌드 및 주요 기업의 사업 방향 분석',
                'description': '이 보고서는 전기차 시장의 트렌드를 분석하고, 기업/소비자들의 패턴과 방향성을 조사하여 향후 전기차 시장의 방향성을 분석합니다.',
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '1.0',
                'report_id': f"EV-REPORT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'analysis_period': analysis_data['metadata']['analysis_period'],
                'data_sources': analysis_data['metadata']['data_sources']
            },
            'summary': summary,
            'market_analysis': market_analysis,
            'consumer_analysis': consumer_analysis,
            'company_analysis': company_analysis,
            'technology_analysis': technology_analysis,
            'stock_analysis': stock_analysis,
            'future_outlook': future_outlook,
            'references': references,
            'methodology': self._get_methodology()
        }
    
    def _get_methodology(self) -> str:
        """분석 방법론"""
        return """
본 보고서는 Multi-Agent 시스템과 실시간 웹 검색을 활용한 종합적 분석 방법론을 적용했습니다.
Tavily API를 통해 최신 웹 정보를 수집하고, OpenAI GPT-4를 활용하여 데이터를 분석하고 인사이트를 도출했습니다.
시장 조사, 기업 분석, 소비자 분석, 기술 분석, 주가 분석을 병렬로 수행하여 통합적인 시장 전망을 제시합니다.
"""
    
    def _format_as_markdown(self, report: Dict) -> str:
        """Markdown 형식으로 변환"""
        md = f"""# {report['metadata']['title']}

**생성일:** {report['metadata']['generated_date']}  
**버전:** {report['metadata']['version']}  
**리포트 ID:** {report['metadata']['report_id']}

---

## 보고서 설명

{report['metadata']['description']}

---

## {report['summary']['title']}

{report['summary']['content']}

---

## {report['market_analysis']['title']}

{report['market_analysis']['content']}

---

## {report['consumer_analysis']['title']}

{report['consumer_analysis']['content']}

---

## {report['company_analysis']['title']}

{report['company_analysis']['content']}

---

## {report['technology_analysis']['title']}

{report['technology_analysis']['content']}

---

## {report['stock_analysis']['title']}

{report['stock_analysis']['content']}

---

## {report['future_outlook']['title']}

{report['future_outlook']['content']}

---

## {report['references']['title']}

### 참고한 문헌 및 사이트

"""
        
        for i, source in enumerate(report['references']['sources'], 1):
            md += f"\n**{i}. {source['name']}**\n"
            md += f"- 유형: {source['type']}\n"
            md += f"- 설명: {source['description']}\n"
            if 'url' in source:
                md += f"- URL: {source['url']}\n"
            if 'note' in source:
                md += f"- 비고: {source['note']}\n"
        
        md += f"\n---\n\n## 분석 방법론\n\n{report['methodology']}\n"
        
        return md
    
    def _format_as_html(self, report: Dict) -> str:
        """HTML 형식으로 변환"""
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report['metadata']['title']}</title>
    <style>
        body {{
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            line-height: 1.8;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 4px solid #2c3e50;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 40px;
            border-left: 6px solid #3498db;
            padding-left: 20px;
            font-size: 1.8em;
        }}
        h3 {{
            color: #34495e;
            margin-top: 25px;
            font-size: 1.3em;
        }}
        .metadata {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .metadata p {{
            margin: 5px 0;
            color: #555;
        }}
        .description {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin: 30px 0;
            font-size: 1.1em;
        }}
        .section {{
            background-color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .section-content {{
            line-height: 1.9;
            font-size: 1.05em;
        }}
        .references {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 40px;
        }}
        .reference-item {{
            background-color: white;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .reference-item h4 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .reference-item p {{
            margin: 5px 0;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .methodology {{
            background-color: #e8f8f5;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #27ae60;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <h1>{report['metadata']['title']}</h1>
    
    <div class="metadata">
        <p><strong>생성일:</strong> {report['metadata']['generated_date']}</p>
        <p><strong>버전:</strong> {report['metadata']['version']}</p>
        <p><strong>리포트 ID:</strong> {report['metadata']['report_id']}</p>
        <p><strong>분석 기간:</strong> {report['metadata']['analysis_period']}</p>
    </div>
    
    <div class="description">
        <h3>보고서 설명</h3>
        <p>{report['metadata']['description']}</p>
    </div>
    
    <div class="section">
        <h2>{report['summary']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['summary']['content'])}
        </div>
    </div>
    
    <div class="section">
        <h2>{report['market_analysis']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['market_analysis']['content'])}
        </div>
    </div>
    
    <div class="section">
        <h2>{report['consumer_analysis']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['consumer_analysis']['content'])}
        </div>
    </div>
    
    <div class="section">
        <h2>{report['company_analysis']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['company_analysis']['content'])}
        </div>
    </div>
    
    <div class="section">
        <h2>{report['technology_analysis']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['technology_analysis']['content'])}
        </div>
    </div>
    
    <div class="section">
        <h2>{report['stock_analysis']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['stock_analysis']['content'])}
        </div>
    </div>
    
    <div class="section">
        <h2>{report['future_outlook']['title']}</h2>
        <div class="section-content">
            {self._format_text_to_html(report['future_outlook']['content'])}
        </div>
    </div>
    
    <div class="references">
        <h2>{report['references']['title']}</h2>
        <h3>참고한 문헌 및 사이트</h3>
"""
        
        for i, source in enumerate(report['references']['sources'], 1):
            html += f"""
        <div class="reference-item">
            <h4>{i}. {source['name']}</h4>
            <p><strong>유형:</strong> {source['type']}</p>
            <p><strong>설명:</strong> {source['description']}</p>
"""
            if 'url' in source:
                html += f"            <p><strong>URL:</strong> <a href=\"{source['url']}\" target=\"_blank\">{source['url']}</a></p>\n"
            if 'note' in source:
                html += f"            <p><strong>비고:</strong> {source['note']}</p>\n"
            html += "        </div>\n"
        
        html += f"""
    </div>
    
    <div class="methodology">
        <h2>분석 방법론</h2>
        <p>{report['methodology']}</p>
    </div>
</body>
</html>"""
        
        return html
    
    def _format_text_to_html(self, text: str) -> str:
        """텍스트를 HTML로 변환 (줄바꿈 및 포맷팅)"""
        # 문단 분리
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 표 형식 감지 (|로 시작하는 경우)
            if para.startswith('|'):
                # 표를 HTML 테이블로 변환
                html_paragraphs.append(self._convert_table_to_html(para))
            # 번호 매기기 목록 감지
            elif para.startswith(('1.', '2.', '3.', '4.', '5.')):
                html_paragraphs.append(f'<p>{para}</p>')
            # 일반 문단
            else:
                # 굵은 글씨 변환 (**text** → <strong>text</strong>)
                para = para.replace('**', '<strong>', 1)
                para = para.replace('**', '</strong>', 1)
                html_paragraphs.append(f'<p>{para}</p>')
        
        return '\n'.join(html_paragraphs)
    
    def _convert_table_to_html(self, table_text: str) -> str:
        """마크다운 표를 HTML 테이블로 변환"""
        lines = table_text.strip().split('\n')
        
        html = '<table>\n'
        
        for i, line in enumerate(lines):
            # 구분선 무시
            if '---' in line or '===' in line:
                continue
            
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            
            if i == 0:
                # 헤더
                html += '  <thead>\n    <tr>\n'
                for cell in cells:
                    html += f'      <th>{cell}</th>\n'
                html += '    </tr>\n  </thead>\n  <tbody>\n'
            else:
                # 데이터 행
                html += '    <tr>\n'
                for cell in cells:
                    html += f'      <td>{cell}</td>\n'
                html += '    </tr>\n'
        
        html += '  </tbody>\n</table>'
        
        return html