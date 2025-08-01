🧠 AI Math Tutor
An Agentic-RAG System with Self-Improvement
This project is a sophisticated AI Math Tutor built on an advanced Retrieval-Augmented Generation (RAG) architecture. It features an intelligent agent that can dynamically decide how to solve a user's math problem, learn from human feedback, and improve its performance over time.

🚀 Workflow
<p align="center">
  <img src="[https://i.imgur.com/eGkH9fP.jpeg](https://drive.google.com/file/d/1PywF3QKX2DYQOvgQ_DPSo_qzVE_tR6-9/view?usp=sharing)" alt="Math Question Solving Architecture" width="85%">
</p>


✨ Features
Agentic Routing: A core agent built with LangGraph intelligently decides whether to answer a question using its internal knowledge base or to perform a targeted web search.

Hybrid Knowledge Base: Utilizes a Qdrant vector database with a hybrid search approach for fast and accurate retrieval from curated datasets like gsm8k.

Custom KB Creation: Users can dynamically create new knowledge bases by uploading their own PDF documents or pointing to a web-based PDF.

Secure & Curated Web Search: Implements a custom MCP (Model-Controlled Procedure) server that forces the agent to use a pre-approved list of high-quality educational websites (e.g., Khan Academy, WolframAlpha).

Privacy-First Guardrails: Proactively redacts Personally Identifiable Information (PII) from user inputs before they are processed by any LLM.

Human-in-the-Loop (HITL) Learning: A complete feedback loop allows users to correct the agent's mistakes. This feedback is then used by the DSPy library to automatically optimize the agent's core prompting logic.

Modern Tech Stack: Built with a FastAPI backend for high performance and a responsive React frontend with React-Bootstrap.

🏛️ System Architecture
graph TD
    A[User @ React Frontend] --> B{FastAPI Backend};

    subgraph B [FastAPI Backend]
        C[Input Guardrails] --> D{LangGraph Agent};
        D --> E[Retrieve from KB];
        D --> F[Web Search Node];
        E --> G[Generate Solution];
        F --> G;
        G --> H[Output Guardrails];
        H --> I[Final Answer];
    end

    F --> J((MCP Server));
    J --> K[Tavily API];
    K --> L[Internet];

    subgraph HITL [Human-in-the-Loop Optimization]
        M[User Feedback] --> N[feedback.csv];
        O[Optimize Button] --> P{DSPy Optimizer};
        N --> P;
        P --> Q[optimized_prompt.json];
        Q -.-> G;
    end

    style A fill:#cde4ff
    style J fill:#d2ffd2
    style HITL fill:#fff8c4

🛠️ Tech Stack
Backend: Python, FastAPI, LangGraph, DSPy, Qdrant

Frontend: React, React-Bootstrap, Bootstrap

AI & LLMs: SambaNova, Hugging Face datasets

Web Search: Tavily API, FastMCP

Guardrails: Detoxify (Toxicity), Presidio (PII)

Observability: Opik Tracer

🚀 Setup and Installation
1. Prerequisites
Python 3.10+

Node.js 18+ and npm

An active SambaNova API key and a Tavily API key.

2. Backend Setup
Navigate to the backend/ directory:

cd backend

# Install all required Python packages
pip install -r requirements.txt

# Download the necessary model for the PII guardrail
python -m spacy download en_core_web_lg

3. Environment Variables
Create a .env file in the backend/ directory and populate it with your API keys:

SAMBANOVA_API_KEY="your-sambanova-key"
TAVILY_API_KEY="your-tavily-key"
OPIK_API_KEY="your-opik-key"
OPIK_WORKSPACE="your-opik-workspace"

4. Frontend Setup
Navigate to the frontend/ directory:

cd frontend

# Install all required Node.js packages
npm install

▶️ How to Run the Application
The application requires running two backend services and the frontend.

Terminal 1: Start the MCP Server
This server provides the curated web search tools for the agent.

cd backend
python mcp_server.py

This will typically start on http://localhost:8000.

Terminal 2: Start the FastAPI Application
This is the main application server that the frontend interacts with.

cd backend
uvicorn app.main:app --reload --port 8001

This will run on http://localhost:8001.

Terminal 3: Start the React Frontend
cd frontend
npm start

Open your browser to http://localhost:3000 to use the application.

📖 Usage Guide
1. Create a Knowledge Base
The default knowledge bases (gsm8k-base, math500-base) are created automatically the first time you select them and ask a question.

To create a custom KB:

In the sidebar, give your new KB a unique name.

Choose to either upload a PDF from your computer or provide a public URL to a PDF.

Click "Create KB". The process will start in the background.

The new KB will appear in the "Active Knowledge Base" dropdown.

2. Ask a Question
Select your desired knowledge base from the dropdown.

Type your math problem into the input box and press Send.

3. Provide Feedback and Optimize
If the agent's answer is incorrect, click the "👎" button.

In the modal that appears, provide the correct, step-by-step solution and submit.

After collecting feedback, click the "Optimize with Feedback" button.

You must restart the FastAPI server (Terminal 2) after the optimization is complete for the agent to load the new, improved prompt.
