# Trustworthy RAG over complex documents using TLM and LlamaParse

<video src="https://www.loom.com/embed/bf7df9ccda0c420ea907e436162db8d2?sid=852934f4-22a7-49b9-b640-f1651abae648" controls></video>

This project leverages Cleanlab's Trustworthy Language Model (TLM) for reliable document analysis with confidence scoring, combined with LlamaParse's advanced document parsing capabilities to process complex legal documents into structured markdown format.

Before you begin, obtain your API keys:
- [LlamaParse API Key](https://docs.cloud.llamaindex.ai/llamacloud/getting_started/api_key)
- [Cleanlab TLM API Key](https://tlm.cleanlab.ai/)

---
## Features
- Automated parsing of legal contracts and agreements
- Clause identification with confidence scoring
- Compliance requirement highlighting
- Multi-document analysis capabilities

## Setup Instructions

**1. Configure Environment:**
```bash
cp .env.example .env
# Add your API keys to the .env file
```

**2. Install Dependencies:**
```bash
# Requires Python 3.11+
pip install llama-index-llms-cleanlab llama-index llama-index-embeddings-huggingface python-dotenv
pip install python-pptx  # For Office document support
```

**3. Run the Application:**
```bash
streamlit run app.py --server.port 8502
```

**4. Usage Examples:**
```bash
# Analyze a single contract
python analyze.py --input lease_agreement.pdf

# Batch process documents
python batch_process.py --dir ./contracts --output analysis_results
```

## Docker Setup

```bash
# Build the Docker image
docker build -t trustworthy-rag .

# Run the container
docker run -p 8502:8502 --env-file .env trustworthy-rag

# Or using docker-compose
docker-compose up
```

> **Note:** Ensure your `.env` file contains:
> - CLEANLAB_API_KEY
> - LLAMA_CLOUD_API_KEY

## Document Support
- PDF Contracts (scanned and digital)
- Microsoft Word (.docx) and PowerPoint (.pptx)
- Markdown legal templates
- Images with embedded text (PNG/JPG)

## Troubleshooting
If you encounter rate limits with LlamaParse:
```python
from llama_parse import LlamaParse

parser = LlamaParse(
    api_key="llx-...",
    result_type="markdown",
    parsing_instruction="legal",  # Special parsing mode for legal docs
    max_timeout=600  # Increase timeout for complex documents
)
```

> **Note:** The TLM confidence threshold can be adjusted in `config/settings.py` to balance precision and recall based on your requirements.

## Understanding Trust Scores

Score | Meaning
---|---
1.0 | System is certain about its response (including "I don't know")
0.8-0.99 | High confidence factual answer  
<0.5 | Potential hallucination - verify with sources

> **Note**: A score of 1 for "I don't know" indicates the system is reliably avoiding speculation, not that the answer is factually correct.
