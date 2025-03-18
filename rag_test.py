import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API Key
api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint="https://ai-proxy.lab.epam.com",
    api_version="2024-02-01-preview",
)

# Input text
text = """Abstract— The rapid expansion of digital content, 
particularly multimedia, necessitates efficient and accurate 
information retrieval mechanisms. Traditional search engines 
primarily rely on keyword-based indexing techniques, often 
leading to suboptimal search results due to a lack of contextual 
understanding. This research explores the integration of 
Retrieval-Augmented Generation (RAG) for enhancing 
transcript-based search functionality, replacing traditional 
indexing methods such as Elasticsearch with a dynamic AI-driven pipeline. Utilizing LangChain, LangGraph, and 
ChromaDB, we develop a scalable and context-aware retrieval 
system that processes video transcripts and applies the GPT-3.5-
Turbo model to refine search queries and generate insightful 
responses. The proposed system leverages vector embeddings to 
index and retrieve relevant transcript segments, ensuring high 
semantic accuracy in search results. Our experimental evaluation 
compares the effectiveness of this approach against conventional 
search methods, measuring accuracy, retrieval relevance, and 
user experience. The results demonstrate the superiority of RAG-based retrieval in delivering precise, contextually relevant 
information, paving the way for advanced AI-driven search 
systems.
Keywords—Retrieval-Augmented Generation, LangChain, 
LangGraph, ChromaDB, GPT-3.5-Turbo, Information Retrieval, AI 
Search Engines, Transcript Indexing.
"""

# Correct API call format for Claude Instant v1
response = client.chat.completions.create(
    model="anthropic.claude-instant-v1",  # Using Claude Instant
    messages=[
        {"role": "system", "content": "You are an AI that converts text into slide-friendly summaries."},
        {"role": "user", "content": f"Summarize the following text and split it into slide-friendly content:\n\n{text}"}
    ],
    max_tokens=1024,
)

# Extract and format the response
slides = response.choices[0].message.content.strip().split("\n\n")
print(slides)
