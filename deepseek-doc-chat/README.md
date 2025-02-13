
# Agentic RAG using CrewAI

This project leverages CrewAI to build an Agentic RAG that can search through your docs and fallbacks to web search incase it don't find the answer in the docs, have option to use either of deep-seek-r1 or llama 3.2 that runs locally. More details un Running the app section below!

## Installation and setup

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install crewai crewai-tools semantic_text_splitter tokenizers markitdown qdrant-client fastembed
   ```

**Running the app**:

To use deep-seek-rq use command ``` streamlit run app_deep_seek.py ```

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
