import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field, ConfigDict
from markitdown import MarkItDown
from qdrant_client import QdrantClient
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer
import requests
from crewai_tools import TXTSearchTool
from dotenv import load_dotenv
load_dotenv()

class DocumentSearchToolInput(BaseModel):
    """Input schema for DocumentSearchTool."""
    query: str = Field(..., description="Query to search the document.")

class DocumentSearchTool(BaseTool):
    name: str = "DocumentSearchTool"
    description: str = "Search the document for the given query."
    args_schema: Type[BaseModel] = DocumentSearchToolInput
    
    model_config = ConfigDict(extra="allow")
    def __init__(self, file_path: str):
        """Initialize the searcher with a PDF file path and set up the Qdrant collection."""
        super().__init__()
        self.file_path = file_path
        self.client = QdrantClient(":memory:")  # For small experiments
        self._process_document()

    def _extract_text(self) -> str:
        """Extract raw text from PDF using MarkItDown."""
        md = MarkItDown()
        result = md.convert(self.file_path)
        return result.text_content

    def _create_chunks(self, raw_text: str) -> list:
        """Create semantic chunks from raw text."""
        splitter = TextSplitter.from_huggingface_tokenizer(
            Tokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2"),
        capacity=512)
        return splitter.chunks(raw_text)

    def _process_document(self):
        """Process the document and add chunks to Qdrant collection."""
        raw_text = self._extract_text()
        chunks = self._create_chunks(raw_text)
        docs = [chunk for chunk in chunks]
        metadata = [{"source": os.path.basename(self.file_path)} for _ in range(len(chunks))]
        ids = list(range(len(chunks)))

        self.client.add(
            collection_name="demo_collection",
            documents=docs,
            metadata=metadata,
            ids=ids
        )

    def _run(self, query: str) -> list:
        """Search the document with a query string."""
        relevant_chunks = self.client.query(
            collection_name="demo_collection",
            query_text=query
        )
        docs = [chunk.document for chunk in relevant_chunks]
        separator = "\n___\n"
        return separator.join(docs)


class FireCrawlWebSearchToolInput(BaseModel):
    """Input schema for FireCrawlWebSearchTool."""
    query: str = Field(..., description="Query to search the web.")

class FireCrawlWebSearchTool(BaseTool):
    """A web search tool using FireCrawl API."""
    
    name: str = "FireCrawlWebSearchTool"
    description: str = "Search the web using FireCrawl API for the given query."
    args_schema: Type[BaseModel] = FireCrawlWebSearchToolInput
    api_key: str = os.getenv("FIRECRAWL_API_KEY")
    api_url: str = "https://api.firecrawl.com/search"

    def _run(self, query: str) -> list:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        params = {"q": query, "num": 5}
        response = requests.get(self.api_url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"FireCrawl API Error: {response.text}")
        
        return [{"title": r["title"], "link": r["link"], "snippet": r.get("snippet", "")} 
                for r in response.json().get("results", [])]