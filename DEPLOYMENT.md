# 🚀 Deployment Guide

This guide will help you deploy the Indian Stock Price Prediction System to various platforms.

## 🌐 Streamlit Cloud (Recommended)

### **Step 1: Prepare Your Repository**
1. **Fork this repository** to your GitHub account
2. **Ensure all files are committed** and pushed to GitHub
3. **Verify the main file** is `web_app.py`

### **Step 2: Deploy to Streamlit Cloud**
1. **Visit [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub** and authorize Streamlit
3. **Click "New app"**
4. **Configure deployment**:
   - **Repository**: Select your forked repository
   - **Branch**: `main` (or your preferred branch)
   - **Main file path**: `web_app.py`
   - **App URL**: Choose a custom subdomain (optional)
5. **Click "Deploy"**

### **Step 3: Configure Environment**
1. **Go to your app settings** in Streamlit Cloud
2. **Set environment variables** (if needed):
   ```
   YAHOO_FINANCE_API_KEY=your_key_here
   ```
3. **Configure advanced settings**:
   - **Python version**: 3.9 or higher
   - **Memory**: 1GB or higher recommended
   - **Timeout**: 300 seconds

### **Step 4: Monitor & Update**
- **Check deployment logs** for any errors
- **Monitor app performance** and usage
- **Update automatically** when you push to GitHub

## 🐳 Docker Deployment

### **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_streamlit.txt .
RUN pip install --no-cache-dir -r requirements_streamlit.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Build and Run**
```bash
# Build Docker image
docker build -t stock-prediction .

# Run container
docker run -p 8501:8501 stock-prediction

# Or with docker-compose
docker-compose up -d
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  stock-prediction:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## ☁️ Cloud Platforms

### **Heroku**
1. **Create `Procfile`**:
   ```
   web: streamlit run web_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create `runtime.txt`**:
   ```
   python-3.9.18
   ```

3. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### **Google Cloud Run**
1. **Create `Dockerfile`** (use the one above)
2. **Deploy**:
   ```bash
   gcloud run deploy stock-prediction \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### **AWS App Runner**
1. **Create `Dockerfile`** (use the one above)
2. **Push to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
   docker tag stock-prediction:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/stock-prediction:latest
   docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/stock-prediction:latest
   ```

## 🔧 Environment Configuration

### **Required Environment Variables**
```bash
# Optional: Custom API keys
YAHOO_FINANCE_API_KEY=your_key_here

# Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### **Optional Environment Variables**
```bash
# Custom configuration
STOCK_PREDICTION_DEBUG=false
STOCK_PREDICTION_LOG_LEVEL=INFO
STOCK_PREDICTION_CACHE_TTL=300
```

## 📊 Performance Optimization

### **Streamlit Cloud Settings**
- **Memory**: 1GB minimum, 2GB recommended
- **Timeout**: 300 seconds for long-running predictions
- **Concurrency**: Enable for multiple users

### **Code Optimization**
- **Caching**: Use `@st.cache_data` for expensive operations
- **Lazy Loading**: Load models only when needed
- **Data Compression**: Compress large datasets

### **Monitoring**
- **Streamlit Cloud Analytics**: Built-in usage tracking
- **Custom Metrics**: Add performance monitoring
- **Error Tracking**: Implement error logging

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Import Errors**
```bash
# Ensure all dependencies are in requirements_streamlit.txt
pip install -r requirements_streamlit.txt
```

#### **2. Memory Issues**
```bash
# Reduce model complexity in config.py
LSTM_EPOCHS = 25  # Reduce from 50
LSTM_BATCH_SIZE = 16  # Reduce from 32
```

#### **3. Timeout Errors**
```bash
# Increase timeout in Streamlit Cloud settings
# Or optimize model training in config.py
```

#### **4. Data Loading Issues**
```bash
# Check internet connectivity for yfinance API
# Verify stock symbols are valid NSE symbols
```

### **Debug Mode**
```python
# Add to web_app.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use Streamlit's debug mode
st.set_option('deprecation.showPyplotGlobalUse', False)
```

## 🔄 Continuous Deployment

### **GitHub Actions**
```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Streamlit Cloud
        run: |
          echo "Deployment triggered by push to main branch"
```

### **Auto-update Strategy**
1. **Development branch**: `develop` for testing
2. **Main branch**: `main` for production
3. **Feature branches**: `feature/*` for new features
4. **Automatic deployment** on push to main

## 📱 Mobile Optimization

### **Responsive Design**
- **Mobile-first approach** in Streamlit components
- **Touch-friendly** interface elements
- **Optimized charts** for small screens

### **Performance on Mobile**
- **Reduced data loading** on mobile devices
- **Simplified charts** for better mobile experience
- **Caching strategies** for mobile networks

## 🔒 Security Considerations

### **API Security**
- **Rate limiting** for external API calls
- **Input validation** for stock symbols
- **Error handling** without exposing sensitive data

### **Data Privacy**
- **No user data storage** (stateless application)
- **Secure API calls** to financial data sources
- **HTTPS enforcement** in production

---

## 📞 Support

If you encounter deployment issues:

1. **Check the logs** in your deployment platform
2. **Verify dependencies** in requirements files
3. **Test locally** before deploying
4. **Open an issue** on GitHub with error details

**Happy Deploying! 🚀**
