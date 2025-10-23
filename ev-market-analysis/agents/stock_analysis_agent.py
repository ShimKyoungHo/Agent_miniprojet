# 주가 분석 Agent - yfinance를 활용한 실제 주가 데이터 수집
# agents/stock_analysis_agent.py

from typing import Dict, Any, Optional, List, Tuple
import asyncio
from datetime import datetime, timedelta
import os
from tavily import TavilyClient
from .base_agent import BaseAgent
import pandas as pd

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  경고: yfinance가 설치되지 않았습니다. pip install yfinance를 실행하세요.")

class StockAnalysisAgent(BaseAgent):
    """주가 분석 Agent - yfinance 활용"""
    
    def __init__(self, llm=None, config: Optional[Dict] = None):
        super().__init__("stock_analysis", llm, config)
        
        # 기본 티커 맵핑 (회사명 → 티커)
        self.default_ticker_map = {
            'Tesla': 'TSLA',
            'BYD': '1211.HK',  # Hong Kong Stock Exchange
            'Volkswagen': 'VOW3.DE',  # Frankfurt
            'Hyundai': '005380.KS',  # Korea
            'GM': 'GM',
            'General Motors': 'GM',
            'Ford': 'F',
            'Stellantis': 'STLA',
            'Rivian': 'RIVN',
            'Lucid': 'LCID',
            'NIO': 'NIO',
            'XPeng': 'XPEV',
            'Li Auto': 'LI',
            'Mercedes-Benz': 'MBG.DE',
            'BMW': 'BMW.DE',
            'Renault': 'RNO.PA',  # Paris
            'Nissan': '7201.T',  # Tokyo
            'Toyota': '7203.T',
            'Geely': '0175.HK',
            'Kia': '000270.KS',
            'Polestar': 'PSNY',
            'Fisker': 'FSR',
            'Arrival': 'ARVL',
            'Canoo': 'GOEV',
            'Lordstown': 'RIDE'
        }
        
        # 설정에서 커스텀 티커 로드
        self.custom_tickers = config.get('tickers', {}) if config else {}
        self.ticker_map = {**self.default_ticker_map, **self.custom_tickers}
        
        # Tavily 클라이언트 (티커 검색용)
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
        else:
            self.tavily_client = None
        
        # yfinance 사용 가능 여부
        self.use_yfinance = YFINANCE_AVAILABLE and config.get('use_real_data', True) if config else YFINANCE_AVAILABLE
        
        if not self.use_yfinance:
            self.logger.warning("yfinance를 사용할 수 없습니다. 시뮬레이션 데이터를 사용합니다.")
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """주가 분석 메인 프로세스"""
        self.logger.info("주가 분석 시작...")
        
        try:
            # 1단계: 분석할 기업 목록 가져오기
            companies = self._get_companies_to_analyze(state)
            self.logger.info(f"분석 대상 기업 ({len(companies)}개): {', '.join(companies)}")
            
            # 2단계: 기업명 → 티커 매핑
            ticker_company_map = await self._map_companies_to_tickers(companies)
            self.logger.info(f"티커 매핑 완료: {len(ticker_company_map)}개")
            
            # 3단계: 병렬로 주가 데이터 수집 및 분석
            tasks = []
            for ticker, company in ticker_company_map.items():
                tasks.append(self._analyze_stock(ticker, company))
            
            stock_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 4단계: 결과 통합
            stocks_data = {}
            for i, (ticker, company) in enumerate(ticker_company_map.items()):
                if not isinstance(stock_results[i], Exception):
                    stocks_data[ticker] = stock_results[i]
                else:
                    self.logger.error(f"{ticker} ({company}) 분석 실패: {stock_results[i]}")
            
            if not stocks_data:
                self.logger.warning("분석 가능한 주식 데이터가 없습니다.")
                state['stock_analysis'] = {'error': '주식 데이터 수집 실패'}
                return state
            
            # 5단계: 섹터 분석
            sector_analysis = await self._analyze_sector_performance(stocks_data)
            
            # 6단계: 상관관계 분석
            correlation_analysis = self._analyze_correlations(stocks_data)
            
            # 7단계: 투자 지표 계산
            valuation_metrics = self._calculate_valuation_metrics(stocks_data)
            
            # 8단계: LLM을 통한 투자 인사이트
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
                'data_source': 'yfinance' if self.use_yfinance else 'simulation',
                'timestamp': self.get_timestamp()
            }
            
            # 상태 업데이트
            state['stock_analysis'] = analysis_result
            
            # 결과 저장
            self.save_output(analysis_result, f'stock_analysis_{datetime.now().strftime("%Y%m%d")}.json')
            
            self.logger.info(f"✅ 주가 분석 완료 ({len(stocks_data)}개 종목)")
            
        except Exception as e:
            self.logger.error(f"주가 분석 중 오류: {e}")
            import traceback
            traceback.print_exc()
            state['stock_analysis_error'] = str(e)
            
        return state
    
    def _get_companies_to_analyze(self, state: Dict[str, Any]) -> List[str]:
        """분석할 기업 목록 가져오기"""
        # company_analysis에서 발굴된 기업 목록 우선 사용
        company_analysis = state.get('company_analysis', {})
        discovered_companies = company_analysis.get('discovered_companies', [])
        
        if discovered_companies:
            return discovered_companies
        
        # 없으면 companies 키에서 추출
        companies_data = company_analysis.get('companies', {})
        if companies_data:
            return list(companies_data.keys())
        
        # 그것도 없으면 기본 티커 맵에서
        return list(self.default_ticker_map.keys())[:10]
    
    async def _map_companies_to_tickers(self, companies: List[str]) -> Dict[str, str]:
        """기업명을 티커로 매핑"""
        ticker_company_map = {}
        
        for company in companies:
            # 기존 맵에 있는지 확인
            if company in self.ticker_map:
                ticker = self.ticker_map[company]
                ticker_company_map[ticker] = company
                self.logger.info(f"  ✓ {company} → {ticker}")
            else:
                # 동적으로 티커 검색
                ticker = await self._find_ticker_for_company(company)
                if ticker:
                    ticker_company_map[ticker] = company
                    self.logger.info(f"  🔍 {company} → {ticker} (검색)")
                else:
                    self.logger.warning(f"  ✗ {company}: 티커를 찾을 수 없습니다")
        
        return ticker_company_map
    
    async def _find_ticker_for_company(self, company: str) -> Optional[str]:
        """웹 검색으로 기업의 티커 찾기"""
        if not self.tavily_client or not self.llm:
            return None
        
        try:
            query = f"{company} stock ticker symbol"
            search_results = await asyncio.to_thread(
                self.tavily_client.search,
                query=query,
                max_results=3
            )
            
            results_text = "\n".join([
                f"{r.get('title', '')}: {r.get('content', '')[:150]}"
                for r in search_results.get('results', [])[:3]
            ])
            
            prompt = f"""다음 검색 결과에서 {company}의 주식 티커 심볼을 찾으세요:

{results_text}

조건:
1. 정확한 티커 심볼만 추출 (예: TSLA, 005380.KS, VOW3.DE)
2. 거래소 접미사 포함 (한국: .KS, 홍콩: .HK, 독일: .DE 등)
3. 찾을 수 없으면 null

JSON 형식으로만 응답:
{{"ticker": "TSLA"}} 또는 {{"ticker": null}}"""
            
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            import json
            import re
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('ticker')
            
        except Exception as e:
            self.logger.error(f"{company} 티커 검색 오류: {e}")
        
        return None
    
    async def _analyze_stock(self, ticker: str, company: str) -> Dict:
        """개별 주식 분석"""
        self.logger.info(f"  📈 {ticker} ({company}) 분석 중...")
        
        if self.use_yfinance:
            return await self._analyze_stock_yfinance(ticker, company)
        else:
            return self._analyze_stock_simulation(ticker, company)
    
    async def _analyze_stock_yfinance(self, ticker: str, company: str) -> Dict:
        """yfinance로 실제 주식 데이터 수집"""
        try:
            # yfinance Ticker 객체 생성
            stock = await asyncio.to_thread(yf.Ticker, ticker)
            
            # 1. 기본 정보
            info = await asyncio.to_thread(lambda: stock.info)
            
            # 2. 가격 히스토리 (1년)
            hist = await asyncio.to_thread(
                lambda: stock.history(period="1y")
            )
            
            if hist.empty:
                self.logger.warning(f"{ticker}: 가격 데이터가 없습니다")
                return None
            
            # 3. 재무 데이터
            financials = await asyncio.to_thread(lambda: stock.financials)
            balance_sheet = await asyncio.to_thread(lambda: stock.balance_sheet)
            
            # 4. 애널리스트 추천
            recommendations = await asyncio.to_thread(lambda: stock.recommendations)
            
            # 데이터 가공
            current_price = info.get('currentPrice', hist['Close'].iloc[-1])
            
            # 가격 변동률 계산
            price_history = self._calculate_price_changes(hist)
            
            # 거래량 분석
            volume_analysis = self._analyze_volume(hist)
            
            # 재무 지표
            financial_metrics = self._extract_financial_metrics(info, financials, balance_sheet)
            
            # 기술적 지표
            technical_indicators = self._calculate_technical_indicators(hist)
            
            # 애널리스트 평가
            analyst_ratings = self._process_analyst_ratings(recommendations, info)
            
            # 리스크 지표
            risk_metrics = self._calculate_risk_metrics(hist, info)
            
            return {
                'company': company,
                'ticker': ticker,
                'current_price': current_price,
                'currency': info.get('currency', 'USD'),
                'price_history': price_history,
                'volume': volume_analysis,
                'financials': financial_metrics,
                'technical_indicators': technical_indicators,
                'analyst_ratings': analyst_ratings,
                'risk_metrics': risk_metrics,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'data_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"{ticker} yfinance 분석 오류: {e}")
            return None
    
    def _calculate_price_changes(self, hist) -> Dict:
        """가격 변동률 계산"""
        try:
            close_prices = hist['Close']
            
            changes = {
                '1d_change': (close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2] if len(close_prices) > 1 else 0,
                '1w_change': (close_prices.iloc[-1] - close_prices.iloc[-5]) / close_prices.iloc[-5] if len(close_prices) > 5 else 0,
                '1m_change': (close_prices.iloc[-1] - close_prices.iloc[-21]) / close_prices.iloc[-21] if len(close_prices) > 21 else 0,
                '3m_change': (close_prices.iloc[-1] - close_prices.iloc[-63]) / close_prices.iloc[-63] if len(close_prices) > 63 else 0,
                '6m_change': (close_prices.iloc[-1] - close_prices.iloc[-126]) / close_prices.iloc[-126] if len(close_prices) > 126 else 0,
                '1y_change': (close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0],
                'ytd_change': (close_prices.iloc[-1] - close_prices[close_prices.index.year == datetime.now().year].iloc[0]) / close_prices[close_prices.index.year == datetime.now().year].iloc[0] if any(close_prices.index.year == datetime.now().year) else 0,
                '52w_high': close_prices.max(),
                '52w_low': close_prices.min()
            }
            
            return changes
        except Exception as e:
            self.logger.error(f"가격 변동률 계산 오류: {e}")
            return {'1y_change': 0}
    
    def _analyze_volume(self, hist) -> Dict:
        """거래량 분석"""
        try:
            volumes = hist['Volume']
            
            return {
                'current_volume': int(volumes.iloc[-1]),
                'avg_volume_3m': int(volumes.iloc[-63:].mean()) if len(volumes) > 63 else int(volumes.mean()),
                'avg_volume_1m': int(volumes.iloc[-21:].mean()) if len(volumes) > 21 else int(volumes.mean()),
                'volume_trend': self._determine_trend(volumes.iloc[-10:]) if len(volumes) > 10 else 'stable'
            }
        except Exception as e:
            self.logger.error(f"거래량 분석 오류: {e}")
            return {'current_volume': 0, 'avg_volume_3m': 0}
    
    def _extract_financial_metrics(self, info: Dict, financials, balance_sheet) -> Dict:
        """재무 지표 추출"""
        try:
            return {
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'ps_ratio': info.get('priceToSalesTrailing12Months', None),
                'pb_ratio': info.get('priceToBook', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'earnings_growth': info.get('earningsGrowth', None),
                'profit_margins': info.get('profitMargins', None),
                'gross_margins': info.get('grossMargins', None),
                'operating_margins': info.get('operatingMargins', None),
                'roe': info.get('returnOnEquity', None),
                'roa': info.get('returnOnAssets', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'quick_ratio': info.get('quickRatio', None),
                'free_cash_flow': info.get('freeCashflow', None)
            }
        except Exception as e:
            self.logger.error(f"재무 지표 추출 오류: {e}")
            return {}
    
    def _calculate_technical_indicators(self, hist) -> Dict:
        """기술적 지표 계산"""
        try:
            close = hist['Close']
            
            # RSI 계산
            rsi = self._calculate_rsi(close)
            
            # 이동평균
            ma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
            ma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
            
            # MACD
            macd_signal = self._calculate_macd_signal(close)
            
            # 볼린저 밴드
            bb_upper, bb_lower = self._calculate_bollinger_bands(close)
            
            return {
                'rsi': rsi,
                'ma_50': ma_50,
                'ma_200': ma_200,
                'macd_signal': macd_signal,
                'bb_upper': bb_upper,
                'bb_lower': bb_lower,
                'current_price': close.iloc[-1],
                'support_level': close.rolling(window=20).min().iloc[-1] if len(close) >= 20 else None,
                'resistance_level': close.rolling(window=20).max().iloc[-1] if len(close) >= 20 else None
            }
        except Exception as e:
            self.logger.error(f"기술적 지표 계산 오류: {e}")
            return {}
    
    def _calculate_rsi(self, prices, period=14) -> Optional[float]:
        """RSI 계산"""
        try:
            if len(prices) < period:
                return None
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1])
        except:
            return None
    
    def _calculate_macd_signal(self, prices) -> str:
        """MACD 신호 계산"""
        try:
            if len(prices) < 26:
                return 'neutral'
            
            ema_12 = prices.ewm(span=12, adjust=False).mean()
            ema_26 = prices.ewm(span=26, adjust=False).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9, adjust=False).mean()
            
            if macd.iloc[-1] > signal.iloc[-1]:
                return 'bullish'
            elif macd.iloc[-1] < signal.iloc[-1]:
                return 'bearish'
            else:
                return 'neutral'
        except:
            return 'neutral'
    
    def _calculate_bollinger_bands(self, prices, period=20) -> Tuple[Optional[float], Optional[float]]:
        """볼린저 밴드 계산"""
        try:
            if len(prices) < period:
                return None, None
            
            ma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper = ma + (std * 2)
            lower = ma - (std * 2)
            
            return float(upper.iloc[-1]), float(lower.iloc[-1])
        except:
            return None, None
    
    def _process_analyst_ratings(self, recommendations, info: Dict) -> Dict:
        """애널리스트 평가 처리"""
        try:
            ratings = {
                'strong_buy': 0,
                'buy': 0,
                'hold': 0,
                'sell': 0,
                'strong_sell': 0,
                'average_target': info.get('targetMeanPrice', None),
                'high_target': info.get('targetHighPrice', None),
                'low_target': info.get('targetLowPrice', None),
                'number_of_analysts': info.get('numberOfAnalystOpinions', 0)
            }
            
            # ⭐ None 체크
            if recommendations is None:
                self.logger.debug("recommendations가 None입니다")
                return ratings
            
            # ⭐ empty 체크
            if not hasattr(recommendations, 'empty'):
                self.logger.debug("recommendations가 DataFrame이 아닙니다")
                return ratings
                
            if recommendations.empty:
                self.logger.debug("recommendations가 비어있습니다")
                return ratings
            
            try:
                # ⭐ 최근 20개 레코드만 사용 (날짜 필터링 제거)
                recent = recommendations.tail(20)
                self.logger.debug(f"애널리스트 추천 데이터: {len(recent)}개 레코드")
                
                # 컬럼별로 집계
                if hasattr(recent, 'columns') and recent.columns is not None:
                    for col in recent.columns:
                        try:
                            col_lower = str(col).lower()
                            col_sum = recent[col].sum()
                            
                            # 정수로 변환 가능한지 확인
                            if pd.notna(col_sum):
                                col_sum = int(col_sum)
                            else:
                                continue
                            
                            if 'strong buy' in col_lower or 'strongbuy' in col_lower:
                                ratings['strong_buy'] += col_sum
                            elif 'buy' in col_lower and 'strong' not in col_lower:
                                ratings['buy'] += col_sum
                            elif 'hold' in col_lower:
                                ratings['hold'] += col_sum
                            elif 'strong sell' in col_lower or 'strongsell' in col_lower:
                                ratings['strong_sell'] += col_sum
                            elif 'sell' in col_lower and 'strong' not in col_lower:
                                ratings['sell'] += col_sum
                                
                        except (ValueError, TypeError, AttributeError) as col_error:
                            self.logger.debug(f"컬럼 {col} 처리 중 오류: {col_error}")
                            continue
                
            except Exception as processing_error:
                self.logger.warning(f"추천 데이터 처리 중 오류: {processing_error}")
            
            return ratings
            
        except Exception as e:
            self.logger.error(f"애널리스트 평가 처리 오류: {e}")
            # 오류 발생 시 기본값 반환
            return {
                'strong_buy': 0,
                'buy': 0,
                'hold': 0,
                'sell': 0,
                'strong_sell': 0,
                'average_target': info.get('targetMeanPrice') if info else None,
                'high_target': info.get('targetHighPrice') if info else None,
                'low_target': info.get('targetLowPrice') if info else None,
                'number_of_analysts': info.get('numberOfAnalystOpinions', 0) if info else 0
            }
    
    def _calculate_risk_metrics(self, hist, info: Dict) -> Dict:
        """리스크 지표 계산"""
        try:
            returns = hist['Close'].pct_change().dropna()
            
            # 베타
            beta = info.get('beta', None)
            
            # 변동성 (30일)
            volatility_30d = returns.iloc[-30:].std() * (252 ** 0.5) if len(returns) >= 30 else None
            
            # 샤프 비율 (간단 계산, 무위험 수익률 2% 가정)
            if volatility_30d and volatility_30d > 0:
                avg_return = returns.iloc[-30:].mean() * 252 if len(returns) >= 30 else 0
                sharpe_ratio = (avg_return - 0.02) / volatility_30d
            else:
                sharpe_ratio = None
            
            # 최대 낙폭
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                'beta': beta,
                'volatility_30d': volatility_30d,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95': returns.quantile(0.05) if len(returns) > 0 else None  # Value at Risk
            }
        except Exception as e:
            self.logger.error(f"리스크 지표 계산 오류: {e}")
            return {}
    
    def _determine_trend(self, values) -> str:
        """트렌드 판단"""
        try:
            if len(values) < 3:
                return 'stable'
            
            first_half = values[:len(values)//2].mean()
            second_half = values[len(values)//2:].mean()
            
            change = (second_half - first_half) / first_half
            
            if change > 0.1:
                return 'increasing'
            elif change < -0.1:
                return 'decreasing'
            else:
                return 'stable'
        except:
            return 'stable'
    
    def _analyze_stock_simulation(self, ticker: str, company: str) -> Dict:
        """시뮬레이션 데이터 (yfinance 사용 불가 시)"""
        import random
        
        base_price = random.uniform(10, 300)
        
        return {
            'company': company,
            'ticker': ticker,
            'current_price': base_price * (1 + random.uniform(-0.05, 0.05)),
            'currency': 'USD',
            'price_history': {
                '1d_change': random.uniform(-0.05, 0.05),
                '1w_change': random.uniform(-0.10, 0.10),
                '1m_change': random.uniform(-0.15, 0.15),
                '3m_change': random.uniform(-0.25, 0.25),
                '1y_change': random.uniform(-0.30, 0.50),
                'ytd_change': random.uniform(-0.20, 0.40)
            },
            'volume': {
                'current_volume': random.randint(10000000, 100000000),
                'avg_volume_3m': random.randint(10000000, 100000000)
            },
            'financials': {
                'market_cap': base_price * random.randint(100000000, 1000000000),
                'pe_ratio': random.uniform(15, 100),
                'revenue_growth': random.uniform(-0.1, 0.5)
            },
            'data_source': 'simulation'
        }
    
    async def _analyze_sector_performance(self, stocks_data: Dict) -> Dict:
        """섹터 성과 분석"""
        try:
            sector_performance = {}
            
            for ticker, data in stocks_data.items():
                sector = data.get('sector', 'Unknown')
                if sector not in sector_performance:
                    sector_performance[sector] = {
                        'stocks': [],
                        'avg_return_1y': 0,
                        'count': 0
                    }
                
                sector_performance[sector]['stocks'].append(ticker)
                sector_performance[sector]['avg_return_1y'] += data.get('price_history', {}).get('1y_change', 0)
                sector_performance[sector]['count'] += 1
            
            # 평균 계산
            for sector, data in sector_performance.items():
                if data['count'] > 0:
                    data['avg_return_1y'] /= data['count']
            
            return sector_performance
        except Exception as e:
            self.logger.error(f"섹터 분석 오류: {e}")
            return {}
    
    def _analyze_correlations(self, stocks_data: Dict) -> Dict:
        """상관관계 분석 (간단 버전)"""
        try:
            # 1년 수익률 기반 상관관계
            tickers = list(stocks_data.keys())
            returns = {
                ticker: data.get('price_history', {}).get('1y_change', 0)
                for ticker, data in stocks_data.items()
            }
            
            return {
                'note': '상관관계 분석은 실제 구현 시 pandas로 계산',
                'returns': returns
            }
        except Exception as e:
            self.logger.error(f"상관관계 분석 오류: {e}")
            return {}
    
    def _calculate_valuation_metrics(self, stocks_data: Dict) -> Dict:
        """밸류에이션 지표 계산"""
        try:
            pe_ratios = []
            ps_ratios = []
            pb_ratios = []
            
            for data in stocks_data.values():
                financials = data.get('financials', {})
                
                pe = financials.get('pe_ratio')
                if pe and pe > 0:
                    pe_ratios.append(pe)
                
                ps = financials.get('ps_ratio')
                if ps and ps > 0:
                    ps_ratios.append(ps)
                
                pb = financials.get('pb_ratio')
                if pb and pb > 0:
                    pb_ratios.append(pb)
            
            return {
                'avg_pe': sum(pe_ratios) / len(pe_ratios) if pe_ratios else None,
                'median_pe': sorted(pe_ratios)[len(pe_ratios)//2] if pe_ratios else None,
                'avg_ps': sum(ps_ratios) / len(ps_ratios) if ps_ratios else None,
                'avg_pb': sum(pb_ratios) / len(pb_ratios) if pb_ratios else None,
                'sample_size': len(stocks_data)
            }
        except Exception as e:
            self.logger.error(f"밸류에이션 지표 계산 오류: {e}")
            return {}
    
    def _analyze_market_sentiment(self, stocks_data: Dict) -> Dict:
        """시장 감성 분석"""
        try:
            positive = 0
            negative = 0
            neutral = 0
            
            for data in stocks_data.values():
                change_1m = data.get('price_history', {}).get('1m_change', 0)
                
                if change_1m > 0.05:
                    positive += 1
                elif change_1m < -0.05:
                    negative += 1
                else:
                    neutral += 1
            
            total = positive + negative + neutral
            
            return {
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'positive_ratio': positive / total if total > 0 else 0,
                'sentiment': 'bullish' if positive > negative else 'bearish' if negative > positive else 'neutral'
            }
        except Exception as e:
            self.logger.error(f"시장 감성 분석 오류: {e}")
            return {}
    
    async def _generate_investment_insights(self, stocks_data: Dict, 
                                           sector_analysis: Dict,
                                           valuation_metrics: Dict) -> str:
        """투자 인사이트 생성"""
        if not self.llm:
            return "투자 인사이트 생성 불가 (LLM 미설정)"
        
        try:
            # 상위 5개 주식 요약
            top_performers = sorted(
                stocks_data.items(),
                key=lambda x: x[1].get('price_history', {}).get('1y_change', 0),
                reverse=True
            )[:5]
            
            performers_text = "\n".join([
                f"- {ticker} ({data['company']}): 1년 수익률 {data['price_history']['1y_change']*100:.1f}%, "
                f"P/E {data.get('financials', {}).get('pe_ratio', 'N/A')}"
                for ticker, data in top_performers
            ])
            
            prompt = f"""전기차 관련 주식들의 분석 결과를 바탕으로 투자 인사이트를 제공하세요:

**상위 수익률 종목:**
{performers_text}

**밸류에이션:**
- 평균 P/E: {valuation_metrics.get('avg_pe', 'N/A')}
- 평균 P/S: {valuation_metrics.get('avg_ps', 'N/A')}

**분석 종목 수:** {len(stocks_data)}개

다음 내용을 포함하여 작성하세요:
1. 전반적인 섹터 전망 (3-4문장)
2. 주목할 만한 종목과 그 이유 (3-4문장)
3. 밸류에이션 관점에서의 평가 (2-3문장)
4. 투자 시 주의사항 (2-3문장)

한국어로 작성하세요."""
            
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            self.logger.error(f"투자 인사이트 생성 오류: {e}")
            return "투자 인사이트 생성 중 오류 발생"