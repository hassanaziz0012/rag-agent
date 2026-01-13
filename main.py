from lib.semantic_search import (
    load_or_generate_embeddings,
    get_embedding_model,
    search_paragraphs,
)
from lib.gemini import load_api_key, generate_response
from lib.prompts import build_answer_prompt

def main():
    """Main function to run the RAG pipeline."""
    print("[1/6] Loading API key...")
    api_key = load_api_key()
    print("      API key loaded successfully.")

    print("[2/6] Loading or generating embeddings...")
    embedded_paragraphs = load_or_generate_embeddings()
    print(f"      Loaded {len(embedded_paragraphs)} embedded paragraphs.")

    print("[3/6] Loading embedding model...")
    model = get_embedding_model()
    print("      Embedding model loaded.")

    print("[4/6] Searching for relevant paragraphs...")
    query = "What is the purpose of life?"
    results = search_paragraphs(query, embedded_paragraphs, model)
    print(f"      Found {len(results)} relevant paragraphs.")

    print("[5/6] Search results:")
    for result in results:
        print(f"      ({result['score']:.4f}) {result['paragraph'][:80]}...")
        print()

    print("[6/6] Generating LLM response...")
    prompt = build_answer_prompt(query, results)
    response = generate_response(api_key, prompt)
    print("      Response from the LLM:")
    print(response)


if __name__ == "__main__":
    main()