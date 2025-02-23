# src/api/endpoints/rag.py
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from src.config.settings import *
from src.services.prompt_services import PromptServices


class InputData(BaseModel):
    """
    Data model for request validation and parsing
    """
    input_text: str


router = APIRouter()

# Making prompt_services global so we don't need to construct this object for every query
prompt_services = PromptServices(
    OPENAI_API_KEY,
    QDRANT_URL,
    QDRANT_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_GPT_MODEL
)


def get_answer_from_llm(query):
    try:
        embedding = prompt_services.get_embedding(query)
        search_results = prompt_services.get_context(embedding, 1)
        response = prompt_services.get_response_consecutive_points(query, search_results)
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return response


@router.post("/query")
async def ask(question: InputData):
    response = get_answer_from_llm(question.input_text)
    return {"answer": response}


# create a FastAPI application instance
app = FastAPI()
# include a router for organizing routes
app.include_router(router)
