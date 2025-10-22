# 차트 생성 Agent - 데이터 시각화
# agents/chart_generation_agent.py

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import json
from .base_agent import BaseAgent

class ChartGenerationAgent(BaseAgent):
    """차트 생성 Agent"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("chart_generation", llm, config)
        
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """차트 생성 메인 프로세스"""
        self.logger.info("차트 생성 시작...")
        
        try:
            # 필요한 데이터 수집
            market_data = state.get('market_data', {})
            consumer_patterns = state.get('consumer_patterns', {})
            company_analysis = state.get('company_analysis', {})
            tech_trends = state.get('tech_trends', {})
            stock_analysis = state.get('stock_analysis', {})
            
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
            
            # 대시보드 구성
            dashboard = self._create_dashboard_layout(charts)
            
            # 차트 메타데이터 생성
            chart_metadata = {
                'total_charts': len(charts),
                'chart_types': self._get_chart_types(charts),
                'generated_at': self.get_timestamp(),
                'dashboard_config': dashboard
            }
            
            # 결과 저장
            output_data = {
                'charts': charts,
                'metadata': chart_metadata,
                'dashboard': dashboard
            }
            
            # 차트 데이터를 JSON으로 저장
            self.save_output(output_data, f'charts_{datetime.now().strftime("%Y%m%d")}.json')
            
            # HTML 대시보드 생성
            html_dashboard = self._generate_html_dashboard(charts, dashboard)
            self.save_output(html_dashboard, f'dashboard_{datetime.now().strftime("%Y%m%d")}.html')
            
            # 상태 업데이트
            state['charts_generated'] = True
            state['charts'] = charts
            state['dashboard'] = dashboard
            
            self.logger.info(f"차트 생성 완료: {len(charts)}개 차트")
            
        except Exception as e:
            self.logger.error(f"차트 생성 중 오류: {e}")
            state['chart_generation_error'] = str(e)
            
        return state
    
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
        """주가 성과 차트 생성"""
        self.logger.info("주가 성과 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        stocks = stock_analysis.get('individual_stocks', {})
        
        performance_data = []
        for ticker, data in stocks.items():
            performance_data.append({
                'ticker': ticker,
                'ytd': data['price_history']['ytd_change'] * 100,
                '1y': data['price_history']['1y_change'] * 100
            })
        
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
            'insights': 'Chinese EV stocks showing strong momentum'
        }
    
    async def _create_consumer_preference_chart(self, consumer_patterns: Dict) -> Dict:
        """소비자 선호도 차트 생성"""
        self.logger.info("소비자 선호도 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        preferences = consumer_patterns.get('preferences', {}).get('vehicle_type', {})
        
        return {
            'id': 'consumer_preference_chart',
            'type': 'horizontal_bar',
            'title': 'Consumer Vehicle Type Preferences',
            'data': {
                'categories': list(preferences.keys()),
                'values': [v * 100 for v in preferences.values()],
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
    
    async def _create_regional_comparison_chart(self, market_data: Dict) -> Dict:
        """지역별 비교 차트 생성"""
        self.logger.info("지역별 비교 차트 생성 중...")
        
        await asyncio.sleep(0.5)
        
        regional = market_data.get('regional_markets', {})
        
        regions_data = []
        for region, data in regional.items():
            regions_data.append({
                'region': region.replace('_', ' ').title(),
                'market_size': data.get('market_size', 0) / 1000000000,  # Convert to billions
                'growth_rate': data.get('growth_rate', 0) * 100,
                'ev_penetration': data.get('ev_penetration', 0) * 100
            })
        
        return {
            'id': 'regional_comparison_chart',
            'type': 'scatter',
            'title': 'Regional EV Markets: Size vs Growth',
            'data': {
                'x': [d['market_size'] for d in regions_data],
                'y': [d['growth_rate'] for d in regions_data],
                'size': [d['ev_penetration'] * 5 for d in regions_data],  # Bubble size
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
            'insights': 'Asia Pacific leads in both size and growth rate'
        }
    
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