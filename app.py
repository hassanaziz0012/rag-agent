from contextlib import asynccontextmanager
import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from lib.gemini import generate_stream_response
from lib.prompts import build_query_prompt, build_answer_prompt
from main import (
    load_api_key,
    load_or_generate_embeddings,
    get_embedding_model,
    search_paragraphs,
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


@app.websocket("/ws/ask-agent")
async def ask_agent(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("query", "")

            if not query:
                await websocket.send_json(
                    {"type": "error", "message": "No query provided"}
                )
                continue

            rewrite_query_prompt = build_query_prompt(query)
            rewritten_query = generate_response(
                resources["api_key"], rewrite_query_prompt
            )
            print(rewrite_query_prompt)
            print(f"Rewritten: {rewritten_query}")

            if "INVALID_QUERY" in rewritten_query:
                error_msg = 'I am only able to answer questions related to the book "Purpose and Profit" by Dan Koe.'
                await websocket.send_json({"type": "error", "message": error_msg})
                continue

            await websocket.send_json(
                {"type": "rewritten_query", "query": rewritten_query}
            )
            print("reached here #1")
            try:
                results = search_paragraphs(
                    rewritten_query,
                    resources["embedded_paragraphs"],
                    resources["model"],
                )
                print("reached here #2")

                await websocket.send_json(
                    {"type": "search_results", "results": results}
                )
                print("reached here #3")

                prompt = build_answer_prompt(rewritten_query, results)
                stream = generate_stream_response(resources["api_key"], prompt)

                async for chunk in stream:
                    if chunk:
                        await websocket.send_json({"type": "chunk", "content": chunk})

                await websocket.send_json({"type": "done", "success": True})

            except Exception as e:
                print(f"Error during generation: {e}")
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        print("Client disconnected")
