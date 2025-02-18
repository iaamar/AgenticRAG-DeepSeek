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
    llama-index-llms-cleanlab \
    llama-index \
    llama-index-embeddings-huggingface \
    python-dotenv \
    python-pptx \
    streamlit

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8502
EXPOSE 8502

CMD ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"] 