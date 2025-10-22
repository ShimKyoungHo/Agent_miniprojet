# 주가 분석 Agent - 주가 및 재무 분석
# agents/stock_analysis_agent.py

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import random  # 시뮬레이션용
from .base_agent import BaseAgent

class StockAnalysisAgent(BaseAgent):
    """주가 분석 Agent"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("stock_analysis", llm, config)
        self.tickers = config.get('tickers', {
            'TSLA': 'Tesla',
            'BYD': 'BYD',
            'RIVN': 'Rivian',
            'LCID': 'Lucid',
            'NIO': 'NIO',
            'XPEV': 'XPeng',
            'LI': 'Li Auto',
            'F': 'Ford',
            'GM': 'General Motors',
            'STLA': 'Stellantis'
        }) if config else {}
        
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """주가 분석 메인 프로세스"""
        self.logger.info("주가 분석 시작...")
        
        try:
            # 병렬로 주가 데이터 수집 및 분석
            tasks = []
            for ticker, company in self.tickers.items():
                tasks.append(self._analyze_stock(ticker, company))
            
            stock_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 통합
            stocks_data = {}
            for i, (ticker, company) in enumerate(self.tickers.items()):
                if not isinstance(stock_results[i], Exception):
                    stocks_data[ticker] = stock_results[i]
            
            # 섹터 분석
            sector_analysis = await self._analyze_sector_performance(stocks_data)
            
            # 상관관계 분석
            correlation_analysis = self._analyze_correlations(stocks_data)
            
            # 투자 지표 계산
            valuation_metrics = self._calculate_valuation_metrics(stocks_data)
            
            # LLM을 통한 투자 인사이트
            investment_insights = None
            if self.llm:
                investment_insights = await self._generate_investment_insights(
                    stocks_data, sector_analysis, valuation_metrics
                )
            
            # 최종 분석 결과
            analysis_result = {
                'individual_stocks': stocks_data,
                'sector_analysis': sector_analysis,
                'correlation_analysis': correlation_analysis,
                'valuation_metrics': valuation_metrics,
                'investment_insights': investment_insights,
                'market_sentiment': self._analyze_market_sentiment(stocks_data),
                'timestamp': self.get_timestamp()
            }
            
            # 상태 업데이트
            state['stock_analysis'] = analysis_result
            
            # 결과 저장
            self.save_output(analysis_result, f'stock_analysis_{datetime.now().strftime("%Y%m%d")}.json')
            
            self.logger.info("주가 분석 완료")
            
        except Exception as e:
            self.logger.error(f"주가 분석 중 오류: {e}")
            state['stock_analysis_error'] = str(e)
            
        return state
    
    async def _analyze_stock(self, ticker: str, company: str) -> Dict:
        """개별 주식 분석"""
        self.logger.info(f"{ticker} ({company}) 분석 중...")
        
        # 실제로는 yfinance 또는 Alpha Vantage API 사용
        # 여기서는 시뮬레이션 데이터
        await asyncio.sleep(0.5)
        
        # 시뮬레이션 데이터 생성
        base_price = {
            'TSLA': 250, 'BYD': 35, 'RIVN': 15, 'LCID': 4,
            'NIO': 8, 'XPEV': 12, 'LI': 25, 'F': 12,
            'GM': 40, 'STLA': 20
        }.get(ticker, 50)
        
        return {
            'company': company,
            'current_price': base_price * (1 + random.uniform(-0.05, 0.05)),
            'price_history': {
                '1d_change': random.uniform(-0.05, 0.05),
                '1w_change': random.uniform(-0.10, 0.10),
                '1m_change': random.uniform(-0.15, 0.15),
                '3m_change': random.uniform(-0.25, 0.25),
                '1y_change': random.uniform(-0.30, 0.50),
                'ytd_change': random.uniform(-0.20, 0.40)
            },
            'volume': {
                'avg_volume_3m': random.randint(10000000, 100000000),
                'current_volume': random.randint(8000000, 120000000),
                'volume_trend': random.choice(['increasing', 'stable', 'decreasing'])
            },
            'financials': {
                'market_cap': base_price * random.randint(100000000, 1000000000),
                'pe_ratio': random.uniform(15, 100) if ticker not in ['RIVN', 'LCID'] else None,
                'ps_ratio': random.uniform(1, 10),
                'pb_ratio': random.uniform(1, 15),
                'revenue_growth': random.uniform(-0.1, 0.5),
                'gross_margin': random.uniform(0.05, 0.25),
                'operating_margin': random.uniform(-0.1, 0.15)
            },
            'technical_indicators': {
                'rsi': random.uniform(30, 70),
                'macd': random.choice(['bullish', 'bearish', 'neutral']),
                'ma_50': base_price * (1 + random.uniform(-0.1, 0.1)),
                'ma_200': base_price * (1 + random.uniform(-0.15, 0.15)),
                'support_level': base_price * 0.85,
                'resistance_level': base_price * 1.15
            },
            'analyst_ratings': {
                'strong_buy': random.randint(0, 10),
                'buy': random.randint(0, 15),
                'hold': random.randint(5, 20),
                'sell': random.randint(0, 5),
                'strong_sell': random.randint(0, 3),
                'average_target': base_price * (1 + random.uniform(-0.2, 0.4)),
                'high_target': base_price * (1 + random.uniform(0.3, 0.7)),
                'low_target': base_price * (1 + random.uniform(-0.3, -0.1))
            },
            'risk_metrics': {
                'beta': random.uniform(0.8, 2.0),
                'volatility_30d': random.uniform(0.2, 0.6),
                'sharpe_ratio': random.uniform(-0.5, 2.0),
                'max_drawdown': random.uniform(-0.2, -0.5)
            }
        }
    
    async def _analyze_sector_performance(self, stocks_data: Dict) -> Dict:
        """섹터 전체 성과 분석"""
        self.logger.info("섹터 성과 분석 중...")
        
        # 전체 섹터 지표 계산
        total_market_cap = sum(
            stock['financials']['market_cap'] 
            for stock in stocks_data.values()
        )
        
        avg_performance = {
            '1y': sum(stock['price_history']['1y_change'] for stock in stocks_data.values()) / len(stocks_data),
            'ytd': sum(stock['price_history']['ytd_change'] for stock in stocks_data.values()) / len(stocks_data)
        }
        
        return {
            'sector_market_cap': total_market_cap,
            'sector_performance': avg_performance,
            'vs_sp500': {
                'outperformance_1y': avg_performance['1y'] - 0.15,  # 가정: S&P500 15% 상승
                'correlation': random.uniform(0.5, 0.8)
            },
            'subsector_performance': {
                'pure_play_ev': ['TSLA', 'RIVN', 'LCID'],
                'chinese_ev': ['BYD', 'NIO', 'XPEV', 'LI'],
                'traditional_oem': ['F', 'GM', 'STLA']
            },
            'momentum_indicators': {
                'sector_trend': 'upward' if avg_performance['ytd'] > 0 else 'downward',
                'strength': 'strong' if abs(avg_performance['ytd']) > 0.2 else 'moderate'
            }
        }
    
    def _analyze_correlations(self, stocks_data: Dict) -> Dict:
        """주식 간 상관관계 분석"""
        # 실제로는 주가 시계열 데이터로 상관계수 계산
        # 여기서는 간단한 시뮬레이션
        
        correlations = {}
        tickers = list(stocks_data.keys())
        
        for i, ticker1 in enumerate(tickers):
            for ticker2 in tickers[i+1:]:
                # 같은 서브섹터면 높은 상관관계
                if ticker1 in ['NIO', 'XPEV', 'LI'] and ticker2 in ['NIO', 'XPEV', 'LI']:
                    corr = random.uniform(0.7, 0.9)
                elif ticker1 in ['F', 'GM', 'STLA'] and ticker2 in ['F', 'GM', 'STLA']:
                    corr = random.uniform(0.6, 0.8)
                else:
                    corr = random.uniform(0.3, 0.6)
                
                correlations[f'{ticker1}_vs_{ticker2}'] = corr
        
        return {
            'correlations': correlations,
            'highest_correlation': max(correlations, key=correlations.get),
            'lowest_correlation': min(correlations, key=correlations.get),
            'diversification_score': 1 - (sum(correlations.values()) / len(correlations))
        }
    
    def _calculate_valuation_metrics(self, stocks_data: Dict) -> Dict:
        """밸류에이션 지표 계산"""
        # PE 비율이 있는 주식들만 필터링
        stocks_with_pe = {
            ticker: data for ticker, data in stocks_data.items()
            if data['financials'].get('pe_ratio')
        }
        
        if stocks_with_pe:
            avg_pe = sum(s['financials']['pe_ratio'] for s in stocks_with_pe.values()) / len(stocks_with_pe)
        else:
            avg_pe = None
        
        return {
            'sector_average_pe': avg_pe,
            'sector_average_ps': sum(s['financials']['ps_ratio'] for s in stocks_data.values()) / len(stocks_data),
            'most_expensive': max(stocks_data, key=lambda x: stocks_data[x]['financials']['ps_ratio']),
            'cheapest': min(stocks_data, key=lambda x: stocks_data[x]['financials']['ps_ratio']),
            'valuation_spread': {
                'high_ps': max(s['financials']['ps_ratio'] for s in stocks_data.values()),
                'low_ps': min(s['financials']['ps_ratio'] for s in stocks_data.values())
            }
        }
    
    def _analyze_market_sentiment(self, stocks_data: Dict) -> Dict:
        """시장 심리 분석"""
        # 애널리스트 평가 집계
        total_ratings = {
            'bullish': 0,
            'neutral': 0,
            'bearish': 0
        }
        
        for stock in stocks_data.values():
            ratings = stock['analyst_ratings']
            total_ratings['bullish'] += ratings['strong_buy'] + ratings['buy']
            total_ratings['neutral'] += ratings['hold']
            total_ratings['bearish'] += ratings['sell'] + ratings['strong_sell']
        
        total = sum(total_ratings.values())
        
        # RSI 기반 momentum
        avg_rsi = sum(s['technical_indicators']['rsi'] for s in stocks_data.values()) / len(stocks_data)
        
        return {
            'analyst_sentiment': {
                'bullish_percent': total_ratings['bullish'] / total if total > 0 else 0,
                'neutral_percent': total_ratings['neutral'] / total if total > 0 else 0,
                'bearish_percent': total_ratings['bearish'] / total if total > 0 else 0,
                'overall': 'bullish' if total_ratings['bullish'] > total_ratings['bearish'] else 'bearish'
            },
            'technical_sentiment': {
                'average_rsi': avg_rsi,
                'condition': 'overbought' if avg_rsi > 70 else 'oversold' if avg_rsi < 30 else 'neutral'
            },
            'volume_sentiment': {
                'trending_stocks': [
                    ticker for ticker, data in stocks_data.items()
                    if data['volume']['volume_trend'] == 'increasing'
                ]
            }
        }
    
    async def _generate_investment_insights(self, stocks_data: Dict, 
                                           sector_analysis: Dict, 
                                           valuation_metrics: Dict) -> Dict:
        """LLM을 통한 투자 인사이트 생성"""
        if not self.llm:
            return {}
        
        prompt = f"""
        다음 주가 분석 데이터를 기반으로 투자 인사이트를 생성하세요:
        
        개별 주식 데이터: {list(stocks_data.keys())}
        섹터 분석: {sector_analysis}
        밸류에이션: {valuation_metrics}
        
        다음을 포함하여 분석하세요:
        1. 가장 매력적인 투자 기회
        2. 주요 리스크 요인
        3. 섹터 로테이션 전망
        4. 포트폴리오 구성 추천
        5. 진입/청산 시점 제안
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return {
                'investment_thesis': response.content,
                'top_picks': self._identify_top_picks(stocks_data),
                'risk_warnings': self._identify_risks(stocks_data),
                'generated_at': self.get_timestamp()
            }
        except Exception as e:
            self.logger.error(f"투자 인사이트 생성 중 오류: {e}")
            return {'error': str(e)}
    
    def _identify_top_picks(self, stocks_data: Dict) -> List[Dict]:
        """상위 추천 종목 선정"""
        # 간단한 스코어링 시스템
        scores = {}
        for ticker, data in stocks_data.items():
            score = 0
            
            # 성과 점수
            if data['price_history']['1y_change'] > 0.2:
                score += 2
            
            # 애널리스트 평가
            ratings = data['analyst_ratings']
            if ratings['strong_buy'] + ratings['buy'] > ratings['sell'] + ratings['strong_sell']:
                score += 1
            
            # 기술적 지표
            if data['technical_indicators']['rsi'] < 50:  # Oversold
                score += 1
            
            scores[ticker] = score
        
        # 상위 3개 선정
        top_tickers = sorted(scores, key=scores.get, reverse=True)[:3]
        
        return [
            {
                'ticker': ticker,
                'company': stocks_data[ticker]['company'],
                'reason': 'Strong fundamentals and growth potential'
            }
            for ticker in top_tickers
        ]
    
    def _identify_risks(self, stocks_data: Dict) -> List[str]:
        """주요 리스크 식별"""
        risks = []
        
        # 높은 변동성 체크
        high_vol_stocks = [
            ticker for ticker, data in stocks_data.items()
            if data['risk_metrics']['volatility_30d'] > 0.4
        ]
        if high_vol_stocks:
            risks.append(f"High volatility in {', '.join(high_vol_stocks)}")
        
        # 과매수 상태 체크
        overbought = [
            ticker for ticker, data in stocks_data.items()
            if data['technical_indicators']['rsi'] > 70
        ]
        if overbought:
            risks.append(f"Overbought conditions in {', '.join(overbought)}")
        
        return risks