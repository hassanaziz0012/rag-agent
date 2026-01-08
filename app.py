from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from main import (
    load_api_key,
    load_or_generate_embeddings,
    get_embedding_model,
    search_paragraphs,
    build_prompt,
    generate_response,
)

# Global variables to store resources
resources = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load resources on startup
    print("Loading Gemini API key...")
    resources["api_key"] = load_api_key()
    
    print("Loading embeddings...")
    resources["embedded_paragraphs"] = load_or_generate_embeddings()
    
    print("Loading embedding model...")
    resources["model"] = get_embedding_model()
    
    print("Startup complete. Ready to serve requests.")
    yield
    # Clean up resources on shutdown if needed
    resources.clear()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


class QueryRequest(BaseModel):
    query: str


@app.post("/api/ask-agent")
async def ask_agent(request: QueryRequest):
    query = request.query
    results = search_paragraphs(query, resources["embedded_paragraphs"], resources["model"])
    prompt = build_prompt(query, results)
    response = generate_response(resources["api_key"], prompt)
    return response
