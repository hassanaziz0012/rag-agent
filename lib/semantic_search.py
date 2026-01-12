from sentence_transformers import SentenceTransformer
import pickle
import torch

model_name = "thenlper/gte-large"


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