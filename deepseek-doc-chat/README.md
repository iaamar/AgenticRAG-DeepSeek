# Agentic RAG using CrewAI

This project leverages CrewAI to build an Agentic RAG that can search through your docs and fallback to web search in case it doesn't find the answer in the docs. It has the option to use either deep-seek-r1 or llama 3.2 that runs locally. More details in the Running the app section below!

## Architecture and Flow Diagram

![Flowchart](./assets/Flowchart.jpg)

## Installation and Setup

### Prerequisites

- Docker
- Docker Compose

### Steps

1. **Clone the repository**:

    ```sh
    git clone https://github.com/iaamar/deepseek-doc-chat.git
    cd deepseek-doc-chat
    ```

2. **Build and run the Docker container**:

    ```sh
    docker-compose up --build
    ```

3. **Access the application**:

    Open your web browser and navigate to `http://localhost:8501`.

### Running the App Locally

If you prefer to run the app locally without Docker, follow these steps:

1. **Install Dependencies**:

    Ensure you have Python 3.11 or later installed.

    ```sh
    pip install crewai crewai-tools semantic_text_splitter tokenizers markitdown qdrant-client fastembed
    ```

2. **Run the Streamlit app**:

    ```sh
    streamlit run app_deep_seek.py
    ```

## Project Structure

```plaintext
deepseek-doc-chat/
├── assets/
│   └── deepseek.png
├── src/
│   └── agentic_rag/
│       └── tools/
│           └── custom_tool.py
├── app_deep_seek.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
