# AI Trading Research Agent- Mindmap
## High-Level Architecture
User
 ↓
LangGraph Workflow
 ↓
Chatbot Node
 ↓
Tools / Retrieval
 ↓
Research + Analysis
 ↓
Memory Storage
 ↓
Final Response

## Current LangGraph Flow
START
 ↓
chatbot
 ↓
tools
 ↓
chatbot
 ↓
sentiment_node
 ↓
news_agent
 ↓
risk_agent
 ↓
END

## Memory Systems
### 1. Short Term Memory
Memory-Saver + thread_id

Purpose:
- Conversation continuity
- Temporary memory
- session awareness

### 2. Long Term Memory (RAG)
Chroma Vector Database

Purpose:
- semantic research storage
- historical analysis retrieval
- persistent AI memory

## Rag Flow

Research Note
 ↓
Embedding Model
 ↓
Vector Embedding
 ↓
Chroma Vector DB


User Query
 ↓
Embedding Model
 ↓
Query Vector
 ↓
Retriever
 ↓
Similarity Search
 ↓
Relevant Documents
 ↓
LLm COntext
 ↓
Final Response


## Core Components

### LLM
- reasoning engine
- decision making
- response generation


### Embedding Model
- converts text → vectors
- semantic representation


### Chroma DB
- stores vectors
- stores metadata
- persistent semantic memory


### Retriever
- retrieves relevant documents
- abstracts retrieval logic


### Metadata
- structured filtering
- improves retrieval quality


### LangGraph
- workflow orchestration
- node execution management

## Current Folder Structure

project/
│
├── agents/
├── memory/
│   ├── vector_store.py
│   ├── retriever.py
│
├── graphs/
├── tools/
│   ├──market_tools.py
├── schemas/
├── docs/
│   └── mindmap.md
│
└── app.py

## Important Engineering Lessons

- Retriever quality is extremely important
- Metadata improves retrieval quality
- RAG is retrieval system, not reasoning system
- Embeddings store semantic meaning
- Factory functions improve architecture scalability
- MemorySaver ≠ Vector Memory
- Chunking heavily affects RAG quality
- Vector DB persistence means: insert once, retrieve many times not reinsert every execution

## Current Learning Roadmap

[Done]
✔ LangGraph basics
✔ ReAct architecture
✔ Tool calling
✔ MemorySaver
✔ Structured outputs
✔ Multi-agent basics
✔ Vector DB
✔ Retriever architecture


[Current]
→ Chunking
→ Document splitting
→ Retrieval pipelines


[Future]
→ Hybrid Search
→ Reranking
→ Reflection Agents
→ Supervisor Architecture
→ Autonomous Research Workflows


## Questions / Confusions

- How does chunk overlap improve retrieval?
- When should metadata filtering be used?
- How should long-term memory be updated?


