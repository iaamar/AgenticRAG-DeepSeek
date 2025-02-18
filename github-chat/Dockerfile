FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    gitingest \
    llama-index \
    llama-index-llms-ollama \
    llama-index-agent-openai \
    llama-index-llms-openai \
    streamlit

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 