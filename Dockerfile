# Dockerfile for Financial Event Tracker (Streamlit app)
# ---
# - Uses official Python image
# - Installs dependencies from requirements.txt
# - Sets up environment for Streamlit
# - Expects SUPABASE_URL and SUPABASE_KEY as environment variables (do not hardcode secrets)
# - Runs the Streamlit app

FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Set environment variables for Streamlit (optional, can be overridden)
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

# Command to run the Streamlit app
CMD ["streamlit", "run", "src/financial_tracker.py"]
