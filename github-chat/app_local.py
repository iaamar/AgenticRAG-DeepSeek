import os

import gc
import tempfile
import uuid
import pandas as pd

from gitingest import ingest_async

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
import streamlit as st

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

@st.cache_resource
def load_llm():
    llm = Ollama(model="llama3.2", request_timeout=120.0)
    return llm

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

# Replace the ingest import with:

from github import Github
from llama_index.readers.github import GithubRepositoryReader

def process_with_gitingets(github_url):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)  # Load from env variable
    github_client = Github(GITHUB_TOKEN, base_url="https://github.com") if GITHUB_TOKEN else Github()  # Use token if available
    
    parts = github_url.strip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    
    loader = GithubRepositoryReader(
        github_client=github_client,
        owner=owner,
        repo=repo,
        filter_directories=(["docs", "src"], GithubRepositoryReader.FilterType.INCLUDE),
        filter_file_extensions=([".py", ".md", ".json", ".txt"], GithubRepositoryReader.FilterType.INCLUDE),
        verbose=True,
        concurrent_requests=2
    )
    
    try:
        docs = loader.load_data(branch="main")
    except Exception as e:
        if "API rate limit exceeded" in str(e):
            st.error("GitHub API rate limit exceeded - try again later or use a token")
        else:
            st.error(f"Error loading repository: {str(e)}")
        raise
    content = "\n".join([doc.text for doc in docs])
    return [], [], content if content.strip() else None



with st.sidebar:
    st.header(f"Add your GitHub repository!")
    
    github_url = st.text_input("Enter GitHub repository URL", placeholder="GitHub URL")
    load_repo = st.button("Load Repository")

    if github_url and load_repo:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                st.write("Processing your repository...")
                repo_name = github_url.split('/')[-1]
                file_key = f"{session_id}-{repo_name}"
                
                if file_key not in st.session_state.get('file_cache', {}):

                    if os.path.exists(temp_dir):
                        summary, tree, content = process_with_gitingets(github_url)

                        # Write summary to a markdown file
                        with open("content.md", "w", encoding="utf-8") as f:
                            f.write(content)

                        # Write summary to a markdown file in temp directory
                        content_path = os.path.join(temp_dir, f"{repo_name}_content.md")
                        with open(content_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        loader = SimpleDirectoryReader(
                            input_dir=temp_dir,
                        )
                    else:    
                        st.error('Could not find the file you uploaded, please check again...')
                        st.stop()
                    
                    docs = loader.load_data()

                    # setup llm & embedding model
                    llm=load_llm()
                    embed_model = HuggingFaceEmbedding( model_name="BAAI/bge-large-en-v1.5", trust_remote_code=True)
                    # Creating an index over loaded data
                    print(f"📂 Creating index with {len(docs)} documents")
                    Settings.embed_model = embed_model
                    node_parser = MarkdownNodeParser()
                    index = VectorStoreIndex.from_documents(documents=docs, transformations=[node_parser], show_progress=True)
                    print(f"🔖 Index created with {len(index.docstore.docs)} nodes")

                    # Create the query engine
                    print("🛠️ Creating query engine...")
                    Settings.llm = llm
                    query_engine = index.as_query_engine(streaming=True)
                    
                    # ====== Customise prompt template ======
                    print("📝 Applying custom prompt template")
                    qa_prompt_tmpl_str = (
                    "Context information is below.\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "Given the context information above I want you to think step by step to answer the query in a highly precise and crisp manner focused on the final answer, incase case you don't know the answer say 'I don't know!'.\n"
                    "Query: {query_str}\n"
                    "Answer: "
                    )
                    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

                    query_engine.update_prompts(
                        {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
                    )
                    
                    st.session_state.file_cache[file_key] = query_engine
                else:
                    query_engine = st.session_state.file_cache[file_key]

                # Inform the user that the file is processed and Display the PDF uploaded
                st.success("Ready to Chat!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

col1, col2 = st.columns([6, 1])

with col1:
    st.header(f"Chat with GitHub using RAG </>")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()


# Display chat messages from history on app rerun
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            repo_name = github_url.split('/')[-1]
            file_key = f"{session_id}-{repo_name}"
            query_engine = st.session_state.file_cache.get(file_key)

            if query_engine is None:
                st.error("Please load a repository first!")
                st.stop()

            response = query_engine.query(prompt)
            if hasattr(response, 'response_gen'):
                for chunk in response.response_gen:
                    if isinstance(chunk, str):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
            else:
                full_response = getattr(response, 'response', str(response)) or "I don't know!"
                message_placeholder.markdown(full_response)

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            full_response = "Sorry, I encountered an error."
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
