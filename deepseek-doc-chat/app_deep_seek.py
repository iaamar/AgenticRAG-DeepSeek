import streamlit as st
import os
import tempfile
import gc
import time
import base64
from crewai import Agent, Crew, Process, Task, LLM
from src.agentic_rag.tools.custom_tool import DocumentSearchTool
from src.agentic_rag.tools.custom_tool import FireCrawlWebSearchTool
from crewai_tools import SerperDevTool


@st.cache_resource
def load_llm():
    return LLM(
        model="ollama/deepseek-r1:1.5b",
        base_url="http://localhost:11434"
    )

def create_agents_and_tasks(pdf_tool):
    """Creates a Crew with the given PDF tool (if any) and a web search tool."""
    web_search_tool = FireCrawlWebSearchTool()

    retriever_agent = Agent(
        role="Retrieve relevant information to answer the user query: {query}",
        goal=(
            "Retrieve the most relevant information from the available sources "
            "for the user query: {query}. Always try to use the PDF search tool first. "
            "If you are not able to retrieve the information from the PDF search tool, "
            "then try to use the web search tool."
        ),
        backstory=(
            "You're a meticulous analyst with a keen eye for detail. "
            "You're known for your ability to understand user queries: {query} "
            "and retrieve knowledge from the most suitable knowledge base."
        ),
        verbose=True,
        tools=[t for t in [pdf_tool, web_search_tool] if t],
        llm=load_llm()
    )

    response_synthesizer_agent = Agent(
        role="Response synthesizer agent for the user query: {query}",
        goal=(
            "Synthesize the retrieved information into a concise and coherent response "
            "based on the user query: {query}. If you are not able to retrieve the "
            'information then respond with "I\'m sorry, I couldn\'t find the information '
            'you\'re looking for."'
        ),
        backstory=(
            "You're a skilled communicator with a knack for turning "
            "complex information into clear and concise responses."
        ),
        verbose=True,
        llm=load_llm()
    )

    retrieval_task = Task(
        description=(
            "Retrieve the most relevant information from the available "
            "sources for the user query: {query}"
        ),
        expected_output=(
            "The most relevant information in the form of text as retrieved "
            "from the sources."
        ),
        agent=retriever_agent
    )

    response_task = Task(
        description="Synthesize the final response for the user query: {query}",
        expected_output=(
            "A concise and coherent response based on the retrieved information "
            "from the right source for the user query: {query}. If you are not "
            "able to retrieve the information, then respond with: "
            '"I\'m sorry, I couldn\'t find the information you\'re looking for."'
        ),
        agent=response_synthesizer_agent
    )

    crew = Crew(
        agents=[retriever_agent, response_synthesizer_agent],
        tasks=[retrieval_task, response_task],
        process=Process.sequential,
        verbose=True
    )
    return crew

st.set_page_config(page_title="Agentic RAG")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_tool" not in st.session_state:
    st.session_state.pdf_tool = None

if "crew" not in st.session_state:
    st.session_state.crew = None  

def reset_chat():
    st.session_state.messages = []

    # Delete the temporary file if it exists
    if "temp_file_path" in st.session_state and os.path.exists(st.session_state.temp_file_path):
        os.remove(st.session_state.temp_file_path)
        del st.session_state.temp_file_path  # Remove from session state

    gc.collect()

def display_pdf(file_bytes: bytes, file_name: str):
    """Displays the uploaded PDF in an iframe."""
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe 
        src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" 
        height="600px" 
        type="application/pdf"
    >
    </iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1>Agentic RAG using</h1>", unsafe_allow_html=True)
    st.image("assets/deepseek.png", use_container_width=True)
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # If there's a new file and we haven't set pdf_tool yet...
        if st.session_state.pdf_tool is None:
            # Create a persistent temp file instead of a directory
            temp_fd, temp_file_path = tempfile.mkstemp(suffix=".pdf")
            os.close(temp_fd)  # Close the file descriptor, we only need the path

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            st.session_state.temp_file_path = temp_file_path  # Store path in session

            with st.spinner("Indexing PDF... Please wait..."):
                st.session_state.pdf_tool = DocumentSearchTool(file_path=temp_file_path)
            
            st.success("PDF indexed! Ready to chat.")

        # Optionally display the PDF in the sidebar
        display_pdf(uploaded_file.getvalue(), uploaded_file.name)
    
    st.button("Clear Chat", on_click=reset_chat)


# Render existing conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask a question about your PDF...")

if prompt:
    # 1. Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build or reuse the Crew (only once after PDF is loaded)
    if st.session_state.crew is None:
        st.session_state.crew = create_agents_and_tasks(st.session_state.pdf_tool)

    # 3. Get the response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Get the complete response first
        with st.spinner("Thinking..."):
            inputs = {"query": prompt}
            result = st.session_state.crew.kickoff(inputs=inputs).raw
        
        # Split by lines first to preserve code blocks and other markdown
        lines = result.split('\n')
        for i, line in enumerate(lines):
            full_response += line
            if i < len(lines) - 1:  # Don't add newline to the last line
                full_response += '\n'
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.15)  # Adjust the speed as needed
        
        # Show the final response without the cursor
        message_placeholder.markdown(full_response)

    # 4. Save assistant's message to session
    st.session_state.messages.append({"role": "assistant", "content": result})
