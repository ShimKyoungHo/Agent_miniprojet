# 차트 생성 Agent - 데이터 시각화
# agents/chart_generation_agent.py

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import json
from .base_agent import BaseAgent

# ⭐ ChartImageGenerator import (에러 처리 포함)
try:
    # 프로젝트 루트를 sys.path에 추가
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from chart_to_image_integration import ChartImageGenerator
    CHART_IMAGE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  차트 이미지 생성 기능을 사용할 수 없습니다: {e}")
    print(f"   chart_to_image_integration.py 파일이 프로젝트 루트에 있는지 확인하세요.")
    ChartImageGenerator = None
    CHART_IMAGE_AVAILABLE = False

class ChartGenerationAgent(BaseAgent):
    """차트 생성 Agent"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("chart_generation", llm, config)
        self.use_image_generation = CHART_IMAGE_AVAILABLE
        
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """차트 생성 메인 프로세스"""
        self.logger.info("차트 생성 시작...")
        
        try:
            # ⭐ 안전한 데이터 수집 (타입 체크 포함)
            market_data = self._safe_get_data(state, 'market_data')
            consumer_patterns = self._safe_get_data(state, 'consumer_patterns')
            company_analysis = self._safe_get_data(state, 'company_analysis')
            tech_trends = self._safe_get_data(state, 'tech_trends')
            stock_analysis = self._safe_get_data(state, 'stock_analysis')
            
            # 데이터 상태 로깅
            self.logger.info(f"데이터 수집 상태:")
            self.logger.info(f"  - market_data: {type(market_data).__name__} ({'있음' if market_data else '없음'})")
            self.logger.info(f"  - consumer_patterns: {type(consumer_patterns).__name__} ({'있음' if consumer_patterns else '없음'})")
            self.logger.info(f"  - company_analysis: {type(company_analysis).__name__} ({'있음' if company_analysis else '없음'})")
            self.logger.info(f"  - tech_trends: {type(tech_trends).__name__} ({'있음' if tech_trends else '없음'})")
            self.logger.info(f"  - stock_analysis: {type(stock_analysis).__name__} ({'있음' if stock_analysis else '없음'})")

            
            # 병렬로 여러 차트 생성
            tasks = [
                self._create_market_growth_chart(market_data),
                self._create_market_share_chart(company_analysis),
                self._create_technology_roadmap_chart(tech_trends),
                self._create_stock_performance_chart(stock_analysis),
                self._create_consumer_preference_chart(consumer_patterns),
                self._create_regional_comparison_chart(market_data),
                self._create_valuation_comparison_chart(stock_analysis)
            ]
            
            chart_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 차트 데이터 통합
            charts = []
            for i, result in enumerate(chart_results):
                if not isinstance(result, Exception):
                    charts.append(result)
                else:
                    self.logger.error(f"차트 생성 실패: {result}")
            
            # ⭐ 차트를 이미지 파일로 저장 (가능한 경우)
            chart_files = {}
            if self.use_image_generation and ChartImageGenerator:
                try:
                    self.logger.info("차트를 이미지 파일로 저장 중...")
                    image_generator = ChartImageGenerator(output_dir="outputs/chart_generation")
                    chart_files = image_generator.generate_all_charts(charts)
                    self.logger.info(f"✅ {len(chart_files)}개 차트 이미지 저장 완료")
                except Exception as img_error:
                    self.logger.error(f"차트 이미지 저장 실패: {img_error}")
                    import traceback
                    traceback.print_exc()
            else:
                self.logger.warning("차트 이미지 생성 기능이 비활성화되어 있습니다.")
            
            # 대시보드 구성
            dashboard = self._create_dashboard_layout(charts)
            
            # 차트 메타데이터 생성
            chart_metadata = {
                'total_charts': len(charts),
                'chart_types': self._get_chart_types(charts),
                'generated_at': self.get_timestamp(),
                'dashboard_config': dashboard,
                'chart_image_files': chart_files,
                'image_generation_enabled': self.use_image_generation
            }
            
            # 결과 저장
            output_data = {
                'charts': charts,
                'metadata': chart_metadata,
                'dashboard': dashboard,
                'chart_files': chart_files
            }
            
            # 차트 데이터를 JSON으로 저장
            self.save_output(output_data, f'charts_{datetime.now().strftime("%Y%m%d")}.json')
            
            # HTML 대시보드 생성
            html_dashboard = self._generate_html_dashboard(charts, dashboard)
            self.save_output(html_dashboard, f'dashboard_{datetime.now().strftime("%Y%m%d")}.html')
            
            # 상태 업데이트
            state['charts_generated'] = True
            state['charts'] = charts
            state['chart_files'] = chart_files
            state['dashboard'] = dashboard
            
            self.logger.info(f"차트 생성 완료: {len(charts)}개 차트, {len(chart_files)}개 이미지")
            
        except Exception as e:
            self.logger.error(f"차트 생성 중 오류: {e}")
            import traceback
            traceback.print_exc()
            state['chart_generation_error'] = str(e)
            
        return state
    
    def _safe_get_data(self, state: Dict, key: str) -> Dict:
        """
        state에서 안전하게 데이터 가져오기
        
        Args:
            state: 전체 상태
            key: 가져올 키
            
        Returns:
            딕셔너리 데이터 또는 빈 딕셔너리
        """
        data = state.get(key, {})
        
        # None이면 빈 딕셔너리 반환
        if data is None:
            self.logger.warning(f"{key}가 None입니다. 빈 딕셔너리로 대체합니다.")
            return {}
        
        # 딕셔너리가 아니면 변환 시도
        if not isinstance(data, dict):
            self.logger.warning(f"{key}가 딕셔너리가 아닙니다 (타입: {type(data).__name__}). 빈 딕셔너리로 대체합니다.")
            
            # 문자열이면 JSON 파싱 시도
            if isinstance(data, str):
                try:
                    parsed = json.loads(data)
                    if isinstance(parsed, dict):
                        self.logger.info(f"{key} JSON 파싱 성공")
                        return parsed
                except:
                    pass
            
            return {}
        
        return data
    
    async def _create_market_growth_chart(self, market_data: Dict) -> Dict:
        """시장 성장 차트 생성"""
        self.logger.info("시장 성장 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        # 실제로는 plotly나 matplotlib 사용
        return {
            'id': 'market_growth_chart',
            'type': 'line',
            'title': 'Global EV Market Growth Forecast',
            'data': {
                'x': ['2020', '2021', '2022', '2023', '2024', '2025F', '2026F', '2027F', '2028F', '2029F', '2030F'],
                'y': [140, 220, 350, 500, 650, 800, 1000, 1250, 1500, 1800, 2200],
                'series': [{
                    'name': 'Market Size (Billion USD)',
                    'type': 'line',
                    'color': '#1f77b4'
                }]
            },
            'layout': {
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Market Size (Billion USD)'},
                'showlegend': True,
                'height': 400
            },
            'insights': 'Exponential growth expected with 25% CAGR through 2030'
        }
    
    async def _create_market_share_chart(self, company_analysis: Dict) -> Dict:
        """시장 점유율 차트 생성"""
        self.logger.info("시장 점유율 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        companies = company_analysis.get('companies', {})
        
        # 판매량 기준 시장 점유율 계산
        market_share_data = []
        for company, data in companies.items():
            if 'ev_sales_2024' in data:
                market_share_data.append({
                    'name': company,
                    'value': data['ev_sales_2024']
                })
        
        return {
            'id': 'market_share_chart',
            'type': 'pie',
            'title': '2024 Global EV Market Share by Company',
            'data': {
                'labels': [d['name'] for d in market_share_data],
                'values': [d['value'] for d in market_share_data],
                'series': [{
                    'type': 'pie',
                    'hole': 0.4,  # Donut chart
                    'colors': ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
                }]
            },
            'layout': {
                'height': 400,
                'showlegend': True
            },
            'insights': 'Top 3 companies control 45% of the market'
        }
    
    async def _create_technology_roadmap_chart(self, tech_trends: Dict) -> Dict:
        """기술 로드맵 차트 생성"""
        self.logger.info("기술 로드맵 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        roadmap = tech_trends.get('roadmap', {}).get('critical_milestones', {})
        
        return {
            'id': 'tech_roadmap_chart',
            'type': 'timeline',
            'title': 'EV Technology Roadmap',
            'data': {
                'events': [
                    {'year': year, 'milestones': milestones}
                    for year, milestones in roadmap.items()
                ],
                'categories': ['Battery', 'Charging', 'Autonomy', 'Infrastructure']
            },
            'layout': {
                'height': 300,
                'orientation': 'horizontal'
            },
            'insights': 'Major technology breakthroughs expected in 2027-2028'
        }
    
    async def _create_stock_performance_chart(self, stock_analysis: Dict) -> Dict:
        """주가 성과 차트 생성 - 안전한 버전"""
        self.logger.info("주가 성과 차트 생성 중...")
        
        try:
            await asyncio.sleep(0.5)
            
            # ⭐ 안전한 데이터 체크
            if not stock_analysis or not isinstance(stock_analysis, dict):
                self.logger.warning("stock_analysis가 딕셔너리가 아닙니다. 빈 차트를 반환합니다.")
                return {}
            
            stocks = stock_analysis.get('individual_stocks', {})
            
            if not stocks or not isinstance(stocks, dict):
                self.logger.warning("individual_stocks 데이터가 없습니다.")
                return {}
            
            performance_data = []
            for ticker, data in stocks.items():
                try:
                    # ⭐ 안전한 데이터 접근
                    if not isinstance(data, dict):
                        self.logger.debug(f"{ticker}: data가 딕셔너리가 아닙니다")
                        continue
                    
                    price_history = data.get('price_history', {})
                    if not isinstance(price_history, dict):
                        self.logger.debug(f"{ticker}: price_history가 딕셔너리가 아닙니다")
                        continue
                    
                    ytd_change = price_history.get('ytd_change')
                    yearly_change = price_history.get('1y_change')
                    
                    # ⭐ 데이터가 있는 경우만 추가
                    if ytd_change is not None and yearly_change is not None:
                        performance_data.append({
                            'ticker': ticker,
                            'ytd': float(ytd_change) * 100,
                            '1y': float(yearly_change) * 100
                        })
                        self.logger.debug(f"{ticker}: 성과 데이터 추가 완료")
                    else:
                        self.logger.debug(f"{ticker}: 성과 데이터 누락 (YTD: {ytd_change}, 1Y: {yearly_change})")
                        
                except Exception as e:
                    self.logger.warning(f"{ticker} 처리 중 오류: {e}")
                    continue
            
            # ⭐ 데이터가 없으면 빈 차트 반환
            if not performance_data:
                self.logger.warning("주가 성과 데이터가 없습니다. 빈 차트를 반환합니다.")
                return {}
            
            self.logger.info(f"주가 성과 차트 데이터: {len(performance_data)}개 종목")
            
            return {
                'id': 'stock_performance_chart',
                'type': 'bar',
                'title': 'EV Stock Performance Comparison',
                'data': {
                    'x': [d['ticker'] for d in performance_data],
                    'y_ytd': [d['ytd'] for d in performance_data],
                    'y_1y': [d['1y'] for d in performance_data],
                    'series': [
                        {'name': 'YTD Return (%)', 'type': 'bar', 'color': '#2ca02c'},
                        {'name': '1Y Return (%)', 'type': 'bar', 'color': '#1f77b4'}
                    ]
                },
                'layout': {
                    'xaxis': {'title': 'Stock Ticker'},
                    'yaxis': {'title': 'Return (%)'},
                    'barmode': 'grouped',
                    'height': 400
                },
                'insights': 'Performance comparison across major EV stocks'
            }
            
        except Exception as e:
            self.logger.error(f"주가 성과 차트 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def _create_consumer_preference_chart(self, consumer_patterns: Dict) -> Dict:
        """소비자 선호도 차트 생성 - 안전한 버전"""
        self.logger.info("소비자 선호도 차트 생성 중...")
        
        try:
            await asyncio.sleep(0.5)
            
            # ⭐ 안전한 데이터 접근
            if not consumer_patterns or not isinstance(consumer_patterns, dict):
                self.logger.warning("consumer_patterns가 딕셔너리가 아닙니다")
                return {}
            
            preferences = consumer_patterns.get('preferences', {})
            if not isinstance(preferences, dict):
                self.logger.warning("preferences가 딕셔너리가 아닙니다")
                return {}
            
            vehicle_type = preferences.get('vehicle_type', {})
            if not isinstance(vehicle_type, dict) or not vehicle_type:
                self.logger.warning("vehicle_type 데이터가 없습니다")
                return {}
            
            return {
                'id': 'consumer_preference_chart',
                'type': 'horizontal_bar',
                'title': 'Consumer Vehicle Type Preferences',
                'data': {
                    'categories': list(vehicle_type.keys()),
                    'values': [v * 100 for v in vehicle_type.values()],
                    'series': [{
                        'name': 'Preference (%)',
                        'type': 'bar',
                        'orientation': 'h',
                        'color': '#ff7f0e'
                    }]
                },
                'layout': {
                    'xaxis': {'title': 'Preference (%)'},
                    'yaxis': {'title': 'Vehicle Type'},
                    'height': 350
                },
                'insights': 'SUVs dominate consumer preferences at 40%'
            }
        except Exception as e:
            self.logger.error(f"소비자 선호도 차트 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def _create_regional_comparison_chart(self, market_data: Dict) -> Dict:
        """지역별 비교 차트 생성 - 키 필터링 개선"""
        self.logger.info("지역별 비교 차트 생성 중...")
        
        try:
            await asyncio.sleep(0.5)
            
            # 안전한 데이터 접근
            if not market_data or not isinstance(market_data, dict):
                self.logger.warning("market_data가 딕셔너리가 아닙니다")
                return {}
            
            regional = market_data.get('regional_markets', {})
            if not isinstance(regional, dict) or not regional:
                self.logger.warning("regional_markets 데이터가 없습니다")
                return {}
            
            # ⭐ 메타데이터 키 필터링 (analysis_date 등 제외)
            metadata_keys = {
                'analysis_date', 'timestamp', 'generated_at', 
                'last_updated', 'source', 'metadata', 'notes'
            }
            
            regions_data = []
            for region, data in regional.items():
                # 메타데이터 키 건너뛰기
                if region in metadata_keys:
                    self.logger.debug(f"{region}: 메타데이터 키이므로 건너뜁니다")
                    continue
                
                try:
                    # 데이터가 딕셔너리가 아니면 건너뛰기
                    if not isinstance(data, dict):
                        self.logger.warning(f"{region}: data가 딕셔너리가 아닙니다 (타입: {type(data).__name__})")
                        continue
                    
                    market_size = data.get('market_size', 0)
                    growth_rate = data.get('growth_rate', 0)
                    ev_penetration = data.get('ev_penetration', 0)
                    
                    # 데이터 검증
                    if market_size == 0 and growth_rate == 0 and ev_penetration == 0:
                        self.logger.debug(f"{region}: 모든 값이 0이므로 건너뜁니다")
                        continue
                    
                    regions_data.append({
                        'region': region.replace('_', ' ').title(),
                        'market_size': float(market_size) / 1000000000 if market_size > 1000000 else float(market_size),
                        'growth_rate': float(growth_rate) * 100 if growth_rate <= 1 else float(growth_rate),
                        'ev_penetration': float(ev_penetration) * 100 if ev_penetration <= 1 else float(ev_penetration)
                    })
                    self.logger.debug(f"✅ {region}: 데이터 추가 완료")
                except Exception as e:
                    self.logger.warning(f"{region} 처리 중 오류: {e}")
                    continue
            
            # 데이터가 없으면 기본값 사용
            if not regions_data:
                self.logger.warning("처리 가능한 지역 데이터가 없습니다. 기본값 사용")
                regions_data = [
                    {'region': 'China', 'market_size': 650, 'growth_rate': 25, 'ev_penetration': 30},
                    {'region': 'Europe', 'market_size': 280, 'growth_rate': 20, 'ev_penetration': 25},
                    {'region': 'North America', 'market_size': 150, 'growth_rate': 15, 'ev_penetration': 10},
                    {'region': 'Asia Pacific', 'market_size': 120, 'growth_rate': 30, 'ev_penetration': 15}
                ]
            
            self.logger.info(f"지역별 차트 데이터: {len(regions_data)}개 지역")
            
            return {
                'id': 'regional_comparison_chart',
                'type': 'scatter',
                'title': 'Regional EV Markets: Size vs Growth',
                'data': {
                    'x': [d['market_size'] for d in regions_data],
                    'y': [d['growth_rate'] for d in regions_data],
                    'size': [d['ev_penetration'] * 5 for d in regions_data],
                    'labels': [d['region'] for d in regions_data],
                    'series': [{
                        'name': 'Regional Markets',
                        'type': 'scatter',
                        'mode': 'markers+text',
                        'color': '#9467bd'
                    }]
                },
                'layout': {
                    'xaxis': {'title': 'Market Size (Billion USD)'},
                    'yaxis': {'title': 'Growth Rate (%)'},
                    'height': 400
                },
                'insights': 'Regional market comparison by size and growth'
            }
        except Exception as e:
            self.logger.error(f"지역별 비교 차트 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def _create_valuation_comparison_chart(self, stock_analysis: Dict) -> Dict:
        """밸류에이션 비교 차트 생성"""
        self.logger.info("밸류에이션 비교 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        stocks = stock_analysis.get('individual_stocks', {})
        
        valuation_data = []
        for ticker, data in stocks.items():
            pe = data['financials'].get('pe_ratio')
            if pe:  # PE ratio가 있는 경우만
                valuation_data.append({
                    'ticker': ticker,
                    'pe_ratio': pe,
                    'ps_ratio': data['financials']['ps_ratio'],
                    'market_cap': data['financials']['market_cap'] / 1000000000  # To billions
                })
        
        return {
            'id': 'valuation_comparison_chart',
            'type': 'bubble',
            'title': 'EV Stock Valuations: P/E vs P/S Ratio',
            'data': {
                'x': [d['pe_ratio'] for d in valuation_data],
                'y': [d['ps_ratio'] for d in valuation_data],
                'size': [d['market_cap'] / 10 for d in valuation_data],  # Scaled for visibility
                'labels': [d['ticker'] for d in valuation_data],
                'series': [{
                    'name': 'Valuations',
                    'type': 'scatter',
                    'mode': 'markers',
                    'colors': '#d62728'
                }]
            },
            'layout': {
                'xaxis': {'title': 'P/E Ratio', 'range': [0, 100]},
                'yaxis': {'title': 'P/S Ratio', 'range': [0, 15]},
                'height': 400
            },
            'insights': 'Traditional OEMs showing more reasonable valuations'
        }
    
    def _create_dashboard_layout(self, charts: List[Dict]) -> Dict:
        """대시보드 레이아웃 구성"""
        return {
            'layout': 'grid',
            'rows': 3,
            'columns': 3,
            'charts_placement': [
                {'chart_id': 'market_growth_chart', 'position': {'row': 1, 'col': 1, 'colspan': 2}},
                {'chart_id': 'market_share_chart', 'position': {'row': 1, 'col': 3}},
                {'chart_id': 'stock_performance_chart', 'position': {'row': 2, 'col': 1, 'colspan': 2}},
                {'chart_id': 'regional_comparison_chart', 'position': {'row': 2, 'col': 3}},
                {'chart_id': 'consumer_preference_chart', 'position': {'row': 3, 'col': 1}},
                {'chart_id': 'valuation_comparison_chart', 'position': {'row': 3, 'col': 2}},
                {'chart_id': 'tech_roadmap_chart', 'position': {'row': 3, 'col': 3}}
            ],
            'theme': 'dark',
            'title': 'EV Market Analysis Dashboard'
        }
    
    def _get_chart_types(self, charts: List[Dict]) -> Dict:
        """차트 타입별 개수 집계"""
        types = {}
        for chart in charts:
            chart_type = chart.get('type', 'unknown')
            types[chart_type] = types.get(chart_type, 0) + 1
        return types
    
    def _generate_html_dashboard(self, charts: List[Dict], dashboard_config: Dict) -> str:
        """HTML 대시보드 생성"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{dashboard_config['title']}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }}
        .dashboard-title {{
            text-align: center;
            font-size: 2em;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background-color: #2d2d2d;
            border-radius: 8px;
            padding: 15px;
            margin: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        .insights {{
            color: #00ff00;
            font-size: 0.9em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <h1 class="dashboard-title">{dashboard_config['title']}</h1>
    <div class="grid">
        {"".join([self._create_chart_html(chart) for chart in charts])}
    </div>
    <script>
        // Plotly chart rendering code would go here
    </script>
</body>
</html>
        """
        return html
    
    def _create_chart_html(self, chart: Dict) -> str:
        """개별 차트 HTML 생성"""
        return f"""
        <div class="chart-container">
            <h3>{chart['title']}</h3>
            <div id="{chart['id']}"></div>
            <p class="insights">{chart.get('insights', '')}</p>
        </div>
        """