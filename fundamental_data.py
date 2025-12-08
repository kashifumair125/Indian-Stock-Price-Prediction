"""
Fundamental Data Analysis Module
Fetches and analyzes fundamental data for stocks
"""
import yfinance as yf
import pandas as pd

class FundamentalAnalyzer:
    def __init__(self, symbol):
        """
        Initialize fundamental analyzer

        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
        self.info = {}
        self.financials = {}

    def fetch_fundamental_data(self):
        """Fetch all fundamental data"""
        try:
            self.info = self.ticker.info
            return self.info
        except Exception as e:
            print(f"Error fetching fundamental data: {e}")
            return {}

    def get_key_metrics(self):
        """
        Get key fundamental metrics

        Returns:
            dict with key metrics
        """
        if not self.info:
            self.fetch_fundamental_data()

        metrics = {
            # Valuation Ratios
            'P/E Ratio': self.info.get('trailingPE', 'N/A'),
            'Forward P/E': self.info.get('forwardPE', 'N/A'),
            'P/B Ratio': self.info.get('priceToBook', 'N/A'),
            'P/S Ratio': self.info.get('priceToSalesTrailing12Months', 'N/A'),
            'PEG Ratio': self.info.get('pegRatio', 'N/A'),

            # Profitability
            'Profit Margin': self._format_pct(self.info.get('profitMargins')),
            'Operating Margin': self._format_pct(self.info.get('operatingMargins')),
            'ROE': self._format_pct(self.info.get('returnOnEquity')),
            'ROA': self._format_pct(self.info.get('returnOnAssets')),

            # Growth
            'Revenue Growth': self._format_pct(self.info.get('revenueGrowth')),
            'Earnings Growth': self._format_pct(self.info.get('earningsGrowth')),

            # Financial Health
            'Current Ratio': self.info.get('currentRatio', 'N/A'),
            'Quick Ratio': self.info.get('quickRatio', 'N/A'),
            'Debt/Equity': self.info.get('debtToEquity', 'N/A'),

            # Dividend
            'Dividend Yield': self._format_pct(self.info.get('dividendYield')),
            'Payout Ratio': self._format_pct(self.info.get('payoutRatio')),

            # Market Data
            'Market Cap': self._format_number(self.info.get('marketCap')),
            'Enterprise Value': self._format_number(self.info.get('enterpriseValue')),
            'Beta': self.info.get('beta', 'N/A'),

            # Analyst Data
            'Target Price': self.info.get('targetMeanPrice', 'N/A'),
            'Recommendation': self.info.get('recommendationKey', 'N/A'),
        }

        return metrics

    def get_company_profile(self):
        """Get company profile information"""
        if not self.info:
            self.fetch_fundamental_data()

        profile = {
            'Company Name': self.info.get('longName', 'N/A'),
            'Sector': self.info.get('sector', 'N/A'),
            'Industry': self.info.get('industry', 'N/A'),
            'Country': self.info.get('country', 'N/A'),
            'Website': self.info.get('website', 'N/A'),
            'Business Summary': self.info.get('longBusinessSummary', 'No description available')[:500] + '...',
            'Full Time Employees': self._format_number(self.info.get('fullTimeEmployees')),
        }

        return profile

    def get_financial_highlights(self):
        """Get financial highlights"""
        if not self.info:
            self.fetch_fundamental_data()

        highlights = {
            # Income Statement
            'Revenue (TTM)': self._format_currency(self.info.get('totalRevenue')),
            'Net Income (TTM)': self._format_currency(self.info.get('netIncomeToCommon')),
            'EPS (TTM)': self.info.get('trailingEps', 'N/A'),
            'EBITDA': self._format_currency(self.info.get('ebitda')),

            # Balance Sheet
            'Total Cash': self._format_currency(self.info.get('totalCash')),
            'Total Debt': self._format_currency(self.info.get('totalDebt')),
            'Total Assets': self._format_currency(self.info.get('totalAssets')),
            'Total Equity': self._format_currency(self.info.get('totalStockholderEquity')),

            # Cash Flow
            'Operating Cash Flow': self._format_currency(self.info.get('operatingCashflow')),
            'Free Cash Flow': self._format_currency(self.info.get('freeCashflow')),
        }

        return highlights

    def get_analyst_recommendations(self):
        """Get analyst recommendations"""
        try:
            recommendations = self.ticker.recommendations
            if recommendations is not None and not recommendations.empty:
                # Get latest recommendations
                recent = recommendations.tail(10)
                return recent
        except:
            pass
        return pd.DataFrame()

    def get_valuation_grade(self):
        """
        Calculate a simple valuation grade

        Returns:
            dict with grade and explanation
        """
        if not self.info:
            self.fetch_fundamental_data()

        score = 0
        max_score = 0
        reasons = []

        # P/E Ratio check
        pe = self.info.get('trailingPE')
        if pe:
            max_score += 1
            if pe < 15:
                score += 1
                reasons.append("✅ P/E Ratio < 15 (Undervalued)")
            elif pe > 30:
                reasons.append("⚠️ P/E Ratio > 30 (Overvalued)")
            else:
                score += 0.5
                reasons.append("📊 P/E Ratio is moderate")

        # P/B Ratio check
        pb = self.info.get('priceToBook')
        if pb:
            max_score += 1
            if pb < 1.5:
                score += 1
                reasons.append("✅ P/B Ratio < 1.5 (Good value)")
            elif pb > 3:
                reasons.append("⚠️ P/B Ratio > 3 (Expensive)")
            else:
                score += 0.5

        # Debt/Equity check
        de = self.info.get('debtToEquity')
        if de:
            max_score += 1
            if de < 1:
                score += 1
                reasons.append("✅ Low debt (D/E < 1)")
            elif de > 2:
                reasons.append("⚠️ High debt (D/E > 2)")
            else:
                score += 0.5

        # ROE check
        roe = self.info.get('returnOnEquity')
        if roe:
            max_score += 1
            if roe > 0.15:
                score += 1
                reasons.append("✅ Strong ROE (> 15%)")
            elif roe < 0.05:
                reasons.append("⚠️ Weak ROE (< 5%)")
            else:
                score += 0.5

        # Calculate grade
        if max_score > 0:
            grade_pct = (score / max_score) * 100
        else:
            grade_pct = 50

        if grade_pct >= 80:
            grade = 'A'
            color = 'green'
            label = 'Strong Buy'
        elif grade_pct >= 60:
            grade = 'B'
            color = 'lightgreen'
            label = 'Buy'
        elif grade_pct >= 40:
            grade = 'C'
            color = 'yellow'
            label = 'Hold'
        elif grade_pct >= 20:
            grade = 'D'
            color = 'orange'
            label = 'Sell'
        else:
            grade = 'F'
            color = 'red'
            label = 'Strong Sell'

        return {
            'grade': grade,
            'score': grade_pct,
            'label': label,
            'color': color,
            'reasons': reasons
        }

    def _format_pct(self, value):
        """Format percentage value"""
        if value is None or value == 'N/A':
            return 'N/A'
        try:
            return f"{float(value) * 100:.2f}%"
        except:
            return 'N/A'

    def _format_number(self, value):
        """Format large numbers"""
        if value is None or value == 'N/A':
            return 'N/A'
        try:
            value = float(value)
            if value >= 1e12:
                return f"{value/1e12:.2f}T"
            elif value >= 1e9:
                return f"{value/1e9:.2f}B"
            elif value >= 1e6:
                return f"{value/1e6:.2f}M"
            elif value >= 1e3:
                return f"{value/1e3:.2f}K"
            else:
                return f"{value:.2f}"
        except:
            return 'N/A'

    def _format_currency(self, value):
        """Format currency value"""
        if value is None or value == 'N/A':
            return 'N/A'
        try:
            formatted = self._format_number(value)
            return f"₹{formatted}" if formatted != 'N/A' else 'N/A'
        except:
            return 'N/A'

    def compare_peers(self, peer_symbols):
        """
        Compare with peer companies

        Args:
            peer_symbols: List of peer stock symbols

        Returns:
            DataFrame with comparison
        """
        comparison_data = []

        # Add current stock
        current_metrics = {
            'Symbol': self.symbol,
            'P/E': self.info.get('trailingPE', 'N/A'),
            'P/B': self.info.get('priceToBook', 'N/A'),
            'ROE': self._format_pct(self.info.get('returnOnEquity')),
            'Debt/Equity': self.info.get('debtToEquity', 'N/A'),
            'Dividend Yield': self._format_pct(self.info.get('dividendYield')),
        }
        comparison_data.append(current_metrics)

        # Add peers
        for peer in peer_symbols:
            try:
                peer_ticker = yf.Ticker(peer)
                peer_info = peer_ticker.info

                peer_metrics = {
                    'Symbol': peer,
                    'P/E': peer_info.get('trailingPE', 'N/A'),
                    'P/B': peer_info.get('priceToBook', 'N/A'),
                    'ROE': self._format_pct(peer_info.get('returnOnEquity')),
                    'Debt/Equity': peer_info.get('debtToEquity', 'N/A'),
                    'Dividend Yield': self._format_pct(peer_info.get('dividendYield')),
                }
                comparison_data.append(peer_metrics)
            except:
                continue

        return pd.DataFrame(comparison_data)
