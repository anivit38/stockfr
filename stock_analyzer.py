import yfinance as yf
import math
from fredapi import Fred

class StockAnalyzer:
    def __init__(self, fred_api_key):
        self.stock_rating = 0
        self.user_intent = None  # To store the user's intention (buy or sell)
        self.fred = Fred(api_key=fred_api_key)  # Initialize the FRED API with your key

    def get_stock_data(self, symbol):
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if data.empty:
            return None
        latest_data = data.iloc[-1]
        info = stock.info

        return {
            'volume': latest_data['Volume'],
            'current_price': latest_data['Close'],
            'pe_ratio': info.get('trailingPE', None),
            'pb_ratio': info.get('priceToBook', None),
            'dividend_yield': info.get('dividendYield', None),
            'earnings_growth': info.get('earningsQuarterlyGrowth', None),
            'debt_ratio': info.get('debtToEquity', None),
            'rsi': None,  # Not provided by yfinance
            'avg_50_days': stock.history(period="1y")['Close'].mean(),
            'avg_200_days': stock.history(period="1y")['Close'].mean(),
            'interest_rates': self.get_interest_rate(),  # Fetch interest rate from FRED
            'unemployment_rate': self.get_unemployment_rate(),  # Fetch unemployment rate from FRED
            'gdp_growth': self.get_gdp_growth(),  # Fetch GDP growth from FRED
            'sentiment_score': None,  # Not provided by yfinance
            'insider_actions': None,  # Not provided by yfinance
            'value_score': None,  # Not provided by yfinance
            'growth_score': None,  # Not provided by yfinance
        }

    def get_interest_rate(self):
        try:
            return self.fred.get_series('DFF').iloc[-1] / 100  # Effective Federal Funds Rate
        except Exception as e:
            print(f"Error fetching interest rate: {e}")
            return None

    def get_unemployment_rate(self):
        try:
            return self.fred.get_series('UNRATE').iloc[-1] / 100  # Unemployment Rate
        except Exception as e:
            print(f"Error fetching unemployment rate: {e}")
            return None

    def get_gdp_growth(self):
        try:
            return self.fred.get_series('A191RL1Q225SBEA').iloc[-1] / 100  # Real GDP Growth Rate
        except Exception as e:
            print(f"Error fetching GDP growth: {e}")
            return None

    def set_user_intent(self, intent):
        self.user_intent = intent.lower()

    def volume_analysis(self, volume, avg_volume):
        if volume and avg_volume:
            if volume > avg_volume * 1.1:
                self.stock_rating += 2
            elif volume < avg_volume * 0.9:
                self.stock_rating -= 2

    def pe_ratio_analysis(self, pe_ratio):
        if pe_ratio:
            if 10 <= pe_ratio <= 20:
                self.stock_rating += 2
            elif pe_ratio > 20:
                self.stock_rating -= 1

    def pb_ratio_analysis(self, pb_ratio):
        if pb_ratio:
            if 0 < pb_ratio < 1:
                self.stock_rating += 2
            elif pb_ratio > 3:
                self.stock_rating -= 2

    def dividend_yield_analysis(self, dividend_yield):
        if dividend_yield:
            if dividend_yield > 0.05:
                self.stock_rating += 2

    def earnings_growth_analysis(self, earnings_growth):
        if earnings_growth:
            if earnings_growth > 0.05:
                self.stock_rating += 2

    def debt_equity_analysis(self, debt_ratio):
        if debt_ratio:
            if 0 <= debt_ratio <= 0.5:
                self.stock_rating += 2
            elif debt_ratio > 0.7:
                self.stock_rating -= 2

    def rsi_analysis(self, rsi):
        if rsi:
            if rsi > 70:
                self.stock_rating -= 2
            elif rsi < 30:
                self.stock_rating += 2

    def moving_average_analysis(self, current_price, avg_50_days, avg_200_days):
        if current_price and avg_50_days and avg_200_days:
            if current_price > avg_50_days > avg_200_days:
                self.stock_rating += 2
            elif current_price < avg_50_days < avg_200_days:
                self.stock_rating -= 2

    def economic_data_analysis(self, interest_rates, unemployment_rate, gdp_growth):
        if interest_rates is not None and interest_rates < 0.03:
            self.stock_rating += 1
        if unemployment_rate is not None and unemployment_rate < 0.05:
            self.stock_rating += 1
        if gdp_growth is not None and gdp_growth > 0.03:
            self.stock_rating += 1

    def sentiment_analysis(self, sentiment_score):
        if sentiment_score is not None:
            self.stock_rating += math.floor(sentiment_score * 5)

    def insider_trading_analysis(self, insider_actions):
        if insider_actions:
            if insider_actions == 'buy':
                self.stock_rating += 2
            elif insider_actions == 'sell':
                self.stock_rating -= 2

    def value_vs_growth(self, value_score, growth_score):
        if value_score is not None:
            self.stock_rating += math.floor(value_score * 5)
        if growth_score is not None:
            self.stock_rating += math.floor(growth_score * 5)

    def perform_analysis(self, stock_data):
        self.volume_analysis(stock_data['volume'], stock_data['avg_50_days'])  # Assume avg_volume is close to avg_50_days for simplicity
        self.pe_ratio_analysis(stock_data['pe_ratio'])
        self.pb_ratio_analysis(stock_data['pb_ratio'])
        self.dividend_yield_analysis(stock_data['dividend_yield'])
        self.earnings_growth_analysis(stock_data['earnings_growth'])
        self.debt_equity_analysis(stock_data['debt_ratio'])
        self.rsi_analysis(stock_data['rsi'])
        self.moving_average_analysis(stock_data['current_price'], stock_data['avg_50_days'], stock_data['avg_200_days'])
        self.economic_data_analysis(stock_data['interest_rates'], stock_data['unemployment_rate'], stock_data['gdp_growth'])
        self.sentiment_analysis(stock_data['sentiment_score'])
        self.insider_trading_analysis(stock_data['insider_actions'])
        self.value_vs_growth(stock_data['value_score'], stock_data['growth_score'])

    def evaluate_stock(self):
        rating = self.stock_rating
        movement = "likely to go up" if rating > 0 else "likely to go down" if rating < 0 else "movement is uncertain"

        if self.user_intent == 'buy':
            if rating >= 25:
                advice = "Very Good Stock to Buy"
            elif 15 <= rating < 25:
                advice = "Good Stock to Buy"
            elif 5 <= rating < 15:
                advice = "Okay Stock to Buy"
            elif -5 <= rating < 5:
                advice = "Neutral Stock"
            else:
                advice = "Bad Stock to Buy"
        elif self.user_intent == 'sell':
            if rating < 0:
                advice = "Sell the Stock"
            else:
                advice = "Hold the Stock"

        return advice, movement
