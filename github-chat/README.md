
This project leverages GitIngest to parse a GitHub repo in markdown format and the use LlamaIndex for RAG orchestration over it.


## Installation and setup

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install gitingest llama-index llama-index-llms-ollama llama-index-agent-openai llama-index-llms-openai --upgrade --quiet
   ```

**Running**:

Make sure you have Ollama Server running then you can run following command to start the streamlit application ```streamlit run app_local.py```.
