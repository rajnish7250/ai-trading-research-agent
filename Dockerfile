FROM python:3.13-slim

WORKDIR /app

# Install lightweight frontend dependencies
COPY requirements.frontend.txt .

RUN pip install --no-cache-dir -r requirements.frontend.txt

# Copy only the Streamlit application
COPY streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]