import yfinance as yf
from icecream import ic
import numpy as np
from typing import Dict, Tuple, Optional
import streamlit as st

# Friendly labels for metrics
METRIC_LABELS = {
    'pe_ratio': 'P/E Ratio (Price to Earnings)',
    'pb_ratio': 'P/B Ratio (Price to Book)',
    'debt_to_equity': 'Debt to Equity Ratio',
    'current_ratio': 'Current Ratio (Liquidity)',
    'profit_margin': 'Profit Margins',
    'market_cap': 'Market Capitalization',
    'dividend_yield': 'Dividend Yield'
}

# Score description labels
SCORE_LABELS = {
    'pe': 'Price to Earnings Analysis',
    'pb': 'Price to Book Analysis',
    'debt': 'Debt Level Analysis',
    'liquidity': 'Liquidity Analysis',
    'profitability': 'Profitability Analysis',
    'size': 'Company Size Analysis'
}

# Constants for analysis thresholds
GOOD_PE_RATIO = 15.0
GOOD_PB_RATIO = 3.0
GOOD_DEBT_TO_EQUITY = 2.0
GOOD_CURRENT_RATIO = 1.5
GOOD_PROFIT_MARGIN = 0.10
MIN_MARKET_CAP = 1_000_000_000  # $1B minimum market cap

def get_fundamental_data(ticker: str) -> Dict:
    """
    Fetch fundamental data for a given stock ticker.
    Returns key financial metrics as a dictionary.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'pe_ratio': info.get('forwardPE', float('inf')),
            'pb_ratio': info.get('priceToBook', float('inf')),
            'debt_to_equity': info.get('debtToEquity', float('inf')),
            'current_ratio': info.get('currentRatio', 0.0),
            'profit_margin': info.get('profitMargins', 0.0),
            'market_cap': info.get('marketCap', 0.0),
            'dividend_yield': info.get('dividendYield', 0.0)
        }
    except Exception as e:
        ic(f"Error fetching data for {ticker}: {e}")
        return {}

def calculate_fundamental_score(metrics: Dict) -> Tuple[float, Dict[str, int]]:
    """
    Calculate a fundamental score based on various metrics.
    Returns a tuple of (overall_score, individual_scores).
    """
    scores = {}
    
    # Score each metric (1 for good, 0 for neutral, -1 for bad)
    scores['pe'] = 1 if metrics['pe_ratio'] < GOOD_PE_RATIO else \
                   (-1 if metrics['pe_ratio'] > GOOD_PE_RATIO * 2 else 0)
                   
    scores['pb'] = 1 if metrics['pb_ratio'] < GOOD_PB_RATIO else \
                   (-1 if metrics['pb_ratio'] > GOOD_PB_RATIO * 2 else 0)
                   
    scores['debt'] = 1 if metrics['debt_to_equity'] < GOOD_DEBT_TO_EQUITY else \
                     (-1 if metrics['debt_to_equity'] > GOOD_DEBT_TO_EQUITY * 1.5 else 0)
                     
    scores['liquidity'] = 1 if metrics['current_ratio'] > GOOD_CURRENT_RATIO else \
                         (-1 if metrics['current_ratio'] < 1.0 else 0)
                         
    scores['profitability'] = 1 if metrics['profit_margin'] > GOOD_PROFIT_MARGIN else \
                             (-1 if metrics['profit_margin'] < 0 else 0)
                             
    scores['size'] = 1 if metrics['market_cap'] > MIN_MARKET_CAP else -1

    # Calculate overall score
    total_score = sum(scores.values()) / len(scores)
    
    return total_score, scores

def get_recommendation(score: float) -> str:
    """
    Convert a fundamental score into a buy/hold/sell recommendation.
    """
    if score >= 0.5:
        return "BUY"
    elif score <= -0.3:
        return "SELL"
    else:
        return "HOLD"

def analyze_stock(ticker: str) -> Optional[Dict]:
    """
    Perform complete fundamental analysis on a stock and return results.
    """
    ic(f"Analyzing {ticker}")
    
    # Get fundamental data
    metrics = get_fundamental_data(ticker)
    if not metrics:
        return None
        
    # Calculate scores
    overall_score, individual_scores = calculate_fundamental_score(metrics)
    recommendation = get_recommendation(overall_score)
    
    analysis_results = {
        'ticker': ticker,
        'metrics': metrics,
        'scores': individual_scores,
        'overall_score': overall_score,
        'recommendation': recommendation
    }
    
    ic(analysis_results)
    return analysis_results

def create_streamlit_ui():
    """
    Create a Streamlit UI for stock analysis.
    """
    st.title("Stock Fundamental Analysis")
    
    ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()
    
    if st.button("Analyze"):
        results = analyze_stock(ticker)
        
        if results:
            st.header(f"Analysis Results for {ticker}")
            st.subheader(f"Recommendation: {results['recommendation']}")
            st.metric("Overall Score", f"{results['overall_score']:.2f}")
            
            st.subheader("Fundamental Metrics")
            metrics_df = {
                'Metric': [METRIC_LABELS[key] for key in results['metrics'].keys()],
                'Value': list(results['metrics'].values())
            }
            st.table(metrics_df)
            
            st.subheader("Individual Scores")
            scores_df = {
                'Analysis Type': [SCORE_LABELS[key] for key in results['scores'].keys()],
                'Score': list(results['scores'].values())
            }
            st.table(scores_df)
        else:
            st.error(f"Could not fetch data for {ticker}")

if __name__ == "__main__":
    create_streamlit_ui()
