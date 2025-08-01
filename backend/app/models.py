#
# This file contains Pydantic models to validate the data for API requests.
#
from pydantic import BaseModel
from typing import Literal

class KBCreationRequest(BaseModel):
    collection_name: str
    source_type: Literal["gsm8k", "math500", "pdf_url"]
    source_name: str # For datasets: 'main'/'test'. For PDF: the actual URL.

class QueryRequest(BaseModel):
    collection_name: str
    question: str

class QueryResponse(BaseModel):
    answer: str
    source: str # To tell the frontend if the answer came from 'Knowledge Base' or 'Web Search'

class FeedbackRequest(BaseModel):
    question: str
    bad_answer: str
    correction: str