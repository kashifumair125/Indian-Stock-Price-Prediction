"""
Demo Script for Advanced Stock Prediction Features
Showcases: Advanced Technical Indicators, Ensemble Models, Real-Time Data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Import our new modules
from advanced_indicators import AdvancedTechnicalIndicators
from ensemble_models import EnsembleModels
from realtime_data import RealTimeDataFeed, RealTimeAnalyzer

def demo_advanced_indicators():
    """Demo advanced technical indicators"""
    print("🚀 Demo: Advanced Technical Indicators")
    print("=" * 50)
    
    # Get sample data
    import yfinance as yf
    stock = yf.Ticker("TCS.NS")
    data = stock.history(period="1y")
    
    print(f"📊 Analyzing {len(data)} days of data for TCS")
    
    # Initialize advanced indicators
    indicators = AdvancedTechnicalIndicators(data)
    
    # Calculate all indicators
    results = indicators.get_all_indicators()
    
    print("\n📈 Results Summary:")
    print(f"   • Fractal Dimension: {results['fractal_dimension'].dropna().mean():.4f}")
    
    if 'market_regime' in results:
        regime_counts = results['market_regime'].value_counts()
        print(f"   • Market Regimes: {len(regime_counts)} detected")
        for regime, count in regime_counts.items():
            print(f"     - {regime}: {count} periods")
    
    if 'composite_sentiment' in results:
        sentiment = results['composite_sentiment'].dropna()
        print(f"   • Sentiment Score: {sentiment.mean():.3f} (range: {sentiment.min():.3f} to {sentiment.max():.3f})")
    
    # Plot indicators
    try:
        fig = indicators.plot_indicators()
        plt.show()
        print("   ✅ Charts displayed successfully")
    except Exception as e:
        print(f"   ❌ Error displaying charts: {e}")
    
    return results

def demo_ensemble_models():
    """Demo ensemble models"""
    print("\n🤖 Demo: Ensemble Models")
    print("=" * 50)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Generate synthetic stock-like data
    X = np.random.randn(n_samples, n_features)
    # Create target with some relationship to features
    y = (X[:, 0] * 0.3 + X[:, 1] * 0.2 + X[:, 2] * 0.1 + 
         np.random.randn(n_samples) * 0.1)
    
    # Split data
    split_idx = int(0.8 * n_samples)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"📊 Training on {len(X_train)} samples, testing on {len(X_test)} samples")
    
    # Initialize ensemble models
    ensemble = EnsembleModels(X_train, y_train, X_test, y_test)
    
    # Train base models
    print("\n🔄 Training base models...")
    base_metrics = ensemble.train_base_models()
    
    # Create voting ensemble
    print("\n🔄 Creating voting ensemble...")
    voting_model = ensemble.create_voting_ensemble()
    
    # Create stacking ensemble
    print("\n🔄 Creating stacking ensemble...")
    stacking_model = ensemble.create_stacking_ensemble()
    
    # Create weighted ensemble
    print("\n🔄 Creating weighted ensemble...")
    weighted_pred = ensemble.create_weighted_ensemble()
    
    # Get summary
    summary = ensemble.get_ensemble_summary()
    print("\n📊 Model Performance Summary:")
    print(summary.round(4))
    
    # Cross-validate best ensemble
    best_model = summary.index[0]
    print(f"\n🔄 Cross-validating best model: {best_model}")
    cv_scores = ensemble.cross_validate_ensemble(best_model)
    
    return ensemble, summary

def demo_realtime_data():
    """Demo real-time data feed"""
    print("\n⚡ Demo: Real-Time Data Feed")
    print("=" * 50)
    
    # Initialize real-time data feed
    symbols = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS']
    data_feed = RealTimeDataFeed(symbols=symbols, update_interval=2)
    
    # Initialize real-time analyzer
    analyzer = RealTimeAnalyzer(data_feed)
    
    # Start simulated feed
    print("🔄 Starting simulated real-time feed...")
    data_feed.start_simulated_feed()
    
    # Monitor for a few updates
    print("📊 Monitoring real-time data for 10 seconds...")
    import time
    
    for i in range(5):  # 5 updates
        time.sleep(2)
        
        # Get latest data
        latest_data = data_feed.get_all_data()
        if not latest_data.empty:
            print(f"\n📈 Update {i+1}:")
            print(latest_data[['price', 'change_pct', 'volume']].round(2))
        
        # Get analysis summary
        analysis = analyzer.get_analysis_summary()
        if analysis:
            print("   📊 Analysis:")
            for symbol, metrics in analysis.items():
                if metrics:
                    print(f"     {symbol}: RSI={metrics.get('rsi', 'N/A'):.1f}, "
                          f"Trend={metrics.get('trend', 'N/A')}")
        
        # Check for alerts
        alerts = analyzer.get_alerts(limit=3)
        if alerts:
            print("   🚨 Recent Alerts:")
            for alert in alerts:
                print(f"     {alert['symbol']}: {alert['alert_type']}")
    
    # Stop the feed
    data_feed.stop_feed()
    
    # Export sample data
    for symbol in symbols[:1]:  # Export first symbol only
        filename = analyzer.export_data(symbol)
        if filename:
            print(f"\n💾 Data exported to: {filename}")
    
    return data_feed, analyzer

def demo_integration():
    """Demo integration of all features"""
    print("\n🔗 Demo: Feature Integration")
    print("=" * 50)
    
    # Get sample data
    import yfinance as yf
    stock = yf.Ticker("RELIANCE.NS")
    data = stock.history(period="6mo")
    
    print(f"📊 Integrated analysis for RELIANCE.NS ({len(data)} days)")
    
    # 1. Advanced Indicators
    print("\n1️⃣ Calculating Advanced Indicators...")
    indicators = AdvancedTechnicalIndicators(data)
    indicator_results = indicators.get_all_indicators()
    
    # 2. Prepare data for ensemble models
    print("\n2️⃣ Preparing Data for Ensemble Models...")
    # Create features from indicators
    features = pd.DataFrame()
    
    # Price-based features
    features['returns'] = data['Close'].pct_change()
    features['volatility'] = features['returns'].rolling(20).std()
    features['volume_ratio'] = data['Volume'] / data['Volume'].rolling(20).mean()
    
    # Add indicator features
    if 'fractal_dimension' in indicator_results:
        features['fractal_dim'] = indicator_results['fractal_dimension']
    
    if 'composite_sentiment' in indicator_results:
        features['sentiment'] = indicator_results['composite_sentiment']
    
    # Clean data
    features = features.dropna()
    
    # Create target (next day's return)
    target = features['returns'].shift(-1).dropna()
    features = features[:-1]  # Remove last row (no target)
    
    # Align data
    features = features.loc[target.index]
    
    print(f"   ✅ Created {len(features)} features for {len(target)} targets")
    
    # 3. Train Ensemble Models
    print("\n3️⃣ Training Ensemble Models...")
    split_idx = int(0.8 * len(features))
    X_train, X_test = features[:split_idx], features[split_idx:]
    y_train, y_test = target[:split_idx], target[split_idx:]
    
    ensemble = EnsembleModels(X_train, y_train, X_test, y_test)
    ensemble.train_base_models()
    ensemble.create_voting_ensemble()
    ensemble.create_stacking_ensemble()
    
    # 4. Get Results
    summary = ensemble.get_ensemble_summary()
    print("\n📊 Integrated Analysis Results:")
    print(summary.round(4))
    
    # 5. Real-time Integration
    print("\n4️⃣ Setting up Real-time Integration...")
    realtime_feed = RealTimeDataFeed(symbols=['RELIANCE.NS'], update_interval=5)
    realtime_analyzer = RealTimeAnalyzer(realtime_feed)
    
    print("   ✅ Real-time system ready for live data")
    
    return {
        'indicators': indicator_results,
        'ensemble': ensemble,
        'realtime': realtime_feed,
        'summary': summary
    }

def main():
    """Run all demos"""
    print("🎯 Advanced Stock Prediction Features Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Advanced Technical Indicators
        indicator_results = demo_advanced_indicators()
        
        # Demo 2: Ensemble Models
        ensemble, summary = demo_ensemble_models()
        
        # Demo 3: Real-time Data
        data_feed, analyzer = demo_realtime_data()
        
        # Demo 4: Integration
        integration_results = demo_integration()
        
        print("\n🎉 All demos completed successfully!")
        print("\n📋 Summary of Features:")
        print("   ✅ Advanced Technical Indicators (Fractal, Regimes, Sentiment)")
        print("   ✅ Ensemble Models (Voting, Stacking, Weighted)")
        print("   ✅ Real-time Data Feed (WebSocket + Simulated)")
        print("   ✅ Real-time Analysis & Alerts")
        print("   ✅ Feature Integration & Pipeline")
        
        print("\n🚀 Ready to use in production!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

