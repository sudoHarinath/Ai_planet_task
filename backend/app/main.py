import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from qdrant_client import QdrantClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import pandas as pd
from .models import KBCreationRequest, QueryRequest, QueryResponse, FeedbackRequest
from .kb_manager import create_new_kb
from .agent import get_agent_executor, is_math_question, anonymize_pii
import nest_asyncio

nest_asyncio.apply()
from .optimizer import run_optimization
# Load environment variables from .env file
load_dotenv()
os.environ['SAMBANOVA_API_KEY'] = os.getenv("SAMBANOVA_API_KEY")
# Create the main FastAPI app instance
app = FastAPI(title="AI Math Tutor API")
import tempfile

# Add CORS middleware to allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Adjust for your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the agent on startup for efficiency
agent_executor = get_agent_executor()

# --- API Endpoints ---

# ... (all other imports)
import glob # NEW: Import glob to scan for directories

# ... (app setup, etc.)

# NEW: Endpoint to list all available knowledge base collections
@app.get("/kb/list")
async def list_knowledge_bases():
    """Scans the storage directory and returns a list of available KB collections."""
    qdrant_path = "./qdrant_data"
    if not os.path.exists(qdrant_path):
        return {"collections": []}
    
    # List subdirectories, which correspond to collection names
    collections = [d for d in os.listdir(qdrant_path) if os.path.isdir(os.path.join(qdrant_path, d))]
    return {"collections": collections}

# ... (all your other endpoints like /kb/create and /agent/ask remain the same)

@app.post("/kb/create", status_code=202)
async def create_knowledge_base(
    background_tasks: BackgroundTasks,
    collection_name: str = Form(...),
    source_type: str = Form(...),
    source_name: str = Form(None),
    file: UploadFile = File(None)
):
    """Endpoint to create a new KB from a dataset, PDF URL, or an uploaded PDF file."""
    
    # FIX: Restructured logic to be more explicit and robust.
    if source_type == 'pdf_file':
        if not file:
            raise HTTPException(status_code=400, detail="source_type 'pdf_file' requires a file upload.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        background_tasks.add_task(create_new_kb, collection_name=collection_name, source_type=source_type, source_name=None, file_path=tmp_path)
        return {"message": f"KB creation for '{collection_name}' from uploaded file started."}

    elif source_type == 'pdf_url':
        if not source_name:
            raise HTTPException(status_code=400, detail="source_type 'pdf_url' requires a source_name (the URL).")
        background_tasks.add_task(create_new_kb, collection_name=collection_name, source_type=source_type, source_name=source_name, file_path=None)
        return {"message": f"KB creation for '{collection_name}' from URL started."}

    elif source_type in ['gsm8k', 'math500']:
        if not source_name:
            raise HTTPException(status_code=400, detail=f"source_name (e.g., 'main') is required for source_type '{source_type}'")
        # FIX: Ensure all arguments for create_new_kb are provided, including file_path=None
        background_tasks.add_task(create_new_kb, collection_name=collection_name, source_type=source_type, source_name=source_name, file_path=None)
        return {"message": f"KB creation for '{collection_name}' from source '{source_type}' started."}
    
    # If none of the above conditions are met, raise a more specific error
    raise HTTPException(status_code=400, detail=f"Invalid source_type '{source_type}'. Must be one of ['gsm8k', 'math500', 'pdf_file', 'pdf_url'].")
# Helper function for dependency injection
def get_qdrant_client():
    return QdrantClient(path="./qdrant_data")


@app.post("/agent/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    """Main endpoint to ask the math tutor a question."""
    # --- Input Guardrails ---
    # 1. Anonymize PII
    anonymized_question = anonymize_pii(request.question)
    
    # 2. Check if the question is about math
    if not is_math_question(anonymized_question):
        raise HTTPException(status_code=400, detail="This is not a math question. Please ask a math-related question.")
        
    # Prepare the initial state for the agent
    initial_state = {
        "original_question": request.question,
        "question": anonymized_question,
        "collection_name": request.collection_name
    }
    
    # Invoke the agent to get the response
    response = agent_executor.invoke(initial_state)
    
    return QueryResponse(answer=response.get("answer"), source=response.get("source"))

@app.post("/feedback/submit")
async def submit_feedback(request: FeedbackRequest):
    """Endpoint to receive and store user feedback."""
    feedback_file = "app/feedback.csv"
    
    # Create new DataFrame for the feedback
    new_feedback = pd.DataFrame([{
        "question": request.question,
        "bad_answer": request.bad_answer,
        "correction": request.correction
    }])
    
    # Append to CSV file, create if it doesn't exist
    if not os.path.exists(feedback_file):
        new_feedback.to_csv(feedback_file, index=False)
    else:
        new_feedback.to_csv(feedback_file, mode='a', header=False, index=False)
        
    return {"message": "Feedback received. Thank you!"}

@app.get("/")
def read_root():
    return {"status": "AI Math Tutor API is running."}


@app.post("/agent/optimize", status_code=202)
async def optimize_agent(background_tasks: BackgroundTasks):
    """Triggers the DSPy optimization process in the background."""
    background_tasks.add_task(run_optimization)
    return {"message": "Agent optimization process has started in the background. The agent will improve on the next server restart."}