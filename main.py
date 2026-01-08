from google import genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import pickle
import os
import torch


model_name = "thenlper/gte-large"

def load_api_key():
    """Load the Gemini API key from environment variables or Colab."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        from google.colab import userdata
        api_key = userdata.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    return api_key


def load_or_generate_embeddings(embedding_file="embedded_paragraphs.pkl", book_file="book.md"):
    """Load embeddings from file or generate them if not found."""
    try:
        with open(embedding_file, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        print("Embedded paragraphs not found. Generating embeddings...")
        return generate_embeddings(embedding_file, book_file)


def generate_embeddings(embedding_file, book_file):
    """Generate embeddings for paragraphs in the book."""
    model = SentenceTransformer(model_name, trust_remote_code=True)

    with open(book_file, "r") as file:
        book = file.read()

    paragraphs = book.split("\n\n")

    batch_size = 8  # smaller to avoid OOM
    all_embeddings = []

    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i : i + batch_size]
        embeddings = model.encode(batch, batch_size=len(batch), show_progress_bar=False, convert_to_tensor=True)
        # Move to CPU for portable storage
        all_embeddings.extend([e.cpu() for e in embeddings])

    embedded_paragraphs = []
    for i, p in enumerate(paragraphs):
        embedded_paragraphs.append(
            {"id": i, "embedding": all_embeddings[i], "paragraph": p}
        )

    with open(embedding_file, "wb") as file:
        pickle.dump(embedded_paragraphs, file)

    return embedded_paragraphs


def get_embedding_model():
    """Load and return the sentence transformer model."""
    return SentenceTransformer(model_name, trust_remote_code=True)


def search_paragraphs(query, embedded_paragraphs, model, top_k=5):
    """Search for the most relevant paragraphs based on the query."""
    query_embedding = model.encode([query], convert_to_tensor=True).cpu()

    results = []
    for i, paragraph in enumerate(embedded_paragraphs):
        score = torch.cosine_similarity(query_embedding, paragraph["embedding"]).item()
        results.append({"id": i, "paragraph": paragraph["paragraph"], "score": score})

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]


def build_prompt(query, results):
    """Build the prompt for the LLM."""
    return f"""
You are an LLM tasked with answering questions on the book "Purpose and Profit" by Dan Koe.

This is how the author described the book:
```
Transform Your Relationship With Money & Discover Your Life's Work
Money controls most people's lives, but it doesn't have to. Money is only superficial to the superficial. There is, in fact, a way to merge purpose and profit to create a life filled with work you don't want to escape from.
```

I'll give you the search query and the top 5 paragraphs from the book that are most relevant to the user's search query. Your job is to use those 5 paragraphs to answer the user's question as best as you can.

- Do not deviate from the given paragraphs.
- If you don't have an answer, say "I don't know".
- Keep your answer concise and information-dense.

Here is the user's search query:
{query}

Here are the top 5 paragraphs from the book that are most relevant to the user's search query:
{results}
"""


def generate_response(api_key, prompt):
    """Generate a response from the LLM."""
    llm = genai.Client(api_key=api_key)
    resp = llm.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return resp.text


# def main():
#     """Main function to run the RAG pipeline."""
#     print("[1/6] Loading API key...")
#     api_key = load_api_key()
#     print("      API key loaded successfully.")

#     print("[2/6] Loading or generating embeddings...")
#     embedded_paragraphs = load_or_generate_embeddings()
#     print(f"      Loaded {len(embedded_paragraphs)} embedded paragraphs.")

#     print("[3/6] Loading embedding model...")
#     model = get_embedding_model()
#     print("      Embedding model loaded.")

#     print("[4/6] Searching for relevant paragraphs...")
#     query = "What is the purpose of life?"
#     results = search_paragraphs(query, embedded_paragraphs, model)
#     print(f"      Found {len(results)} relevant paragraphs.")

#     print("[5/6] Search results:")
#     for result in results:
#         print(f"      ({result['score']:.4f}) {result['paragraph'][:80]}...")
#         print()

#     print("[6/6] Generating LLM response...")
#     prompt = build_prompt(query, results)
#     response = generate_response(api_key, prompt)
#     print("      Response from the LLM:")
#     print(response)


# if __name__ == "__main__":
#     main()