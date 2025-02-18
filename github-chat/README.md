This project leverages GitIngest to parse a GitHub repo in markdown format and the use LlamaIndex for RAG orchestration over it.


## Installation and setup

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install gitingest llama-index llama-index-llms-ollama llama-index-agent-openai llama-index-llms-openai --upgrade --quiet
   ```

**Running**:

Make sure you have Ollama Server running then you can run following command to start the streamlit application ```streamlit run app_local.py```.

## Docker Setup

```bash
# Build the Docker image
docker build -t github-chat .

# Run the container
docker run -p 8501:8501 --env-file .env github-chat

# Or using docker-compose
docker-compose up
```

> **Note:** Ensure your `.env` file contains:
> - GITHUB_TOKEN
> - OPENAI_API_KEY (if using OpenAI models)
